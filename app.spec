# -*- mode: python ; coding: utf-8 -*-

# IQ-TC-01: Binary Integrity & Versioning Verification
# Version information for Windows executable properties
version_info = {
    'version': '1.1.0',
    'description': 'Air Quality Review System - GAMP 5 Compliant',
    'company': 'AQR Program',
    'product': 'Air Quality Review',
    'file_version': '1.1.0.0',
    'product_version': '1.1.0.0',
    'copyright': '© 2026 AQR Program. All rights reserved.',
    'trademark': '',
}

a = Analysis(
    ['app.py'], # IQ-TC-06: Standalone Python Bundling
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static')],
    hiddenimports=['waitress'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AirQualityReview_1.1.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='app_version_info.txt',
)
