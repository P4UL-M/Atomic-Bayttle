# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules


project_root = Path(SPECPATH)
icon = project_root / "assets" / ("ico.icns" if sys.platform == "darwin" else "ico.ico")
binaries = collect_dynamic_libs("glcontext")
hiddenimports = (
    collect_submodules("moderngl")
    + collect_submodules("glcontext")
    + collect_submodules("pygame_easy_menu")
)

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root), str(project_root.parent / "pygame_easy_menu")],
    binaries=binaries,
    datas=[
        (str(project_root / "assets"), "assets"),
        (str(project_root / "data"), "data"),
    ] + collect_data_files("pygame_easy_menu"),
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["OpenGL"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Atomic-Bayttle",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=str(icon),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="Atomic-Bayttle",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Atomic-Bayttle.app",
        icon=str(icon),
        bundle_identifier="com.atomic-bayttle.game",
    )
