import SwiftUI

struct RootView: View {
    @StateObject private var repo = ShopRepository()
    @StateObject private var location = LocationManager()
    @StateObject private var proximity = ProximityMonitor()
    @StateObject private var nearby = NearbyStoresService()
    @StateObject private var sightings = SightingsService()
    @AppStorage("selectedTab") private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            RadarView()
                .tabItem { Label("レーダー", systemImage: "dot.radiowaves.up.forward") }
                .tag(0)
            MapScreen()
                .tabItem { Label("地図", systemImage: "map") }
                .tag(1)
            ShopListView()
                .tabItem { Label("一覧", systemImage: "list.bullet") }
                .tag(2)
            SightingsView()
                .tabItem { Label("情報", systemImage: "newspaper") }
                .tag(3)
            SettingsView()
                .tabItem { Label("設定", systemImage: "gearshape") }
                .tag(4)
        }
        .tint(Color(red: 0.83, green: 0.31, blue: 0.42))
        .environmentObject(repo)
        .environmentObject(location)
        .environmentObject(proximity)
        .environmentObject(nearby)
        .environmentObject(sightings)
        .task { location.requestWhenInUse() }
        .onReceive(location.$location) { fix in
            guard let fix else { return }
            proximity.refreshIfEnabled(shops: repo.allShops, near: fix)
            if repo.liveSearchEnabled {
                nearby.searchIfNeeded(around: fix.coordinate,
                                      categories: repo.enabledCategories,
                                      radius: repo.radarRange)
            }
        }
        .onReceive(nearby.$results) { repo.liveShops = $0 }
        .onChange(of: repo.enabledCategories) { _, categories in
            guard repo.liveSearchEnabled, let here = location.location else { return }
            nearby.searchIfNeeded(around: here.coordinate, categories: categories, radius: repo.radarRange)
        }
        .onChange(of: repo.radarRange) { _, range in
            guard repo.liveSearchEnabled, let here = location.location else { return }
            nearby.force(around: here.coordinate, categories: repo.enabledCategories, radius: range)
        }
        .onChange(of: repo.liveSearchEnabled) { _, enabled in
            if enabled, let here = location.location {
                nearby.force(around: here.coordinate, categories: repo.enabledCategories, radius: repo.radarRange)
            }
        }
    }
}
