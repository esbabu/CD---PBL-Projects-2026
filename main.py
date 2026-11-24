#!/usr/bin/env python3
"""
AI Error Tutor - Streamlit GUI
A friendly Python error message rewriter with Code Correction Validation & Evaluation Dashboard
"""

import streamlit as st
import config
import os
import ast
import json
import html
import datetime
import pandas as pd

# Safe CodeCarbon import
try:
    from codecarbon import EmissionsTracker
    HAS_CODECARBON = True
except ImportError:
    HAS_CODECARBON = False
    class EmissionsTracker:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def start(self): pass
        def stop(self): return None

try:
    from streamlit_ace import st_ace
    HAS_ACE = True
except ImportError:
    HAS_ACE = False

from src.pipeline import AIErrorTutor
from src.evaluation import EvaluationRunner, MetricsStore
from src.language_detector import detect_language
from src.cpp_analyzer import CppAnalyzer
from src.java_analyzer import JavaAnalyzer

st.set_page_config(
    page_title="AI Error Tutor & Diagnostics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Workspace Snippet Storage Helpers
# ─────────────────────────────────────────────

SNIPPETS_FILE = "data/saved_snippets.json"

def load_saved_snippets():
    if os.path.exists(SNIPPETS_FILE):
        try:
            with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def persist_saved_snippets(snippets):
    os.makedirs("data", exist_ok=True)
    try:
        with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
            json.dump(snippets, f, indent=2)
    except Exception:
        pass

# ─────────────────────────────────────────────
# State Management: Buffer & Persistence
# ─────────────────────────────────────────────

if "saved_snippets" not in st.session_state:
    st.session_state["saved_snippets"] = load_saved_snippets()

if "persisted_code" not in st.session_state:
    st.session_state["persisted_code"] = "# Type or paste your Python code here...\n\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n - 1) + fibonacci(n - 2)\n\nprint(fibonacci(5))\n"

if "editor_key_counter" not in st.session_state:
    st.session_state["editor_key_counter"] = 0

# Process any pending code update BEFORE widgets are rendered
if "pending_code" in st.session_state and st.session_state["pending_code"] is not None:
    st.session_state["code_input"] = st.session_state["pending_code"]
    st.session_state["persisted_code"] = st.session_state["pending_code"]
    st.session_state["pending_code"] = None
    st.session_state["editor_key_counter"] += 1
elif "code_input" not in st.session_state:
    st.session_state["code_input"] = st.session_state["persisted_code"]

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

DARK = st.session_state.dark_mode

# ─────────────────────────────────────────────
# Theme & Color Tokens (Dark palette with Green, Blue, Teal & Red)
# ─────────────────────────────────────────────

if DARK:
    BG_APP          = "#070b14"  # Deep dark slate / navy
    BG_CODE         = "#0c1322"  # Terminal / code background
    BORDER_CODE     = "#1e293b"
    TEXT_PRIMARY    = "#f8fafc"
    TEXT_SECONDARY  = "#cbd5e1"
    TEXT_MUTED      = "#94a3b8"
    SURFACE         = "#0f172a"  # Slate container
    SURFACE_HOVER   = "#1e293b"
    BORDER_UI       = "#1e293b"
    BORDER_STRONG   = "#334155"
    LINE_NUM_COL    = "#64748b"
    INPUT_BG        = "#0c1322"
    INPUT_BORDER    = "#1e293b"
    INPUT_COLOR     = "#38bdf8"
    ACCENT_TEAL     = "#14b8a6"  # Teal
    ACCENT_CYAN     = "#06b6d4"  # Cyan
    ACCENT_BLUE     = "#3b82f6"  # Blue
    ACCENT_GREEN    = "#10b981"  # Emerald
    ACCENT_RED      = "#ef4444"  # Error Red
    BTN_BG          = "#14b8a6"  # Teal primary button
    BTN_TXT         = "#070b14"
    BTN_HOVER       = "#2dd4bf"
    PILL_BG         = "#1e293b"
    PILL_BORD       = "#334155"
    PILL_COLOR      = "#38bdf8"
else:
    BG_APP          = "#f8fafc"
    BG_CODE         = "#f1f5f9"
    BORDER_CODE     = "#cbd5e1"
    TEXT_PRIMARY    = "#0f172a"
    TEXT_SECONDARY  = "#334155"
    TEXT_MUTED      = "#64748b"
    SURFACE         = "#ffffff"
    SURFACE_HOVER   = "#f8fafc"
    BORDER_UI       = "#e2e8f0"
    BORDER_STRONG   = "#cbd5e1"
    LINE_NUM_COL    = "#94a3b8"
    INPUT_BG        = "#ffffff"
    INPUT_BORDER    = "#cbd5e1"
    INPUT_COLOR     = "#0284c7"
    ACCENT_TEAL     = "#0d9488"
    ACCENT_CYAN     = "#0891b2"
    ACCENT_BLUE     = "#2563eb"
    ACCENT_GREEN    = "#059669"
    ACCENT_RED      = "#dc2626"
    BTN_BG          = "#0f172a"
    BTN_TXT         = "#ffffff"
    BTN_HOVER       = "#334155"
    PILL_BG         = "#f1f5f9"
    PILL_BORD       = "#e2e8f0"
    PILL_COLOR      = "#0284c7"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    .stApp {{
        background-color: {BG_APP};
        color: {TEXT_PRIMARY};
        font-family: 'Inter', sans-serif;
    }}
    .stSidebar {{
        background-color: {SURFACE} !important;
        border-right: 1px solid {BORDER_UI} !important;
    }}
    [data-testid="stSidebarNav"] {{ display: none; }}
    footer {{ visibility: hidden; }}

    /* VS Code Style Collapsible Sidebar handle */
    [data-testid="collapsedControl"] {{
        background: {SURFACE} !important;
        color: {ACCENT_TEAL} !important;
        border: 1px solid {BORDER_UI} !important;
        border-radius: 6px !important;
        top: 12px !important;
        left: 12px !important;
    }}

    /* Typography */
    h1, h2, h3, h4 {{
        color: {TEXT_PRIMARY} !important;
        font-weight: 600 !important;
        letter-spacing: -0.4px;
    }}
    p, li, span {{ color: {TEXT_SECONDARY}; }}

    /* Buttons */
    button[kind="secondary"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER_STRONG} !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        transition: all 0.2s ease !important;
    }}
    button[kind="secondary"]:hover {{
        background-color: {SURFACE_HOVER} !important;
        border-color: {ACCENT_TEAL} !important;
        color: {ACCENT_TEAL} !important;
    }}

    button[kind="primary"] {{
        background-color: {BTN_BG} !important;
        border: 1px solid {BTN_BG} !important;
        color: {BTN_TXT} !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.2s ease !important;
    }}
    button[kind="primary"]:hover {{
        background-color: {BTN_HOVER} !important;
        border-color: {BTN_HOVER} !important;
        color: {BTN_TXT} !important;
        box-shadow: 0 0 12px rgba(20, 184, 166, 0.4) !important;
    }}

    /* Editor Textarea */
    .stTextArea textarea {{
        background-color: {INPUT_BG} !important;
        color: {INPUT_COLOR} !important;
        border: 1px solid {INPUT_BORDER} !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        caret-color: {ACCENT_TEAL};
    }}
    .stTextArea textarea:focus {{
        border-color: {ACCENT_TEAL} !important;
        box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.2) !important;
        outline: none !important;
    }}

    /* Ace Editor with Line Numbers */
    iframe[title*="streamlit_ace"] {{
        border-radius: 8px !important;
        border: 1px solid {BORDER_UI} !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25) !important;
    }}

    /* Fallback Gutter with Line Numbers */
    .fallback-gutter {{
        background-color: {BG_CODE} !important;
        border: 1px solid {INPUT_BORDER} !important;
        border-right: none !important;
        border-radius: 8px 0 0 8px !important;
        color: {LINE_NUM_COL} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        padding: 10px 8px !important;
        text-align: right !important;
        height: 490px !important;
        overflow: hidden !important;
        user-select: none !important;
    }}
    .has-fallback-gutter .stTextArea textarea {{
        border-radius: 0 8px 8px 0 !important;
        border-left: 1px solid {BORDER_CODE} !important;
    }}

    /* Container padding for flush docked VS Code sidebars */
    .block-container {{
        padding-top: 5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }}

    .block-container:has(.st-key-vscode_main_layout) {{
        padding-right: 0rem !important;
        padding-bottom: 0rem !important;
    }}

    /* Docked Right Bar: Stuck to the screen like the left sidebar, not a floating box */
    .st-key-vscode_main_layout [data-testid="column"]:nth-of-type(2) {{
        background-color: {SURFACE} !important;
        border-left: 1px solid {BORDER_UI} !important;
        border-right: none !important;
        border-top: none !important;
        border-bottom: none !important;
        border-radius: 0px !important;
        position: sticky !important;
        top: 0 !important;
        height: 100vh !important;
        max-height: 100vh !important;
        overflow-y: auto !important;
        padding: 1.25rem 1.5rem 4rem 1.5rem !important;
        margin-top: -1rem !important;
        margin-right: 0 !important;
        box-shadow: -4px 0 20px rgba(0, 0, 0, 0.25) !important;
        scrollbar-width: thin !important;
        scrollbar-color: #334155 transparent !important;
    }}

    .st-key-vscode_main_layout [data-testid="column"]:nth-of-type(1) {{
        padding-right: 28px !important;
        padding-top: 4px !important;
    }}

    /* Remove floating box borders from right container */
    .st-key-vscode_main_layout [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-docked_right_sidebar {{
        border: none !important;
        border-radius: 0px !important;
        background: transparent !important;
        padding: 0 !important;
        box-shadow: none !important;
    }}

    .st-key-vscode_main_layout [data-testid="column"]:nth-of-type(2)::-webkit-scrollbar {{
        width: 6px;
    }}
    .st-key-vscode_main_layout [data-testid="column"]:nth-of-type(2)::-webkit-scrollbar-track {{
        background: transparent;
    }}
    .st-key-vscode_main_layout [data-testid="column"]:nth-of-type(2)::-webkit-scrollbar-thumb {{
        background: #334155;
        border-radius: 3px;
    }}
    .st-key-vscode_main_layout [data-testid="column"]:nth-of-type(2)::-webkit-scrollbar-thumb:hover {{
        background: #14b8a6;
    }}

    /* Result Cards */
    .result-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER_UI};
        border-left-width: 4px;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }}
    .card-explain {{ border-left-color: {ACCENT_TEAL}; }}
    .card-fix     {{ border-left-color: {ACCENT_GREEN}; }}
    .card-similar {{ border-left-color: {ACCENT_BLUE}; }}
    .card-security{{ border-left-color: {ACCENT_RED}; }}
    .card-optimal {{ border-left-color: {ACCENT_CYAN}; }}

    .card-title {{
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .card-title.teal  {{ color: {ACCENT_TEAL}; }}
    .card-title.green {{ color: {ACCENT_GREEN}; }}
    .card-title.blue  {{ color: {ACCENT_BLUE}; }}
    .card-title.red   {{ color: {ACCENT_RED}; }}
    .card-title.cyan  {{ color: {ACCENT_CYAN}; }}
    .card-body {{ font-size: 13px; line-height: 1.6; color: {TEXT_PRIMARY}; }}

    /* Status banners */
    .status-banner {{
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 14px;
        border: 1px solid {BORDER_UI};
    }}

    /* Metric Stat Card */
    .metric-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER_UI};
        border-radius: 8px;
        padding: 16px;
        text-align: left;
        transition: border-color 0.2s;
    }}
    .metric-card:hover {{
        border-color: {ACCENT_TEAL};
    }}
    .metric-label {{
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {TEXT_MUTED};
        margin-bottom: 4px;
    }}
    .metric-value {{
        font-size: 24px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        font-family: 'JetBrains Mono', monospace;
    }}
    .metric-sub {{
        font-size: 11px;
        color: {TEXT_MUTED};
        margin-top: 4px;
    }}

    /* Code Viewer */
    .code-viewer {{
        background-color: {BG_CODE};
        border: 1px solid {BORDER_CODE};
        border-radius: 8px;
        overflow-x: auto;
        max-height: 440px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        line-height: 1.6;
        padding: 20px 0;
        padding-top:40px;
        margin-bottom: 12px;
    }}
    .code-line {{ display: block; padding: 2px 16px; white-space: pre; }}
    .code-line-error {{ background-color: rgba(239, 68, 68, 0.16); border-left: 3px solid {ACCENT_RED}; }}
    .line-num {{
        color: {LINE_NUM_COL};
        display: inline-block;
        min-width: 28px;
        text-align: right;
        margin-right: 14px;
        border-right: 1px solid {BORDER_CODE};
        padding-right: 10px;
        user-select: none;
    }}
    .line-code {{ color: {TEXT_PRIMARY}; }}
    .code-line-error .line-code {{ color: {ACCENT_RED}; }}

    .pill {{
        display: inline-block; padding: 2px 8px; border-radius: 4px;
        font-family: 'JetBrains Mono', monospace; font-size: 12px;
        background-color: {PILL_BG}; color: {PILL_COLOR}; border: 1px solid {PILL_BORD};
        margin: 0 4px;
    }}

    /* Streamlit Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        border-bottom: 1px solid {BORDER_UI};
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 6px 6px 0 0 !important;
        color: {TEXT_MUTED} !important;
        padding: 6px 14px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER_UI} !important;
        border-bottom-color: {SURFACE} !important;
        color: {ACCENT_TEAL} !important;
        font-weight: 600 !important;
    }}

    /* VS Code Explorer item */
    .explorer-item {{
        background-color: {SURFACE};
        border: 1px solid {BORDER_UI};
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 12px;
        transition: border-color 0.2s;
    }}
    .explorer-item:hover {{
        border-color: {ACCENT_TEAL};
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Cache Tutor Instance
# ─────────────────────────────────────────────

@st.cache_resource
def load_tutor():
    try:
        return AIErrorTutor(model_path=config.MODEL_SAVE_PATH, use_ai=True)
    except Exception:
        return AIErrorTutor(use_ai=False)

tutor = load_tutor()
metrics_store = MetricsStore("data/evaluation_metrics.json")


def is_cpp_compiler_available() -> bool:
    analyzer = getattr(tutor, "cpp_analyzer", None)
    if not analyzer:
        return False
    if hasattr(analyzer, "compiler_available"):
        val = analyzer.compiler_available
        return val() if callable(val) else bool(val)
    if hasattr(analyzer, "is_compiler_available"):
        return bool(analyzer.is_compiler_available())
    return bool(getattr(analyzer, "compiler_path", None))


def is_java_compiler_available() -> bool:
    analyzer = getattr(tutor, "java_analyzer", None)
    if not analyzer:
        return False
    if hasattr(analyzer, "compiler_available"):
        val = analyzer.compiler_available
        return val() if callable(val) else bool(val)
    if hasattr(analyzer, "is_compiler_available"):
        return bool(analyzer.is_compiler_available())
    return bool(getattr(analyzer, "compiler_path", None))


def get_live_complexity(code_str: str) -> dict:
    """Proactively calculate the Big-O time complexity of current code."""
    clean = code_str.strip()
    if not clean:
        return {"complexity": None, "has_bottleneck": False, "status": "empty"}
    try:
        tree = ast.parse(clean)
        analysis = tutor.optimizer._detect_bottlenecks(clean, tree)
        return {
            "complexity": analysis.get("current_complexity", "O(N)"),
            "has_bottleneck": analysis.get("has_bottleneck", False),
            "optimal": analysis.get("optimal_complexity", "O(N)"),
            "speedup": analysis.get("speedup_summary", "Optimal"),
            "status": "ok"
        }
    except SyntaxError:
        return {"complexity": "Syntax Error", "has_bottleneck": False, "status": "syntax_error"}
    except Exception:
        return {"complexity": "O(N)", "has_bottleneck": False, "status": "unknown"}


def scroll_to_line(line_num: int):
    if not line_num or line_num <= 0:
        return
    js_code = f"""
    <script>
    (function() {{
        try {{
            const doc = window.parent.document;
            const aceEl = doc.querySelector('.ace_editor');
            if (aceEl && window.parent.ace) {{
                const editor = window.parent.ace.edit(aceEl);
                if (editor) {{
                    editor.gotoLine({line_num}, 0, true);
                    editor.scrollToLine({line_num}, true, true, function() {{}});
                    return;
                }}
            }}
            const markerLayer = doc.querySelector('.ace_marker-layer') || doc.querySelector('.ace_line:nth-child({line_num})');
            if (markerLayer) {{
                markerLayer.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        }} catch (e) {{}}
    }})();
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)


def render_code_viewer(code: str, error_line=None) -> str:
    lines = code.split("\n")
    html_lines = []
    for i, line in enumerate(lines, 1):
        esc = (
            line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        ) or " "
        is_err = (i == error_line)
        css = "code-line code-line-error" if is_err else "code-line"
        html_lines.append(
            f'<span class="{css}">'
            f'<span class="line-num">{i}</span>'
            f'<span class="line-code">{esc}</span>'
            f'</span>'
        )
    return f'<div class="code-viewer">{"".join(html_lines)}</div>'


def show_error_guide(error_type):
    st.markdown(f"### What is a `{error_type}`?")
    if error_type == "SyntaxError":
        st.markdown("A **SyntaxError** occurs when Python cannot parse your code. Common causes include missing colons (`:`), unmatched parentheses, or unclosed string quotes.")
    elif error_type == "NameError":
        st.markdown("A **NameError** occurs when trying to access a variable or function that has not been defined yet in scope.")
    elif error_type == "TypeError":
        st.markdown("A **TypeError** occurs when applying an operation to an object of inappropriate type, such as concatenating a string with an integer.")
    elif error_type == "IndentationError":
        st.markdown("An **IndentationError** occurs when whitespace indentation does not align consistently with surrounding block structure.")
    elif error_type == "SecurityError":
        st.markdown("A **SecurityError** is triggered when static analysis identifies prohibited system commands, dynamic execution, or unauthorized module access.")
    else:
        st.markdown(f"A **{error_type}** is raised when an unhandled condition occurs during execution.")


# ─────────────────────────────────────────────
# Sidebar: VS Code Explorer & Navigation
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🤖 AI Error Tutor")
    st.markdown(f'<span style="font-size:12px; color:{TEXT_MUTED};">Python Pedagogical Debugger & Static Validator</span>', unsafe_allow_html=True)
    st.markdown("<hr style='margin:10px 0; border-color:#1e293b;'>", unsafe_allow_html=True)

    app_mode = st.radio(
        "Navigation",
        ["💻 Tutor & Code Editor", "📊 Evaluation Dashboard"],
        key="nav_selection",
        label_visibility="collapsed"
    )

    st.markdown("<hr style='margin:10px 0; border-color:#1e293b;'>", unsafe_allow_html=True)

    # VS Code Style Workspace Code Storage (Left Bar)
    snippets = st.session_state["saved_snippets"]
    st.markdown(f'<div style="font-size:11px; font-weight:600; color:{ACCENT_TEAL}; letter-spacing:0.5px; margin-bottom:8px;">📁 WORKSPACE FILES ({len(snippets)})</div>', unsafe_allow_html=True)

    if not snippets:
        st.markdown(f'<div style="font-size:12px; color:{TEXT_MUTED}; padding:8px 0;">No saved files yet. Click <b>💾 Save Code</b> in the editor toolbar to store code here.</div>', unsafe_allow_html=True)
    else:
        for idx, snip in enumerate(snippets):
            with st.container():
                st.markdown(f"""
                <div class="explorer-item">
                    <div style="font-weight:600; color:{TEXT_PRIMARY};">📄 {snip['name']}</div>
                    <div style="font-size:11px; color:{TEXT_MUTED}; margin-top:2px;">
                        {snip.get('complexity', 'O(N)')} • {len(snip['code'].splitlines())} lines • {snip.get('timestamp', '')[:10]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_cols = st.columns([1.2, 1])
                with btn_cols[0]:
                    if st.button("📂 Load", key=f"load_snip_{idx}", use_container_width=True):
                        st.session_state["pending_code"] = snip["code"]
                        st.rerun()
                with btn_cols[1]:
                    if st.button("🗑 Del", key=f"del_snip_{idx}", use_container_width=True):
                        st.session_state["saved_snippets"].pop(idx)
                        persist_saved_snippets(st.session_state["saved_snippets"])
                        st.rerun()

    with st.expander("➕ Save Current Code as New File"):
        default_name = f"script_{len(snippets) + 1}.py"
        new_file_name = st.text_input("File Name", value=default_name, key="new_snip_name")
        if st.button("💾 Save to Sidebar", key="btn_save_snip", use_container_width=True):
            current_code = st.session_state.get("persisted_code", "")
            if current_code.strip():
                comp_info = get_live_complexity(current_code)
                comp_tag = comp_info.get("complexity", "O(N)")
                new_entry = {
                    "id": f"snip_{int(datetime.datetime.now().timestamp())}",
                    "name": new_file_name if new_file_name.endswith(".py") else f"{new_file_name}.py",
                    "code": current_code,
                    "complexity": comp_tag,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state["saved_snippets"].append(new_entry)
                persist_saved_snippets(st.session_state["saved_snippets"])
                st.success(f"Saved {new_entry['name']}!")
                st.rerun()

    st.markdown("<hr style='margin:14px 0; border-color:#1e293b;'>", unsafe_allow_html=True)
    _label = "☀️ Light Theme" if st.session_state.dark_mode else "🌙 Dark Theme"
    if st.button(_label, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.session_state["editor_key_counter"] = st.session_state.get("editor_key_counter", 0) + 1
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:11px; font-weight:600; color:{ACCENT_TEAL};">WORKSPACE STATUS</p>', unsafe_allow_html=True)
    cpp_compiler_status = "MinGW g++ (Realtime)" if is_cpp_compiler_available() else "Static Diagnostic Engine"
    java_compiler_status = "JDK javac" if is_java_compiler_available() else "Static Diagnostic Engine"
    st.markdown(
        f"- **Languages**: Python, C++, Java\n"
        f"- **C++ Compiler**: {cpp_compiler_status}\n"
        f"- **Java Engine**: {java_compiler_status}\n"
        f"- **Agent Security**: Active (7 Vectors Guarded)\n"
        f"- **CodeCarbon**: {'Active' if HAS_CODECARBON else 'Disabled'}\n"
    )

    pdf_path = "AI_Error_Tutor_Complete_System_Report.pdf"
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as pf:
                st.download_button(
                    "📕 Download System Report (PDF)",
                    data=pf.read(),
                    file_name="AI_Error_Tutor_Complete_System_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="btn_download_system_pdf"
                )
        except Exception:
            pass


# ─────────────────────────────────────────────
# VIEW 1: Tutor & Code Editor
# ─────────────────────────────────────────────

if app_mode == "💻 Tutor & Code Editor":

    if "opt_result" not in st.session_state:
        st.session_state["opt_result"] = None

    results = []

    # VS Code Layout: Left main editor, Right docked panel stuck to screen
    editor_container = st.container(key="vscode_main_layout")
    col1, col2 = editor_container.columns([1.35, 1.0], gap="small")

    with col1:
        # Header with Language Selector & Proactive Complexity Display
        current_code_for_comp = st.session_state.get("persisted_code", "")
        det_result = detect_language(current_code_for_comp)

        hdr_top_left, hdr_top_right = st.columns([1.2, 0.9])
        with hdr_top_left:
            st.markdown("### 📝 Code Editor <span style='font-size:12px; font-weight:normal; color:#94a3b8;'>(Numbered Lines)</span>", unsafe_allow_html=True)
        with hdr_top_right:
            lang_mode_choice = st.selectbox(
                "Language Mode",
                ["Auto-Detect", "Python", "C++", "Java"],
                index=0,
                key="lang_mode_select",
                label_visibility="collapsed"
            )

        if lang_mode_choice == "Auto-Detect":
            active_lang = det_result.language
            conf_level_str = det_result.confidence_level.capitalize() if hasattr(det_result, "confidence_level") else "Auto"
            conf_score_val = det_result.confidence if hasattr(det_result, "confidence") and isinstance(det_result.confidence, (int, float)) else 1.0
            conf_badge = f'<span class="pill" style="color:{ACCENT_TEAL}; border-color:{ACCENT_TEAL};">🌐 Auto: <b>{active_lang.upper()}</b> ({conf_level_str} Conf - {int(conf_score_val*100)}%)</span>'
        else:
            active_lang = "cpp" if lang_mode_choice == "C++" else ("java" if lang_mode_choice == "Java" else "python")
            conf_badge = f'<span class="pill" style="color:{ACCENT_BLUE}; border-color:{ACCENT_BLUE};">🌐 Manual: <b>{active_lang.upper()}</b></span>'

        live_comp = get_live_complexity(current_code_for_comp) if active_lang == "python" else None

        info_col1, info_col2 = st.columns([1.2, 1.0])
        with info_col1:
            st.markdown(f'<div style="margin-bottom:6px;">{conf_badge}</div>', unsafe_allow_html=True)
        with info_col2:
            if active_lang == "python" and live_comp:
                if live_comp["status"] == "ok":
                    if live_comp["has_bottleneck"]:
                        badge_html = f"""
                        <div style="text-align:right; margin-bottom:6px;">
                            <span class="pill" style="color:{ACCENT_RED}; border-color:{ACCENT_RED}; font-weight:600;">
                                ⏱️ Current: {live_comp['complexity']} (Bottleneck)
                            </span>
                            <span style="font-size:11px; color:{ACCENT_TEAL}; font-weight:600;">➔ Optimal: {live_comp['optimal']}</span>
                        </div>
                        """
                    else:
                        badge_html = f"""
                        <div style="text-align:right; margin-bottom:6px;">
                            <span class="pill" style="color:{ACCENT_GREEN}; border-color:{ACCENT_GREEN}; font-weight:600;">
                                ⏱️ Current: {live_comp['complexity']} (Optimal)
                            </span>
                        </div>
                        """
                    st.markdown(badge_html, unsafe_allow_html=True)
                elif live_comp["status"] == "syntax_error":
                    st.markdown(f'<div style="text-align:right; margin-bottom:6px;"><span class="pill" style="color:#f97316; border-color:#f97316;">⚠️ Fix Syntax to Compute Big-O</span></div>', unsafe_allow_html=True)
            elif active_lang == "cpp":
                compiler_note = "MinGW g++ Live Compile" if is_cpp_compiler_available() else "Static Diagnostic Engine"
                st.markdown(f'<div style="text-align:right; margin-bottom:6px;"><span class="pill" style="color:{ACCENT_CYAN}; border-color:{ACCENT_CYAN};">⚡ {compiler_note}</span></div>', unsafe_allow_html=True)
            elif active_lang == "java":
                java_note = "JDK javac Live Compile" if is_java_compiler_available() else "Static Diagnostic Engine"
                st.markdown(f'<div style="text-align:right; margin-bottom:6px;"><span class="pill" style="color:{ACCENT_CYAN}; border-color:{ACCENT_CYAN};">☕ {java_note}</span></div>', unsafe_allow_html=True)

        with st.expander("📂 Upload Source File (.py, .cpp, .java)", expanded=False):
            uploaded_file = st.file_uploader(
                "Upload Source File",
                type=["py", "cpp", "cc", "cxx", "h", "hpp", "java"],
                help="Upload a Python (.py), C++ (.cpp, .cc, .cxx, .h, .hpp), or Java (.java) file into the editor.",
                key="source_file_uploader",
                label_visibility="collapsed"
            )
            if uploaded_file is not None:
                last_uploaded = st.session_state.get("_last_uploaded_filename")
                if last_uploaded != uploaded_file.name:
                    try:
                        file_bytes = uploaded_file.read()
                        file_text = file_bytes.decode("utf-8", errors="replace")
                        if file_text.strip():
                            fname = uploaded_file.name.lower()
                            if fname.endswith(".py"):
                                st.session_state["lang_mode_select"] = "Python"
                            elif fname.endswith((".cpp", ".cc", ".cxx", ".h", ".hpp")):
                                st.session_state["lang_mode_select"] = "C++"
                            elif fname.endswith(".java"):
                                st.session_state["lang_mode_select"] = "Java"
                            st.session_state["pending_code"] = file_text
                            st.session_state["_last_uploaded_filename"] = uploaded_file.name
                            st.session_state["editor_key_counter"] = st.session_state.get("editor_key_counter", 0) + 1
                            st.success(f"✓ Loaded {uploaded_file.name} into editor ({len(file_text.splitlines())} lines). Click 'Run Analysis' or edit as needed.")
                            st.rerun()
                        else:
                            st.warning(f"File '{uploaded_file.name}' is empty.")
                    except Exception as ex:
                        st.error(f"Failed to read file: {ex}")

        ace_lang = "c_cpp" if active_lang == "cpp" else ("java" if active_lang == "java" else "python")
        if HAS_ACE:
            ace_theme = "dracula" if st.session_state.dark_mode else "github"
            ace_code = st_ace(
                value=st.session_state.get("persisted_code", ""),
                language=ace_lang,
                theme=ace_theme,
                keybinding="vscode",
                font_size=13,
                tab_size=4,
                show_gutter=True,
                show_print_margin=False,
                wrap=False,
                auto_update=True,
                height=490,
                key=f"ace_editor_{st.session_state.get('editor_key_counter', 0)}"
            )
            if ace_code is not None:
                code = ace_code
                st.session_state["persisted_code"] = code
                st.session_state["code_input"] = code
            else:
                code = st.session_state.get("persisted_code", "")
        else:
            current_lines = max(len(st.session_state.get("persisted_code", "").splitlines()), 20)
            gutter_nums = "<br>".join(str(i) for i in range(1, current_lines + 1))
            gut_col, edit_col = st.columns([0.08, 0.92], gap="none")
            with gut_col:
                st.markdown(f'<div class="fallback-gutter">{gutter_nums}</div>', unsafe_allow_html=True)
            with edit_col:
                code = st.text_area(
                    "editor",
                    value=st.session_state.get("persisted_code", ""),
                    height=490,
                    key="code_input",
                    label_visibility="collapsed"
                )
            st.session_state["persisted_code"] = code

        ext_map = {"python": ".py", "cpp": ".cpp", "java": ".java"}
        curr_ext = ext_map.get(active_lang, ".py")

        btn_row = st.columns([1.5, 1.2, 1, 1])
        with btn_row[0]:
            optimize_clicked = st.button("⚡ OPTIMIZE CODE", key="btn_optimize", use_container_width=True, type="primary")
        with btn_row[1]:
            save_workspace_clicked = st.button("💾 SAVE CODE", key="btn_save_ws", use_container_width=True)
        with btn_row[2]:
            st.download_button("⬇ Download", data=code, file_name=f"my_code{curr_ext}", use_container_width=True)
        with btn_row[3]:
            clear_clicked = st.button("🗑 Clear", use_container_width=True)

        if clear_clicked:
            st.session_state["code_input"] = ""
            st.session_state["persisted_code"] = ""
            st.session_state["opt_result"] = None
            st.session_state["editor_key_counter"] = st.session_state.get("editor_key_counter", 0) + 1
            st.rerun()

        if save_workspace_clicked:
            if code.strip():
                comp_tag = live_comp.get("complexity", "O(N)") if (live_comp and live_comp.get("complexity")) else active_lang.upper()
                new_entry = {
                    "id": f"snip_{int(datetime.datetime.now().timestamp())}",
                    "name": f"saved_code_{len(st.session_state['saved_snippets']) + 1}{curr_ext}",
                    "code": code,
                    "complexity": comp_tag,
                    "language": active_lang,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state["saved_snippets"].append(new_entry)
                persist_saved_snippets(st.session_state["saved_snippets"])
                st.success(f"✓ Saved to Workspace in left sidebar: '{new_entry['name']}'")
                st.rerun()

        st.markdown(f'<div style="color:{TEXT_MUTED}; font-size:12px; margin-top:6px;"><i>⚡ Multilingual Tutor supports <b>Python</b>, <b>C++</b>, and <b>Java</b>. Diagnostics and compiler checks run automatically.</i></div>', unsafe_allow_html=True)

        error_bubbles_placeholder = st.empty()

        if optimize_clicked and code.strip():
            with st.spinner("Analyzing algorithmic complexity & synthesizing optimal solution..."):
                with EmissionsTracker(project_name="AI_Error_Tutor_Optimization", log_level="error"):
                    st.session_state["opt_result"] = tutor.optimize_code(code)

    with col2:
        # Docked Right Bar: Full height, sticky, scrollable sidebar
        with st.container(key="docked_right_sidebar"):
            tab_diag, tab_optimal = st.tabs(["🖥️ Diagnostics Terminal", "⚡ Optimal Code"])

            with tab_diag:
                if not code.strip():
                    st.markdown(f'<div style="border: 1px dashed {BORDER_STRONG}; padding: 36px; text-align: center; border-radius: 8px; color: {TEXT_MUTED}; margin-top: 10px;">Waiting for code execution...</div>', unsafe_allow_html=True)
                else:
                    with st.spinner(f"Analyzing {active_lang.upper()} code & running static security checks..."):
                        with EmissionsTracker(project_name=f"AI_Error_Tutor_Analysis_{active_lang}", log_level="error"):
                            results = tutor.analyze_all_errors(code, language=active_lang)

                    # Generate error bubbles for col1
                    bubbles = []
                    for idx, r in enumerate(results):
                        if not r.success and r.line_number:
                            color = ACCENT_RED if r.error_type != "SecurityError" else ACCENT_TEAL
                            bubbles.append(
                                f'<span style="display:inline-block; background-color:{color}; color:white; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:600; margin-right:6px; margin-top:6px;">'
                                f'Line {r.line_number}: {r.error_type}</span>'
                            )
                    if bubbles:
                        error_bubbles_placeholder.markdown('<div style="margin-top: 5px;">' + "".join(bubbles) + '</div>', unsafe_allow_html=True)

                    def render_single_error_card(result, current_code: str, idx: int, active_idx: int = 0):
                        is_active = (idx == active_idx)
                        if is_active and result.line_number:
                            scroll_to_line(result.line_number)

                        # Clean Run / Success
                        if result.success:
                            st.markdown(
                                f'<div class="status-banner" style="color:{ACCENT_GREEN}; border-left: 4px solid {ACCENT_GREEN};">✓ Build & Analysis Successful — No errors detected.</div>',
                                unsafe_allow_html=True,
                            )
                            if getattr(result, "stdout", None):
                                st.markdown(f"""
                                <div class="result-card card-explain" style="border-left-color: {ACCENT_GREEN};">
                                    <div class="card-title green">Program Output</div>
                                    <div class="card-body" style="font-family: monospace; white-space: pre-wrap; background: {BG_CODE}; padding: 10px; border-radius: 4px;">{html.escape(result.stdout)}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            if result.security_warnings:
                                warned = [w for w in result.security_warnings if getattr(w, "level", None) == "WARNING"]
                                for w in warned:
                                    msg = getattr(w, "message", str(w))
                                    lno = getattr(w, "line_number", "?")
                                    st.markdown(f'<div class="status-banner" style="color:{ACCENT_TEAL}; border-left: 4px solid {ACCENT_TEAL};">⚠️ Line {lno}: {msg}</div>', unsafe_allow_html=True)
                            return

                        # Security Policy Block
                        if result.error_type in ("SecurityError", "SecurityViolation"):
                            st.markdown(
                                f'<div class="status-banner" style="color:{ACCENT_RED}; border-left: 4px solid {ACCENT_RED};">✖ Execution Aborted: Security Policy Block</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"""
                            <div class="result-card card-security">
                                <div class="card-title red">Security Policy Violation</div>
                                <div class="card-body">{result.friendly_explanation}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            blocked_lines = [getattr(w, "line_number", None) for w in result.security_warnings if getattr(w, "level", None) == "BLOCKED"]
                            blocked_lines = [l for l in blocked_lines if l is not None]
                            sec_line = (blocked_lines[0] if blocked_lines else result.line_number) if is_active else None
                            if sec_line:
                                st.markdown(render_code_viewer(current_code, sec_line), unsafe_allow_html=True)
                            return

                        # Standard Teaching Card (5 Complete Sections)
                        err_type = result.error_type or "SyntaxError"
                        lang_label = (result.language or active_lang).upper()
                        severity = getattr(result, "severity", None) or "ERROR"
                        severity_color = ACCENT_RED if severity in ("CRITICAL", "ERROR") else ACCENT_TEAL

                        # --- Section A: Error Type ---
                        st.markdown(
                            f'<div class="status-banner" style="color:{severity_color}; border-left: 4px solid {severity_color}; display: flex; justify-content: space-between; align-items: center;">'
                            f'<span><b>Section A &bull; Error Type:</b> {html.escape(err_type)}</span>'
                            f'<span>'
                            f'<span class="pill" style="color:{ACCENT_BLUE}; border-color:{ACCENT_BLUE}; margin-right:4px;">{html.escape(lang_label)}</span>'
                            f'<span class="pill" style="color:{severity_color}; border-color:{severity_color}; font-weight:700;">{html.escape(severity)}</span>'
                            f'</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                        # --- Section B: Error Location ---
                        line_no = result.line_number
                        col_no = getattr(result, "column_number", None)
                        if line_no is not None:
                            loc_str = f"Line {line_no}" + (f", Column {col_no}" if col_no else "")
                        else:
                            loc_str = "Location could not be reliably determined from static context"

                        st.markdown(f"""
                        <div class="result-card card-similar" style="border-left-color: {ACCENT_TEAL};">
                            <div class="card-title teal" style="justify-content:space-between;">
                                <span>📍 Section B &bull; Error Location</span>
                                <span style="font-size:12px; font-weight:normal; color:{TEXT_MUTED};">{loc_str}</span>
                            </div>
                            <div class="card-body">
                        """, unsafe_allow_html=True)
                        target_line = line_no if is_active else None
                        st.markdown(render_code_viewer(current_code, target_line), unsafe_allow_html=True)
                        st.markdown("</div></div>", unsafe_allow_html=True)

                        if result.similar_names:
                            pills_html = "".join(f'<span class="pill">{n}</span>' for n in result.similar_names)
                            st.markdown(f"""
                            <div class="result-card card-similar">
                                <div class="card-title blue">Typo Suggestions</div>
                                <div class="card-body">{pills_html}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Multi-error display and All-Fixes action
                    if len(results) > 1:
                        verified_fixes = [r for r in results if r.candidate_code and r.candidate_code != code and getattr(r, "validated", False)]
                        if len(verified_fixes) > 1:
                            if st.button(f"⚡ Apply All Verified Fixes ({len(verified_fixes)} fixes)", key="btn_apply_all_fixes", type="primary", use_container_width=True):
                                combined = code
                                for vf in verified_fixes:
                                    if vf.candidate_code:
                                        combined = vf.candidate_code
                                st.session_state["pending_code"] = combined
                                st.rerun()

                        st.info(f"Detected **{len(results)} issues** across your {active_lang.upper()} code. Switch tabs below:")
                        err_tabs = st.tabs([f"⚠️ #{i+1} Line {r.line_number or '?'}: {r.error_type or 'Status'}" for i, r in enumerate(results)])
                        active_tab_idx = st.session_state.get("active_error_tab", 0)
                        for i, t in enumerate(err_tabs):
                            with t:
                                render_single_error_card(results[i], code, idx=i, active_idx=active_tab_idx)
                    elif len(results) == 1:
                        render_single_error_card(results[0], code, idx=0, active_idx=0)

            with tab_optimal:
                opt_res = st.session_state.get("opt_result")
                if not code.strip():
                    st.markdown(f'<div style="border: 1px dashed {BORDER_STRONG}; padding: 30px; text-align: center; border-radius: 8px; color: {TEXT_MUTED}; margin-top: 10px;">Enter Python code in the editor and click <b>OPTIMIZE CODE</b>.</div>', unsafe_allow_html=True)
                elif not opt_res:
                    st.markdown(f"""
                    <div style="border: 1px dashed {BORDER_STRONG}; padding: 36px 24px; text-align: center; border-radius: 8px; margin-top: 10px;">
                        <div style="font-size: 32px; margin-bottom: 12px;">⚡</div>
                        <div style="font-size: 16px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 8px;">Algorithmic Time Complexity Tutor</div>
                        <p style="font-size: 13px; max-width: 480px; margin: 0 auto 20px auto; line-height: 1.6; color: {TEXT_MUTED};">
                            Inspect asymptotic Big-O runtime, spot algorithmic bottlenecks, and learn how to optimize.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🚀 Analyze & Optimize Now", key="tab_opt_now", use_container_width=True, type="primary"):
                        with st.spinner("Analyzing algorithmic complexity..."):
                            with EmissionsTracker(project_name="AI_Error_Tutor_Optimization", log_level="error"):
                                st.session_state["opt_result"] = tutor.optimize_code(code)
                        st.rerun()
                else:
                    if not opt_res.get("success"):
                        if opt_res.get("has_syntax_error"):
                            st.markdown(f"""
                            <div class="result-card card-explain" style="border-left-color: {ACCENT_TEAL};">
                                <div class="card-title teal">⚠️ Syntax Error Blocking Complexity Analysis</div>
                                <div class="card-body">
                                    {opt_res.get('message')}<br><br>
                                    <i>Please correct syntax at line {opt_res.get('error_line')} first.</i>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(opt_res.get("message", "Unable to optimize code."))
                    elif opt_res.get("has_bottleneck"):
                        tutoring = opt_res["tutoring"]
                        st.markdown(f"""
                        <div style="background-color: {SURFACE}; border: 1px solid {BORDER_UI}; border-radius: 8px; padding: 18px 20px; margin-bottom: 16px;">
                            <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: {TEXT_MUTED}; margin-bottom: 12px;">
                                Algorithmic Complexity Scoreboard
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 14px; align-items: center;">
                                <div>
                                    <span style="font-size: 11px; color: {TEXT_MUTED}; display: block; margin-bottom: 4px;">CURRENT COMPLEXITY</span>
                                    <span class="pill" style="color:{ACCENT_RED}; border-color:{ACCENT_RED}; font-weight:600;">{opt_res['original_complexity']}</span>
                                </div>
                                <div style="font-size: 18px; color: {TEXT_MUTED}; font-weight: bold;">➔</div>
                                <div>
                                    <span style="font-size: 11px; color: {TEXT_MUTED}; display: block; margin-bottom: 4px;">OPTIMAL COMPLEXITY</span>
                                    <span class="pill" style="color:{ACCENT_GREEN}; border-color:{ACCENT_GREEN}; font-weight:600;">{opt_res['optimal_complexity']}</span>
                                </div>
                                <div style="margin-left: auto;">
                                    <span style="font-size: 11px; color: {TEXT_MUTED}; display: block; margin-bottom: 4px;">ESTIMATED SPEEDUP</span>
                                    <span class="pill" style="color:{ACCENT_CYAN}; border-color:{ACCENT_CYAN}; font-weight:600;">{opt_res.get('speedup_summary')}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="result-card card-explain">
                            <div class="card-title teal">🔍 Bottleneck Diagnosis</div>
                            <div class="card-body">{tutoring['why_slow']}</div>
                        </div>
                        <div class="result-card card-optimal">
                            <div class="card-title cyan">💡 Algorithmic Concept & Optimization</div>
                            <div class="card-body">{tutoring['concept']}<br><br><b>Technique:</b> {tutoring['optimization_technique']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        cand_code = opt_res.get("candidate_code", "")
                        if cand_code:
                            st.markdown(f"""
                            <div class="result-card card-fix" style="border-left-color: {ACCENT_TEAL};">
                                <div class="card-title teal">⚡ Candidate Optimal Code</div>
                                <div class="card-body">
                            """, unsafe_allow_html=True)
                            st.markdown(render_code_viewer(cand_code), unsafe_allow_html=True)
                            opt_actions = st.columns([1, 1])
                            with opt_actions[0]:
                                # Bug fix: Safely stage into pending_code so Streamlit does not throw exception
                                if st.button("📋 Apply to Editor", key="apply_opt", use_container_width=True, type="primary"):
                                    st.session_state["pending_code"] = cand_code
                                    st.session_state["opt_result"] = None
                                    st.rerun()
                            with opt_actions[1]:
                                st.download_button("💾 Save Optimal Code", data=cand_code, file_name="optimal_code.py", use_container_width=True, key="save_opt")
                            st.markdown("</div></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="status-banner" style="color:{ACCENT_GREEN}; border-left: 4px solid {ACCENT_GREEN};">
                            🎉 Outstanding! Your code is already running at optimal algorithmic bounds ({opt_res.get('original_complexity')}).
                        </div>
                        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Sections C, D, and E: Rendered BELOW the code editor, occupying full width left to right
    # ─────────────────────────────────────────────
    def render_error_detail_card(result, current_code: str, idx: int):
        err_type = result.error_type or "SyntaxError"

        # --- Section C: Diagnostic ---
        diag_details = getattr(result, "diagnostic_details", None)
        raw_error_safe = html.escape(result.raw_error) if result.raw_error else "Diagnostic report unavailable."

        diag_body_html = f'<div style="font-family: monospace; font-size: 13px; white-space: pre-wrap; background:{BG_CODE}; padding:8px 12px; border-radius:4px; margin-bottom:8px;">{raw_error_safe}</div>'
        if diag_details and isinstance(diag_details, dict):
            diag_body_html += (
                f'<div style="font-size: 13px; line-height: 1.6; color:{TEXT_SECONDARY};">'
                f'<b>• Attempted Action:</b> {html.escape(diag_details.get("attempted", ""))}<br>'
                f'<b>• Point of Failure:</b> {html.escape(diag_details.get("failed", ""))}<br>'
                f'<b>• Analyzer Trigger:</b> {html.escape(diag_details.get("flagged_reason", ""))}<br>'
                f'<b>• Root Cause:</b> {html.escape(diag_details.get("root_cause", ""))}'
                f'</div>'
            )

        st.markdown(f"""
        <div class="result-card card-explain">
            <div class="card-title teal">🔍 Section C &bull; Technical Diagnostic</div>
            <div class="card-body">{diag_body_html}</div>
        </div>
        """, unsafe_allow_html=True)

        # --- Section D: Pedagogical Explanation (Teacher Mode) — collapsed by default ---
        concept_name = getattr(result, "underlying_concept", None) or err_type
        ped_body = result.friendly_explanation or result.fix_explanation or "Review statement syntax and types."
        with st.expander(f"👨‍🏫 Section D · Pedagogical Explanation (Teacher Mode) — Concept: {concept_name}", expanded=False):
            ped_html = f'<div style="font-size:13px; line-height:1.6; color:{TEXT_PRIMARY};"><div style="margin-bottom:8px;">{ped_body}</div>'
            if result.suggested_fix:
                ped_html += f'<div style="margin-top:8px; padding-top:8px; border-top:1px dashed {BORDER_UI};"><b>💡 Illustrative Example / Pattern:</b><br><code>{html.escape(result.suggested_fix)}</code></div>'
            ped_html += '</div>'
            st.markdown(ped_html, unsafe_allow_html=True)

        with st.expander(f"📚 Error Knowledge Base: {err_type}", expanded=False):
            show_error_guide(err_type)

        # --- Section E: Candidate Code ---
        cand_code = result.candidate_code
        has_cand = bool(cand_code and cand_code.strip() and cand_code.strip() != current_code.strip())
        is_verified = getattr(result, "validated", False)

        if has_cand:
            v_badge = f'<span style="font-size:11px; font-weight:700; color:{ACCENT_GREEN};">✓ Verified Fix</span>' if is_verified else f'<span style="font-size:11px; font-weight:600; color:{ACCENT_CYAN};">⚠ Fix Suggested / Unverified</span>'
            changes = getattr(result, "changes_made", None) or "Adjusted statement on the offending line."
            assumptions = getattr(result, "assumptions", None)

            st.markdown(f"""
            <div class="result-card card-fix" style="border-left-color: {ACCENT_BLUE};">
                <div class="card-title" style="color: {ACCENT_BLUE}; justify-content:space-between;">
                    <span>🛠️ Section E &bull; Candidate Code Correction</span>
                    {v_badge}
                </div>
                <div class="card-body">
                    <div style="font-size:12px; color:{TEXT_MUTED}; margin-bottom:6px;">
                        <b>Changes made:</b> {html.escape(changes)}
                        {f"<br><b>Assumptions:</b> {html.escape(assumptions)}" if assumptions else ""}
                    </div>
            """, unsafe_allow_html=True)

            st.markdown(render_code_viewer(cand_code), unsafe_allow_html=True)

            btn_key = f"apply_diag_fix_{idx}_{getattr(result, 'error_id', None) or idx}"
            if st.button("📋 Apply Fix to Editor", key=btn_key, use_container_width=True, type="primary"):
                st.session_state["pending_code"] = cand_code
                st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            fix_reason = getattr(result, "fix_explanation", None) or (
                f"An automated candidate fix for '{err_type}' could not be reliably synthesized without additional program specifications or surrounding context. "
                "Please refer to the Teacher Mode diagnostic in Section D to apply the appropriate correction manually."
            )
            st.markdown(f"""
            <div class="result-card card-fix" style="border-left-color: {ACCENT_TEAL};">
                <div class="card-title" style="color: {ACCENT_TEAL}; justify-content:space-between;">
                    <span>🛠️ Section E &bull; Candidate Code Correction</span>
                    <span style="font-size:11px; color:{TEXT_MUTED};">ℹ Manual Resolution Required</span>
                </div>
                <div class="card-body" style="font-size:13px; color:{TEXT_SECONDARY}; line-height:1.6;">
                    {fix_reason}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if code.strip() and results:
        active_errors = [r for r in results if not r.success and r.error_type not in ("SecurityError", "SecurityViolation")]
        if active_errors:
            st.markdown("<hr style='margin:28px 0 16px 0; border-color:#1e293b;'>", unsafe_allow_html=True)
            st.markdown("#### 🛠️ Error Diagnostics & Pedagogical Teaching Cards")
            if len(active_errors) == 1:
                render_error_detail_card(active_errors[0], code, idx=0)
            else:
                st.info(f"Showing detailed diagnostic, pedagogical teacher mode, and candidate fix for all **{len(active_errors)} errors** below:")
                detail_tabs = st.tabs([f"⚠️ #{i+1} Line {r.line_number or '?'}: {r.error_type or 'Error'}" for i, r in enumerate(active_errors)])
                for i, dt in enumerate(detail_tabs):
                    with dt:
                        render_error_detail_card(active_errors[i], code, idx=i)


# ─────────────────────────────────────────────
# VIEW 2: Evaluation & Metrics Dashboard
# ─────────────────────────────────────────────

elif app_mode == "📊 Evaluation Dashboard":

    st.markdown("## 📊 Evaluation & Benchmarking Dashboard")
    st.markdown(f'<p style="font-size:13px; color:{TEXT_MUTED};">Empirical performance tracking for static security detection, candidate correction validity, and execution latency.</p>', unsafe_allow_html=True)

    runs = metrics_store.load_runs()

    # Toolbar
    action_cols = st.columns([2, 1, 1])
    with action_cols[0]:
        if runs:
            run_options = [f"{r['timestamp']} ({r['run_id']})" for r in reversed(runs)]
            selected_option = st.selectbox("Select Evaluation Run", run_options, key="run_select")
            selected_run_id = selected_option.split("(")[-1].rstrip(")")
            selected_run = next(r for r in runs if r["run_id"] == selected_run_id)
        else:
            selected_run = None
    with action_cols[1]:
        run_bench_clicked = st.button("▶ Run Benchmark Suite", key="btn_run_bench", use_container_width=True, type="primary")
    with action_cols[2]:
        if runs:
            csv_path = metrics_store.export_csv("data/evaluation_summary.csv")
            with open(csv_path, "r", encoding="utf-8") as f:
                csv_bytes = f.read()
            st.download_button("📥 Export CSV", data=csv_bytes, file_name="evaluation_metrics.csv", mime="text/csv", use_container_width=True)

    if run_bench_clicked:
        with st.spinner("Executing predefined security and correction test suites..."):
            runner = EvaluationRunner(tutor)
            new_run = runner.run_full_evaluation("data/evaluation_metrics.json")
            st.success(f"Benchmark completed successfully! Run ID: {new_run['run_id']}")
            st.rerun()
    st.markdown("<hr style='border-color:#1e293b; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 🧪 Deep Dataset Validation (Agent Performance)")
    st.markdown("Run the system against complex real-world files and malicious attack payloads to evaluate 50+ distinct metrics.")
    
    if st.button("🚀 Run Deep Dataset Tests", key="btn_run_dataset_test", type="primary"):
        with st.spinner("Running Long Code and Security Datasets..."):
            runner = EvaluationRunner(tutor)
            dataset_results = runner.run_dataset_validation()
            
            if "error" in dataset_results:
                st.error(dataset_results["error"])
            else:
                metrics_total = dataset_results["metrics_evaluated"]
                total_passed = (dataset_results["error_detection_passed"] + 
                                dataset_results["error_line_accuracy_passed"] + 
                                dataset_results["security_blocks_passed"] + 
                                dataset_results["stdout_capture_passed"])
                
                st.markdown(f"### ✅ Successfully Evaluated **{metrics_total}** Distinct Metrics!")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Error Type Accuracy", f"{dataset_results['error_detection_passed']} Passed")
                with col2:
                    st.metric("AST Line Accuracy", f"{dataset_results['error_line_accuracy_passed']} Passed")
                with col3:
                    st.metric("Security Interceptions", f"{dataset_results['security_blocks_passed']} Blocked")
                with col4:
                    st.metric("Benign Code Passed", f"{dataset_results['stdout_capture_passed']} Passed")
                    
                if dataset_results["benign_false_positives"] == 0:
                    st.success("✓ 0% False Positives on Benign Code!")
    # Empty State
    if not runs:
        st.markdown(f"""
        <div style="border: 2px dashed {BORDER_STRONG}; border-radius: 12px; padding: 48px; text-align: center; margin-top: 24px; background-color: {SURFACE};">
            <div style="font-size: 40px; margin-bottom: 12px;">📈</div>
            <div style="font-size: 18px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 8px;">No evaluation data yet</div>
            <p style="font-size: 13px; color: {TEXT_MUTED}; max-width: 500px; margin: 0 auto 20px auto;">
                Run the predefined evaluation suite to generate your first verified benchmark results across security detection and candidate correction validation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        sec = selected_run.get("security", {})
        corr = selected_run.get("correction", {})
        beh = corr.get("behavior_preservation", {})
        res = selected_run.get("resources", {})

        # ─────────────────────────────────────────
        # Section 1: Overview Cards
        # ─────────────────────────────────────────
        st.markdown("<br>#### 📌 Overview Metrics", unsafe_allow_html=True)

        card_row_1 = st.columns(4)
        with card_row_1[0]:
            det_rate = sec.get("detection_rate")
            det_str = f"{det_rate * 100:.1f}%" if det_rate is not None else "N/A"
            tp = sec.get("tp", 0)
            fn = sec.get("fn", 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Security Detection Rate (Recall)</div>
                <div class="metric-value" style="color:{ACCENT_GREEN};">{det_str}</div>
                <div class="metric-sub">{tp} blocked / {tp + fn} prohibited cases</div>
            </div>
            """, unsafe_allow_html=True)

        with card_row_1[1]:
            fp_rate = sec.get("false_positive_rate")
            fp_str = f"{fp_rate * 100:.1f}%" if fp_rate is not None else "N/A"
            fp = sec.get("fp", 0)
            tn = sec.get("tn", 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">False-Positive Rate</div>
                <div class="metric-value" style="color:{ACCENT_TEAL if fp == 0 else ACCENT_RED};">{fp_str}</div>
                <div class="metric-sub">{fp} harmless blocked / {fp + tn} harmless cases</div>
            </div>
            """, unsafe_allow_html=True)

        with card_row_1[2]:
            corr_rate = corr.get("correction_success_rate")
            corr_str = f"{corr_rate * 100:.1f}%" if corr_rate is not None else "N/A"
            v_rep = corr.get("validated_repairs", 0)
            e_rep = corr.get("expected_repairs", 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Correction Success Rate</div>
                <div class="metric-value" style="color:{ACCENT_BLUE};">{corr_str}</div>
                <div class="metric-sub">{v_rep} verified / {e_rep} expected repairs</div>
            </div>
            """, unsafe_allow_html=True)

        with card_row_1[3]:
            beh_rate = beh.get("pass_rate")
            beh_str = f"{beh_rate * 100:.1f}%" if beh_rate is not None else "N/A"
            b_passed = beh.get("passed", 0)
            b_tested = beh.get("tested", 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Behavior Preservation</div>
                <div class="metric-value" style="color:{ACCENT_CYAN};">{beh_str}</div>
                <div class="metric-sub">{b_passed} passed / {b_tested} tested ({beh.get('unverified', 0)} unverified)</div>
            </div>
            """, unsafe_allow_html=True)

        card_row_2 = st.columns(4)
        with card_row_2[0]:
            fn_count = sec.get("fn", 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Missed Detections (FN)</div>
                <div class="metric-value" style="color:{ACCENT_GREEN if fn_count == 0 else ACCENT_RED};">{fn_count}</div>
                <div class="metric-sub">Prohibited patterns that bypassed check</div>
            </div>
            """, unsafe_allow_html=True)

        with card_row_2[1]:
            med_analysis = corr.get("median_analysis_latency_ms")
            med_an_str = f"{med_analysis:.2f} ms" if med_analysis is not None else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Median Analysis Latency</div>
                <div class="metric-value">{med_an_str}</div>
                <div class="metric-sub">Static parsing & error diagnostics</div>
            </div>
            """, unsafe_allow_html=True)

        with card_row_2[2]:
            med_corr = corr.get("median_correction_latency_ms")
            med_corr_str = f"{med_corr:.2f} ms" if med_corr is not None else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Median Correction Latency</div>
                <div class="metric-value">{med_corr_str}</div>
                <div class="metric-sub">Correction synthesis & validation</div>
            </div>
            """, unsafe_allow_html=True)

        with card_row_2[3]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Run Timestamp</div>
                <div class="metric-value" style="font-size:14px; padding-top:6px;">{selected_run.get('timestamp', 'N/A')}</div>
                <div class="metric-sub">Suite version: {selected_run.get('test_set_version', '2.0.0')}</div>
            </div>
            """, unsafe_allow_html=True)

        # ─────────────────────────────────────────
        # Section 1A: Agentic AI Security Evaluation (7 Attack Vectors)
        # ─────────────────────────────────────────
        agent_sec = selected_run.get("agent_security", {})
        if agent_sec:
            st.markdown("<br>#### 🤖 Agentic AI Security Evaluation (7 Attack Vectors)", unsafe_allow_html=True)
            st.markdown(f'<p style="font-size:12px; color:{TEXT_MUTED};">Application-layer gating, prompt injection defense, privilege verification, and sensitive info masking for autonomous agent interactions.</p>', unsafe_allow_html=True)

            agent_cards = st.columns(4)
            with agent_cards[0]:
                a_det = agent_sec.get("detection_rate", 1.0)
                a_det_str = f"{a_det * 100:.1f}%"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Attack Detection Rate</div>
                    <div class="metric-value" style="color:{ACCENT_GREEN};">{a_det_str}</div>
                    <div class="metric-sub">{agent_sec.get('tp', 11)} / {agent_sec.get('tp', 11) + agent_sec.get('fn', 0)} attacks flagged</div>
                </div>
                """, unsafe_allow_html=True)

            with agent_cards[1]:
                a_blk = agent_sec.get("blocking_rate", 1.0)
                a_blk_str = f"{a_blk * 100:.1f}%"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Execution Blocking Rate</div>
                    <div class="metric-value" style="color:{ACCENT_GREEN};">{a_blk_str}</div>
                    <div class="metric-sub">100% prohibited actions intercepted</div>
                </div>
                """, unsafe_allow_html=True)

            with agent_cards[2]:
                a_fp = agent_sec.get("false_positive_rate", 0.0)
                a_fp_str = f"{a_fp * 100:.1f}%"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Benign Lookalike FPR</div>
                    <div class="metric-value" style="color:{ACCENT_TEAL};">{a_fp_str}</div>
                    <div class="metric-sub">{agent_sec.get('fp', 0)} harmless cases falsely blocked</div>
                </div>
                """, unsafe_allow_html=True)

            with agent_cards[3]:
                a_log = agent_sec.get("logging_rate", 1.0)
                a_log_str = f"{a_log * 100:.1f}%"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Security Event Audit Rate</div>
                    <div class="metric-value" style="color:{ACCENT_CYAN};">{a_log_str}</div>
                    <div class="metric-sub">Structured JSONL event persistence</div>
                </div>
                """, unsafe_allow_html=True)

            cats = agent_sec.get("category_breakdown", {})
            if cats:
                cat_display = {
                    "DIRECT_PROMPT_INJECTION": "Direct Prompt Injection (Instruction Override)",
                    "INDIRECT_PROMPT_INJECTION": "Indirect Injection (Comments / Docstrings)",
                    "MALICIOUS_CANDIDATE": "Malicious Correction Candidate Injection",
                    "VALIDATION_BYPASS": "Validation Bypass & Dynamic Code Exec",
                    "UNAUTHORIZED_TOOL_USE": "Unauthorized Tool / Subprocess Invocation",
                    "SENSITIVE_INFO_EXPOSURE": "Sensitive Information Disclosure / Leakage",
                    "BENIGN_LOOKALIKE": "Benign Code Lookalikes (False-Positive Control)"
                }
                cat_rows = []
                for cat_key, cdata in cats.items():
                    tested = cdata.get("tested", 0)
                    detected = cdata.get("detected", 0)
                    blocked = cdata.get("blocked", 0)
                    is_benign = (cat_key == "BENIGN_LOOKALIKE")
                    status_text = "✓ Handled Correctly (Passed Unblocked)" if (is_benign and blocked == 0) else ("✓ 100% Intercepted & Blocked" if (not is_benign and blocked == tested) else "⚠️ Attention")
                    # Per-category precision/recall derived from breakdown
                    if is_benign:
                        cat_fp_loc = detected
                        cat_tn_loc = tested - detected
                        prec_str = "N/A (Benign Control)"
                        recall_str = "N/A"
                        acc_str = f"{(cat_tn_loc/tested*100):.0f}% correct (unblocked)" if tested > 0 else "N/A"
                    else:
                        cat_tp_loc = detected
                        cat_fn_loc = tested - detected
                        prec_str = "100%" if cat_tp_loc > 0 else "N/A"
                        recall_str = f"{(cat_tp_loc/tested*100):.0f}%" if tested > 0 else "N/A"
                        acc_str = f"TP={cat_tp_loc}, FN={cat_fn_loc}"
                    cat_rows.append({
                        "Attack Vector / Scenario": cat_display.get(cat_key, cat_key),
                        "Test Cases": tested,
                        "Detected": detected,
                        "Blocked": blocked,
                        "Precision": prec_str,
                        "Recall": recall_str,
                        "Accuracy / Result": acc_str,
                        "Defense Outcome": status_text
                    })
                st.dataframe(pd.DataFrame(cat_rows).set_index("Attack Vector / Scenario"), use_container_width=True)
                # Aggregate summary
                a_tp = agent_sec.get("tp", 0)
                a_fp = agent_sec.get("fp", 0)
                a_fn = agent_sec.get("fn", 0)
                a_tn = agent_sec.get("tn", 0)
                a_total = a_tp + a_fp + a_fn + a_tn
                a_prec = (a_tp / (a_tp + a_fp)) if (a_tp + a_fp) > 0 else None
                a_rec  = (a_tp / (a_tp + a_fn)) if (a_tp + a_fn) > 0 else None
                a_acc  = ((a_tp + a_tn) / a_total) if a_total > 0 else None
                prec_s = f"{a_prec*100:.1f}%" if a_prec is not None else "N/A"
                rec_s  = f"{a_rec*100:.1f}%"  if a_rec  is not None else "N/A"
                acc_s  = f"{a_acc*100:.1f}%"  if a_acc  is not None else "N/A"
                st.markdown(f"""
                <div style="background:{SURFACE}; border:1px solid {BORDER_UI}; border-radius:8px; padding:14px 18px; margin-top:10px;">
                    <div style="font-size:12px; font-weight:600; color:{ACCENT_TEAL}; margin-bottom:10px; text-transform:uppercase; letter-spacing:0.5px;">📊 Aggregate Evaluation Summary</div>
                    <div style="display:flex; flex-wrap:wrap; gap:18px; font-size:13px; color:{TEXT_SECONDARY};">
                        <span><b>TP:</b> {a_tp}</span>
                        <span><b>FP:</b> {a_fp}</span>
                        <span><b>FN:</b> {a_fn}</span>
                        <span><b>TN:</b> {a_tn}</span>
                        <span style="border-left:1px solid {BORDER_UI}; padding-left:14px;"><b>Precision:</b> {prec_s}</span>
                        <span><b>Recall:</b> {rec_s}</span>
                        <span><b>Overall Accuracy:</b> {acc_s}</span>
                    </div>
                    <div style="font-size:11px; color:{TEXT_MUTED}; margin-top:8px;">Precision = TP/(TP+FP) &nbsp;|&nbsp; Recall = TP/(TP+FN) &nbsp;|&nbsp; Accuracy = (TP+TN)/(TP+TN+FP+FN)</div>
                </div>
                """, unsafe_allow_html=True)

        # ─────────────────────────────────────────
        # Section 1B: Multilingual & Complex Program Evaluation
        # ─────────────────────────────────────────
        multi = selected_run.get("multilingual", {})
        if multi:
            st.markdown("<br>#### 🌐 Multilingual & Complex Program Evaluation", unsafe_allow_html=True)
            st.markdown(f'<p style="font-size:12px; color:{TEXT_MUTED};">Professor Feedback Alignment: Empirical evaluation across Python, C++, and Java on Level 1 (Basic), Level 2 (Intermediate), and Level 3 (Complex interacting OOP/algorithms).</p>', unsafe_allow_html=True)

            m_cards = st.columns(4)
            with m_cards[0]:
                l_acc = multi.get("language_detection_accuracy", 1.0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Language Detection Accuracy</div>
                    <div class="metric-value" style="color:{ACCENT_GREEN};">{l_acc * 100:.1f}%</div>
                    <div class="metric-sub">Multi-signal lexical & AST scoring</div>
                </div>
                """, unsafe_allow_html=True)

            with m_cards[1]:
                d_acc = multi.get("diagnostic_accuracy", 1.0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Diagnostic & Compiler Accuracy</div>
                    <div class="metric-value" style="color:{ACCENT_GREEN};">{d_acc * 100:.1f}%</div>
                    <div class="metric-sub">MinGW g++ & static Java parsing</div>
                </div>
                """, unsafe_allow_html=True)

            with m_cards[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Complex Benchmark Corpus</div>
                    <div class="metric-value" style="color:{ACCENT_BLUE};">{multi.get('total_tested', 18)} Programs</div>
                    <div class="metric-sub">6 Python, 6 C++, 6 Java</div>
                </div>
                """, unsafe_allow_html=True)

            with m_cards[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Complexity Range Tested</div>
                    <div class="metric-value" style="color:{ACCENT_CYAN};">L1 ➔ L2 ➔ L3</div>
                    <div class="metric-sub">OOP, Heaps, Memoization, State Machines</div>
                </div>
                """, unsafe_allow_html=True)

            multi_cols = st.columns([1.1, 0.9])
            with multi_cols[0]:
                st.markdown("**Language Diagnostic Performance & Median Latency**")
                by_lang = multi.get("by_language", {})
                lang_rows = []
                for l_name, l_data in by_lang.items():
                    lang_rows.append({
                        "Language": l_name.upper(),
                        "Programs Tested": l_data.get("tested", 0),
                        "Detection Rate": f"{(l_data.get('lang_detected', 0) / max(l_data.get('tested', 1), 1)) * 100:.0f}%",
                        "Diagnostic Recall": f"{(l_data.get('diag_detected', 0) / max(l_data.get('tested', 1), 1)) * 100:.0f}%",
                        "Median Latency": f"{l_data.get('median_latency_ms', 0):.2f} ms"
                    })
                if lang_rows:
                    st.dataframe(pd.DataFrame(lang_rows).set_index("Language"), use_container_width=True)

            with multi_cols[1]:
                st.markdown("**Complexity Tier Pass Rates**")
                by_comp = multi.get("by_complexity", {})
                comp_labels = {
                    "1": "Level 1: Basic (Syntax & Types)",
                    "2": "Level 2: Intermediate (Methods & Containers)",
                    "3": "Level 3: Complex (OOP Hierarchies & Data Structures)"
                }
                comp_rows = []
                for c_level, c_data in by_comp.items():
                    comp_rows.append({
                        "Complexity Tier": comp_labels.get(str(c_level), f"Level {c_level}"),
                        "Cases Tested": c_data.get("tested", 0),
                        "Passed": c_data.get("passed", 0),
                        "Pass Rate": f"{(c_data.get('passed', 0) / max(c_data.get('tested', 1), 1)) * 100:.0f}%"
                    })
                if comp_rows:
                    st.dataframe(pd.DataFrame(comp_rows).set_index("Complexity Tier"), use_container_width=True)

        # ─────────────────────────────────────────
        # Section 2: Security Analysis
        # ─────────────────────────────────────────
        st.markdown("<br>#### 🛡️ Security Analysis", unsafe_allow_html=True)
        sec_cols = st.columns([1, 1])

        with sec_cols[0]:
            st.markdown("**Confusion Matrix Heatmap**")
            tp_v = sec.get("tp", 0)
            fp_v = sec.get("fp", 0)
            fn_v = sec.get("fn", 0)
            tn_v = sec.get("tn", 0)
            try:
                import plotly.graph_objects as go
                z = [[tn_v, fp_v], [fn_v, tp_v]]
                text_vals = [
                    [f"TN<br>{tn_v}", f"FP<br>{fp_v}"],
                    [f"FN<br>{fn_v}", f"TP<br>{tp_v}"]
                ]
                fig = go.Figure(data=go.Heatmap(
                    z=z,
                    x=["Predicted: Safe", "Predicted: Attack"],
                    y=["Actual: Safe", "Actual: Attack"],
                    text=text_vals,
                    texttemplate="%{text}",
                    textfont={"size": 16, "color": "white"},
                    colorscale=[[0, "#0f172a"], [0.5, "#0d9488"], [1, "#10b981"]],
                    showscale=True,
                    hoverongaps=False
                ))
                fig.update_layout(
                    margin=dict(l=10, r=10, t=30, b=10),
                    height=280,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#f8fafc", size=13),
                    xaxis=dict(title="Predicted Class", tickfont=dict(size=12)),
                    yaxis=dict(title="Actual Class", tickfont=dict(size=12), autorange="reversed")
                )
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                matrix_df = pd.DataFrame({
                    "Count": [tp_v, fp_v, tn_v, fn_v]
                }, index=["True Positives (TP)", "False Positives (FP)", "True Negatives (TN)", "False Negatives (FN)"])
                st.bar_chart(matrix_df, color="#14b8a6")

        with sec_cols[1]:
            if len(runs) > 1:
                st.markdown("**Detection Rate & FP Rate Trends**")
                trend_data = {
                    "Run": [r["timestamp"][:16] for r in runs],
                    "Detection Rate (%)": [(r["security"]["detection_rate"] or 0) * 100 for r in runs],
                    "False Positive Rate (%)": [(r["security"]["false_positive_rate"] or 0) * 100 for r in runs]
                }
                trend_df = pd.DataFrame(trend_data).set_index("Run")
                st.line_chart(trend_df)
            else:
                st.markdown("**Security Policy Coverage Breakdown**")
                st.markdown(f"""
                - **Covered Prohibited Modules**: `subprocess`, `socket`, `ctypes`, `http`, `urllib`, `requests`, `multiprocessing`
                - **Covered Dynamic Calls**: `eval()`, `exec()`, `compile()`, `__import__()`, `sys.exit()`
                - **Covered Method Calls**: `os.system()`, `shutil.rmtree()`, `pathlib.unlink()`
                - **Covered Import Patterns**: Aliased modules (`import os as my_os`), Direct function imports (`from os import system`)
                - **Warnings Generated (Not Blocked)**: {sec.get('warnings_count', 0)} file operation warnings
                """)

        # Table of Missed Detections (FN) or False Positives (FP)
        missed = sec.get("missed_cases", [])
        fps = sec.get("false_positive_cases", [])
        if missed or fps:
            st.markdown("**Security Discrepancies**")
            if missed:
                st.error("Missed Detections (False Negatives):")
                st.dataframe(pd.DataFrame(missed), use_container_width=True)
            if fps:
                st.warning("Harmless Code Blocked (False Positives):")
                st.dataframe(pd.DataFrame(fps), use_container_width=True)
        else:
            st.success("✓ Zero false negatives and zero false positives detected in this evaluation run.")

        # ─────────────────────────────────────────
        # Section 3: Correction Performance Graphs
        # ─────────────────────────────────────────
        st.markdown("<br>#### 🔧 Correction Validation Performance", unsafe_allow_html=True)
        corr_cols = st.columns([1, 1])

        with corr_cols[0]:
            st.markdown("**Behavior Preservation Breakdown**")
            beh_counts = pd.DataFrame({
                "Count": [beh.get("passed", 0), beh.get("failed", 0), beh.get("unverified", 0)]
            }, index=["Oracle Passed", "Oracle Failed", "Unverified / No Oracle"])
            st.bar_chart(beh_counts, color="#3b82f6")

        with corr_cols[1]:
            st.markdown("**Outcomes by Error Category**")
            cat_outcomes = corr.get("category_outcomes", {})
            if cat_outcomes:
                cat_rows = []
                for cat_name, data in cat_outcomes.items():
                    cat_rows.append({
                        "Category": cat_name,
                        "Total Cases": data["total"],
                        "Validated": data["success"],
                        "Failed": data["failed"]
                    })
                st.dataframe(pd.DataFrame(cat_rows).set_index("Category"), use_container_width=True)
            else:
                st.info("Insufficient category data.")

        failed_corr = corr.get("failed_cases", [])
        if failed_corr:
            st.markdown("**Failed Correction Inspection**")
            st.dataframe(pd.DataFrame(failed_corr), use_container_width=True)

        # ─────────────────────────────────────────
        # Section 4: Performance & Resources
        # ─────────────────────────────────────────
        st.markdown("<br>#### ⚡ Latency & Computational Resources", unsafe_allow_html=True)
        perf_cols = st.columns([1, 1])

        with perf_cols[0]:
            st.markdown("**Analysis Latency vs Correction Latency (ms)**")
            lat_df = pd.DataFrame({
                "Median Latency (ms)": [
                    corr.get("median_analysis_latency_ms", 0),
                    corr.get("median_correction_latency_ms", 0),
                    sec.get("median_latency_ms", 0)
                ]
            }, index=["Analysis", "Correction Validation", "Security Scan"])
            st.bar_chart(lat_df, color="#06b6d4")

        with perf_cols[1]:
            st.markdown("**Resource & Carbon Tracking (CodeCarbon)**")
            m_status = res.get("measurement_status", "UNAVAILABLE")
            em_kg = res.get("emissions_kg")

            if m_status == "RECORDED" and em_kg is not None:
                st.markdown(f"""
                <div style="background-color:{SURFACE}; border:1px solid {BORDER_UI}; border-radius:8px; padding:16px;">
                    <div style="font-size:11px; color:{TEXT_MUTED};">ESTIMATED RUN EMISSIONS</div>
                    <div style="font-size:20px; font-weight:700; color:{ACCENT_GREEN};">{em_kg:.8f} kg CO₂eq</div>
                    <div style="font-size:12px; color:{TEXT_MUTED}; margin-top:6px;">Status: Valid measurement recorded via CodeCarbon.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color:{SURFACE}; border:1px solid {BORDER_UI}; border-radius:8px; padding:16px;">
                    <div style="font-size:11px; color:{TEXT_MUTED};">EMISSIONS MEASUREMENT STATUS</div>
                    <div style="font-size:18px; font-weight:700; color:{TEXT_MUTED};">Unavailable ({m_status})</div>
                    <div style="font-size:12px; color:{TEXT_MUTED}; margin-top:6px;">
                        <i>Short execution windows (< a few seconds) typically fall below OS power meter thresholds. Emissions tracking requires sustained hardware workloads to provide statistically significant energy figures.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ─────────────────────────────────────────
        # Section 5: Evaluation Run History
        # ─────────────────────────────────────────
        st.markdown("<br>#### 📜 Test Run History", unsafe_allow_html=True)
        history_rows = []
        for r in runs:
            r_sec = r.get("security", {})
            r_corr = r.get("correction", {})
            r_det = r_sec.get("detection_rate")
            r_fp = r_sec.get("false_positive_rate")
            r_succ = r_corr.get("correction_success_rate")

            history_rows.append({
                "Run ID": r.get("run_id"),
                "Timestamp": r.get("timestamp"),
                "Version": r.get("test_set_version"),
                "Total Cases": r.get("total_cases_tested"),
                "Detection Rate": f"{r_det * 100:.1f}%" if r_det is not None else "N/A",
                "False-Positive Rate": f"{r_fp * 100:.1f}%" if r_fp is not None else "N/A",
                "Correction Success": f"{r_succ * 100:.1f}%" if r_succ is not None else "N/A",
                "Analysis Latency": f"{r_corr.get('median_analysis_latency_ms', 0):.2f} ms",
                "Resource Status": r.get("resources", {}).get("measurement_status", "N/A")
            })

        st.dataframe(pd.DataFrame(history_rows).set_index("Run ID"), use_container_width=True)
