import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var repo: ShopRepository
    @EnvironmentObject var location: LocationManager
    @EnvironmentObject var proximity: ProximityMonitor
    @EnvironmentObject var nearby: NearbyStoresService
    @EnvironmentObject var sightings: SightingsService

    @AppStorage(SightingsService.feedURLKey) private var feedURL = ""

    var body: some View {
        NavigationStack {
            List {
                Section("位置情報") {
                    LabeledContent("許可の状態", value: authText)
                    if !location.isAuthorized {
                        Button("位置情報を許可する") { location.requestWhenInUse() }
                    }
                }

                Section {
                    Toggle("取扱店に近づいたら通知", isOn: Binding(
                        get: { proximity.isEnabled },
                        set: { on in
                            if on {
                                proximity.enable(shops: repo.allShops, near: location.location)
                            } else {
                                proximity.disable()
                            }
                        }
                    ))
                    if proximity.isEnabled {
                        LabeledContent("監視中の店", value: "\(proximity.monitoredCount) / \(proximity.maxRegions)")
                    }
                } header: {
                    Text("近接通知")
                } footer: {
                    Text("「常に許可」と通知の許可が必要です。iOS の制限により、現在地から近い順に最大 \(proximity.maxRegions) 店を半径 \(Int(proximity.triggerRadius)) m で監視します。")
                }

                Section {
                    Toggle("コンビニ・ガシャポンを地図から探す", isOn: $repo.liveSearchEnabled)
                    if repo.liveSearchEnabled {
                        Button {
                            if let here = location.location {
                                nearby.force(around: here.coordinate,
                                             categories: repo.enabledCategories,
                                             radius: repo.radarRange)
                            }
                        } label: {
                            Label("現在地周辺を再検索", systemImage: "arrow.clockwise")
                        }
                        .disabled(location.location == nil || nearby.isSearching)
                        LabeledContent("検索でヒットした候補", value: "\(repo.liveShops.count) 件")
                    }
                } header: {
                    Text("周辺スポットの自動検索")
                } footer: {
                    Text("Apple の地図から、近くのコンビニ（お菓子・くじのコラボ）とガシャポン設置店を探して表示します（要インターネット）。ちいかわグッズの取り扱い・在庫は保証されません。多すぎる場合はカテゴリのチップでオフに、またはここでオフにできます。")
                }

                Section {
                    LabeledContent("収録店舗数", value: "\(repo.allShops.count) 店")
                    if let error = repo.loadError {
                        Label(error, systemImage: "exclamationmark.triangle").foregroundStyle(.red)
                    }
                } header: {
                    Text("データ")
                } footer: {
                    Text("同梱の店舗リストと座標はプロトタイプ用の概算です（2026年9月時点）。最新の営業状況・取扱の有無は各店の公式情報をご確認ください。Resources/shops.json を編集すると店を追加・修正できます。")
                }

                Section {
                    TextField("https://…/sightings.json", text: $feedURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                        .font(.footnote)
                    Button {
                        Task { await sightings.refresh() }
                    } label: {
                        if sightings.isLoading {
                            HStack { Text("更新中"); ProgressView() }
                        } else {
                            Label("今すぐ更新", systemImage: "arrow.clockwise")
                        }
                    }
                    .disabled(sightings.isLoading)
                    LabeledContent("件数", value: "\(sightings.items.count)\(sightings.usingSample ? "（サンプル）" : "")")
                    if let updated = sightings.lastUpdated {
                        LabeledContent("最終更新", value: updated.formatted(date: .abbreviated, time: .shortened))
                    }
                    if let error = sightings.loadError {
                        Label(error, systemImage: "exclamationmark.triangle")
                            .font(.footnote)
                            .foregroundStyle(.orange)
                    }
                } header: {
                    Text("情報フィード（目撃・入荷・発売）")
                } footer: {
                    Text("backend/ を GitHub Actions で動かすと sightings.json が生成されます。その raw URL をここに貼ってください。未設定の間は同梱サンプルを表示します。")
                }

                Section("このアプリについて") {
                    Text("ちいかわレーダー プロトタイプ")
                    Text("オフライン動作・サーバー不要。地図は Apple の MapKit を使用しています。")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("設定")
        }
    }

    private var authText: String {
        switch location.authorizationStatus {
        case .authorizedAlways:    return "常に許可"
        case .authorizedWhenInUse: return "使用中のみ許可"
        case .denied:              return "拒否"
        case .restricted:          return "制限"
        case .notDetermined:       return "未設定"
        @unknown default:          return "不明"
        }
    }
}
