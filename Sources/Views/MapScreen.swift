import SwiftUI
import MapKit
import CoreLocation

struct MapScreen: View {
    @EnvironmentObject var repo: ShopRepository
    @EnvironmentObject var location: LocationManager
    @EnvironmentObject var nearby: NearbyStoresService

    @State private var camera: MapCameraPosition = .userLocation(fallback: .automatic)
    @State private var selectedShop: Shop?

    /// 画面に映っている地図の領域（再検索ボタン用）
    @State private var currentRegion: MKCoordinateRegion?
    /// 最後に検索した領域・角度（変化量の判定用）
    @State private var searchedRegion: MKCoordinateRegion?
    @State private var searchedHeading: Double = 0

    private var shops: [Shop] {
        repo.visibleShops(withLiveResults: nearby.mapResults)
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 8) {
                CategoryFilterBar()

                Map(position: $camera, selection: $selectedShop) {
                    UserAnnotation()
                    ForEach(shops) { shop in
                        Marker(shop.name, systemImage: shop.category.symbolName, coordinate: shop.coordinate)
                            .tint(shop.category.tint)
                            .tag(shop)
                    }
                }
                .mapControls {
                    MapUserLocationButton()
                    MapCompass()
                    MapScaleView()
                }
                .onMapCameraChange(frequency: .onEnd) { context in
                    currentRegion = context.region
                    maybeSearch(region: context.region, heading: context.camera.heading, force: false)
                }
            }
            .navigationTitle("地図")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        if let region = currentRegion {
                            maybeSearch(region: region, heading: searchedHeading, force: true)
                        } else if let here = location.location {
                            nearby.searchForMap(around: here.coordinate,
                                                categories: repo.enabledCategories,
                                                radius: repo.radarRange)
                        }
                    } label: {
                        if nearby.isSearchingMap {
                            ProgressView()
                        } else {
                            Label("この表示範囲で再検索", systemImage: "arrow.clockwise")
                        }
                    }
                    .disabled(!repo.liveSearchEnabled)
                }
            }
            .sheet(item: $selectedShop) { ShopDetailView(shop: $0) }
        }
    }

    /// 地図の中心・縮尺・角度が十分変わっていたら、その範囲で再検索する
    private func maybeSearch(region: MKCoordinateRegion, heading: Double, force: Bool) {
        guard repo.liveSearchEnabled else { return }
        // ワールドビュー等の極端な広域は無視
        guard region.span.latitudeDelta < 0.5 else { return }

        let spanMeters = region.span.latitudeDelta * 111_000
        let radius = min(max(spanMeters / 2, 300), 4000)

        if !force, let last = searchedRegion {
            let moved = CLLocation(latitude: last.center.latitude, longitude: last.center.longitude)
                .distance(from: CLLocation(latitude: region.center.latitude, longitude: region.center.longitude))
            let lastSpan = last.span.latitudeDelta * 111_000
            let spanChanged = abs(spanMeters - lastSpan) / max(lastSpan, 1) > 0.25
            let headingChanged = abs(heading - searchedHeading) > 20
            let movedEnough = moved > max(radius * 0.3, 150)
            guard movedEnough || spanChanged || headingChanged else { return }
        }

        searchedRegion = region
        searchedHeading = heading
        nearby.searchForMap(around: region.center,
                            categories: repo.enabledCategories,
                            radius: radius)
    }
}
