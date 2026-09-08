import SwiftUI
import MapKit

struct ShopDetailView: View {
    let shop: Shop
    @EnvironmentObject var location: LocationManager
    @EnvironmentObject var proximity: ProximityMonitor

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Map(initialPosition: .region(MKCoordinateRegion(
                        center: shop.coordinate,
                        span: MKCoordinateSpan(latitudeDelta: 0.01, longitudeDelta: 0.01)
                    ))) {
                        Marker(shop.name, systemImage: shop.category.symbolName, coordinate: shop.coordinate)
                            .tint(shop.category.tint)
                    }
                    .frame(height: 180)
                    .listRowInsets(EdgeInsets())
                }

                Section {
                    LabeledContent("種類") {
                        Label(shop.category.label, systemImage: shop.category.symbolName)
                            .foregroundStyle(shop.category.tint)
                    }
                    LabeledContent("住所", value: shop.address)
                    if let hours = shop.hours {
                        LabeledContent("営業時間", value: hours)
                    }
                    if let distance = location.location.map({ shop.distance(from: $0) }) {
                        LabeledContent("現在地から", value: distance.shortText)
                    }
                    if shop.approxLocation == true {
                        Label("地図上の位置は概算です", systemImage: "exclamationmark.triangle")
                            .font(.footnote)
                            .foregroundStyle(.orange)
                    }
                    if shop.isLive == true {
                        Label("地図の検索結果です。ちいかわグッズの取り扱い・在庫は保証されません。",
                              systemImage: "sparkle.magnifyingglass")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }

                if let note = shop.note, !note.isEmpty {
                    Section("メモ") { Text(note) }
                }

                Section {
                    Button {
                        openInMaps()
                    } label: {
                        Label("Appleマップで開く（徒歩ルート）", systemImage: "arrow.triangle.turn.up.right.diamond")
                    }
                    if proximity.isEnabled {
                        Label(
                            proximity.isMonitoring(shop) ? "近接通知の対象（最寄り20店）" : "近接通知の範囲外",
                            systemImage: proximity.isMonitoring(shop) ? "bell.fill" : "bell.slash"
                        )
                        .foregroundStyle(.secondary)
                        .font(.footnote)
                    }
                }
            }
            .navigationTitle(shop.name)
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    private func openInMaps() {
        let item = MKMapItem(placemark: MKPlacemark(coordinate: shop.coordinate))
        item.name = shop.name
        item.openInMaps(launchOptions: [MKLaunchOptionsDirectionsModeKey: MKLaunchOptionsDirectionsModeWalking])
    }
}
