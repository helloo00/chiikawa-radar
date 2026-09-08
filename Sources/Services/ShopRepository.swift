import Foundation
import Combine
import CoreLocation

/// 同梱 JSON の読み込みとフィルタリング。
final class ShopRepository: ObservableObject {
    @Published private(set) var allShops: [Shop] = []
    /// 地図検索で得たコンビニ・ガシャポン（NearbyStoresService が供給）
    @Published var liveShops: [Shop] = []
    @Published var liveSearchEnabled: Bool = true
    /// レーダーの表示半径（m）。地図検索の範囲もこれに追従する
    @Published var radarRange: Double = 1000
    @Published var enabledCategories: Set<ShopCategory> = Set(ShopCategory.allCases)
    @Published var searchText: String = ""
    @Published var loadError: String?

    init() { reload() }

    func reload() {
        guard let url = Bundle.main.url(forResource: "shops", withExtension: "json") else {
            loadError = "shops.json がバンドルに見つかりません。ターゲットに追加してください。"
            return
        }
        do {
            let data = try Data(contentsOf: url)
            allShops = try JSONDecoder().decode([Shop].self, from: data)
            loadError = nil
        } catch {
            loadError = "shops.json の読み込みに失敗: \(error.localizedDescription)"
        }
    }

    /// 同梱データ ＋ 任意の地図検索結果に、カテゴリ・検索語フィルタを適用
    func visibleShops(withLiveResults live: [Shop]) -> [Shop] {
        let base = liveSearchEnabled ? allShops + live : allShops
        return base
            .filter { enabledCategories.contains($0.category) }
            .filter { matchesSearch($0) }
    }

    /// レーダー・一覧用（現在地基準の地図検索結果を使う）
    var visibleShops: [Shop] {
        visibleShops(withLiveResults: liveShops)
    }

    func visibleShopsSorted(from location: CLLocation?) -> [Shop] {
        guard let location else { return visibleShops }
        return visibleShops.sorted { $0.distance(from: location) < $1.distance(from: location) }
    }

    func toggle(_ category: ShopCategory) {
        if enabledCategories.contains(category) {
            enabledCategories.remove(category)
        } else {
            enabledCategories.insert(category)
        }
    }

    private func matchesSearch(_ shop: Shop) -> Bool {
        guard !searchText.isEmpty else { return true }
        return shop.name.localizedCaseInsensitiveContains(searchText)
            || shop.address.localizedCaseInsensitiveContains(searchText)
    }
}
