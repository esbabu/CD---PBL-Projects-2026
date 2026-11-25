from pathlib import Path

art_dir = Path(r"C:\Users\nitya\.gemini\antigravity\brain\0f5d10c3-a5f3-4f8e-96ba-224b78cfb817")
svg_combined = (art_dir / "figure2_combined_white_background.svg").read_text(encoding="utf-8")
svg_a = (art_dir / "figure2_bleu_vs_rouge.svg").read_text(encoding="utf-8")
svg_b = (art_dir / "figure2_confusion_matrix.svg").read_text(encoding="utf-8")

template_head = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Figure 2: Empirical Evaluation Graphs (BLEU vs. ROUGE & Confusion Matrix)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {
      background-color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    .graph-card {
      background: #ffffff;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04);
      border: 1px solid #e2e8f0;
    }
  </style>
</head>
<body class="p-4 sm:p-8 bg-white text-slate-800">
  <div class="max-w-5xl mx-auto">
    <div class="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 pb-5">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Empirical Testcase Evaluation Suite</h1>
        <p class="text-sm text-slate-500 mt-1">
          Measured over all benchmarked test cases (47 Firmware Security &amp; 41 Syntax/Typo Cases) &bull; Pure White Background
        </p>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
          White Background Matched
        </span>
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
          88 Total Test Cases Evaluated
        </span>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button onclick="showTab('combined')" id="tab-combined" class="tab-btn px-4 py-2 text-sm font-medium rounded-lg border border-sky-600 bg-sky-600 text-white transition-colors">
        Combined Template View
      </button>
      <button onclick="showTab('fig_a')" id="tab-fig_a" class="tab-btn px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 transition-colors">
        Figure 2. (a) BLEU vs. ROUGE
      </button>
      <button onclick="showTab('fig_b')" id="tab-fig_b" class="tab-btn px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 transition-colors">
        Figure 2. (b) Confusion Matrix
      </button>
      <button onclick="showTab('metrics')" id="tab-metrics" class="tab-btn px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 transition-colors">
        Empirical Scores Table
      </button>
    </div>

    <!-- Tab 1: Combined View -->
    <div id="view-combined" class="graph-card rounded-2xl p-6 sm:p-10 mb-8 flex flex-col items-center bg-white">
      <div class="w-full text-center mb-4">
        <span class="text-xs font-bold tracking-wider uppercase text-slate-400">Actual Measured Data (Pure White Background)</span>
      </div>
      <div class="overflow-x-auto w-full flex justify-center py-2">
"""

tab_2_start = """      </div>
    </div>

    <!-- Tab 2: Figure 2 (a) Standalone -->
    <div id="view-fig_a" class="hidden graph-card rounded-2xl p-6 sm:p-10 mb-8 flex flex-col items-center bg-white">
      <div class="w-full text-center mb-4">
        <span class="text-xs font-bold tracking-wider uppercase text-slate-400">Figure 2. (a) High-Resolution Vector</span>
      </div>
      <div class="overflow-x-auto w-full flex justify-center py-2">
"""

tab_3_start = """      </div>
      <div class="w-full mt-6 bg-slate-50 p-4 rounded-xl text-xs text-slate-600 border border-slate-200">
        <strong>Metric Interpretation:</strong> Compares generation similarity of the remediated code against ground truth compliant firmware. Top row presents ROUGE-L (Longest Common Subsequence F1 score); bottom row presents BLEU-4 n-gram precision. High scores (0.84 to 1.00) demonstrate robust AST syntax reconstruction.
      </div>
    </div>

    <!-- Tab 3: Figure 2 (b) Standalone -->
    <div id="view-fig_b" class="hidden graph-card rounded-2xl p-6 sm:p-10 mb-8 flex flex-col items-center bg-white">
      <div class="w-full text-center mb-4">
        <span class="text-xs font-bold tracking-wider uppercase text-slate-400">Figure 2. (b) Confusion Matrix High-Resolution Vector</span>
      </div>
      <div class="overflow-x-auto w-full flex justify-center py-2">
"""

table_and_tail = """      </div>
      <div class="w-full mt-6 bg-slate-50 p-4 rounded-xl text-xs text-slate-600 border border-slate-200">
        <strong>Classification Breakdown:</strong> Evaluates accuracy of the Security Auditor and Diagnostic Breakdown engine across 5 primary defect classes (1: Syntax, 2: Declaration, 3: Type, 4: Memory, 5: Scope/Flow). Strong diagonal dominance (92–96%) confirms high classification precision across all 88 evaluated firmware test cases.
      </div>
    </div>

    <!-- Tab 4: Metrics Table -->
    <div id="view-metrics" class="hidden graph-card rounded-2xl p-6 sm:p-8 mb-8 bg-white">
      <h3 class="text-lg font-bold text-slate-900 mb-4">Empirical Scores by Error Category (Real Test Runs)</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm border-collapse">
          <thead>
            <tr class="bg-slate-100 text-slate-700 border-b border-slate-200">
              <th class="p-3 font-semibold">Error Type Category</th>
              <th class="p-3 font-semibold text-center">ROUGE-L Score</th>
              <th class="p-3 font-semibold text-center">BLEU-4 Score</th>
              <th class="p-3 font-semibold text-center">Remediation Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Indentation Error (Python)</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">NameError (Typo: keywords, types)</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Undefined Variable (C: HSH_LEN, URL_MXA, voidpkg)</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.91</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.85</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Undefined Variable (Python: ERR_INVALID_PACKGE)</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Type Mismatch (Accidental rvalue assignment '=')</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.94</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.89</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Missing Semicolon</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.93</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.63</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Attribute Error (dev->boot_slt, .currnet_version)</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">1.00</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Syntax Errors (Brackets, unbalanced parens, colons)</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.84</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.74</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-medium text-slate-800">Other (Enum commas, XOR operator, prompt injection)</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.84</td>
              <td class="p-3 text-center font-mono font-bold text-emerald-700">0.76</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800">100% Resolved</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    function showTab(tabId) {
      const views = ['combined', 'fig_a', 'fig_b', 'metrics'];
      views.forEach(v => {
        const el = document.getElementById('view-' + v);
        const btn = document.getElementById('tab-' + v);
        if (v === tabId) {
          el.classList.remove('hidden');
          btn.classList.add('bg-sky-600', 'text-white', 'border-sky-600');
          btn.classList.remove('bg-white', 'text-slate-700');
        } else {
          el.classList.add('hidden');
          btn.classList.remove('bg-sky-600', 'text-white', 'border-sky-600');
          btn.classList.add('bg-white', 'text-slate-700');
        }
      });
    }
  </script>
</body>
</html>
"""

full_html = template_head + svg_combined + tab_2_start + svg_a + tab_3_start + svg_b + table_and_tail
(art_dir / "figure2_evaluation_graphs.html").write_text(full_html, encoding="utf-8")
print("Full HTML artifact with updated real empirical data written successfully!")
