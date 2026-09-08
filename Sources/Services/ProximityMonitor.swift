import Foundation
import Combine
import CoreLocation
import UserNotifications

/// 取扱店に近づいたらローカル通知を出す。iOS の region monitoring を使用。
final class ProximityMonitor: NSObject, ObservableObject {
    private let manager = CLLocationManager()
    private var shopsByRegionID: [String: Shop] = [:]

    @Published private(set) var isEnabled = false
    @Published private(set) var monitoredCount = 0

    /// 監視円の半径（メートル）
    let triggerRadius: CLLocationDistance = 150
    /// iOS のリージョン監視上限
    let maxRegions = 20

    override init() {
        super.init()
        manager.delegate = self
    }

    func enable(shops: [Shop], near location: CLLocation?) {
        manager.requestAlwaysAuthorization()
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { _, _ in }
        isEnabled = true
        if let location {
            rebuildRegions(shops: shops, near: location)
        }
    }

    func disable() {
        isEnabled = false
        for region in manager.monitoredRegions {
            manager.stopMonitoring(for: region)
        }
        shopsByRegionID.removeAll()
        monitoredCount = 0
    }

    func refreshIfEnabled(shops: [Shop], near location: CLLocation) {
        guard isEnabled else { return }
        rebuildRegions(shops: shops, near: location)
    }

    func isMonitoring(_ shop: Shop) -> Bool {
        shopsByRegionID[shop.id] != nil
    }

    private func rebuildRegions(shops: [Shop], near location: CLLocation) {
        let nearest = shops
            .sorted { $0.distance(from: location) < $1.distance(from: location) }
            .prefix(maxRegions)
        let wantedIDs = Set(nearest.map(\.id))

        for region in manager.monitoredRegions where !wantedIDs.contains(region.identifier) {
            manager.stopMonitoring(for: region)
        }
        let currentIDs = Set(manager.monitoredRegions.map(\.identifier))

        shopsByRegionID = Dictionary(uniqueKeysWithValues: nearest.map { ($0.id, $0) })

        for shop in nearest where !currentIDs.contains(shop.id) {
            let region = CLCircularRegion(center: shop.coordinate,
                                          radius: triggerRadius,
                                          identifier: shop.id)
            region.notifyOnEntry = true
            region.notifyOnExit = false
            manager.startMonitoring(for: region)
        }
        monitoredCount = shopsByRegionID.count
    }
}

extension ProximityMonitor: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        guard let shop = shopsByRegionID[region.identifier] else { return }
        let content = UNMutableNotificationContent()
        content.title = "近くにちいかわグッズ！"
        content.body = "\(shop.name)（\(shop.category.label)）が近くにあります"
        content.sound = .default
        let request = UNNotificationRequest(identifier: "enter-\(shop.id)", content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }
}
