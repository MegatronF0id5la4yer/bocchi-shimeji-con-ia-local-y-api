# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['PinkChan.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),
        ('Actions.xml', '.'),
        ('Behaviors.xml', '.'),
    ],
    hiddenimports=[
        'win32gui', 'win32con', 'win32api', 'win32process', 'win32net',
        'winreg', 'requests', 'webbrowser', 'subprocess', 'PIL',
        'PIL.Image', 'PIL.ImageTk', 'PIL.ImageSequence',
        'tkinter', 'tkinter.filedialog', 'tkinter.colorchooser',
        'tkinter.messagebox', 'tkinter.ttk', 'tkinter.font', 'tkinter.scrolledtext',
        'winshell', 'fnmatch', 'urllib.parse'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchvision', 'torchaudio', 'transformers',
        'tokenizers', 'scipy', 'sympy', 'tensorboard', 'matplotlib',
        'numpy.testing', 'IPython', 'jupyter'
    ],
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
    name='PinkChan',
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
    icon=['icon.ico'],
)
