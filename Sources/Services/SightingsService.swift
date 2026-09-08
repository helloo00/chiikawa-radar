import Foundation
import Combine

/// `sightings.json`（バックエンド生成）を取得・キャッシュして配信する。
/// URL 未設定のときは同梱サンプルを表示する。
@MainActor
final class SightingsService: ObservableObject {
    @Published private(set) var items: [Sighting] = []
    @Published private(set) var lastUpdated: Date?
    @Published private(set) var isLoading = false
    @Published private(set) var usingSample = false
    @Published var loadError: String?

    static let feedURLKey = "sightingsFeedURL"

    private let cacheURL: URL = {
        let dir = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
        return dir.appendingPathComponent("sightings.json")
    }()

    private var feedURLString: String {
        UserDefaults.standard.string(forKey: Self.feedURLKey) ?? ""
    }

    init() {
        loadCacheOrSample()
    }

    func refresh() async {
        isLoading = true
        defer { isLoading = false }

        guard let url = URL(string: feedURLString.trimmingCharacters(in: .whitespaces)),
              !feedURLString.isEmpty, url.scheme?.hasPrefix("http") == true else {
            loadError = "情報フィードのURLが未設定です（設定タブ）。サンプルを表示中。"
            loadSample()
            return
        }

        do {
            var request = URLRequest(url: url)
            request.cachePolicy = .reloadIgnoringLocalCacheData
            request.timeoutInterval = 20
            let (data, response) = try await URLSession.shared.data(for: request)
            if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
                throw URLError(.badServerResponse)
            }
            let decoded = try Self.decode(data)
            items = Self.sorted(decoded)
            lastUpdated = Date()
            usingSample = false
            loadError = nil
            try? data.write(to: cacheURL)
        } catch {
            loadError = "取得に失敗: \(error.localizedDescription)"
        }
    }

    func filtered(types: Set<SightingType>) -> [Sighting] {
        items.filter { types.contains($0.type) }
    }

    // MARK: - private

    private func loadCacheOrSample() {
        if let data = try? Data(contentsOf: cacheURL),
           let decoded = try? Self.decode(data), !decoded.isEmpty {
            items = Self.sorted(decoded)
            usingSample = false
        } else {
            loadSample()
        }
    }

    private func loadSample() {
        guard let url = Bundle.main.url(forResource: "sightings.sample", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? Self.decode(data) else { return }
        items = Self.sorted(decoded)
        usingSample = true
    }

    private static let isoFractional: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f
    }()
    private static let isoPlain = ISO8601DateFormatter()

    private static func decode(_ data: Data) throws -> [Sighting] {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .custom { d in
            let s = try d.singleValueContainer().decode(String.self)
            if let date = isoPlain.date(from: s) ?? isoFractional.date(from: s) {
                return date
            }
            throw DecodingError.dataCorrupted(.init(codingPath: d.codingPath,
                                                    debugDescription: "bad date: \(s)"))
        }
        if let feed = try? decoder.decode(Feed.self, from: data) { return feed.items }
        return try decoder.decode([Sighting].self, from: data)
    }

    private struct Feed: Codable {
        let items: [Sighting]
    }

    private static func sorted(_ items: [Sighting]) -> [Sighting] {
        items.sorted { $0.date > $1.date }
    }
}
