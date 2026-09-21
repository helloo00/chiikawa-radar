import XCTest
import CoreLocation
@testable import ChiikawaRadar

final class SightingTests: XCTestCase {
    private func makeSighting(chain: String? = nil, area: String? = nil,
                               latitude: Double? = nil, longitude: Double? = nil) -> Sighting {
        Sighting(id: "1", type: .sighting, title: "テスト", summary: nil,
                 chain: chain, area: area, itemName: nil,
                 date: Date(timeIntervalSince1970: 0),
                 sourceName: "Test", sourceURL: URL(string: "https://example.com")!,
                 latitude: latitude, longitude: longitude, confidence: nil)
    }

    func testSubtitleJoinsChainAndArea() {
        XCTAssertEqual(makeSighting(chain: "ローソン", area: "渋谷").subtitle, "ローソン / 渋谷")
    }

    func testSubtitleOmitsMissingParts() {
        XCTAssertEqual(makeSighting(chain: "ローソン", area: nil).subtitle, "ローソン")
        XCTAssertEqual(makeSighting(chain: nil, area: "渋谷").subtitle, "渋谷")
        XCTAssertEqual(makeSighting(chain: nil, area: nil).subtitle, "")
    }

    func testSubtitleOmitsEmptyStrings() {
        // バックエンドが空文字を送ってくることがあるため、nilと同様に無視されるべき
        XCTAssertEqual(makeSighting(chain: "", area: "渋谷").subtitle, "渋谷")
    }

    func testCoordinateRequiresBothLatitudeAndLongitude() {
        XCTAssertNil(makeSighting(latitude: 35.0, longitude: nil).coordinate)
        XCTAssertNil(makeSighting(latitude: nil, longitude: 139.0).coordinate)
        XCTAssertNotNil(makeSighting(latitude: 35.0, longitude: 139.0).coordinate)
    }

    func testDecodesFeedWrapperOrBareArray() throws {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        let bareArrayJSON = """
        [{"id":"1","type":"news","title":"t","date":"2026-09-18T00:00:00Z","sourceName":"s","sourceURL":"https://example.com"}]
        """.data(using: .utf8)!
        let bare = try decoder.decode([Sighting].self, from: bareArrayJSON)
        XCTAssertEqual(bare.count, 1)
        XCTAssertEqual(bare[0].type, .news)
    }
}
