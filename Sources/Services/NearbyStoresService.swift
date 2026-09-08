import Foundation
import Combine
import CoreLocation
import MapKit

/// コンビニ・ガシャポン設置店を Apple の地図（MapKit）から実行時に検索する。
/// サーバー不要・APIキー不要。ネット接続は必要。
///
/// 注意: MKLocalSearch は 1 リクエストで近い順に十数件しか返さないため、
/// 広い半径では中心＋周囲の複数地点で検索してカバー率を上げている。
/// それでも「その範囲の全店」ではなく「近い順のサンプル」になる。
@MainActor
final class NearbyStoresService: ObservableObject {
    /// レーダー・一覧用（現在地基準）
    @Published private(set) var results: [Shop] = []
    @Published private(set) var isSearching = false

    /// 地図タブ用（表示中の地図の中心・縮尺基準）
    @Published private(set) var mapResults: [Shop] = []
    @Published private(set) var isSearchingMap = false

    private var lastCenter: CLLocationCoordinate2D?
    private var lastRadius: CLLocationDistance = 0
    private var lastMapCenter: CLLocationCoordinate2D?

    private let queries: [ShopCategory: [String]] = [
        .convenience: ["セブン-イレブン", "ファミリーマート", "ローソン", "ミニストップ"],
        .gachapon: ["ガシャポン", "ガチャガチャ", "カプセルトイ"],
    ]
    /// 現在地がこれ以上動いたら自動で再検索
    private let researchThreshold: CLLocationDistance = 300

    var searchableCategories: Set<ShopCategory> { Set(queries.keys) }

    // MARK: - レーダー・一覧（現在地基準）

    func searchIfNeeded(around center: CLLocationCoordinate2D,
                        categories: Set<ShopCategory>,
                        radius: CLLocationDistance) {
        if let last = lastCenter, !results.isEmpty, abs(radius - lastRadius) < 1 {
            let moved = CLLocation(latitude: last.latitude, longitude: last.longitude)
                .distance(from: CLLocation(latitude: center.latitude, longitude: center.longitude))
            if moved < researchThreshold { return }
        }
        force(around: center, categories: categories, radius: radius)
    }

    func force(around center: CLLocationCoordinate2D,
               categories: Set<ShopCategory>,
               radius: CLLocationDistance) {
        let wanted = categories.intersection(searchableCategories)
        guard !wanted.isEmpty else {
            results = []
            lastCenter = nil
            return
        }
        Task {
            isSearching = true
            lastCenter = center
            lastRadius = radius
            results = await performSearch(center: center, categories: wanted, radius: radius)
            isSearching = false
        }
    }

    // MARK: - 地図タブ（表示中の地図基準）

    func searchForMap(around center: CLLocationCoordinate2D,
                      categories: Set<ShopCategory>,
                      radius: CLLocationDistance) {
        let wanted = categories.intersection(searchableCategories)
        guard !wanted.isEmpty else {
            mapResults = []
            lastMapCenter = nil
            return
        }
        Task {
            isSearchingMap = true
            lastMapCenter = center
            mapResults = await performSearch(center: center, categories: wanted, radius: radius)
            isSearchingMap = false
        }
    }

    // MARK: - 共通の検索処理

    private func performSearch(center: CLLocationCoordinate2D,
                               categories: Set<ShopCategory>,
                               radius: CLLocationDistance) async -> [Shop] {
        let origin = CLLocation(latitude: center.latitude, longitude: center.longitude)
        let subCenters = searchCenters(around: center, radius: radius)
        let spanMeters = min(max(radius * 2.0, 1500), 8000)
        let wide = radius > 4000
        let cap = wide ? 35 : 20

        var merged: [Shop] = []

        for category in categories {
            var hits: [(shop: Shop, distance: CLLocationDistance)] = []
            var seen = Set<String>()

            for sub in subCenters {
                let region = MKCoordinateRegion(center: sub,
                                                latitudinalMeters: spanMeters,
                                                longitudinalMeters: spanMeters)
                for term in queries[category] ?? [] {
                    let request = MKLocalSearch.Request()
                    request.naturalLanguageQuery = term
                    request.region = region
                    request.resultTypes = [.pointOfInterest]

                    guard let response = try? await MKLocalSearch(request: request).start() else { continue }

                    for item in response.mapItems {
                        guard let name = item.name else { continue }
                        let coord = item.placemark.coordinate
                        let key = String(format: "%@|%.4f|%.4f", name, coord.latitude, coord.longitude)
                        if !seen.insert(key).inserted { continue }

                        let distance = origin.distance(from: CLLocation(latitude: coord.latitude,
                                                                       longitude: coord.longitude))
                        guard distance <= radius * 1.15 else { continue }

                        var shop = Shop(
                            id: String(format: "live-%@-%.5f-%.5f", category.rawValue, coord.latitude, coord.longitude),
                            name: name,
                            category: category,
                            address: item.placemark.title ?? "",
                            latitude: coord.latitude,
                            longitude: coord.longitude,
                            hours: nil,
                            note: category == .convenience
                                ? "コンビニ限定のちいかわお菓子・グッズが並ぶことがあります（在庫は店舗次第）。"
                                : "ちいかわのカプセルトイが入っている可能性があります（設置状況は店舗次第）。",
                            approxLocation: nil
                        )
                        shop.isLive = true
                        hits.append((shop, distance))
                    }
                }
            }

            hits.sort { $0.distance < $1.distance }
            merged.append(contentsOf: hits.prefix(cap).map(\.shop))
        }

        return merged
    }

    /// 半径が大きいときは中心＋周囲4点で検索してカバー率を上げる
    private func searchCenters(around c: CLLocationCoordinate2D,
                              radius: CLLocationDistance) -> [CLLocationCoordinate2D] {
        guard radius > 4000 else { return [c] }
        let ring = radius * 0.5
        let mPerDegLat = 111_320.0
        let mPerDegLon = 111_320.0 * cos(c.latitude * .pi / 180)
        var pts = [c]
        for bearing in stride(from: 0.0, to: 360.0, by: 90.0) {
            let b = bearing * .pi / 180
            pts.append(CLLocationCoordinate2D(
                latitude: c.latitude + (ring * cos(b)) / mPerDegLat,
                longitude: c.longitude + (ring * sin(b)) / mPerDegLon
            ))
        }
        return pts
    }
}
