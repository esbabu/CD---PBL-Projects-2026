# Compiler Error Explainer (VS Code Extension)

A same-day prototype VS Code extension that connects the C++ Compiler Error Explanation and Classification pipeline directly to VS Code's editor surface via diagnostics and hover cards.

---

## 1. Quick Start

### Prerequisites
- Node.js (>= 18) and npm
- Python 3.10+ with project virtualenv/dependencies installed
- C++ compiler (`g++` or `clang++` supporting C++17)
- VS Code 1.85.0+

### Running from Source in Extension Development Host
1. Clone or open the repository.
2. Navigate to the extension folder:
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   ```
3. Open the repository root in VS Code.
4. Press `F5` (or click **Run > Start Debugging**) to launch the **Extension Development Host** window.
5. In the new window, configure the backend path setting:
   - Open Settings (`Cmd+,` on macOS, `Ctrl+,` on Linux/Windows).
   - Search for `cee.backendPath`.
   - Set it to the absolute path of this project root:
     ```
     /Users/jaisinghsaini/TOACD/VS_Code_Extension/code_final
     ```
6. Open any C/C++ source file (e.g. `benchmark/multi_error/me06_cascade_semicolons.cpp`).
7. Save the file (`Cmd+S`) or run the command `Compiler Error Explainer: Analyze Current File` from the Command Palette (`Cmd+Shift+P`).
8. View diagnostics (red squiggles for errors, yellow for warnings) and hover over the affected tokens to see structured explanations.

---

## 2. Configuration Settings

| Setting | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `cee.backendPath` | `string` | `""` | Absolute path to backend project root containing `tools/vscode_bridge.py`. |
| `cee.pythonPath` | `string` | `"python3"` | Path or command to Python 3 interpreter. |
| `cee.runOnSave` | `boolean` | `true` | Automatically run compiler error analysis on save for C/C++ files. |
| `cee.timeoutMs` | `number` | `15000` | Process execution timeout in milliseconds (kills process tree if exceeded). |
| `cee.showWarnings` | `boolean` | `true` | Whether to display compiler warnings alongside errors. |

---

## 3. Extension Commands

- **`Compiler Error Explainer: Analyze Current File` (`cee.analyze`)**: Immediately compiles and analyzes the active C/C++ document.
- **`Compiler Error Explainer: Clear Diagnostics` (`cee.clear`)**: Clears all diagnostics and squiggles from the editor.
- **`Compiler Error Explainer: Show Output Channel` (`cee.showOutput`)**: Opens the "Compiler Error Explainer" output log window.

---

## 4. Manual Test Matrix

| Benchmark File | Category | Lines | Squiggle Count | Hover Text Verified | Run Time |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `benchmark/multi_error/me06_cascade_semicolons.cpp` | Cascade Semicolons | 12 | 2 errors | Yes (What / Why / How / Suggestion) | ~10.6s |
| `scratch/three_errors.cpp` | 3 Independent Errors | 9 | 3 errors | Yes (Type, Name Resolution, Syntax) | ~12.4s |
| `benchmark/warnings_only/wo05_implicit_conversion.cpp` | Warnings-Only | 9 | 1 warning | Yes (Literal conversion warning) | ~7.8s |
| `benchmark/clean/cl01_hello.cpp` | Clean File | 8 | 0 (Clean) | N/A (Status: `$(check) Explainer: clean`) | ~3.6s |
| `benchmark/linker_errors/lk01_undef_func.cpp` | Linker Error | 8 | 1 error | Yes (`[Linker Error]` anchored line 1) | ~7.8s |
| `enterprise_financial_system.cpp` | 700+ Line File | 1,209 | 4 errors, 14 warnings | Yes (Multi-line rich diagnostics) | ~18.2s |

---

## 5. Automated Unit Tests

Unit tests verify the pure JSON-to-Diagnostic transformation logic:
- `null` column handling: underlines the whole line, trimmed
- `null` line handling: anchors linker errors to line 1 with `[Linker Error]` prefix
- All three severities: Error, Warning, Information
- Malformed and non-JSON backend output handling
- Markdown and HTML escaping for hover security

Run tests:
```bash
npm test
```

---

## 6. LIMITATIONS

- **Requires Python + Backend Project**: The extension communicates via `tools/vscode_bridge.py` and requires Python 3 with the backend project environment present on the host machine.
- **macOS / Linux Only**: The sandboxing and process tree watchdog mechanisms in the backend rely on POSIX APIs and Apple Seatbelt / Linux namespaces.
- **Runs on Save, Not While Typing**: In order to avoid excessive compilation load and ML classifier re-triggering during rapid edits, analysis triggers on file save (debounced by 500 ms) or explicit manual command.
- **No Auto-Fix**: This prototype is strictly scoped to diagnostics presentation and hover explanations. Code auto-healing, patch reviews, and security tabs are excluded.
- **Prototype**: This is an evaluation prototype not intended for VS Code Marketplace distribution.
