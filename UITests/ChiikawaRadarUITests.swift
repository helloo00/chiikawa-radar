import XCTest

/// タブ遷移など「画面が実際に操作できるか」を確認するゴールデンパスのスモークテスト。
/// ロジック（日付パースやフィルタなど）の網羅的な検証はユニットテスト側の役割で、
/// ここでは壊れやすい・自動化しにくいUI導線だけを最小限カバーする。
final class ChiikawaRadarUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    /// 初回起動時に出る位置情報の許可ダイアログを自動で許可する。
    private func addLocationPermissionInterruptionMonitor() -> NSObjectProtocol {
        addUIInterruptionMonitor(withDescription: "Location permission") { alert in
            for label in ["Allow While Using App", "Allow Once", "このAppの使用中は許可", "1度だけ許可"] {
                let button = alert.buttons[label]
                if button.exists {
                    button.tap()
                    return true
                }
            }
            return false
        }
    }

    private func launchApp() -> XCUIApplication {
        let app = XCUIApplication()
        let monitor = addLocationPermissionInterruptionMonitor()
        addTeardownBlock { self.removeUIInterruptionMonitor(monitor) }
        app.launch()
        // interruption monitor はアプリへの操作が発生しないと発火しないため、軽くタップして起こす
        app.tap()
        return app
    }

    func testTabBarShowsAllFiveTabs() {
        let app = launchApp()
        for label in ["レーダー", "地図", "一覧", "情報", "設定"] {
            XCTAssertTrue(app.tabBars.buttons[label].waitForExistence(timeout: 5), "\(label) タブが見つからない")
        }
    }

    func testSettingsShowsSightingsFeedSection() {
        let app = launchApp()
        app.tabBars.buttons["設定"].tap()

        // Listは遅延描画のため、下の方のセクションは画面外だとまだツリーに現れない。見えるまでスクロールする。
        // スワイプ直後はアニメーション中でツリーがまだ更新されていないことがあるため、
        // 1回ごとに一呼吸おいて確認する（回数もシミュレータの速度差を見込んで多めに）。
        let updateButton = app.buttons["今すぐ更新"]
        var attempts = 0
        while !updateButton.waitForExistence(timeout: 0.5) && attempts < 12 {
            app.swipeUp()
            attempts += 1
        }
        XCTAssertTrue(updateButton.waitForExistence(timeout: 5), "設定画面の「今すぐ更新」ボタンが見つからない（\(attempts)回スクロール後）")
    }

    func testSightingsTabOpens() {
        let app = launchApp()
        app.tabBars.buttons["情報"].tap()
        XCTAssertTrue(app.navigationBars["情報"].waitForExistence(timeout: 5))
    }
}
