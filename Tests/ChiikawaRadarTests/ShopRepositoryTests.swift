import XCTest
@testable import ChiikawaRadar

/// ShopRepository はテスト用に依存注入できる作りになっていないため、
/// 同梱の Resources/shops.json（実データ）に対してフィルタロジックだけを検証する。
final class ShopRepositoryTests: XCTestCase {
    func testAllShopsLoadFromBundledJSON() {
        let repo = ShopRepository()
        XCTAssertNil(repo.loadError)
        XCTAssertFalse(repo.allShops.isEmpty)
    }

    func testTogglingCategoryOffExcludesItFromVisibleShops() {
        let repo = ShopRepository()
        XCTAssertTrue(repo.allShops.contains { $0.category == .permanent },
                      "テスト前提: 常設店(permanent)が同梱データに1件以上あること")

        repo.toggle(.permanent)
        XCTAssertFalse(repo.enabledCategories.contains(.permanent))
        XCTAssertFalse(repo.visibleShops(withLiveResults: []).contains { $0.category == .permanent })

        repo.toggle(.permanent)
        XCTAssertTrue(repo.enabledCategories.contains(.permanent))
    }

    func testSearchTextFiltersByNameOrAddress() {
        let repo = ShopRepository()
        let target = repo.allShops.first { $0.category == .permanent }
        XCTAssertNotNil(target, "テスト前提: 常設店が1件以上あること")

        repo.searchText = String(target!.name.prefix(4))
        XCTAssertTrue(repo.visibleShops(withLiveResults: []).contains { $0.id == target!.id })

        repo.searchText = "存在しないはずの検索語xyz123"
        XCTAssertTrue(repo.visibleShops(withLiveResults: []).isEmpty)
    }

    func testLiveSearchDisabledExcludesLiveResults() {
        let repo = ShopRepository()
        let liveShop = Shop(id: "live-1", name: "ライブ検索の候補店", category: .convenience,
                             address: "テスト", latitude: 35.0, longitude: 139.0,
                             hours: nil, note: nil, approxLocation: nil, isLive: true)

        repo.liveSearchEnabled = true
        XCTAssertTrue(repo.visibleShops(withLiveResults: [liveShop]).contains { $0.id == "live-1" })

        repo.liveSearchEnabled = false
        XCTAssertFalse(repo.visibleShops(withLiveResults: [liveShop]).contains { $0.id == "live-1" })
    }
}
