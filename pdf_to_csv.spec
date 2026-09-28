# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata("tabulate")

# Packages that get pulled in transitively by pandas' optional-dependency probes
# (pandas.compat._optional) and by a Jupyter/PyQt6 toolchain in the build env.
# None of them are reachable at runtime from pdf_to_csv.py.
excludes = [
    'scipy',
    'matplotlib',
    'PyQt6',
    'PyQt5',
    'PySide2',
    'PySide6',
    'tkinter',
    'IPython',
    'ipykernel',
    'jupyter_client',
    'nbclient',
    'nbformat',
    'zmq',
    'traitlets',
    'sqlalchemy',
    'psycopg2',
    'jedi',
    'parso',
    'pygments',
    'stack_data',
    'asttokens',
    'executing',
    'prompt_toolkit',
    'pytz',
    'pytest',
    'numpy.f2py',
    'numpy.testing',
    'PIL.ImageQt',
    'PIL.ImageShow',
    'setuptools',
    'pkg_resources',
    '_distutils_hack',
]

a = Analysis(
    ['pdf_to_csv.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['tabulate'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pdf_to_csv',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
