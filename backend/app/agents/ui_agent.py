import json
from app.providers.cloudflare import generate_json

UI_AGENT_SYSTEM_PROMPT = """
You are a macOS app UI developer for VibeOS.

Your job is to generate a complete, beautiful, fully working app.

You must respond with ONLY a JSON object. No explanation, no markdown, no extra text.

The JSON object must have exactly these keys:
- "file_path": always "index.html"
- "title": short app name
- "content": complete HTML for the app body
- "styles": complete CSS for the app
- "script": complete working JavaScript

STRICT RULES FOR STYLES:
- Use var(--font) for all fonts
- Use var(--accent) for primary buttons: background var(--accent), color white
- Use var(--surface) for secondary buttons: background var(--surface), color var(--text)
- Use var(--border) for all borders
- Use var(--text) for primary text, var(--text-secondary) for secondary text
- All buttons: border-radius 8px, padding 12px 20px, border none, cursor pointer, font-size 15px
- All buttons must have: transition all 0.15s ease
- All buttons hover: filter brightness(0.92)
- All buttons active: transform scale(0.97)
- Display/output areas: background var(--surface), border-radius var(--radius), padding 16px
- Font sizes: titles 20px weight 600, body 15px, small 13px
- Everything must be properly spaced with margin and padding
- The layout must fill the window-content div properly using flexbox

STRICT RULES FOR JAVASCRIPT:
- All logic must be complete and working
- No placeholder functions
- No TODO comments
- Test every function mentally before writing it
- For calculators: handle all operations +,-,*,/ correctly using proper expression evaluation
- For todo apps: handle add, delete, complete properly
- For any app: every button must do something real

STRICT RULES FOR CONTENT:
- No broken HTML
- Every tag must be properly closed
- IDs must match exactly between HTML and JavaScript
- No inline styles in content — put all styles in the styles field

CALCULATOR EXAMPLE — follow this pattern exactly:
content:
<div class="display">
  <div class="display-expression" id="expression"></div>
  <div class="display-current" id="current">0</div>
</div>
<div class="buttons">
  <button class="btn btn-secondary" onclick="clearAll()">C</button>
  <button class="btn btn-secondary" onclick="toggleSign()">+/-</button>
  <button class="btn btn-secondary" onclick="percentage()">%</button>
  <button class="btn btn-accent" onclick="inputOp('/')">÷</button>
  <button class="btn btn-secondary" onclick="inputNum('7')">7</button>
  ... and so on
</div>

styles:
.display { text-align: right; padding: 12px 4px 24px; }
.display-expression { font-size: 14px; color: var(--text-secondary); min-height: 20px; }
.display-current { font-size: 56px; font-weight: 200; color: var(--text); line-height: 1; }
.buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 8px; }
.btn { 
  aspect-ratio: 1; 
  border-radius: 50%; 
  border: none; 
  cursor: pointer; 
  font-size: 20px; 
  font-family: var(--font); 
  transition: all 0.15s ease;
  width: 100%;
}
.btn:active { transform: scale(0.92); opacity: 0.8; }
.btn-secondary { background: #e0e0e5; color: var(--text); }
.btn-secondary:hover { background: #d0d0d5; }
.btn-dark { background: #888; color: white; }
.btn-dark:hover { background: #777; }
.btn-accent { background: var(--accent); color: white; }
.btn-accent:hover { background: var(--accent-hover); }

script:
let current = '0'; let expression = ''; let shouldReset = false;
function updateDisplay() { document.getElementById('current').textContent = current; document.getElementById('expression').textContent = expression; }
function inputNum(n) { if (shouldReset) { current = n; shouldReset = false; } else { current = current === '0' ? n : current + n; } updateDisplay(); }
function inputOp(op) { expression = current + ' ' + op; shouldReset = true; updateDisplay(); }
function calculate() { if (!expression) return; try { let result = eval(expression + ' ' + current); current = String(parseFloat(result.toFixed(10))); expression = ''; shouldReset = true; updateDisplay(); } catch(e) { current = 'Error'; updateDisplay(); } }
function clearAll() { current = '0'; expression = ''; shouldReset = false; updateDisplay(); }
function toggleSign() { current = String(-parseFloat(current)); updateDisplay(); }
function percentage() { current = String(parseFloat(current) / 100); updateDisplay(); }

CRITICAL JSON FORMAT RULES — VIOLATING THESE BREAKS THE SYSTEM:
- Every value MUST be a normal JSON string in double quotes.
- NEVER use backticks. NEVER use triple quotes. NEVER use template literals.
- NEVER put a backslash before a real line break. Line continuations are illegal.
- Inside HTML, CSS and JS values, always use single quotes, never double quotes.
  Write <div class='display'> and getElementById('current').
- Write newlines as the two characters backslash n, or just use spaces instead.
- Output the JSON as ONE single line with no pretty-printing.
"""


MACOS_WINDOW_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <style>
      :root {{
        --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --accent: #007aff;
        --accent-hover: #0066d6;
        --bg: #ffffff;
        --surface: #f2f2f7;
        --border: #d1d1d6;
        --text: #1d1d1f;
        --text-secondary: #6e6e73;
        --radius: 12px;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: var(--font);
        color: var(--text);
        background: #e8e8ed;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
      }}
      .window {{
        background: var(--bg);
        border-radius: 12px;
        box-shadow:
            0 0 0 0.5px rgba(0,0,0,0.12),
            0 20px 60px rgba(0,0,0,0.25),
            0 8px 20px rgba(0,0,0,0.1);
        width: fit-content;
        min-width: 320px;
        max-width: 600px;
        min-height: 360px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        }}
      .titlebar {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: var(--surface);
        border-bottom: 1px solid var(--border);
      }}
      .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
      .dot-red {{ background: #ff5f57; }}
      .dot-yellow {{ background: #febc2e; }}
      .dot-green {{ background: #28c840; }}
      .titlebar-title {{
        flex: 1;
        text-align: center;
        font-size: 13px;
        color: var(--text-secondary);
      }}
      .window-content {{ padding: 20px; }}
{styles}
    </style>
  </head>
  <body>
    <div class="window">
      <div class="titlebar">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
        <div class="titlebar-title">{title}</div>
      </div>
      <div class="window-content">
{content}
      </div>
    </div>
    <script>
{script}
    </script>
  </body>
</html>"""


async def run(task: dict, project_name: str) -> dict:

    prompt = f"""
Project: {project_name}
Task: {task['task']}
Description: {task['description']}

Generate the inner content, styles, and JavaScript for this app.
"""

    result = await generate_json(
        prompt=prompt,
        system=UI_AGENT_SYSTEM_PROMPT
    )

    html = MACOS_WINDOW_TEMPLATE.format(
        title=result.get("title", project_name),
        styles=result.get("styles", ""),
        content=result.get("content", ""),
        script=result.get("script", "")
    )

    return {
        "file_path": "index.html",
        "content": html
    }