"""Run the local dashboard in a desktop window, with native CSV/PNG save dialogs."""

import argparse
import base64
import json
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path

# Direct execution and frozen builds use the same package imports.
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from werkzeug.serving import make_server
from src.visualization.app import create_app


@contextmanager
def local_server(app):
    server = make_server("127.0.0.1", 0, app.server, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class SaveBridge:
    """Explicit file saves only; the renderer never writes application data."""

    def __init__(self, smoke_directory=None):
        self.window = None
        self.smoke_directory = smoke_directory

    def save_file(self, filename, content, base64_encoded=False):
        filename = Path(filename).name
        if Path(filename).suffix.lower() not in {".csv", ".png"}:
            raise ValueError("Only CSV and PNG exports are supported")
        if self.smoke_directory is not None:
            # Automated smoke runs use a caller-specified output directory only.
            self.smoke_directory.mkdir(parents=True, exist_ok=True)
            destination = self.smoke_directory / filename
        else:
            import webview
            result = self.window.create_file_dialog(webview.FileDialog.SAVE, save_filename=filename)
            if not result:
                return {"saved": False}
            destination = Path(result[0] if isinstance(result, (tuple, list)) else result)
        contents = base64.b64decode(content, validate=True) if base64_encoded else content.encode("utf-8")
        destination.write_bytes(contents)
        return {"saved": True, "filename": destination.name}


def check_desktop_interaction(window, report_path):
    """Exercise actual rendered callbacks, tab state, resources, and export bridge."""
    report = {"passed": False, "platform": sys.platform}

    def evaluate(expression):
        return window.evaluate_js(expression)

    def wait_for(expression, description):
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline:
            result = evaluate(expression)
            if result:
                return result
            time.sleep(0.2)
        raise RuntimeError(f"Timed out: {description}")

    try:
        if not window.events.loaded.wait(timeout=30):
            raise RuntimeError("Desktop page did not load")
        wait_for("document.querySelectorAll('.js-plotly-plot').length === 6", "six rendered charts")
        initial = wait_for("""(() => {
            const p = document.querySelector('#indexed-trend .js-plotly-plot');
            return p && p.data.length === 2 && p.data[0].name.includes('Germany') &&
                   p.data[0].x[0] === 1990 && p.data[0].y[0] === 100 &&
                   {name:p.data[0].name, baseline:p.data[0].y[0]};
        })()""", "initial Germany/baseline data")
        evaluate("window.dash_clientside.set_props('focus-country', {value:'USA'})")
        wait_for("document.querySelector('#indexed-trend .js-plotly-plot').data[0].name.includes('United States')", "focus callback")
        evaluate("window.dash_clientside.set_props('start-year', {value:2000})")
        wait_for("""(() => {const p=document.querySelector('#indexed-trend .js-plotly-plot');
            return p.data[0].x[0]===2000 && p.data[0].y[0]===100;})()""", "selected-year rebasing")
        evaluate("window.dash_clientside.set_props('compare-countries', {value:['CHN','DEU']})")
        wait_for("document.querySelector('#indexed-trend .js-plotly-plot').data.length === 6", "three-country comparison")
        evaluate("window.dash_clientside.set_props('source-units', {value:'share'})")
        wait_for("document.querySelector('#source-trend .js-plotly-plot').layout.yaxis.title.text.includes('Share')", "source-unit callback")
        evaluate("window.dash_clientside.set_props('view', {value:'footprints'})")
        evaluate("window.dash_clientside.set_props('snapshot-year', {value:2024})")
        wait_for("document.getElementById('pair-status').textContent.includes('0/20')", "missing-consumption case")
        wait_for("document.querySelector('#country-ranking .js-plotly-plot').data[0].x.length === 10", "territorial ranking remains available")
        evaluate("window.dash_clientside.set_props('ranking-metric', {value:'co2_per_capita'})")
        wait_for("document.querySelector('#country-ranking .js-plotly-plot').layout.xaxis.title.text.includes('person')", "per-capita callback")
        evaluate("document.getElementById('export-csv').click()")
        wait_for("document.getElementById('export-status').textContent.includes('.csv')", "CSV export bridge")
        evaluate("document.querySelector('[data-chart=country-ranking]').click()")
        wait_for("document.getElementById('export-status').textContent.includes('.png')", "PNG export bridge")
        evaluate("document.getElementById('reset').click()")
        wait_for("""(() => {const p=document.querySelector('#indexed-trend .js-plotly-plot');
            return p.data.length===2 && p.data[0].name.includes('Germany') && p.data[0].x[0]===1990 &&
                document.getElementById('footprints-panel').style.display==='none';})()""", "reset across tabs")
        external = evaluate("""performance.getEntriesByType('resource').map(e=>e.name)
            .filter(url=>/^https?:/.test(url) && new URL(url).origin!==location.origin)""")
        if external:
            raise RuntimeError(f"Unexpected external resources: {external}")
        report.update(passed=True, initial=initial, rendered_charts=6,
                      checks=["focus", "selected-year rebase", "three-country trend", "source share",
                              "tab state", "2024 accounting unavailable", "territorial ranking", "per-capita switch",
                              "CSV save bridge", "PNG save bridge", "reset", "local assets"],
                      external_resources=external)
    except Exception as error:
        report["error"] = str(error)
    finally:
        destination = Path(report_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n")
        window.destroy()


def main():
    import webview
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-report", type=Path, help="Check UI/callbacks/exports, write JSON and exit")
    args = parser.parse_args()
    bridge = SaveBridge(args.smoke_report.parent / "smoke-exports" if args.smoke_report else None)
    with local_server(create_app()) as url:
        window = webview.create_window("Green Decoupling", url, width=1380, height=900,
                                       min_size=(800, 600), js_api=bridge)
        bridge.window = window
        gui = "edgechromium" if sys.platform == "win32" else None
        if args.smoke_report:
            webview.start(check_desktop_interaction, (window, args.smoke_report), gui=gui)
        else:
            webview.start(gui=gui)
    if args.smoke_report:
        return 0 if json.loads(args.smoke_report.read_text())["passed"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
