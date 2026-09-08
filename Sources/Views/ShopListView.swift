import SwiftUI
import CoreLocation

struct ShopListView: View {
    @EnvironmentObject var repo: ShopRepository
    @EnvironmentObject var location: LocationManager

    var body: some View {
        NavigationStack {
            List {
                Section {
                    CategoryFilterBar()
                        .listRowInsets(EdgeInsets(top: 6, leading: 0, bottom: 6, trailing: 0))
                        .listRowBackground(Color.clear)
                }
                Section {
                    ForEach(sortedShops) { shop in
                        NavigationLink(value: shop) {
                            ShopRow(shop: shop, distance: distance(to: shop))
                        }
                    }
                } footer: {
                    Text("\(sortedShops.count) 店を表示中")
                }
            }
            .navigationTitle("一覧")
            .searchable(text: $repo.searchText, prompt: "店名・住所で検索")
            .navigationDestination(for: Shop.self) { ShopDetailView(shop: $0) }
        }
    }

    private var sortedShops: [Shop] {
        repo.visibleShopsSorted(from: location.location)
    }

    private func distance(to shop: Shop) -> CLLocationDistance? {
        location.location.map { shop.distance(from: $0) }
    }
}

private struct ShopRow: View {
    let shop: Shop
    let distance: CLLocationDistance?

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: shop.category.symbolName)
                .font(.system(size: 14, weight: .bold))
                .foregroundStyle(Color.white)
                .frame(width: 34, height: 34)
                .background(shop.category.tint, in: RoundedRectangle(cornerRadius: 9))

            VStack(alignment: .leading, spacing: 2) {
                Text(shop.name).font(.body.weight(.semibold))
                Text(shop.address).font(.caption).foregroundStyle(.secondary).lineLimit(1)
            }

            Spacer(minLength: 8)

            if let distance {
                Text(distance.shortText)
                    .font(.caption.weight(.semibold).monospacedDigit())
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 2)
    }
}
