import SwiftUI
import CoreLocation
import MapKit

struct RadarView: View {
    @EnvironmentObject var repo: ShopRepository
    @EnvironmentObject var location: LocationManager
    @EnvironmentObject var nearby: NearbyStoresService
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @AppStorage("radarShowMap") private var showMap = false
    /// true = 端末の向きに追従（ヘディングアップ）、false = 北固定（ノースアップ）
    @AppStorage("radarHeadingUp") private var headingUp = true
    @State private var selected: Shop?

    private let ranges: [Double] = [500, 1000]
    private var rangeMeters: Double { repo.radarRange }

    private var headingDegrees: Double {
        guard let heading = location.heading else { return 0 }
        return heading.trueHeading >= 0 ? heading.trueHeading : heading.magneticHeading
    }

    /// 画面の「上」が真北から何度回っているか（0 = 北が上）
    private var screenRotation: Double {
        guard headingUp, location.heading != nil else { return 0 }
        return (headingDegrees / 3).rounded() * 3   // 細かい揺れを抑える
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                Picker("表示範囲", selection: $repo.radarRange) {
                    ForEach(ranges, id: \.self) { Text(rangeLabel($0)).tag($0) }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)

                CategoryFilterBar()

                GeometryReader { geo in
                    let side = min(geo.size.width, geo.size.height) - 16
                    ZStack {
                        if showMap, let here = location.location {
                            Map(position: .constant(mapCamera(here)), interactionModes: [])
                                .mapStyle(.standard(pointsOfInterest: .excludingAll))
                                .frame(width: side, height: side)
                                .clipShape(Circle())
                                .overlay(Circle().fill(Color(.systemBackground).opacity(0.22)))
                                .overlay(Circle().strokeBorder(Color.primary.opacity(0.15), lineWidth: 1))
                                .allowsHitTesting(false)
                        }

                        ZStack {
                            RadarDial(reduceMotion: reduceMotion, overMap: showMap)
                                .frame(width: side, height: side)

                            ForEach(blips) { blip in
                                let p = blip.point(radarRadius: side / 2, mapAligned: showMap)
                                Button {
                                    selected = blip.shop
                                } label: {
                                    BlipView(category: blip.shop.category)
                                        .rotationEffect(.degrees(screenRotation))   // アイコンは常に正立
                                }
                                .buttonStyle(.plain)
                                .offset(x: p.x, y: p.y)
                            }

                            userMarker
                        }
                        .frame(width: geo.size.width, height: geo.size.height)
                        .rotationEffect(.degrees(-screenRotation))
                        .animation(.easeOut(duration: 0.2), value: screenRotation)
                    }
                    .frame(width: geo.size.width, height: geo.size.height)
                }

                statusLine
            }
            .padding(.vertical, 8)
            .navigationTitle("ちいかわレーダー")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItemGroup(placement: .topBarTrailing) {
                    Button {
                        headingUp.toggle()
                    } label: {
                        Image(systemName: headingUp ? "location.fill" : "location.north.line.fill")
                    }
                    .accessibilityLabel(headingUp ? "北固定にする" : "端末の向きに合わせる")

                    Button {
                        showMap.toggle()
                    } label: {
                        Image(systemName: showMap ? "map.fill" : "map")
                    }
                    .accessibilityLabel(showMap ? "地図を隠す" : "地図を表示")

                    Button {
                        if let here = location.location {
                            nearby.force(around: here.coordinate,
                                         categories: repo.enabledCategories,
                                         radius: repo.radarRange)
                        }
                    } label: {
                        if nearby.isSearching {
                            ProgressView()
                        } else {
                            Image(systemName: "arrow.clockwise")
                        }
                    }
                    .disabled(location.location == nil || !repo.liveSearchEnabled)
                }
            }
            .sheet(item: $selected) { ShopDetailView(shop: $0) }
        }
    }

    private func mapCamera(_ here: CLLocation) -> MapCameraPosition {
        .camera(MapCamera(
            centerCoordinate: here.coordinate,
            distance: repo.radarRange * 2.1,
            heading: screenRotation,
            pitch: 0
        ))
    }

    @ViewBuilder
    private var userMarker: some View {
        ZStack {
            if location.heading != nil {
                ZStack {
                    Color.clear.frame(width: 1, height: 1)
                    Image(systemName: "location.north.fill")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundStyle(Color.blue)
                        .offset(y: -20)
                }
                .rotationEffect(.degrees(headingDegrees))
                .animation(.easeOut(duration: 0.2), value: headingDegrees)
            }
            Circle()
                .fill(Color.blue)
                .frame(width: 14, height: 14)
                .overlay(Circle().stroke(Color.white, lineWidth: 2))
        }
    }

    private var statusLine: some View {
        VStack(spacing: 2) {
            if !location.isAuthorized {
                Text("位置情報を許可すると現在地からの方角と距離が表示されます")
            } else if location.location == nil {
                Text("現在地を取得中…")
            } else {
                Text("範囲 \(rangeLabel(rangeMeters)) 内に \(blips.count) 店")
                if headingUp && location.heading == nil {
                    Text("※ 端末の向きは実機のコンパスで表示（シミュレータは北固定）")
                        .font(.caption2)
                }
            }
        }
        .font(.caption)
        .foregroundStyle(.secondary)
        .multilineTextAlignment(.center)
        .padding(.horizontal)
    }

    private var blips: [Blip] {
        guard let here = location.location else { return [] }
        return repo.visibleShops.compactMap { shop in
            let d = shop.distance(from: here)
            guard d <= rangeMeters else { return nil }
            let bearing = GeoMath.bearing(from: here.coordinate, to: shop.coordinate)
            return Blip(shop: shop, distance: d, bearing: bearing, range: rangeMeters)
        }
    }

    private func rangeLabel(_ meters: Double) -> String {
        meters < 1000 ? "\(Int(meters)) m" : "\(Int(meters / 1000)) km"
    }
}

private struct Blip: Identifiable {
    let shop: Shop
    let distance: Double
    let bearing: Double
    let range: Double

    var id: String { shop.id }

    /// レーダー中心からのオフセット（真北基準。画面の回転は親の rotationEffect が担当）。
    /// mapAligned=true: 距離に比例（地図上の実際の位置に一致）。
    /// mapAligned=false: 近距離を外へ広げるカーブ＋角度ジッターで団子を防ぐ。
    func point(radarRadius: CGFloat, mapAligned: Bool) -> CGPoint {
        let frac = min(max(distance / range, 0), 1)
        let r: CGFloat
        let a: Double
        if mapAligned {
            r = radarRadius * CGFloat(frac)
            a = bearing * .pi / 180
        } else {
            let curved = pow(frac, 0.55)
            r = radarRadius * CGFloat(0.12 + 0.86 * curved)
            let jitter = (Double(abs(shop.id.hashValue % 1000)) / 1000.0 - 0.5) * (10 * .pi / 180)
            a = bearing * .pi / 180 + jitter
        }
        return CGPoint(x: r * sin(a), y: -r * cos(a))
    }
}

private struct BlipView: View {
    let category: ShopCategory

    var body: some View {
        Image(systemName: category.symbolName)
            .font(.system(size: 12, weight: .bold))
            .foregroundStyle(Color.white)
            .padding(6)
            .background(category.tint, in: Circle())
            .overlay(Circle().stroke(Color.white, lineWidth: 1.5))
            .shadow(radius: 2)
    }
}

private struct RadarDial: View {
    let reduceMotion: Bool
    var overMap: Bool = false

    var body: some View {
        TimelineView(.animation(minimumInterval: reduceMotion ? 3600 : 1.0 / 30.0)) { context in
            Canvas { ctx, size in
                let c = CGPoint(x: size.width / 2, y: size.height / 2)
                let radius = min(size.width, size.height) / 2
                let ring = overMap ? Color.primary.opacity(0.35) : Color.green.opacity(0.35)
                let axis = overMap ? Color.primary.opacity(0.22) : Color.green.opacity(0.25)

                for i in 1...3 {
                    let rr = radius * CGFloat(i) / 3
                    let rect = CGRect(x: c.x - rr, y: c.y - rr, width: rr * 2, height: rr * 2)
                    ctx.stroke(Path(ellipseIn: rect), with: .color(ring), lineWidth: 1)
                }

                var cross = Path()
                cross.move(to: CGPoint(x: c.x - radius, y: c.y))
                cross.addLine(to: CGPoint(x: c.x + radius, y: c.y))
                cross.move(to: CGPoint(x: c.x, y: c.y - radius))
                cross.addLine(to: CGPoint(x: c.x, y: c.y + radius))
                ctx.stroke(cross, with: .color(axis), lineWidth: 1)

                if !reduceMotion && !overMap {
                    let t = context.date.timeIntervalSinceReferenceDate
                    let angle = (t.truncatingRemainder(dividingBy: 4) / 4) * 2 * .pi - .pi / 2
                    var sweep = Path()
                    sweep.move(to: c)
                    sweep.addArc(center: c, radius: radius,
                                 startAngle: .radians(angle - 0.6),
                                 endAngle: .radians(angle),
                                 clockwise: false)
                    sweep.closeSubpath()
                    ctx.fill(sweep, with: .radialGradient(
                        Gradient(colors: [Color.green.opacity(0.28), Color.green.opacity(0.0)]),
                        center: c, startRadius: 0, endRadius: radius))
                }

                let north = Text("N").font(.caption2.bold())
                    .foregroundColor(overMap ? .primary : .green)
                ctx.draw(north, at: CGPoint(x: c.x, y: c.y - radius + 10))
            }
        }
        .background(overMap ? Color.clear : Color.green.opacity(0.06), in: Circle())
    }
}
