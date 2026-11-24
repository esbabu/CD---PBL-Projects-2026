import html

def build_svg():
    width = 2500
    height = 1650

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('''<defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=JetBrains+Mono:wght@500;700&amp;display=swap');
      text { font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
      .mono { font-family: 'JetBrains Mono', monospace; }
      .title { font-size: 38px; font-weight: 800; fill: #0f172a; letter-spacing: -0.5px; }
      .subtitle { font-size: 18px; font-weight: 500; fill: #64748b; }
      .col-header { font-size: 26px; font-weight: 800; letter-spacing: -0.3px; }
      .col-desc { font-size: 14px; font-weight: 500; fill: #64748b; }
      .card-title { font-size: 18px; font-weight: 700; }
      .card-sub { font-size: 13px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
      .card-body { font-size: 13.5px; font-weight: 400; line-height: 1.5; }
      .badge-txt { font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
      .tag { font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
      .arrow { stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
    </style>
    
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f8fafc" />
      <stop offset="100%" stop-color="#f1f5f9" />
    </linearGradient>

    <linearGradient id="before-badge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ef4444" />
      <stop offset="100%" stop-color="#f97316" />
    </linearGradient>

    <linearGradient id="after-badge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#6366f1" />
      <stop offset="100%" stop-color="#8b5cf6" />
    </linearGradient>

    <linearGradient id="hero-bar-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="50%" stop-color="#8b5cf6" />
      <stop offset="100%" stop-color="#ec4899" />
    </linearGradient>

    <!-- Drop Shadows -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#0f172a" flood-opacity="0.06"/>
    </filter>
    <filter id="shadow-card" x="-4%" y="-4%" width="108%" height="112%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.05"/>
    </filter>
    
    <!-- Markers -->
    <marker id="arrow-gray" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#94a3b8" />
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#8b5cf6" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#10b981" />
    </marker>
  </defs>''')

    # Background
    svg.append(f'<rect width="{width}" height="{height}" fill="url(#bg-grad)"/>')

    # Top colorful accent bar
    svg.append(f'<rect x="0" y="0" width="{width}" height="8" fill="url(#hero-bar-grad)"/>')

    # Header section
    svg.append('''
    <g transform="translate(80, 55)">
      <rect x="0" y="0" width="168" height="28" rx="14" fill="#e0e7ff"/>
      <text x="84" y="19" text-anchor="middle" fill="#4338ca" class="badge-txt">SYSTEM EVOLUTION</text>
      
      <text x="0" y="70" class="title">Password Policy Compiler &amp; Validator Architecture</text>
      <text x="0" y="100" class="subtitle">Architectural Evolution from Legacy Linear Compiler to Modern Agentic AI &amp; Neuro-Symbolic Security Platform</text>
    </g>
    ''')

    # -------------------------------------------------------------
    # LEFT COLUMN: BEFORE ARCHITECTURE (X: 80 to 1200)
    # -------------------------------------------------------------
    bx = 80
    bw = 1130
    
    # Left container card
    svg.append(f'''
    <rect x="{bx}" y="180" width="{bw}" height="1400" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="2" filter="url(#shadow)"/>
    
    <!-- Left Column Header -->
    <g transform="translate({bx + 40}, 220)">
      <rect x="0" y="0" width="190" height="32" rx="16" fill="#fee2e2"/>
      <text x="95" y="21" text-anchor="middle" fill="#b91c1c" class="badge-txt">BEFORE ARCHITECTURE</text>
      
      <text x="0" y="68" class="col-header" fill="#1e293b">Traditional Linear Rule Compiler</text>
      <text x="0" y="94" class="col-desc">Rigid 5-stage pipeline · Strict error aborts · Naive character-count validation</text>
    </g>
    ''')

    # Helper for Before Cards
    def before_card(y, tag, title, filename, lines, status_color="#94a3b8"):
        h = 135
        card_svg = f'''
        <g transform="translate({bx + 40}, {y})" filter="url(#shadow-card)">
          <rect x="0" y="0" width="{bw - 80}" height="{h}" rx="14" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
          <rect x="0" y="0" width="6" height="{h}" rx="3" fill="{status_color}"/>
          <rect x="24" y="16" width="70" height="22" rx="6" fill="#f1f5f9"/>
          <text x="59" y="31" text-anchor="middle" fill="#475569" class="tag">{tag}</text>
          
          <text x="106" y="32" class="card-title" fill="#0f172a">{title}</text>
          <text x="{bw - 110}" y="32" text-anchor="end" class="card-sub" fill="#64748b">{filename}</text>
          
          <g transform="translate(24, 62)">
        '''
        for idx, line in enumerate(lines):
            card_svg += f'<text x="0" y="{idx * 24}" class="card-body" fill="#475569">{line}</text>\n'
        card_svg += '''
          </g>
        </g>
        '''
        return card_svg

    # Before Pipeline Cards
    svg.append(before_card(350, "STAGE 1", "Lexical Tokenizer", "lexer.cpp / lexer.h", [
        "• Reads raw policy character stream (minLength 8, requireUpper true)",
        "• Emits tokens: Identifier, Number, Boolean, Newline, End",
        "• Hard failure on unknown or malformed characters with zero recovery"
    ]))

    # Arrow 1
    svg.append(f'''
    <line x1="{bx + bw/2}" y1="485" x2="{bx + bw/2}" y2="515" class="arrow" stroke="#94a3b8" marker-end="url(#arrow-gray)"/>
    ''')

    svg.append(before_card(515, "STAGE 2", "Recursive Descent Parser", "parser.cpp / parser.h", [
        "• Validates policy syntax against grammar: Rule -&gt; Identifier Value",
        "• Throws ParseError immediately on syntax deviations or swapped tokens",
        "• ❌ Aborts entire build immediately; provides NO fix suggestions"
    ], "#ef4444"))

    # Arrow 2
    svg.append(f'''
    <line x1="{bx + bw/2}" y1="650" x2="{bx + bw/2}" y2="680" class="arrow" stroke="#94a3b8" marker-end="url(#arrow-gray)"/>
    ''')

    svg.append(before_card(680, "STAGE 3", "Basic Semantic Checker", "semantic.cpp / semantic.h", [
        "• Checks rule names and range boundaries (minLength &lt;= maxLength)",
        "• Uncaught std::invalid_argument crashes on non-numeric lengths",
        "• ❌ Disallows typos; no fuzzy matching or duplicate resolution suggestions"
    ], "#ef4444"))

    # Arrow 3
    svg.append(f'''
    <line x1="{bx + bw/2}" y1="815" x2="{bx + bw/2}" y2="845" class="arrow" stroke="#94a3b8" marker-end="url(#arrow-gray)"/>
    ''')

    svg.append(before_card(845, "STAGE 4", "IR Generator &amp; Target Emitter", "ir.cpp / codegen.cpp", [
        "• Converts valid AST rules into flat Constraints data structure",
        "• Generates static C++ validator binary (generated_validator.cpp)",
        "• Performs basic heuristic checks (minLength &lt; 6 warning)"
    ]))

    # Arrow 4
    svg.append(f'''
    <line x1="{bx + bw/2}" y1="980" x2="{bx + bw/2}" y2="1010" class="arrow" stroke="#94a3b8" marker-end="url(#arrow-gray)"/>
    ''')

    svg.append(before_card(1010, "STAGE 5", "Naive Password Validator", "main.cpp (Legacy)", [
        "• Checks candidate password against compiled boolean criteria",
        "• Length verification: len &gt;= minLength &amp;&amp; len &lt;= maxLength",
        "• Isolated character count checks: uppercase, lowercase, digits, symbols"
    ]))

    # Before Vulnerabilities Box
    svg.append(f'''
    <g transform="translate({bx + 40}, 1175)">
      <rect x="0" y="0" width="{bw - 80}" height="375" rx="14" fill="#fff1f2" stroke="#fecdd3" stroke-width="1.5"/>
      <rect x="24" y="20" width="160" height="26" rx="6" fill="#ffe4e6"/>
      <text x="104" y="38" text-anchor="middle" fill="#be123c" class="badge-txt">CRITICAL LIMITATIONS</text>
      
      <text x="24" y="78" class="card-title" fill="#9f1239">Vulnerabilities in Baseline Architecture</text>
      
      <g transform="translate(24, 110)">
        <text x="0" y="0" class="card-body" fill="#881337" font-weight="600">❌ Zero Error Recovery / No Guidance:</text>
        <text x="20" y="24" class="card-body" fill="#9f1239">Typing "reqiureDigit true" or "requireUpper maybe" aborted the compiler instantly.</text>
        
        <text x="0" y="60" class="card-body" fill="#881337" font-weight="600">❌ Common Password Blindspot:</text>
        <text x="20" y="84" class="card-body" fill="#9f1239">"Password123!" passed all checks (12 chars, upper, lower, digit, symbol) despite being #1 leaked.</text>
        
        <text x="0" y="120" class="card-body" fill="#881337" font-weight="600">❌ Leetspeak Obfuscation Bypass:</text>
        <text x="20" y="144" class="card-body" fill="#9f1239">"P@ssw0rd!" satisfied symbol/digit rules without recognizing the underlying trivial word "password".</text>
        
        <text x="0" y="180" class="card-body" fill="#881337" font-weight="600">❌ Rigid Binary Output &amp; Clunky UX:</text>
        <text x="20" y="204" class="card-body" fill="#9f1239">Only PASS/FAIL without multi-tier strength scoring or keyboard-first instant execution.</text>
      </g>
    </g>
    ''')

    # -------------------------------------------------------------
    # RIGHT COLUMN: CURRENT ARCHITECTURE (X: 1290 to 2420)
    # -------------------------------------------------------------
    ax = 1290
    aw = 1130

    svg.append(f'''
    <rect x="{ax}" y="180" width="{aw}" height="1400" rx="20" fill="#ffffff" stroke="#c7d2fe" stroke-width="2" filter="url(#shadow)"/>
    
    <!-- Right Column Header -->
    <g transform="translate({ax + 40}, 220)">
      <rect x="0" y="0" width="200" height="32" rx="16" fill="#ede9fe"/>
      <text x="100" y="21" text-anchor="middle" fill="#6d28d9" class="badge-txt">CURRENT ARCHITECTURE</text>
      
      <text x="0" y="68" class="col-header" fill="#0f172a">Agentic AI &amp; Neuro-Symbolic Platform</text>
      <text x="0" y="94" class="col-desc">Self-healing parser/semantic AI · Adversarial leetspeak defense · 14-pt scoring</text>
    </g>
    ''')

    # Helper for Current Cards
    def current_card(y, tag, title, filename, lines, accent_color="#8b5cf6", tag_bg="#ede9fe", tag_color="#6d28d9", h=135):
        card_svg = f'''
        <g transform="translate({ax + 40}, {y})" filter="url(#shadow-card)">
          <rect x="0" y="0" width="{aw - 80}" height="{h}" rx="14" fill="#ffffff" stroke="#e0e7ff" stroke-width="1.5"/>
          <rect x="0" y="0" width="6" height="{h}" rx="3" fill="{accent_color}"/>
          <rect x="24" y="16" width="95" height="22" rx="6" fill="{tag_bg}"/>
          <text x="71" y="31" text-anchor="middle" fill="{tag_color}" class="tag">{tag}</text>
          
          <text x="130" y="32" class="card-title" fill="#0f172a">{title}</text>
          <text x="{aw - 110}" y="32" text-anchor="end" class="card-sub" fill="#6366f1">{filename}</text>
          
          <g transform="translate(24, 62)">
        '''
        for idx, line in enumerate(lines):
            card_svg += f'<text x="0" y="{idx * 24}" class="card-body" fill="#334155">{line}</text>\n'
        card_svg += '''
          </g>
        </g>
        '''
        return card_svg

    # Current Cards
    svg.append(current_card(350, "LEXER", "Standard Lexical Tokenizer", "lexer.cpp / lexer.h", [
        "• Strict, high-precision tokenization preserved (no hallucinated tokens)",
        "• Accurate line/column tracking for precise downstream AI diagnostics",
        "• Unqualified std::move clean compilation with 0 warnings"
    ], "#3b82f6", "#dbeafe", "#1d4ed8"))

    # Arrow 1
    svg.append(f'''
    <line x1="{ax + aw/2}" y1="485" x2="{ax + aw/2}" y2="515" class="arrow" stroke="#8b5cf6" marker-end="url(#arrow-purple)"/>
    ''')

    svg.append(current_card(515, "AGENTIC AI", "Agentic AI Syntax Assistant", "parser.cpp / ast.h", [
        "• Inverted Token Recovery: Detects 'true requireDigit' -&gt; repairs to 'requireDigit true'",
        "• Type Heuristic Repair: Flags 'requireUpper maybe' -&gt; suggests standard 'true'",
        "• Emits structured AgentSuggestion with exact source diffs and reasoning"
    ], "#8b5cf6", "#ede9fe", "#6d28d9"))

    # Arrow 2
    svg.append(f'''
    <line x1="{ax + aw/2}" y1="650" x2="{ax + aw/2}" y2="680" class="arrow" stroke="#8b5cf6" marker-end="url(#arrow-purple)"/>
    ''')

    svg.append(current_card(680, "AGENTIC AI", "Agentic AI Semantic Assistant", "semantic.cpp / semantic.h", [
        "• Levenshtein Typo Repair: 'reqiureDigit' -&gt; calculates distance &amp; suggests 'requireDigit'",
        "• Safe stoi &amp; Deduplication: Catches crashes; suggests removal of duplicate lines",
        "• Adaptive Zero-Trust Hardening: Enforces NIST minLength &gt;= 8 floor safely"
    ], "#8b5cf6", "#ede9fe", "#6d28d9"))

    # Interactive loop arrow / box
    svg.append(f'''
    <!-- Interactive Loop Badge -->
    <g transform="translate({ax + aw - 240}, 625)">
      <rect x="0" y="0" width="170" height="28" rx="8" fill="#dcfce7" stroke="#86efac"/>
      <text x="85" y="19" text-anchor="middle" fill="#15803d" class="tag">✓ [OKAY / APPLY] UI LOOP</text>
    </g>
    ''')

    # Arrow 3
    svg.append(f'''
    <line x1="{ax + aw/2}" y1="815" x2="{ax + aw/2}" y2="845" class="arrow" stroke="#8b5cf6" marker-end="url(#arrow-purple)"/>
    ''')

    svg.append(current_card(845, "IR &amp; TARGET", "Optimized IR &amp; Target Code Generator", "ir.cpp / codegen.cpp", [
        "• Tri-state constraint system (-1: unset, 0: false, 1: true) for unambiguous logic",
        "• Emits robust generated_validator.cpp C++ executable target",
        "• Static IR Analyzer detects fixed length policies and weak constraint risks"
    ], "#3b82f6", "#dbeafe", "#1d4ed8"))

    # Arrow 4
    svg.append(f'''
    <line x1="{ax + aw/2}" y1="980" x2="{ax + aw/2}" y2="1010" class="arrow" stroke="#10b981" marker-end="url(#arrow-green)"/>
    ''')

    # Big Neuro-Symbolic Engine Box (Height 540)
    svg.append(f'''
    <g transform="translate({ax + 40}, 1010)" filter="url(#shadow-card)">
      <rect x="0" y="0" width="{aw - 80}" height="540" rx="14" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
      <rect x="0" y="0" width="6" height="540" rx="3" fill="#10b981"/>
      
      <rect x="24" y="18" width="170" height="24" rx="6" fill="#dcfce7"/>
      <text x="109" y="34" text-anchor="middle" fill="#166534" class="tag">NEURO-SYMBOLIC CORE</text>
      
      <text x="206" y="36" class="card-title" fill="#0f172a">Advanced Adversarial Evaluation Engine</text>
      <text x="{aw - 110}" y="36" text-anchor="end" class="card-sub" fill="#15803d">main.cpp / web IDE</text>
      
      <!-- Sub-modules grid -->
      <g transform="translate(24, 65)">
        <!-- Sub 1 -->
        <rect x="0" y="0" width="490" height="135" rx="10" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="18" y="28" font-size="15px" font-weight="700" fill="#166534">1. Adversarial Leetspeak Normalizer</text>
        <text x="18" y="52" class="card-body" fill="#1e293b">• Maps homoglyphs &amp; substitutions: @-&gt;a, 0-&gt;o, 1-&gt;i, 3-&gt;e</text>
        <text x="18" y="74" class="card-body" fill="#1e293b">• Maps symbols: 4-&gt;a, 5-&gt;s, 7-&gt;t, $-&gt;s, !-&gt;i</text>
        <text x="18" y="96" class="card-body" fill="#15803d" font-weight="600">✓ Neutralizes bypasses like "P@ssw0rd!" and "Adm!n0"</text>

        <!-- Sub 2 -->
        <rect x="515" y="0" width="490" height="135" rx="10" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="18" y="28" font-size="15px" font-weight="700" fill="#166534">2. Base-Word Stemming &amp; Stripper</text>
        <text x="18" y="52" class="card-body" fill="#1e293b">• Strips trailing numbers and delimiters (e.g. "99!", "#2026")</text>
        <text x="18" y="74" class="card-body" fill="#1e293b">• Unveils disguised dictionary roots beneath affixes</text>
        <text x="18" y="96" class="card-body" fill="#15803d" font-weight="600">✓ Catches "P@ssw0rd99!" -&gt; stems to "password"</text>

        <!-- Sub 3 -->
        <rect x="0" y="150" width="490" height="135" rx="10" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="18" y="28" font-size="15px" font-weight="700" fill="#166534">3. Common Password Intelligence Library</text>
        <text x="18" y="52" class="card-body" fill="#1e293b">• Built-in blacklist of top compromised passwords</text>
        <text x="18" y="74" class="card-body" fill="#1e293b">• Blocks: password, 123456, admin, qwerty, sunshine...</text>
        <text x="18" y="96" class="card-body" fill="#15803d" font-weight="600">✓ Immediate score override to 0 (Very Weak)</text>

        <!-- Sub 4 -->
        <rect x="515" y="150" width="490" height="135" rx="10" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="18" y="28" font-size="15px" font-weight="700" fill="#166534">4. Pattern Penalties &amp; 14-Pt Scoring</text>
        <text x="18" y="52" class="card-body" fill="#1e293b">• Penalizes sequential runs (abc, 123) and repeats (aaa)</text>
        <text x="18" y="74" class="card-body" fill="#1e293b">• Multi-tier rating: Very Weak (0-2), Weak, Medium, Strong</text>
        <text x="18" y="96" class="card-body" fill="#15803d" font-weight="600">✓ Qualitative explanation badge + breakdown meters</text>

        <!-- Sub 5: UI & UX Integration -->
        <rect x="0" y="300" width="1005" height="145" rx="10" fill="#f8fafc" stroke="#cbd5e1"/>
        <text x="18" y="28" font-size="15px" font-weight="700" fill="#0f172a">5. Interactive Agentic UI &amp; Keyboard UX</text>
        <text x="18" y="52" class="card-body" fill="#334155">• <tspan font-weight="700" fill="#6d28d9">[✓ Okay / Apply]</tspan> Buttons: Interactive cards allow 1-click in-place code patching in browser IDE</text>
        <text x="18" y="76" class="card-body" fill="#334155">• <tspan font-weight="700" fill="#6d28d9">[✓ Accept All AI Fixes]</tspan>: Batch-resolves all syntax &amp; semantic errors at once</text>
        <text x="18" y="100" class="card-body" fill="#334155">• <tspan font-weight="700" fill="#0369a1">Instant "Return / Enter" Key</tspan>: Evaluates password on Enter without moving cursor to evaluate button</text>
      </g>
    </g>
    ''')

    svg.append('</svg>')
    return '\n'.join(svg)

if __name__ == '__main__':
    content = build_svg()
    with open('architecture_comparison.svg', 'w') as f:
        f.write(content)
    print("architecture_comparison.svg generated successfully.")

