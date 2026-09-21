#!/usr/bin/env python3
"""Generate ChiikawaRadar.xcodeproj (no external deps)."""
import hashlib, os, re, pathlib

ROOT = pathlib.Path(__file__).parent
NAME = "ChiikawaRadar"
UITEST_NAME = "ChiikawaRadarUITests"
UNITTEST_NAME = "ChiikawaRadarTests"
# 実機テスト用に固有の Bundle ID（無料の Personal Team でも通るよう独自ドメイン風に）
BUNDLE_ID = os.environ.get("BUNDLE_ID", "com.kentarotakeuchi.chiikawaradar")
# Xcode に追加した Apple ID の Team ID（10桁）を入れると xcodebuild でも自動署名される
DEVELOPMENT_TEAM = os.environ.get("DEVELOPMENT_TEAM", "")

SOURCES = [
    "Sources/ChiikawaRadarApp.swift",
    "Sources/Models/GeoMath.swift",
    "Sources/Models/Shop.swift",
    "Sources/Models/Sighting.swift",
    "Sources/Services/LocationManager.swift",
    "Sources/Services/NearbyStoresService.swift",
    "Sources/Services/ProximityMonitor.swift",
    "Sources/Services/ShopRepository.swift",
    "Sources/Services/SightingsService.swift",
    "Sources/Views/CategoryFilterBar.swift",
    "Sources/Views/MapScreen.swift",
    "Sources/Views/RadarView.swift",
    "Sources/Views/RootView.swift",
    "Sources/Views/SettingsView.swift",
    "Sources/Views/ShopDetailView.swift",
    "Sources/Views/ShopListView.swift",
    "Sources/Views/SightingsView.swift",
]
RESOURCES = ["Assets.xcassets", "Resources/shops.json", "Resources/sightings.sample.json"]

# XCUITest（画面操作の自動テスト）用ターゲットのソース。ロジックのユニットテストは別途。
UITEST_SOURCES = [
    "UITests/ChiikawaRadarUITests.swift",
]

# ロジック単体のユニットテスト（XCTest, @testable import ChiikawaRadar）。
UNITTEST_SOURCES = [
    "Tests/ChiikawaRadarTests/GeoMathTests.swift",
    "Tests/ChiikawaRadarTests/ShopTests.swift",
    "Tests/ChiikawaRadarTests/SightingTests.swift",
    "Tests/ChiikawaRadarTests/ShopRepositoryTests.swift",
]

RES_TYPES = {".xcassets": "folder.assetcatalog", ".json": "text.json"}


def oid(*parts):
    return hashlib.md5("::".join(parts).encode()).hexdigest().upper()[:24]


def v(x):
    """Serialize a build-setting value for pbxproj."""
    s = str(x)
    if s.startswith('"') or s.startswith('('):
        return s
    if s in ("YES", "NO") or re.fullmatch(r"-?\d+(\.\d+)?", s) or re.fullmatch(r"[A-Za-z0-9_]+", s):
        return s
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


PROJECT = oid("project")
MAINGROUP = oid("maingroup")
PRODUCTS_GROUP = oid("products_group")
FRAMEWORKS_GROUP = oid("frameworks_group")
SRC_GROUP = oid("src_group")
UITEST_GROUP = oid("uitest_group")
UNITTEST_GROUP = oid("unittest_group")
TARGET = oid("target")
UITEST_TARGET = oid("uitest_target")
UNITTEST_TARGET = oid("unittest_target")
PRODUCT_REF = oid("product_ref")
UITEST_PRODUCT_REF = oid("uitest_product_ref")
UNITTEST_PRODUCT_REF = oid("unittest_product_ref")
XCTEST_FRAMEWORK_REF = oid("xctest_framework_ref")
SOURCES_PHASE = oid("sources_phase")
RESOURCES_PHASE = oid("resources_phase")
FRAMEWORKS_PHASE = oid("frameworks_phase")
UITEST_SOURCES_PHASE = oid("uitest_sources_phase")
UITEST_RESOURCES_PHASE = oid("uitest_resources_phase")
UITEST_FRAMEWORKS_PHASE = oid("uitest_frameworks_phase")
UNITTEST_SOURCES_PHASE = oid("unittest_sources_phase")
UNITTEST_RESOURCES_PHASE = oid("unittest_resources_phase")
UNITTEST_FRAMEWORKS_PHASE = oid("unittest_frameworks_phase")
PROJ_CFG_LIST = oid("proj_cfg_list")
TARGET_CFG_LIST = oid("target_cfg_list")
UITEST_CFG_LIST = oid("uitest_cfg_list")
UNITTEST_CFG_LIST = oid("unittest_cfg_list")
PROJ_DEBUG = oid("proj_debug")
PROJ_RELEASE = oid("proj_release")
TARGET_DEBUG = oid("target_debug")
TARGET_RELEASE = oid("target_release")
UITEST_DEBUG = oid("uitest_debug")
UITEST_RELEASE = oid("uitest_release")
UNITTEST_DEBUG = oid("unittest_debug")
UNITTEST_RELEASE = oid("unittest_release")
UITEST_CONTAINER_ITEM_PROXY = oid("uitest_container_item_proxy")
UITEST_TARGET_DEPENDENCY = oid("uitest_target_dependency")
UNITTEST_CONTAINER_ITEM_PROXY = oid("unittest_container_item_proxy")
UNITTEST_TARGET_DEPENDENCY = oid("unittest_target_dependency")
XCTEST_BUILD_FILE = oid("buildfile", "XCTest.framework")
XCTEST_BUILD_FILE_UNITTEST = oid("buildfile", "XCTest.framework.unittest")

file_refs = {p: oid("fileref", p) for p in SOURCES + RESOURCES + UITEST_SOURCES + UNITTEST_SOURCES}
build_files = {p: oid("buildfile", p) for p in SOURCES + RESOURCES + UITEST_SOURCES + UNITTEST_SOURCES}

L = []
L.append("// !$*UTF8*$!")
L.append("{")
L.append("\tarchiveVersion = 1;")
L.append("\tclasses = {\n\t};")
L.append("\tobjectVersion = 56;")
L.append("\tobjects = {")

L.append("\n/* Begin PBXBuildFile section */")
for p in SOURCES + RESOURCES + UITEST_SOURCES + UNITTEST_SOURCES:
    b = os.path.basename(p)
    L.append(f"\t\t{build_files[p]} /* {b} */ = {{isa = PBXBuildFile; fileRef = {file_refs[p]} /* {b} */; }};")
L.append(f"\t\t{XCTEST_BUILD_FILE} /* XCTest.framework in Frameworks */ = {{isa = PBXBuildFile; fileRef = {XCTEST_FRAMEWORK_REF} /* XCTest.framework */; }};")
L.append(f"\t\t{XCTEST_BUILD_FILE_UNITTEST} /* XCTest.framework in Frameworks */ = {{isa = PBXBuildFile; fileRef = {XCTEST_FRAMEWORK_REF} /* XCTest.framework */; }};")
L.append("/* End PBXBuildFile section */")

L.append("\n/* Begin PBXContainerItemProxy section */")
L.append(f"\t\t{UITEST_CONTAINER_ITEM_PROXY} /* PBXContainerItemProxy */ = {{\n\t\t\tisa = PBXContainerItemProxy;\n\t\t\tcontainerPortal = {PROJECT} /* Project object */;\n\t\t\tproxyType = 1;\n\t\t\tremoteGlobalIDString = {TARGET};\n\t\t\tremoteInfo = {q(NAME)};\n\t\t}};")
L.append(f"\t\t{UNITTEST_CONTAINER_ITEM_PROXY} /* PBXContainerItemProxy */ = {{\n\t\t\tisa = PBXContainerItemProxy;\n\t\t\tcontainerPortal = {PROJECT} /* Project object */;\n\t\t\tproxyType = 1;\n\t\t\tremoteGlobalIDString = {TARGET};\n\t\t\tremoteInfo = {q(NAME)};\n\t\t}};")
L.append("/* End PBXContainerItemProxy section */")

L.append("\n/* Begin PBXFileReference section */")
for p in SOURCES + UITEST_SOURCES + UNITTEST_SOURCES:
    b = os.path.basename(p)
    L.append(f"\t\t{file_refs[p]} /* {b} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; name = {q(b)}; path = {q(p)}; sourceTree = \"<group>\"; }};")
for p in RESOURCES:
    b = os.path.basename(p)
    ftype = RES_TYPES.get(os.path.splitext(p)[1], "text")
    L.append(f"\t\t{file_refs[p]} /* {b} */ = {{isa = PBXFileReference; lastKnownFileType = {ftype}; name = {q(b)}; path = {q(p)}; sourceTree = \"<group>\"; }};")
L.append(f"\t\t{PRODUCT_REF} /* {NAME}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {q(NAME + '.app')}; sourceTree = BUILT_PRODUCTS_DIR; }};")
L.append(f"\t\t{UITEST_PRODUCT_REF} /* {UITEST_NAME}.xctest */ = {{isa = PBXFileReference; explicitFileType = wrapper.cfbundle; includeInIndex = 0; path = {q(UITEST_NAME + '.xctest')}; sourceTree = BUILT_PRODUCTS_DIR; }};")
L.append(f"\t\t{UNITTEST_PRODUCT_REF} /* {UNITTEST_NAME}.xctest */ = {{isa = PBXFileReference; explicitFileType = wrapper.cfbundle; includeInIndex = 0; path = {q(UNITTEST_NAME + '.xctest')}; sourceTree = BUILT_PRODUCTS_DIR; }};")
L.append(f"\t\t{XCTEST_FRAMEWORK_REF} /* XCTest.framework */ = {{isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = \"XCTest.framework\"; path = \"Platforms/iPhoneOS.platform/Developer/Library/Frameworks/XCTest.framework\"; sourceTree = DEVELOPER_DIR; }};")
L.append("/* End PBXFileReference section */")

L.append("\n/* Begin PBXFrameworksBuildPhase section */")
L.append(f"\t\t{FRAMEWORKS_PHASE} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (\n\t\t\t); runOnlyForDeploymentPostprocessing = 0; }};")
L.append(f"\t\t{UITEST_FRAMEWORKS_PHASE} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (\n\t\t\t\t{XCTEST_BUILD_FILE} /* XCTest.framework in Frameworks */,\n\t\t\t); runOnlyForDeploymentPostprocessing = 0; }};")
L.append(f"\t\t{UNITTEST_FRAMEWORKS_PHASE} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (\n\t\t\t\t{XCTEST_BUILD_FILE_UNITTEST} /* XCTest.framework in Frameworks */,\n\t\t\t); runOnlyForDeploymentPostprocessing = 0; }};")
L.append("/* End PBXFrameworksBuildPhase section */")

L.append("\n/* Begin PBXGroup section */")
src_children = "\n".join(f"\t\t\t\t{file_refs[p]} /* {os.path.basename(p)} */," for p in SOURCES + RESOURCES)
uitest_children = "\n".join(f"\t\t\t\t{file_refs[p]} /* {os.path.basename(p)} */," for p in UITEST_SOURCES)
unittest_children = "\n".join(f"\t\t\t\t{file_refs[p]} /* {os.path.basename(p)} */," for p in UNITTEST_SOURCES)
L.append(f"\t\t{MAINGROUP} = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{SRC_GROUP} /* {NAME} */,\n\t\t\t\t{UITEST_GROUP} /* {UITEST_NAME} */,\n\t\t\t\t{UNITTEST_GROUP} /* {UNITTEST_NAME} */,\n\t\t\t\t{FRAMEWORKS_GROUP} /* Frameworks */,\n\t\t\t\t{PRODUCTS_GROUP} /* Products */,\n\t\t\t);\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append(f"\t\t{SRC_GROUP} /* {NAME} */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n{src_children}\n\t\t\t);\n\t\t\tname = {q(NAME)};\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append(f"\t\t{UITEST_GROUP} /* {UITEST_NAME} */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n{uitest_children}\n\t\t\t);\n\t\t\tname = {q(UITEST_NAME)};\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append(f"\t\t{UNITTEST_GROUP} /* {UNITTEST_NAME} */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n{unittest_children}\n\t\t\t);\n\t\t\tname = {q(UNITTEST_NAME)};\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append(f"\t\t{FRAMEWORKS_GROUP} /* Frameworks */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{XCTEST_FRAMEWORK_REF} /* XCTest.framework */,\n\t\t\t);\n\t\t\tname = Frameworks;\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append(f"\t\t{PRODUCTS_GROUP} /* Products */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{PRODUCT_REF} /* {NAME}.app */,\n\t\t\t\t{UITEST_PRODUCT_REF} /* {UITEST_NAME}.xctest */,\n\t\t\t\t{UNITTEST_PRODUCT_REF} /* {UNITTEST_NAME}.xctest */,\n\t\t\t);\n\t\t\tname = Products;\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append("/* End PBXGroup section */")

L.append("\n/* Begin PBXNativeTarget section */")
L.append(f"\t\t{TARGET} /* {NAME} */ = {{\n\t\t\tisa = PBXNativeTarget;\n\t\t\tbuildConfigurationList = {TARGET_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{NAME}\" */;\n\t\t\tbuildPhases = (\n\t\t\t\t{SOURCES_PHASE} /* Sources */,\n\t\t\t\t{FRAMEWORKS_PHASE} /* Frameworks */,\n\t\t\t\t{RESOURCES_PHASE} /* Resources */,\n\t\t\t);\n\t\t\tbuildRules = (\n\t\t\t);\n\t\t\tdependencies = (\n\t\t\t);\n\t\t\tname = {q(NAME)};\n\t\t\tproductName = {q(NAME)};\n\t\t\tproductReference = {PRODUCT_REF} /* {NAME}.app */;\n\t\t\tproductType = \"com.apple.product-type.application\";\n\t\t}};")
L.append(f"\t\t{UITEST_TARGET} /* {UITEST_NAME} */ = {{\n\t\t\tisa = PBXNativeTarget;\n\t\t\tbuildConfigurationList = {UITEST_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{UITEST_NAME}\" */;\n\t\t\tbuildPhases = (\n\t\t\t\t{UITEST_SOURCES_PHASE} /* Sources */,\n\t\t\t\t{UITEST_FRAMEWORKS_PHASE} /* Frameworks */,\n\t\t\t\t{UITEST_RESOURCES_PHASE} /* Resources */,\n\t\t\t);\n\t\t\tbuildRules = (\n\t\t\t);\n\t\t\tdependencies = (\n\t\t\t\t{UITEST_TARGET_DEPENDENCY} /* PBXTargetDependency */,\n\t\t\t);\n\t\t\tname = {q(UITEST_NAME)};\n\t\t\tproductName = {q(UITEST_NAME)};\n\t\t\tproductReference = {UITEST_PRODUCT_REF} /* {UITEST_NAME}.xctest */;\n\t\t\tproductType = \"com.apple.product-type.bundle.ui-testing\";\n\t\t}};")
L.append(f"\t\t{UNITTEST_TARGET} /* {UNITTEST_NAME} */ = {{\n\t\t\tisa = PBXNativeTarget;\n\t\t\tbuildConfigurationList = {UNITTEST_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{UNITTEST_NAME}\" */;\n\t\t\tbuildPhases = (\n\t\t\t\t{UNITTEST_SOURCES_PHASE} /* Sources */,\n\t\t\t\t{UNITTEST_FRAMEWORKS_PHASE} /* Frameworks */,\n\t\t\t\t{UNITTEST_RESOURCES_PHASE} /* Resources */,\n\t\t\t);\n\t\t\tbuildRules = (\n\t\t\t);\n\t\t\tdependencies = (\n\t\t\t\t{UNITTEST_TARGET_DEPENDENCY} /* PBXTargetDependency */,\n\t\t\t);\n\t\t\tname = {q(UNITTEST_NAME)};\n\t\t\tproductName = {q(UNITTEST_NAME)};\n\t\t\tproductReference = {UNITTEST_PRODUCT_REF} /* {UNITTEST_NAME}.xctest */;\n\t\t\tproductType = \"com.apple.product-type.bundle.unit-test\";\n\t\t}};")
L.append("/* End PBXNativeTarget section */")

L.append("\n/* Begin PBXProject section */")
L.append(f"\t\t{PROJECT} /* Project object */ = {{\n\t\t\tisa = PBXProject;\n\t\t\tattributes = {{\n\t\t\t\tBuildIndependentTargetsInParallel = 1;\n\t\t\t\tLastSwiftUpdateCheck = 2600;\n\t\t\t\tLastUpgradeCheck = 2600;\n\t\t\t\tTargetAttributes = {{\n\t\t\t\t\t{TARGET} = {{\n\t\t\t\t\t\tCreatedOnToolsVersion = 26.0;\n\t\t\t\t\t}};\n\t\t\t\t\t{UITEST_TARGET} = {{\n\t\t\t\t\t\tCreatedOnToolsVersion = 26.0;\n\t\t\t\t\t\tTestTargetID = {TARGET};\n\t\t\t\t\t}};\n\t\t\t\t\t{UNITTEST_TARGET} = {{\n\t\t\t\t\t\tCreatedOnToolsVersion = 26.0;\n\t\t\t\t\t\tTestTargetID = {TARGET};\n\t\t\t\t\t}};\n\t\t\t\t}};\n\t\t\t}};\n\t\t\tbuildConfigurationList = {PROJ_CFG_LIST} /* Build configuration list for PBXProject \"{NAME}\" */;\n\t\t\tcompatibilityVersion = \"Xcode 14.0\";\n\t\t\tdevelopmentRegion = en;\n\t\t\thasScannedForEncodings = 0;\n\t\t\tknownRegions = (\n\t\t\t\ten,\n\t\t\t\tBase,\n\t\t\t\tja,\n\t\t\t);\n\t\t\tmainGroup = {MAINGROUP};\n\t\t\tproductRefGroup = {PRODUCTS_GROUP} /* Products */;\n\t\t\tprojectDirPath = \"\";\n\t\t\tprojectRoot = \"\";\n\t\t\ttargets = (\n\t\t\t\t{TARGET} /* {NAME} */,\n\t\t\t\t{UITEST_TARGET} /* {UITEST_NAME} */,\n\t\t\t\t{UNITTEST_TARGET} /* {UNITTEST_NAME} */,\n\t\t\t);\n\t\t}};")
L.append("/* End PBXProject section */")

L.append("\n/* Begin PBXResourcesBuildPhase section */")
res_files = "\n".join(f"\t\t\t\t{build_files[p]} /* {os.path.basename(p)} in Resources */," for p in RESOURCES)
L.append(f"\t\t{RESOURCES_PHASE} /* Resources */ = {{\n\t\t\tisa = PBXResourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{res_files}\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append(f"\t\t{UITEST_RESOURCES_PHASE} /* Resources */ = {{\n\t\t\tisa = PBXResourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append(f"\t\t{UNITTEST_RESOURCES_PHASE} /* Resources */ = {{\n\t\t\tisa = PBXResourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append("/* End PBXResourcesBuildPhase section */")

L.append("\n/* Begin PBXSourcesBuildPhase section */")
src_files = "\n".join(f"\t\t\t\t{build_files[p]} /* {os.path.basename(p)} in Sources */," for p in SOURCES)
uitest_src_files = "\n".join(f"\t\t\t\t{build_files[p]} /* {os.path.basename(p)} in Sources */," for p in UITEST_SOURCES)
unittest_src_files = "\n".join(f"\t\t\t\t{build_files[p]} /* {os.path.basename(p)} in Sources */," for p in UNITTEST_SOURCES)
L.append(f"\t\t{SOURCES_PHASE} /* Sources */ = {{\n\t\t\tisa = PBXSourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{src_files}\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append(f"\t\t{UITEST_SOURCES_PHASE} /* Sources */ = {{\n\t\t\tisa = PBXSourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{uitest_src_files}\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append(f"\t\t{UNITTEST_SOURCES_PHASE} /* Sources */ = {{\n\t\t\tisa = PBXSourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{unittest_src_files}\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append("/* End PBXSourcesBuildPhase section */")

L.append("\n/* Begin PBXTargetDependency section */")
L.append(f"\t\t{UITEST_TARGET_DEPENDENCY} /* PBXTargetDependency */ = {{\n\t\t\tisa = PBXTargetDependency;\n\t\t\ttarget = {TARGET} /* {NAME} */;\n\t\t\ttargetProxy = {UITEST_CONTAINER_ITEM_PROXY} /* PBXContainerItemProxy */;\n\t\t}};")
L.append(f"\t\t{UNITTEST_TARGET_DEPENDENCY} /* PBXTargetDependency */ = {{\n\t\t\tisa = PBXTargetDependency;\n\t\t\ttarget = {TARGET} /* {NAME} */;\n\t\t\ttargetProxy = {UNITTEST_CONTAINER_ITEM_PROXY} /* PBXContainerItemProxy */;\n\t\t}};")
L.append("/* End PBXTargetDependency section */")

PROJ_COMMON = {
    "ALWAYS_SEARCH_USER_PATHS": "NO",
    "CLANG_ANALYZER_NONNULL": "YES",
    "CLANG_ENABLE_MODULES": "YES",
    "CLANG_ENABLE_OBJC_ARC": "YES",
    "CLANG_WARN_BOOL_CONVERSION": "YES",
    "CLANG_WARN_DOCUMENTATION_COMMENTS": "YES",
    "CLANG_WARN_UNGUARDED_AVAILABILITY": "YES_AGGRESSIVE",
    "COPY_PHASE_STRIP": "NO",
    "ENABLE_STRICT_OBJC_MSGSEND": "YES",
    "ENABLE_USER_SCRIPT_SANDBOXING": "YES",
    "GCC_C_LANGUAGE_STANDARD": "gnu17",
    "GCC_NO_COMMON_BLOCKS": "YES",
    "GCC_WARN_ABOUT_RETURN_TYPE": "YES_ERROR",
    "GCC_WARN_UNINITIALIZED_AUTOS": "YES_AGGRESSIVE",
    "GCC_WARN_UNUSED_VARIABLE": "YES",
    "IPHONEOS_DEPLOYMENT_TARGET": "17.0",
    "MTL_FAST_MATH": "YES",
    "SDKROOT": "iphoneos",
    "SWIFT_COMPILATION_MODE": "wholemodule",
}
PROJ_DEBUG_S = dict(PROJ_COMMON, **{
    "DEBUG_INFORMATION_FORMAT": "dwarf",
    "ENABLE_TESTABILITY": "YES",
    "GCC_DYNAMIC_NO_PIC": "NO",
    "GCC_OPTIMIZATION_LEVEL": "0",
    "MTL_ENABLE_DEBUG_INFO": "INCLUDE_SOURCE",
    "ONLY_ACTIVE_ARCH": "YES",
    "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG $(inherited)",
    "SWIFT_OPTIMIZATION_LEVEL": "-Onone",
})
PROJ_RELEASE_S = dict(PROJ_COMMON, **{
    "DEBUG_INFORMATION_FORMAT": "dwarf-with-dsym",
    "ENABLE_NS_ASSERTIONS": "NO",
    "MTL_ENABLE_DEBUG_INFO": "NO",
    "SWIFT_OPTIMIZATION_LEVEL": "-O",
})

LOC_WHEN = "近くのちいかわグッズ取扱店を探すために位置情報を使います。"
LOC_ALWAYS = "取扱店に近づいたときに通知するため、位置情報を使います。"
TARGET_COMMON = {
    "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
    "CODE_SIGN_STYLE": "Automatic",
    "CURRENT_PROJECT_VERSION": "1",
    "ENABLE_PREVIEWS": "YES",
    "GENERATE_INFOPLIST_FILE": "YES",
    "INFOPLIST_KEY_NSLocationWhenInUseUsageDescription": LOC_WHEN,
    "INFOPLIST_KEY_NSLocationAlwaysAndWhenInUseUsageDescription": LOC_ALWAYS,
    "INFOPLIST_KEY_UIApplicationSceneManifest_Generation": "YES",
    "INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents": "YES",
    "INFOPLIST_KEY_UILaunchScreen_Generation": "YES",
    "INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone": "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight",
    "LD_RUNPATH_SEARCH_PATHS": "@executable_path/Frameworks",
    "MARKETING_VERSION": "1.0",
    "PRODUCT_BUNDLE_IDENTIFIER": BUNDLE_ID,
    "PRODUCT_NAME": "$(TARGET_NAME)",
    "INFOPLIST_KEY_CFBundleDisplayName": "ちいかわレーダー",
    "SWIFT_EMIT_LOC_STRINGS": "YES",
    "SWIFT_VERSION": "5.0",
    "TARGETED_DEVICE_FAMILY": "1,2",
}
UITEST_TARGET_COMMON = {
    "CODE_SIGN_STYLE": "Automatic",
    "CURRENT_PROJECT_VERSION": "1",
    "GENERATE_INFOPLIST_FILE": "YES",
    "LD_RUNPATH_SEARCH_PATHS": "@executable_path/Frameworks @loader_path/Frameworks",
    "MARKETING_VERSION": "1.0",
    "PRODUCT_BUNDLE_IDENTIFIER": BUNDLE_ID + ".UITests",
    "PRODUCT_NAME": "$(TARGET_NAME)",
    "SWIFT_EMIT_LOC_STRINGS": "NO",
    "SWIFT_VERSION": "5.0",
    "TARGETED_DEVICE_FAMILY": "1,2",
    # xcodebuild/Xcode がどのアプリを操作対象にするかを解決するための必須設定
    "TEST_TARGET_NAME": NAME,
}


UNITTEST_TARGET_COMMON = {
    "CODE_SIGN_STYLE": "Automatic",
    "CURRENT_PROJECT_VERSION": "1",
    "GENERATE_INFOPLIST_FILE": "YES",
    "LD_RUNPATH_SEARCH_PATHS": "@executable_path/Frameworks @loader_path/Frameworks @executable_path/../../Frameworks",
    "MARKETING_VERSION": "1.0",
    "PRODUCT_BUNDLE_IDENTIFIER": BUNDLE_ID + ".Tests",
    "PRODUCT_NAME": "$(TARGET_NAME)",
    "SWIFT_EMIT_LOC_STRINGS": "NO",
    "SWIFT_VERSION": "5.0",
    "TARGETED_DEVICE_FAMILY": "1,2",
    # ホストアプリ内で動かすことで @testable import ChiikawaRadar を可能にする
    "TEST_HOST": f"$(BUILT_PRODUCTS_DIR)/{NAME}.app/{NAME}",
    "BUNDLE_LOADER": "$(TEST_HOST)",
}


if DEVELOPMENT_TEAM:
    TARGET_COMMON["DEVELOPMENT_TEAM"] = DEVELOPMENT_TEAM
    UITEST_TARGET_COMMON["DEVELOPMENT_TEAM"] = DEVELOPMENT_TEAM
    UNITTEST_TARGET_COMMON["DEVELOPMENT_TEAM"] = DEVELOPMENT_TEAM


def cfg_block(cid, name, settings):
    body = "\n".join(f"\t\t\t\t{k} = {v(val)};" for k, val in settings.items())
    return (f"\t\t{cid} /* {name} */ = {{\n"
            f"\t\t\tisa = XCBuildConfiguration;\n"
            f"\t\t\tbuildSettings = {{\n{body}\n\t\t\t}};\n"
            f"\t\t\tname = {name};\n\t\t}};")


L.append("\n/* Begin XCBuildConfiguration section */")
L.append(cfg_block(PROJ_DEBUG, "Debug", PROJ_DEBUG_S))
L.append(cfg_block(PROJ_RELEASE, "Release", PROJ_RELEASE_S))
L.append(cfg_block(TARGET_DEBUG, "Debug", TARGET_COMMON))
L.append(cfg_block(TARGET_RELEASE, "Release", TARGET_COMMON))
L.append(cfg_block(UITEST_DEBUG, "Debug", UITEST_TARGET_COMMON))
L.append(cfg_block(UITEST_RELEASE, "Release", UITEST_TARGET_COMMON))
L.append(cfg_block(UNITTEST_DEBUG, "Debug", UNITTEST_TARGET_COMMON))
L.append(cfg_block(UNITTEST_RELEASE, "Release", UNITTEST_TARGET_COMMON))
L.append("/* End XCBuildConfiguration section */")

L.append("\n/* Begin XCConfigurationList section */")
L.append(f"\t\t{PROJ_CFG_LIST} /* Build configuration list for PBXProject \"{NAME}\" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{PROJ_DEBUG} /* Debug */,\n\t\t\t\t{PROJ_RELEASE} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};")
L.append(f"\t\t{TARGET_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{NAME}\" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{TARGET_DEBUG} /* Debug */,\n\t\t\t\t{TARGET_RELEASE} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};")
L.append(f"\t\t{UITEST_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{UITEST_NAME}\" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{UITEST_DEBUG} /* Debug */,\n\t\t\t\t{UITEST_RELEASE} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};")
L.append(f"\t\t{UNITTEST_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{UNITTEST_NAME}\" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{UNITTEST_DEBUG} /* Debug */,\n\t\t\t\t{UNITTEST_RELEASE} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};")
L.append("/* End XCConfigurationList section */")

L.append("\t};")
L.append(f"\trootObject = {PROJECT} /* Project object */;")
L.append("}")

proj_dir = ROOT / f"{NAME}.xcodeproj"
proj_dir.mkdir(exist_ok=True)
(proj_dir / "project.pbxproj").write_text("\n".join(L) + "\n", encoding="utf-8")

schemes_dir = proj_dir / "xcshareddata" / "xcschemes"
schemes_dir.mkdir(parents=True, exist_ok=True)
scheme = f"""<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="2600" version="1.7">
   <BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES">
      <BuildActionEntries>
         <BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">
            <BuildableReference
               BuildableIdentifier="primary"
               BlueprintIdentifier="{TARGET}"
               BuildableName="{NAME}.app"
               BlueprintName="{NAME}"
               ReferencedContainer="container:{NAME}.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
         <BuildActionEntry buildForTesting="YES" buildForRunning="NO" buildForProfiling="NO" buildForArchiving="NO" buildForAnalyzing="NO">
            <BuildableReference
               BuildableIdentifier="primary"
               BlueprintIdentifier="{UITEST_TARGET}"
               BuildableName="{UITEST_NAME}.xctest"
               BlueprintName="{UITEST_NAME}"
               ReferencedContainer="container:{NAME}.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
         <BuildActionEntry buildForTesting="YES" buildForRunning="NO" buildForProfiling="NO" buildForArchiving="NO" buildForAnalyzing="NO">
            <BuildableReference
               BuildableIdentifier="primary"
               BlueprintIdentifier="{UNITTEST_TARGET}"
               BuildableName="{UNITTEST_NAME}.xctest"
               BlueprintName="{UNITTEST_NAME}"
               ReferencedContainer="container:{NAME}.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration="Debug"
      selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv="YES"
      shouldAutocreateTestPlan="YES">
      <Testables>
         <TestableReference
            skipped="NO">
            <BuildableReference
               BuildableIdentifier="primary"
               BlueprintIdentifier="{UNITTEST_TARGET}"
               BuildableName="{UNITTEST_NAME}.xctest"
               BlueprintName="{UNITTEST_NAME}"
               ReferencedContainer="container:{NAME}.xcodeproj">
            </BuildableReference>
         </TestableReference>
         <TestableReference
            skipped="NO">
            <BuildableReference
               BuildableIdentifier="primary"
               BlueprintIdentifier="{UITEST_TARGET}"
               BuildableName="{UITEST_NAME}.xctest"
               BlueprintName="{UITEST_NAME}"
               ReferencedContainer="container:{NAME}.xcodeproj">
            </BuildableReference>
         </TestableReference>
      </Testables>
   </TestAction>
   <LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES">
      <BuildableProductRunnable runnableDebuggingMode="0">
         <BuildableReference
            BuildableIdentifier="primary"
            BlueprintIdentifier="{TARGET}"
            BuildableName="{NAME}.app"
            BlueprintName="{NAME}"
            ReferencedContainer="container:{NAME}.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </LaunchAction>
</Scheme>
"""
(schemes_dir / f"{NAME}.xcscheme").write_text(scheme, encoding="utf-8")
print("wrote", proj_dir)
