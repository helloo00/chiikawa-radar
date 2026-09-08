# ちいかわレーダー（プロトタイプ）

現在地の近くで「ちいかわグッズ」を扱っている場所を、**レーダー / 地図 / 一覧**で確認できる iOS アプリのプロトタイプ。

- オフライン動作・**サーバー不要・API キー不要**（地図は Apple MapKit）
- 収録データはアプリ同梱の `Resources/shops.json`
  （ちいかわらんど等の常設店＋主要取扱店＋ガシャポン拠点＋催事、計 23 件）
- SNS 連携なし

---

## 必要環境

- macOS + **Xcode 15 以降**、ターゲット **iOS 17 以降**
- レーダーの方角表示と近接通知は **実機が必要**（シミュレータはコンパス非対応）

---

## セットアップ（約5分）

1. **Xcode → File → New → Project → iOS → App**
   - Product Name: `ChiikawaRadar`
   - Interface: **SwiftUI** / Language: **Swift** / Storage: **None**
   - Minimum Deployments: **iOS 17.0**
2. 自動生成された `ContentView.swift` を削除。
   自動生成の `ChiikawaRadarApp.swift` は、この `Sources/ChiikawaRadarApp.swift` で置き換える。
3. Finder から **`Sources/` 内の全 `.swift`** と **`Resources/shops.json`** をプロジェクトナビゲータへドラッグ。
   - "Copy items if needed" ✔ / "Create groups" ✔ / Target: `ChiikawaRadar` ✔
   - `shops.json` が **Build Phases → Copy Bundle Resources** に入っているか確認
4. ターゲット → **Info** タブに次の2キーを追加：

   | Key | 値（例） |
   |---|---|
   | `Privacy - Location When In Use Usage Description`<br>(`NSLocationWhenInUseUsageDescription`) | 近くのちいかわグッズ取扱店を探すために位置情報を使います。 |
   | `Privacy - Location Always and When In Use Usage Description`<br>(`NSLocationAlwaysAndWhenInUseUsageDescription`) | 取扱店に近づいたときに通知するため、位置情報を使います。 |

5. **Signing & Capabilities** で自分の Team を選択。
6. 実機（またはシミュレータ）を選んで **Run**。

---

## 使い方

| タブ | 内容 |
|---|---|
| **レーダー** | 中心が現在地。リング外周＝選択した表示範囲（1 / 3 / 10 km）。ブリップをタップで詳細。実機では端末の向きが「上」になる。 |
| **地図** | 取扱店をピン表示。カテゴリごとに色分け。ピンをタップで詳細。 |
| **一覧** | 現在地から近い順。上部チップでカテゴリ絞り込み、検索対応。 |
| **設定** | 位置情報の許可、近接通知の ON/OFF。 |

**近接通知**：設定でオンにすると「常に許可」＋通知許可を要求し、現在地から近い順に最大 20 店を半径 150 m で監視。エリアに入ると「近くにちいかわグッズ！」とローカル通知。

---

## データの更新・追加

`Resources/shops.json` を編集するだけ。1 件の形式：

```json
{
  "id": "unique-id",
  "name": "店名",
  "category": "permanent | retailer | gachapon | event",
  "address": "住所",
  "latitude": 35.0,
  "longitude": 139.0,
  "hours": "11:00–21:00",
  "note": "備考（不要なら null）",
  "approxLocation": true
}
```

- `permanent`=常設店 / `retailer`=取扱店 / `gachapon`=ガシャポン専門店 / `event`=催事

---

## 制限・注意

- 同梱の店舗リストと**座標は 2026 年 9 月時点の概算**。営業状況・取扱の有無は各店の公式で要確認。
- 「今その店にちいかわ在庫があるか」までは分からない（“取扱の可能性がある場所” のリスト）。
- 近接通知は iOS の region monitoring を使用。1 アプリ最大 20 リージョンのため近い順に絞って監視。
- **シミュレータでは方角が北固定**（`Features → Location` で移動をシミュレートは可能）。

---

## 次の一歩（拡張案）

- `MKLocalSearch` で店名から座標を実行時取得して精度アップ
- 「行った / 見た」をオンデバイス保存するユーザー投稿
- 公式カレンダー（催事・発売日）の取り込み
- ウィジェット化（最寄りの取扱店を常時表示）

---

## ファイル構成

```
ChiikawaRadar/
├── README.md
├── Resources/
│   └── shops.json           … 収録データ（編集して拡張可）
└── Sources/
    ├── ChiikawaRadarApp.swift   … エントリポイント + 通知デリゲート
    ├── Models/
    │   ├── Shop.swift            … Shop / ShopCategory / 距離表示
    │   └── GeoMath.swift         … 2点間の方位計算
    ├── Services/
    │   ├── LocationManager.swift … 現在地・ヘディング配信
    │   ├── ProximityMonitor.swift… 近接通知（region monitoring）
    │   └── ShopRepository.swift  … JSON 読み込み・フィルタ
    └── Views/
        ├── RootView.swift        … TabView と依存性注入
        ├── RadarView.swift       … レーダー描画（Canvas）
        ├── MapScreen.swift       … MapKit 地図
        ├── ShopListView.swift    … 距離順リスト
        ├── ShopDetailView.swift  … 店の詳細 + Appleマップ起動
        ├── SettingsView.swift    … 許可・通知トグル
        └── CategoryFilterBar.swift … カテゴリ絞り込みチップ
```
