import Foundation
import CoreLocation
import SwiftUI

enum SightingType: String, Codable, CaseIterable, Identifiable {
    case restock    // 入荷・再入荷
    case sighting   // 目撃（買えた・売ってた）
    case release    // 発売・新作
    case kuji       // くじ
    case event      // 催事・POP UP
    case news       // その他ニュース

    var id: String { rawValue }

    var label: String {
        switch self {
        case .restock:  return "入荷"
        case .sighting: return "目撃"
        case .release:  return "発売"
        case .kuji:     return "くじ"
        case .event:    return "催事"
        case .news:     return "ニュース"
        }
    }

    var symbolName: String {
        switch self {
        case .restock:  return "shippingbox.fill"
        case .sighting: return "eye.fill"
        case .release:  return "sparkles"
        case .kuji:     return "ticket.fill"
        case .event:    return "calendar"
        case .news:     return "newspaper.fill"
        }
    }

    var tint: Color {
        switch self {
        case .restock:  return Color(red: 0.36, green: 0.62, blue: 0.33)
        case .sighting: return Color(red: 0.20, green: 0.55, blue: 0.62)
        case .release:  return Color(red: 0.83, green: 0.31, blue: 0.42)
        case .kuji:     return Color(red: 0.55, green: 0.40, blue: 0.75)
        case .event:    return Color(red: 0.90, green: 0.55, blue: 0.20)
        case .news:     return Color(red: 0.45, green: 0.45, blue: 0.50)
        }
    }
}

/// バックエンド（backend/）が生成する 1 件分の情報。
struct Sighting: Identifiable, Codable, Hashable {
    let id: String
    let type: SightingType
    let title: String
    var summary: String?
    var chain: String?      // チェーン/店名（例: ローソン、渋谷ロフト）
    var area: String?       // エリア（例: 渋谷、大阪）
    var itemName: String?   // 品名
    let date: Date
    let sourceName: String  // 例: Bluesky, PR TIMES, ちいかわマーケット
    let sourceURL: URL
    var latitude: Double?
    var longitude: Double?
    var confidence: Double?  // 0.0–1.0（抽出の確からしさ）

    var coordinate: CLLocationCoordinate2D? {
        guard let latitude, let longitude else { return nil }
        return CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }

    var subtitle: String {
        [chain, area].compactMap { $0 }.filter { !$0.isEmpty }.joined(separator: " / ")
    }
}
