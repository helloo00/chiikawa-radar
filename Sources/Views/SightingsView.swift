import SwiftUI

struct SightingsView: View {
    @EnvironmentObject var service: SightingsService
    @Environment(\.openURL) private var openURL

    @State private var selectedTypes: Set<SightingType> = Set(SightingType.allCases)

    private var shown: [Sighting] {
        service.filtered(types: selectedTypes)
    }

    var body: some View {
        NavigationStack {
            List {
                if shown.isEmpty {
                    ContentUnavailableView(
                        "情報がありません",
                        systemImage: "newspaper",
                        description: Text(service.loadError ?? "下に引っぱって更新、または設定でフィードURLを登録してください。")
                    )
                    .listRowSeparator(.hidden)
                }
                ForEach(shown) { item in
                    Button {
                        openURL(item.sourceURL)
                    } label: {
                        SightingRow(item: item)
                    }
                    .buttonStyle(.plain)
                }
            }
            .listStyle(.plain)
            .navigationTitle("情報")
            .navigationBarTitleDisplayMode(.inline)
            .safeAreaInset(edge: .top, spacing: 0) {
                VStack(spacing: 6) {
                    typeFilter
                    HStack(spacing: 6) {
                        if service.usingSample {
                            Text("サンプル表示中")
                        } else if let updated = service.lastUpdated {
                            Text("更新 \(updated.formatted(date: .omitted, time: .shortened))")
                        }
                        if service.isLoading { ProgressView().controlSize(.mini) }
                    }
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)
                }
                .padding(.vertical, 6)
                .background(.bar)
            }
            .refreshable { await service.refresh() }
            .task {
                if service.lastUpdated == nil { await service.refresh() }
            }
        }
    }

    private var typeFilter: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(SightingType.allCases) { type in
                    let on = selectedTypes.contains(type)
                    Button {
                        if on { selectedTypes.remove(type) } else { selectedTypes.insert(type) }
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: type.symbolName)
                            Text(type.label)
                        }
                        .font(.footnote.weight(.semibold))
                        .padding(.horizontal, 11)
                        .padding(.vertical, 6)
                        .background(on ? type.tint : Color(.secondarySystemBackground), in: Capsule())
                        .foregroundStyle(on ? Color.white : Color.primary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal)
        }
    }
}

private struct SightingRow: View {
    let item: Sighting

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            HStack(spacing: 6) {
                Label(item.type.label, systemImage: item.type.symbolName)
                    .font(.caption2.weight(.bold))
                    .padding(.horizontal, 7)
                    .padding(.vertical, 3)
                    .background(item.type.tint.opacity(0.16), in: Capsule())
                    .foregroundStyle(item.type.tint)
                Spacer()
                Text(item.date, format: .relative(presentation: .named))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }

            Text(item.title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.primary)
                .lineLimit(3)

            if !item.subtitle.isEmpty {
                Label(item.subtitle, systemImage: item.coordinate != nil ? "mappin.circle.fill" : "tag")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            HStack(spacing: 4) {
                Image(systemName: "link")
                Text(item.sourceName)
                Spacer()
                Image(systemName: "arrow.up.right.square")
            }
            .font(.caption2)
            .foregroundStyle(.tertiary)
        }
        .padding(.vertical, 4)
        .contentShape(Rectangle())
    }
}
