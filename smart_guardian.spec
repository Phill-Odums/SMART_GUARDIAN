# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# We need to include all the folders for the web UI and AI
added_files = [
    ('web/templates', 'web/templates'),
    ('web/static', 'web/static'),
    ('weapon_detect_v5n.pt', '.'),
    ('app', 'app'),
    ('database', 'database')
]

a = Analysis(
    ['guardian_desktop.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['pywebview', 'clr', 'waitress', 'cv2', 'ultralytics'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SmartGuardian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True if you want a terminal window in background
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='web/static/images/alert-placeholder.png' # You can replace with a real .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartGuardian',
)
