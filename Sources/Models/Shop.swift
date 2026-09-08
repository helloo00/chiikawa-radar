import Foundation
import CoreLocation
import SwiftUI

enum ShopCategory: String, Codable, CaseIterable, Identifiable {
    case permanent    // ちいかわらんど等の常設店
    case retailer     // KIDDY LAND / ロフト等の取扱店
    case convenience  // コンビニ（お菓子・くじ等のコラボ）
    case gachapon     // ガシャポン設置店
    case event        // 催事・POP UP

    var id: String { rawValue }

    var label: String {
        switch self {
        case .permanent:   return "常設店"
        case .retailer:    return "取扱店"
        case .convenience: return "コンビニ"
        case .gachapon:    return "ガシャポン"
        case .event:       return "催事"
        }
    }

    var symbolName: String {
        switch self {
        case .permanent:   return "star.fill"
        case .retailer:    return "bag.fill"
        case .convenience: return "cart.fill"
        case .gachapon:    return "circle.grid.2x2.fill"
        case .event:       return "sparkles"
        }
    }

    var tint: Color {
        switch self {
        case .permanent:   return Color(red: 0.83, green: 0.31, blue: 0.42)
        case .retailer:    return Color(red: 0.90, green: 0.55, blue: 0.20)
        case .convenience: return Color(red: 0.36, green: 0.62, blue: 0.33)
        case .gachapon:    return Color(red: 0.20, green: 0.55, blue: 0.62)
        case .event:       return Color(red: 0.55, green: 0.40, blue: 0.75)
        }
    }

    /// 地図検索で動的に集めるカテゴリ（同梱リストではない）
    var isLiveSearched: Bool { self == .convenience || self == .gachapon }
}

struct Shop: Identifiable, Codable, Hashable {
    let id: String
    let name: String
    let category: ShopCategory
    let address: String
    let latitude: Double
    let longitude: Double
    var hours: String?
    var note: String?
    var approxLocation: Bool?
    /// 地図検索で得た候補（同梱データではない）
    var isLive: Bool?

    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }

    func distance(from location: CLLocation) -> CLLocationDistance {
        location.distance(from: CLLocation(latitude: latitude, longitude: longitude))
    }
}

extension CLLocationDistance {
    /// 900 m 未満は 10 m 単位、以降は km 表記
    var shortText: String {
        if self < 900 {
            let rounded = Int((self / 10).rounded()) * 10
            return "\(rounded) m"
        }
        return String(format: "%.1f km", self / 1000)
    }
}
