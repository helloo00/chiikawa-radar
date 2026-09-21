import XCTest
import CoreLocation
@testable import ChiikawaRadar

final class ShopTests: XCTestCase {
    func testShortTextUsesMetersBelow900() {
        XCTAssertEqual(CLLocationDistance(0).shortText, "0 m")
        XCTAssertEqual(CLLocationDistance(123).shortText, "120 m")   // 10m単位に丸め
        XCTAssertEqual(CLLocationDistance(899).shortText, "900 m")
    }

    func testShortTextUsesKilometersAt900AndAbove() {
        XCTAssertEqual(CLLocationDistance(900).shortText, "0.9 km")
        XCTAssertEqual(CLLocationDistance(1500).shortText, "1.5 km")
        XCTAssertEqual(CLLocationDistance(12345).shortText, "12.3 km")
    }

    func testShopDecodesFromBundledJSON() throws {
        let json = """
        {"id":"x","name":"テスト店","category":"permanent","address":"どこか","latitude":35.0,"longitude":139.0}
        """.data(using: .utf8)!
        let shop = try JSONDecoder().decode(Shop.self, from: json)
        XCTAssertEqual(shop.category, .permanent)
        XCTAssertNil(shop.hours)
        XCTAssertNil(shop.approxLocation)
    }
}
