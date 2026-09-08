#!/usr/bin/env python3
"""Generate ChiikawaRadar.xcodeproj (no external deps)."""
import hashlib, os, re, pathlib

ROOT = pathlib.Path(__file__).parent
NAME = "ChiikawaRadar"
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
SRC_GROUP = oid("src_group")
TARGET = oid("target")
PRODUCT_REF = oid("product_ref")
SOURCES_PHASE = oid("sources_phase")
RESOURCES_PHASE = oid("resources_phase")
FRAMEWORKS_PHASE = oid("frameworks_phase")
PROJ_CFG_LIST = oid("proj_cfg_list")
TARGET_CFG_LIST = oid("target_cfg_list")
PROJ_DEBUG = oid("proj_debug")
PROJ_RELEASE = oid("proj_release")
TARGET_DEBUG = oid("target_debug")
TARGET_RELEASE = oid("target_release")

file_refs = {p: oid("fileref", p) for p in SOURCES + RESOURCES}
build_files = {p: oid("buildfile", p) for p in SOURCES + RESOURCES}

L = []
L.append("// !$*UTF8*$!")
L.append("{")
L.append("\tarchiveVersion = 1;")
L.append("\tclasses = {\n\t};")
L.append("\tobjectVersion = 56;")
L.append("\tobjects = {")

L.append("\n/* Begin PBXBuildFile section */")
for p in SOURCES + RESOURCES:
    b = os.path.basename(p)
    L.append(f"\t\t{build_files[p]} /* {b} */ = {{isa = PBXBuildFile; fileRef = {file_refs[p]} /* {b} */; }};")
L.append("/* End PBXBuildFile section */")

L.append("\n/* Begin PBXFileReference section */")
for p in SOURCES:
    b = os.path.basename(p)
    L.append(f"\t\t{file_refs[p]} /* {b} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; name = {q(b)}; path = {q(p)}; sourceTree = \"<group>\"; }};")
for p in RESOURCES:
    b = os.path.basename(p)
    ftype = RES_TYPES.get(os.path.splitext(p)[1], "text")
    L.append(f"\t\t{file_refs[p]} /* {b} */ = {{isa = PBXFileReference; lastKnownFileType = {ftype}; name = {q(b)}; path = {q(p)}; sourceTree = \"<group>\"; }};")
L.append(f"\t\t{PRODUCT_REF} /* {NAME}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {q(NAME + '.app')}; sourceTree = BUILT_PRODUCTS_DIR; }};")
L.append("/* End PBXFileReference section */")

L.append("\n/* Begin PBXFrameworksBuildPhase section */")
L.append(f"\t\t{FRAMEWORKS_PHASE} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (\n\t\t\t); runOnlyForDeploymentPostprocessing = 0; }};")
L.append("/* End PBXFrameworksBuildPhase section */")

L.append("\n/* Begin PBXGroup section */")
src_children = "\n".join(f"\t\t\t\t{file_refs[p]} /* {os.path.basename(p)} */," for p in SOURCES + RESOURCES)
L.append(f"\t\t{MAINGROUP} = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{SRC_GROUP} /* {NAME} */,\n\t\t\t\t{PRODUCTS_GROUP} /* Products */,\n\t\t\t);\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append(f"\t\t{SRC_GROUP} /* {NAME} */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n{src_children}\n\t\t\t);\n\t\t\tname = {q(NAME)};\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append(f"\t\t{PRODUCTS_GROUP} /* Products */ = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{PRODUCT_REF} /* {NAME}.app */,\n\t\t\t);\n\t\t\tname = Products;\n\t\t\tsourceTree = \"<group>\";\n\t\t}};")
L.append("/* End PBXGroup section */")

L.append("\n/* Begin PBXNativeTarget section */")
L.append(f"\t\t{TARGET} /* {NAME} */ = {{\n\t\t\tisa = PBXNativeTarget;\n\t\t\tbuildConfigurationList = {TARGET_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{NAME}\" */;\n\t\t\tbuildPhases = (\n\t\t\t\t{SOURCES_PHASE} /* Sources */,\n\t\t\t\t{FRAMEWORKS_PHASE} /* Frameworks */,\n\t\t\t\t{RESOURCES_PHASE} /* Resources */,\n\t\t\t);\n\t\t\tbuildRules = (\n\t\t\t);\n\t\t\tdependencies = (\n\t\t\t);\n\t\t\tname = {q(NAME)};\n\t\t\tproductName = {q(NAME)};\n\t\t\tproductReference = {PRODUCT_REF} /* {NAME}.app */;\n\t\t\tproductType = \"com.apple.product-type.application\";\n\t\t}};")
L.append("/* End PBXNativeTarget section */")

L.append("\n/* Begin PBXProject section */")
L.append(f"\t\t{PROJECT} /* Project object */ = {{\n\t\t\tisa = PBXProject;\n\t\t\tattributes = {{\n\t\t\t\tBuildIndependentTargetsInParallel = 1;\n\t\t\t\tLastSwiftUpdateCheck = 2600;\n\t\t\t\tLastUpgradeCheck = 2600;\n\t\t\t\tTargetAttributes = {{\n\t\t\t\t\t{TARGET} = {{\n\t\t\t\t\t\tCreatedOnToolsVersion = 26.0;\n\t\t\t\t\t}};\n\t\t\t\t}};\n\t\t\t}};\n\t\t\tbuildConfigurationList = {PROJ_CFG_LIST} /* Build configuration list for PBXProject \"{NAME}\" */;\n\t\t\tcompatibilityVersion = \"Xcode 14.0\";\n\t\t\tdevelopmentRegion = en;\n\t\t\thasScannedForEncodings = 0;\n\t\t\tknownRegions = (\n\t\t\t\ten,\n\t\t\t\tBase,\n\t\t\t\tja,\n\t\t\t);\n\t\t\tmainGroup = {MAINGROUP};\n\t\t\tproductRefGroup = {PRODUCTS_GROUP} /* Products */;\n\t\t\tprojectDirPath = \"\";\n\t\t\tprojectRoot = \"\";\n\t\t\ttargets = (\n\t\t\t\t{TARGET} /* {NAME} */,\n\t\t\t);\n\t\t}};")
L.append("/* End PBXProject section */")

L.append("\n/* Begin PBXResourcesBuildPhase section */")
res_files = "\n".join(f"\t\t\t\t{build_files[p]} /* {os.path.basename(p)} in Resources */," for p in RESOURCES)
L.append(f"\t\t{RESOURCES_PHASE} /* Resources */ = {{\n\t\t\tisa = PBXResourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{res_files}\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append("/* End PBXResourcesBuildPhase section */")

L.append("\n/* Begin PBXSourcesBuildPhase section */")
src_files = "\n".join(f"\t\t\t\t{build_files[p]} /* {os.path.basename(p)} in Sources */," for p in SOURCES)
L.append(f"\t\t{SOURCES_PHASE} /* Sources */ = {{\n\t\t\tisa = PBXSourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n{src_files}\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};")
L.append("/* End PBXSourcesBuildPhase section */")

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


if DEVELOPMENT_TEAM:
    TARGET_COMMON["DEVELOPMENT_TEAM"] = DEVELOPMENT_TEAM


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
L.append("/* End XCBuildConfiguration section */")

L.append("\n/* Begin XCConfigurationList section */")
L.append(f"\t\t{PROJ_CFG_LIST} /* Build configuration list for PBXProject \"{NAME}\" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{PROJ_DEBUG} /* Debug */,\n\t\t\t\t{PROJ_RELEASE} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};")
L.append(f"\t\t{TARGET_CFG_LIST} /* Build configuration list for PBXNativeTarget \"{NAME}\" */ = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{TARGET_DEBUG} /* Debug */,\n\t\t\t\t{TARGET_RELEASE} /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};")
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
      </BuildActionEntries>
   </BuildAction>
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
