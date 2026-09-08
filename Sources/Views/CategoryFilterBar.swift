import SwiftUI

/// カテゴリの絞り込みチップ。3タブで共有。
struct CategoryFilterBar: View {
    @EnvironmentObject var repo: ShopRepository

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(ShopCategory.allCases) { category in
                    let on = repo.enabledCategories.contains(category)
                    Button {
                        repo.toggle(category)
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: category.symbolName)
                            Text(category.label)
                        }
                        .font(.footnote.weight(.semibold))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 7)
                        .background(on ? category.tint : Color(.secondarySystemBackground), in: Capsule())
                        .foregroundStyle(on ? Color.white : Color.primary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal)
        }
    }
}
