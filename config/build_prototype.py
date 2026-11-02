"""Build the local dashboard preview on macOS or Windows (legacy command name)."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    if sys.platform not in {"darwin", "win32"}:
        raise SystemExit("Run this build on macOS or Windows; cross-compilation is not supported.")
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--windowed", "--name", "GreenDecoupling",
        "--distpath", str(root / "dist"),
        "--workpath", str(root / "build" / "pyinstaller"),
        "--specpath", str(root / "build" / "spec"),
        "--collect-data", "dash", "--collect-data", "plotly",
        "--copy-metadata", "dash", "--copy-metadata", "plotly",
        "--paths", str(root),
        "--add-data", f"{root / 'data' / 'processed'}{os.pathsep}data/processed",
        "--add-data", f"{root / 'src' / 'visualization' / 'assets'}{os.pathsep}src/visualization/assets",
    ]
    if sys.platform == "darwin":
        command.extend([
            "--onedir", "--hidden-import", "webview.platforms.cocoa",
            "--osx-bundle-identifier", "at.tuwien.greendecoupling",
        ])
    else:
        # Windows must be delivered as one file. WebView2 delivery is a separate
        # outstanding requirement; do not treat this build as a final release.
        command.extend(["--onefile", "--hidden-import", "webview.platforms.edgechromium"])
    command.append(str(root / "src" / "visualization" / "desktop.py"))
    subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
