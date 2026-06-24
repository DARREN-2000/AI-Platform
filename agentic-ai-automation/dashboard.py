"""Server-rendered HTML dashboard. Kept separate so CSS braces stay literal."""
from html import escape

_CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       margin: 0; background: #0d1117; color: #e6edf3; }
header { padding: 28px 40px; border-bottom: 1px solid #21262d;
         display: flex; align-items: center; gap: 12px; }
header h1 { font-size: 20px; margin: 0; font-weight: 600; }
.wrap { padding: 32px 40px; max-width: 1100px; margin: 0 auto; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
         gap: 16px; margin-bottom: 32px; }
.card { background: #161b22; border: 1px solid #21262d; border-radius: 12px; padding: 20px; }
.card .n { font-size: 30px; font-weight: 700; }
.card .l { color: #8b949e; font-size: 13px; margin-top: 4px; }
table { width: 100%; border-collapse: collapse; background: #161b22;
        border: 1px solid #21262d; border-radius: 12px; overflow: hidden; }
th, td { text-align: left; padding: 12px 16px; border-bottom: 1px solid #21262d; font-size: 14px; }
th { color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase; }
.tag { background: #1f6feb33; color: #79c0ff; padding: 2px 8px; border-radius: 6px; font-size: 12px; }
.summary { color: #8b949e; }
.empty { text-align: center; color: #8b949e; padding: 32px; }
.actions { margin-bottom: 24px; display: flex; gap: 12px; }
button { background: #238636; color: #fff; border: 0; padding: 10px 18px;
         border-radius: 8px; font-size: 14px; cursor: pointer; }
button.secondary { background: #21262d; }
"""

_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agentic AI Automation</title>
<style>__CSS__</style></head>
<body>
  <header><span>🤖</span><h1>Agentic AI Automation</h1></header>
  <div class="wrap">
    <div class="cards">
      <div class="card"><div class="n">__TOTAL__</div><div class="l">Total agent runs</div></div>
      <div class="card"><div class="n">__AGENTS__</div><div class="l">Active agents</div></div>
      <div class="card"><div class="n">__REPO__</div><div class="l">Target repo</div></div>
    </div>
    <div class="actions">
      <button onclick="run('/trigger/triage')">Run triage</button>
      <button class="secondary" onclick="run('/trigger/reminders')">Run reminders</button>
    </div>
    <table>
      <thead><tr><th>Time</th><th>Agent</th><th>Trigger</th><th>OK</th><th>Summary</th></tr></thead>
      <tbody>__ROWS__</tbody>
    </table>
  </div>
  <script>
    async function run(url) { await fetch(url, { method: 'POST' }); location.reload(); }
  </script>
</body></html>"""


def render_dashboard(stats: dict, runs: list[dict], repo: str) -> str:
    if runs:
        rows = "".join(
            "<tr>"
            f"<td>{escape(str(r['created_at'])[:19].replace('T', ' '))}</td>"
            f"<td><span class='tag'>{escape(str(r['agent']))}</span></td>"
            f"<td>{escape(str(r['trigger']))}</td>"
            f"<td>{'✅' if r['success'] else '❌'}</td>"
            f"<td class='summary'>{escape((str(r['summary']) or '')[:140])}</td>"
            "</tr>"
            for r in runs
        )
    else:
        rows = "<tr><td colspan='5' class='empty'>No runs yet — trigger one to get started.</td></tr>"

    return (
        _TEMPLATE.replace("__CSS__", _CSS)
        .replace("__TOTAL__", str(stats.get("total_runs", 0)))
        .replace("__AGENTS__", str(len(stats.get("by_agent", []))))
        .replace("__REPO__", escape(repo or "—"))
        .replace("__ROWS__", rows)
    )
