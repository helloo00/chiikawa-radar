import XCTest
import CoreLocation
@testable import ChiikawaRadar

final class GeoMathTests: XCTestCase {
    private let tokyoStation = CLLocationCoordinate2D(latitude: 35.6812, longitude: 139.7671)

    func testBearingDueNorth() {
        let north = CLLocationCoordinate2D(latitude: tokyoStation.latitude + 0.1, longitude: tokyoStation.longitude)
        XCTAssertEqual(GeoMath.bearing(from: tokyoStation, to: north), 0, accuracy: 0.5)
    }

    func testBearingDueEast() {
        let east = CLLocationCoordinate2D(latitude: tokyoStation.latitude, longitude: tokyoStation.longitude + 0.1)
        XCTAssertEqual(GeoMath.bearing(from: tokyoStation, to: east), 90, accuracy: 0.5)
    }

    func testBearingDueSouth() {
        let south = CLLocationCoordinate2D(latitude: tokyoStation.latitude - 0.1, longitude: tokyoStation.longitude)
        XCTAssertEqual(GeoMath.bearing(from: tokyoStation, to: south), 180, accuracy: 0.5)
    }

    func testBearingDueWest() {
        let west = CLLocationCoordinate2D(latitude: tokyoStation.latitude, longitude: tokyoStation.longitude - 0.1)
        XCTAssertEqual(GeoMath.bearing(from: tokyoStation, to: west), 270, accuracy: 0.5)
    }

    /// 同一座標では方位が定義できない (0/360 のどちらでもおかしくない) が、
    /// 少なくとも NaN にならず 0..<360 の範囲に収まることだけ保証する。
    func testBearingSamePointStaysInRange() {
        let bearing = GeoMath.bearing(from: tokyoStation, to: tokyoStation)
        XCTAssertFalse(bearing.isNaN)
        XCTAssertGreaterThanOrEqual(bearing, 0)
        XCTAssertLessThan(bearing, 360)
    }
}
