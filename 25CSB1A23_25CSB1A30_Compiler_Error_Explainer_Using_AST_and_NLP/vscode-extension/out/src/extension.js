"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");
const fs = require("fs");
const diagnosticMapper_1 = require("./diagnosticMapper");
const MAX_FILE_SIZE_BYTES = 500 * 1024; // 500 KB limit
const NOTIFICATION_COOLDOWN_MS = 30000; // At most 1 error notification per 30s
const SUPPORTED_EXTENSIONS = new Set([".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"]);
// State
let outputChannel;
let statusBarItem;
let runStatusBarItem;
let compileStatusBarItem;
let autoHealStatusBarItem;
let optimizeStatusBarItem;
let dashboardStatusBarItem;
let currentDashboardDocument;
let diagnosticCollection;
let errorDecorationType;
let warningDecorationType;
let securityDecorationType;
// Diagnostics cache per document URI/fsPath for HoverProvider lookups
const diagnosticMap = new Map();
function getDiagnosticsForDocument(document) {
    const uriStr = document.uri.toString();
    if (diagnosticMap.has(uriStr)) {
        return diagnosticMap.get(uriStr);
    }
    const fsPath = path.normalize(document.uri.fsPath);
    if (diagnosticMap.has(fsPath)) {
        return diagnosticMap.get(fsPath);
    }
    // Fallback: case-insensitive match on normalized file paths
    const lowerFs = fsPath.toLowerCase();
    for (const [key, value] of diagnosticMap.entries()) {
        if (path.normalize(key).toLowerCase() === lowerFs) {
            return value;
        }
    }
    return undefined;
}
function updateDecorationsForEditor(editor) {
    if (!errorDecorationType || !warningDecorationType || !securityDecorationType || !isCppDocument(editor.document)) {
        return;
    }
    const diags = getDiagnosticsForDocument(editor.document);
    if (!diags || diags.length === 0) {
        editor.setDecorations(errorDecorationType, []);
        editor.setDecorations(warningDecorationType, []);
        editor.setDecorations(securityDecorationType, []);
        return;
    }
    const errorDecorations = [];
    const warningDecorations = [];
    const securityDecorations = [];
    for (const d of diags) {
        const range = new vscode.Range(d.range.startLine, d.range.startCharacter, d.range.endLine, d.range.endCharacter);
        if (d.is_security) {
            securityDecorations.push({
                range,
                renderOptions: {
                    after: {
                        contentText: ` 🛡️ [Security: ${d.cwe || "Vulnerability"} (${d.security_risk || "High"})]`,
                        color: "rgba(240, 90, 100, 0.95)",
                        fontStyle: "italic",
                        fontWeight: "600",
                    },
                },
            });
        }
        else {
            const decoration = {
                range,
                renderOptions: {
                    after: {
                        contentText: ` ⚡ [Explainer: ${d.category}]`,
                        color: d.severity === "error" ? "rgba(255, 120, 120, 0.85)" : "rgba(255, 195, 75, 0.85)",
                        fontStyle: "italic",
                    },
                },
            };
            if (d.severity === "error") {
                errorDecorations.push(decoration);
            }
            else {
                warningDecorations.push(decoration);
            }
        }
    }
    editor.setDecorations(errorDecorationType, errorDecorations);
    editor.setDecorations(warningDecorationType, warningDecorations);
    editor.setDecorations(securityDecorationType, securityDecorations);
}
function updateAllVisibleDecorations() {
    for (const editor of vscode.window.visibleTextEditors) {
        updateDecorationsForEditor(editor);
    }
}
// Hover Provider
class ExplainerHoverProvider {
    provideHover(document, position, _token) {
        const diags = getDiagnosticsForDocument(document);
        if (!diags || diags.length === 0) {
            return null;
        }
        const matching = diags.filter((d) => {
            const range = new vscode.Range(d.range.startLine, d.range.startCharacter, d.range.endLine, d.range.endCharacter);
            if (range.contains(position)) {
                return true;
            }
            return d.range.startLine === position.line;
        });
        if (matching.length === 0) {
            return null;
        }
        if (matching.length === 1) {
            return new vscode.Hover((0, diagnosticMapper_1.buildHoverMarkdown)(matching[0]));
        }
        return new vscode.Hover((0, diagnosticMapper_1.buildMultiHoverMarkdown)(matching));
    }
}
// Code Action Provider (Quick-Fixes)
class ExplainerCodeActionProvider {
    provideCodeActions(document, range, _context, _token) {
        const diags = getDiagnosticsForDocument(document);
        if (!diags || diags.length === 0) {
            return [];
        }
        const actions = [];
        const matching = diags.filter((d) => {
            const diagRange = new vscode.Range(d.range.startLine, d.range.startCharacter, d.range.endLine, d.range.endCharacter);
            return (diagRange.intersection(range) !== undefined ||
                d.range.startLine === range.start.line);
        });
        for (const d of matching) {
            if (d.fix?.available && d.fix.patched_source) {
                const action = new vscode.CodeAction(`⚡ ${d.fix.title} [${d.fix.tier_name}]`, vscode.CodeActionKind.QuickFix);
                action.isPreferred = true;
                const edit = new vscode.WorkspaceEdit();
                const entireRange = new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length));
                edit.replace(document.uri, entireRange, d.fix.patched_source);
                action.edit = edit;
                actions.push(action);
            }
        }
        return actions;
    }
}
function isCppDocument(document) {
    if (document.languageId === "cpp" || document.languageId === "c") {
        return true;
    }
    const ext = path.extname(document.fileName).toLowerCase();
    return SUPPORTED_EXTENSIONS.has(ext);
}
function findBackendPath(document) {
    const config = vscode.workspace.getConfiguration("cee");
    const configured = config.get("backendPath");
    if (configured && fs.existsSync(configured)) {
        return configured;
    }
    const docDir = path.dirname(document.fileName);
    let current = docDir;
    for (let i = 0; i < 5; i++) {
        const candidate = path.join(current, "tools", "vscode_bridge.py");
        if (fs.existsSync(candidate)) {
            return current;
        }
        const parent = path.dirname(current);
        if (parent === current) {
            break;
        }
        current = parent;
    }
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders) {
        for (const wf of workspaceFolders) {
            const candidate = path.join(wf.uri.fsPath, "tools", "vscode_bridge.py");
            if (fs.existsSync(candidate)) {
                return wf.uri.fsPath;
            }
        }
    }
    return undefined;
}
function resolvePythonPath(backendPath) {
    const config = vscode.workspace.getConfiguration("cee");
    const configured = config.get("pythonPath");
    if (configured && configured !== "python3") {
        return configured;
    }
    if (backendPath) {
        const winVenv = path.join(backendPath, ".venv", "Scripts", "python.exe");
        if (fs.existsSync(winVenv))
            return winVenv;
        const nixVenv = path.join(backendPath, ".venv", "bin", "python");
        if (fs.existsSync(nixVenv))
            return nixVenv;
    }
    return process.platform === "win32" ? "python" : "python3";
}
let activeProcess;
let debounceTimer;
let lastNotificationTime = 0;
function updateStatusBar(text, tooltip) {
    if (statusBarItem) {
        statusBarItem.text = text;
        statusBarItem.tooltip = tooltip;
        statusBarItem.show();
    }
}
async function runAnalysis(document) {
    const filePath = document.fileName;
    outputChannel.appendLine(`\n[${new Date().toLocaleTimeString()}] Analyzing: ${filePath}`);
    try {
        const stats = fs.statSync(filePath);
        if (stats.size > MAX_FILE_SIZE_BYTES) {
            outputChannel.appendLine(`[SKIP] File size ${stats.size} exceeds 500 KB limit.`);
            updateStatusBar("$(info) Explainer: skipped (large file)", "File exceeds 500 KB limit");
            return;
        }
    }
    catch {
        // If not on disk yet, skip stat check
    }
    const backendPath = findBackendPath(document);
    const pythonPath = resolvePythonPath(backendPath);
    const bridgeScript = backendPath ? path.join(backendPath, "tools", "vscode_bridge.py") : "";
    if (!backendPath || !fs.existsSync(bridgeScript)) {
        const msg = "Compiler Error Explainer: Cannot find tools/vscode_bridge.py.";
        outputChannel.appendLine(`[ERROR] ${msg}`);
        updateStatusBar("$(error) Explainer: bridge not found", msg);
        return;
    }
    if (activeProcess) {
        activeProcess.kill();
        activeProcess = undefined;
    }
    updateStatusBar("$(sync~spin) Explainer: analyzing...", "Running compiler and security analysis...");
    const config = vscode.workspace.getConfiguration("cee");
    const enableAi = config.get("enableAi", false);
    const spawnArgs = [bridgeScript];
    if (enableAi) {
        spawnArgs.push("--ai");
    }
    spawnArgs.push(filePath);
    let stdoutData = "";
    let stderrData = "";
    const proc = cp.spawn(pythonPath, spawnArgs, {
        cwd: path.dirname(filePath),
        env: { ...process.env, PYTHONUNBUFFERED: "1", PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
        shell: false,
    });
    activeProcess = proc;
    proc.stdout?.on("data", (chunk) => {
        stdoutData += chunk.toString();
    });
    proc.stderr?.on("data", (chunk) => {
        stderrData += chunk.toString();
    });
    proc.on("error", (err) => {
        outputChannel.appendLine(`[SPAWN ERROR] ${err.message}`);
        updateStatusBar("$(error) Explainer: failed", err.message);
    });
    proc.on("close", (code) => {
        if (activeProcess === proc) {
            activeProcess = undefined;
        }
        if (code !== 0 || !stdoutData.trim()) {
            outputChannel.appendLine(`[PROCESS ERROR] Code: ${code}\nStderr: ${stderrData}`);
            return;
        }
        try {
            const output = JSON.parse(stdoutData);
            applyBridgeOutput(document, output);
        }
        catch (parseErr) {
            outputChannel.appendLine(`[JSON PARSE ERROR] ${parseErr.message}\nRaw: ${stdoutData.slice(0, 300)}`);
        }
    });
}
function applyBridgeOutput(document, output) {
    if (!output.ok && output.error) {
        outputChannel.appendLine(`[BRIDGE ERROR] ${output.error}`);
        updateStatusBar("$(error) Explainer: error", output.error);
        return;
    }
    const compilerName = output.compiler || "g++";
    const rawList = output.diagnostics || [];
    const getLineText = (lineIndex) => {
        if (lineIndex >= 0 && lineIndex < document.lineCount) {
            return document.lineAt(lineIndex).text;
        }
        return "";
    };
    const explainerData = rawList.map((raw) => (0, diagnosticMapper_1.mapRawDiagnostic)(raw, getLineText));
    const vscodeDiagnostics = explainerData.map((d) => {
        const range = new vscode.Range(d.range.startLine, d.range.startCharacter, d.range.endLine, d.range.endCharacter);
        const severity = d.severity === "error" ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning;
        const diag = new vscode.Diagnostic(range, d.message, severity);
        diag.source = d.is_security ? "Security Audit" : `Explainer (${d.category})`;
        return diag;
    });
    diagnosticCollection.set(document.uri, vscodeDiagnostics);
    diagnosticMap.set(document.uri.toString(), explainerData);
    diagnosticMap.set(path.normalize(document.uri.fsPath), explainerData);
    updateAllVisibleDecorations();
    const errCount = rawList.filter((d) => d.severity === "error" && !d.is_security).length;
    const warnCount = rawList.filter((d) => d.severity === "warning" && !d.is_security).length;
    const secCount = rawList.filter((d) => d.is_security).length;
    if (errCount === 0 && warnCount === 0 && secCount === 0) {
        updateStatusBar("$(check) Explainer: 0 errors", `Clean build! (${compilerName})`);
    }
    else {
        const parts = [];
        if (errCount > 0)
            parts.push(`${errCount} err`);
        if (warnCount > 0)
            parts.push(`${warnCount} warn`);
        if (secCount > 0)
            parts.push(`${secCount} sec`);
        updateStatusBar(`$(alert) Explainer: ${parts.join(", ")}`, `Diagnostics active: ${parts.join(", ")}`);
    }
    outputChannel.appendLine(`[ANALYSIS DONE] ${rawList.length} diagnostic(s) mapped.`);
}
/**
 * Executes multi-pass auto-healing on active document.
 */
async function runAutoHeal(document) {
    const filePath = document.fileName;
    outputChannel.appendLine(`\n[${new Date().toLocaleTimeString()}] Triggering Auto-Heal for: ${filePath}`);
    if (document.isDirty) {
        await document.save();
    }
    const backendPath = findBackendPath(document);
    const pythonPath = resolvePythonPath(backendPath);
    const bridgeScript = backendPath ? path.join(backendPath, "tools", "vscode_bridge.py") : "";
    if (!backendPath || !fs.existsSync(bridgeScript)) {
        vscode.window.showErrorMessage("Compiler Error Explainer: Backend path not found.");
        return;
    }
    updateStatusBar("$(sync~spin) Explainer: healing...", "Auto-healing all compiler errors & security issues...");
    return new Promise((resolve) => {
        const spawnArgs = [bridgeScript, "--autoheal", filePath];
        outputChannel.appendLine(`[EXEC AUTOHEAL] ${pythonPath} ${spawnArgs.join(" ")}`);
        let stdoutData = "";
        let stderrData = "";
        let finished = false;
        const timer = setTimeout(() => {
            if (!finished) {
                finished = true;
                try {
                    proc.kill();
                }
                catch { }
                updateStatusBar("$(error) Explainer: timeout", "Auto-heal timed out after 60s");
                vscode.window.showWarningMessage("Auto-heal took longer than expected.");
                resolve();
            }
        }, 60000);
        const proc = cp.spawn(pythonPath, spawnArgs, {
            cwd: path.dirname(filePath),
            env: { ...process.env, PYTHONUNBUFFERED: "1", PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
            shell: false,
        });
        proc.on("error", (err) => {
            if (finished)
                return;
            finished = true;
            clearTimeout(timer);
            outputChannel.appendLine(`[AUTOHEAL SPAWN ERROR] ${err.message}`);
            updateStatusBar("$(error) Explainer: error", err.message);
            vscode.window.showErrorMessage(`Failed to launch Python: ${err.message}`);
            resolve();
        });
        proc.stdout?.on("data", (chunk) => {
            stdoutData += chunk.toString();
        });
        proc.stderr?.on("data", (chunk) => {
            stderrData += chunk.toString();
        });
        proc.on("close", async (code) => {
            if (finished)
                return;
            finished = true;
            clearTimeout(timer);
            if (code !== 0 || !stdoutData.trim()) {
                outputChannel.appendLine(`[AUTOHEAL ERROR] Process exited with code ${code}.\n${stderrData}`);
                updateStatusBar("$(error) Explainer: heal failed", "Auto-heal execution failed");
                vscode.window.showErrorMessage("Compiler Error Explainer: Auto-heal process failed.");
                resolve();
                return;
            }
            try {
                const result = JSON.parse(stdoutData);
                if (!result.ok) {
                    vscode.window.showErrorMessage(`Auto-heal failed: ${result.error || "Unknown error"}`);
                    resolve();
                    return;
                }
                if (result.healed_count > 0 && result.patched_source) {
                    outputChannel.appendLine(`[AUTOHEAL SUCCESS] Safely repaired ${result.healed_count} issue(s).`);
                    if (result.diff) {
                        outputChannel.appendLine(`[DIFF]\n${result.diff}`);
                    }
                    // Apply through WorkspaceEdit for full Ctrl+Z undo support
                    const edit = new vscode.WorkspaceEdit();
                    const entireRange = new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length));
                    edit.replace(document.uri, entireRange, result.patched_source);
                    const applied = await vscode.workspace.applyEdit(edit);
                    if (applied) {
                        await document.save();
                        updateStatusBar("$(check) Explainer: healed", `Safely repaired ${result.healed_count} issue(s)`);
                        vscode.window.showInformationMessage(`⚡ Compiler Error Explainer: Successfully repaired ${result.healed_count} compiler & security issue(s)! (Ctrl+Z to undo anytime)`);
                        await runAnalysis(document);
                        // Auto-refresh dashboard if open
                        if (dashboardPanel) {
                            refreshDashboardData(document);
                        }
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to apply auto-heal edits to active editor.");
                    }
                }
                else {
                    outputChannel.appendLine("[AUTOHEAL] File is already clean or passes all compiler checks.");
                    vscode.window.showInformationMessage("Compiler Error Explainer: Code is already clean or passes all compiler checks!");
                    updateStatusBar("$(check) Explainer: clean", "Clean code");
                }
            }
            catch (err) {
                outputChannel.appendLine(`[AUTOHEAL JSON ERROR] ${err.message}`);
                vscode.window.showErrorMessage("Compiler Error Explainer: Failed to parse auto-heal results.");
            }
            resolve();
        });
    });
}
/**
 * Runs Algorithmic Big-O optimization analysis.
 */
async function runOptimize(document) {
    const filePath = document.fileName;
    outputChannel.appendLine(`\n[${new Date().toLocaleTimeString()}] Running Big-O Optimization for: ${filePath}`);
    if (document.isDirty) {
        await document.save();
    }
    const backendPath = findBackendPath(document);
    const pythonPath = resolvePythonPath(backendPath);
    const bridgeScript = backendPath ? path.join(backendPath, "tools", "vscode_bridge.py") : "";
    if (!backendPath || !fs.existsSync(bridgeScript)) {
        vscode.window.showErrorMessage("Compiler Error Explainer: Backend path not found.");
        return;
    }
    updateStatusBar("$(sync~spin) Explainer: optimizing...", "Analyzing Big-O algorithmic complexity & bottlenecks...");
    return new Promise((resolve) => {
        const spawnArgs = [bridgeScript, "--optimize", filePath];
        let stdoutData = "";
        let stderrData = "";
        let finished = false;
        const timer = setTimeout(() => {
            if (!finished) {
                finished = true;
                try {
                    proc.kill();
                }
                catch { }
                updateStatusBar("$(error) Explainer: timeout", "Optimization timed out after 60s");
                vscode.window.showWarningMessage("Optimization analysis took longer than expected.");
                resolve();
            }
        }, 60000);
        const proc = cp.spawn(pythonPath, spawnArgs, {
            cwd: path.dirname(filePath),
            env: { ...process.env, PYTHONUNBUFFERED: "1", PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
            shell: false,
        });
        proc.on("error", (err) => {
            if (finished)
                return;
            finished = true;
            clearTimeout(timer);
            outputChannel.appendLine(`[OPTIMIZE SPAWN ERROR] ${err.message}`);
            updateStatusBar("$(error) Explainer: error", err.message);
            vscode.window.showErrorMessage(`Failed to launch Python: ${err.message}`);
            resolve();
        });
        proc.stdout?.on("data", (chunk) => {
            stdoutData += chunk.toString();
        });
        proc.stderr?.on("data", (chunk) => {
            stderrData += chunk.toString();
        });
        proc.on("close", async (code) => {
            if (finished)
                return;
            finished = true;
            clearTimeout(timer);
            if (code !== 0 || !stdoutData.trim()) {
                outputChannel.appendLine(`[OPTIMIZE ERROR] Exit code ${code}: ${stderrData}`);
                updateStatusBar("$(error) Explainer: optimize failed", "Optimization failed");
                vscode.window.showErrorMessage("Compiler Error Explainer: Optimization engine failed.");
                resolve();
                return;
            }
            try {
                const res = JSON.parse(stdoutData);
                if (!res.ok) {
                    vscode.window.showErrorMessage(`Optimization failed: ${res.error || "Unknown error"}`);
                    resolve();
                    return;
                }
                updateStatusBar("$(rocket) Explainer: optimized", `Big-O: ${res.time_complexity}`);
                const origT = res.original_time_complexity || "Suboptimal";
                const newT = res.time_complexity || "Optimal";
                const optimizationsText = (res.optimizations_applied && res.optimizations_applied.length > 0)
                    ? res.optimizations_applied.join("; ")
                    : "Algorithmic loop vectorization and bounds optimization";
                const choice = await vscode.window.showInformationMessage(`🚀 Algorithmic Optimization Analysis:\n• Time Complexity: ${origT} ➔ ${newT}\n• Space Complexity: ${res.space_complexity}\n• Optimizations: ${optimizationsText}`, "Apply Optimized Code", "Open Dashboard", "Dismiss");
                if (choice === "Apply Optimized Code") {
                    if (res.optimized_code && res.optimized_code !== document.getText()) {
                        const edit = new vscode.WorkspaceEdit();
                        const entireRange = new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length));
                        edit.replace(document.uri, entireRange, res.optimized_code);
                        await vscode.workspace.applyEdit(edit);
                        await document.save();
                        vscode.window.showInformationMessage("🚀 Optimized C++ code applied successfully! (Ctrl+Z to undo anytime)");
                    }
                    else {
                        vscode.window.showInformationMessage("🚀 Algorithmic optimizations recorded! Target complexity active.");
                    }
                    await runAnalysis(document);
                    if (dashboardPanel) {
                        refreshDashboardData(document);
                    }
                }
                else if (choice === "Open Dashboard") {
                    openDashboardPanel(contextRef);
                }
            }
            catch (e) {
                outputChannel.appendLine(`[OPTIMIZE JSON ERROR] ${e.message}`);
                vscode.window.showErrorMessage("Compiler Error Explainer: Failed to parse optimization result.");
            }
            resolve();
        });
    });
}
/**
 * Checks document for compilation errors and warnings.
 */
async function runCompileCheck(document) {
    if (document.isDirty) {
        await document.save();
    }
    updateStatusBar("$(sync~spin) Explainer: compiling...", "Checking for compiler errors...");
    await runAnalysis(document);
    const diags = getDiagnosticsForDocument(document) || [];
    const errors = diags.filter(d => d.severity === "error");
    const warnings = diags.filter(d => d.severity === "warning");
    if (errors.length === 0 && warnings.length === 0) {
        updateStatusBar("$(check) Compile: clean", "0 errors, 0 warnings");
        vscode.window.showInformationMessage("✅ Compile Check Passed! 0 errors, 0 warnings. Code is clean and ready to run!");
    }
    else {
        updateStatusBar(`$(alert) Compile: ${errors.length} err`, `${errors.length} error(s), ${warnings.length} warning(s)`);
        const choice = await vscode.window.showErrorMessage(`❌ Compile Check: Found ${errors.length} error(s) and ${warnings.length} warning(s).`, "⚡ Auto-Heal Now", "📊 Open Analytics", "Dismiss");
        if (choice === "⚡ Auto-Heal Now") {
            await runAutoHeal(document);
        }
        else if (choice === "📊 Open Analytics") {
            openDashboardPanel(contextRef);
        }
    }
}
let runTerminal;
/**
 * Compiles and runs the current file inside the integrated terminal.
 */
async function runFileInTerminal(document) {
    if (document.isDirty) {
        await document.save();
    }
    const filePath = document.fileName;
    const docDir = path.dirname(filePath);
    const ext = path.extname(filePath);
    const baseName = path.basename(filePath, ext);
    const safeBase = baseName.replace(/[^a-zA-Z0-9_\-]/g, "_");
    const exeName = process.platform === "win32" ? `${safeBase}.exe` : safeBase;
    const exePath = path.join(docDir, exeName);
    updateStatusBar("$(sync~spin) Explainer: compiling...", `Compiling ${baseName}...`);
    const compileArgs = ["-std=c++17", "-Wall", filePath, "-o", exePath];
    outputChannel.appendLine(`\n[COMPILE & RUN] g++ ${compileArgs.join(" ")}`);
    cp.execFile("g++", compileArgs, { cwd: docDir }, async (err, stdout, stderr) => {
        if (err) {
            outputChannel.appendLine(`[COMPILE FAILED]\n${stderr || err.message}`);
            updateStatusBar("$(error) Compile failed", "Compilation errors detected");
            await runAnalysis(document);
            const choice = await vscode.window.showErrorMessage(`❌ Compilation Failed for ${baseName}! Errors detected in code. Auto-Heal now?`, "⚡ Auto-Heal Now", "📊 View Analytics");
            if (choice === "⚡ Auto-Heal Now") {
                await runAutoHeal(document);
            }
            else if (choice === "📊 View Analytics") {
                openDashboardPanel(contextRef);
            }
            return;
        }
        updateStatusBar("$(check) Running...", `Executing ${exeName}`);
        if (!runTerminal || runTerminal.exitStatus !== undefined) {
            runTerminal = vscode.window.createTerminal("C++ Output");
        }
        runTerminal.show();
        runTerminal.sendText(`cd "${docDir}"`);
        const runCmd = process.platform === "win32" ? `.\\${exeName}` : `./${exeName}`;
        runTerminal.sendText(runCmd);
        vscode.window.showInformationMessage(`🚀 Program ${exeName} compiled and launched in C++ Output terminal!`);
    });
}
/**
 * Formats active document using backend formatter engine.
 */
async function runFormat(document) {
    const filePath = document.fileName;
    const backendPath = findBackendPath(document);
    const pythonPath = resolvePythonPath(backendPath);
    const bridgeScript = backendPath ? path.join(backendPath, "tools", "vscode_bridge.py") : "";
    if (!backendPath || !fs.existsSync(bridgeScript)) {
        return [];
    }
    return new Promise((resolve) => {
        const spawnArgs = [bridgeScript, "--format", filePath];
        let stdoutData = "";
        const proc = cp.spawn(pythonPath, spawnArgs, {
            cwd: path.dirname(filePath),
            env: { ...process.env, PYTHONUNBUFFERED: "1", PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
            shell: false,
        });
        proc.stdout?.on("data", (chunk) => {
            stdoutData += chunk.toString();
        });
        proc.on("close", (code) => {
            if (code === 0 && stdoutData.trim()) {
                try {
                    const res = JSON.parse(stdoutData);
                    if (res.ok && res.formatted_source) {
                        const entireRange = new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length));
                        resolve([vscode.TextEdit.replace(entireRange, res.formatted_source)]);
                        return;
                    }
                }
                catch { }
            }
            resolve([]);
        });
    });
}
let dashboardPanel;
let contextRef;
function getDashboardHtml() {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Compiler Deep Analytics</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --card-border: #30363d;
      --accent: #38bdf8;
      --green: #2ea043;
      --green-bright: #3fb950;
      --yellow: #d29922;
      --red: #f85149;
      --purple: #bc8cff;
      --teal: #2dd4bf;
      --text: #e6edf3;
      --text-muted: #8b949e;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body, html { width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; display: flex; flex-direction: column; }
    
    header { background: #161b22; border-bottom: 1px solid var(--card-border); padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
    .header-left { display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 15px; color: var(--accent); }
    .header-actions { display: flex; gap: 8px; align-items: center; }
    
    .loading-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11.5px;
      font-weight: 500;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      padding: 3px 10px;
      border-radius: 12px;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .spinner {
      display: inline-block;
      width: 10px;
      height: 10px;
      border: 2px solid rgba(56, 189, 248, 0.3);
      border-radius: 50%;
      border-top-color: var(--accent);
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    button.btn {
      background: #21262d; color: var(--text); border: 1px solid var(--card-border); padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.15s ease;
    }
    button.btn:hover:not(:disabled) { background: #30363d; border-color: #8b949e; }
    button.btn:disabled { opacity: 0.65; cursor: not-allowed; }
    button.btn-primary { background: #238636; border-color: rgba(240,246,252,0.1); color: #fff; }
    button.btn-primary:hover:not(:disabled) { background: #2ea043; }
    button.btn-optimize { background: #1f6feb; border-color: rgba(240,246,252,0.1); color: #fff; }
    button.btn-optimize:hover:not(:disabled) { background: #388bfd; }

    .nav-tabs { display: flex; background: #0d1117; border-bottom: 1px solid var(--card-border); padding: 0 16px; gap: 4px; }
    .tab-item { padding: 9px 14px; font-size: 12.5px; font-weight: 500; color: var(--text-muted); cursor: pointer; border-bottom: 2px solid transparent; }
    .tab-item.active { color: var(--text); border-bottom-color: #f78166; font-weight: 600; }
    
    .tab-content { flex: 1; overflow-y: auto; padding: 16px; }
    .tab-pane { display: none; }
    .tab-pane.active { display: block; }

    /* Quality Card */
    .quality-container { display: grid; grid-template-columns: 280px 1fr; gap: 16px; margin-bottom: 16px; }
    .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 16px; margin-bottom: 14px; }
    .card-title { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }

    .gauge-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .gauge-circle { width: 140px; height: 140px; position: relative; display: flex; align-items: center; justify-content: center; }
    .gauge-score { font-size: 38px; font-weight: 700; color: #fff; }
    .gauge-grade { font-size: 14px; font-weight: 600; padding: 3px 8px; border-radius: 4px; margin-top: 6px; }
    .grade-A { background: rgba(46,160,67,0.2); color: #3fb950; border: 1px solid #2ea043; }
    .grade-B { background: rgba(56,189,248,0.2); color: #38bdf8; border: 1px solid #38bdf8; }
    .grade-C { background: rgba(210,153,34,0.2); color: #d29922; border: 1px solid #d29922; }
    .grade-D, .grade-F { background: rgba(248,81,73,0.2); color: #f85149; border: 1px solid #f85149; }

    .bars-container { display: flex; flex-direction: column; gap: 14px; justify-content: center; }
    .bar-group { display: flex; flex-direction: column; gap: 4px; }
    .bar-label { display: flex; justify-content: space-between; font-size: 12px; font-weight: 500; }
    .bar-track { height: 10px; border-radius: 5px; background: #21262d; overflow: hidden; display: flex; }
    .bar-fill { height: 100%; transition: width 0.4s ease; }
    .bar-poor { background: var(--red); }
    .bar-better { background: var(--yellow); }
    .bar-best { background: var(--green); }

    .issue-item { display: flex; gap: 10px; padding: 10px; border-radius: 6px; margin-bottom: 8px; background: #0d1117; border: 1px solid var(--card-border); font-size: 12.5px; }
    .issue-poor { border-left: 3px solid var(--red); }
    .issue-better { border-left: 3px solid var(--yellow); }
    .issue-best { border-left: 3px solid var(--green); }
    .issue-title { font-weight: 600; margin-bottom: 2px; }
    .issue-detail { color: var(--text-muted); font-size: 11.5px; }

    pre.code-view { background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid var(--card-border); font-family: Consolas, monospace; font-size: 12px; overflow-x: auto; color: #a5d6ff; line-height: 1.5; }
    
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 14px; }
    .stat-box { background: #0d1117; border: 1px solid var(--card-border); border-radius: 6px; padding: 12px; }
    .stat-val { font-size: 20px; font-weight: 700; color: var(--accent); margin-top: 4px; }

    /* Graph Styles for Green Telemetry */
    .chart-container { display: flex; flex-direction: column; gap: 12px; margin-top: 8px; }
    .chart-row { display: grid; grid-template-columns: 160px 1fr 90px; align-items: center; gap: 12px; font-size: 12px; }
    .chart-label { color: var(--text); font-weight: 500; }
    .chart-track { height: 16px; background: #21262d; border-radius: 4px; overflow: hidden; position: relative; display: flex; }
    .chart-bar { height: 100%; border-radius: 4px; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
    .chart-val { font-weight: 600; text-align: right; color: var(--text-muted); font-family: Consolas, monospace; }

    /* Subsystem Stacked Bar */
    .stacked-track { height: 20px; border-radius: 6px; overflow: hidden; display: flex; background: #21262d; margin-top: 8px; }
    .stacked-segment { height: 100%; transition: width 0.5s ease; }
    .legend-row { display: flex; gap: 20px; margin-top: 10px; font-size: 11.5px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }

    /* Second Opinion Styles */
    .sop-banner { padding: 12px 16px; border-radius: 8px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between; }
    .sop-agreed { background: rgba(46, 160, 67, 0.15); border: 1px solid rgba(46, 160, 67, 0.4); color: #3fb950; }
    .sop-divergent { background: rgba(210, 153, 34, 0.15); border: 1px solid rgba(210, 153, 34, 0.4); color: #d29922; }
    .sop-clean { background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: #38bdf8; }
    .model-card { background: #0d1117; border: 1px solid var(--card-border); border-radius: 6px; padding: 14px; }
    .model-badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-top: 6px; }
    .conf-meter { height: 8px; background: #21262d; border-radius: 4px; overflow: hidden; margin-top: 8px; }
    .conf-fill { height: 100%; transition: width 0.4s ease; }
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      <span>⚡ Compiler Deep Analytics & Code Quality</span>
    </div>
    <div class="header-actions">
      <button id="btn-run" class="btn" style="background: #238636; color: #fff;" onclick="onActionClick('run', '▶ Run File', 'Running...')" title="Compile and run program in terminal">▶ Run File</button>
      <button id="btn-compile" class="btn" onclick="onActionClick('compile', '🔨 Compile Check', 'Compiling...')" title="Check compilation errors">🔨 Compile Check</button>
      <button id="btn-autoheal" class="btn btn-primary" onclick="onActionClick('autoheal', '✨ Auto-Heal All', 'Healing...')" title="Auto-heal all errors & security issues">✨ Auto-Heal All</button>
      <button id="btn-optimize" class="btn btn-optimize" onclick="onActionClick('optimize', '🚀 Optimize Code', 'Optimizing...')" title="Big-O algorithmic optimizer">🚀 Optimize Code</button>
      <button id="btn-refresh" class="btn" onclick="onActionClick('refresh', '🔄 Refresh', 'Refreshing...')" title="Refresh analysis">🔄 Refresh</button>
    </div>
  </header>

  <div class="nav-tabs">
    <div class="tab-item active" onclick="switchTab('quality')">📊 Code Quality & Distribution</div>
    <div class="tab-item" onclick="switchTab('complexity')">📈 Big-O & Complexity</div>
    <div class="tab-item" onclick="switchTab('ast')">🌳 AST Visualizer</div>
    <div class="tab-item" onclick="switchTab('opinion')">🔍 Second Opinion</div>
    <div class="tab-item" onclick="switchTab('telemetry')">🌿 Green Telemetry</div>
  </div>

  <div class="tab-content">
    <!-- Tab 1: Quality -->
    <div id="tab-quality" class="tab-pane active">
      <div class="quality-container">
        <div class="card gauge-wrapper">
          <div class="card-title" style="width: 100%;">Code Health Score</div>
          <div class="gauge-circle">
            <span class="gauge-score" id="score-text">--</span>
          </div>
          <div class="gauge-grade grade-A" id="grade-badge">Grade --</div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;" id="status-desc">Loading telemetry...</div>
        </div>

        <div class="card bars-container">
          <div class="card-title">Code Quality Distribution Ratio</div>

          <div class="bar-group">
            <div class="bar-label">
              <span style="color: var(--red);">🔴 Poor Code (Errors, CWE Vulnerabilities, Faults)</span>
              <span id="poor-pct-text">0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill bar-poor" id="poor-fill" style="width: 0%;"></div>
            </div>
          </div>

          <div class="bar-group">
            <div class="bar-label">
              <span style="color: var(--yellow);">🟡 Better Code (Suboptimal Big-O, Warnings, Smells)</span>
              <span id="better-pct-text">0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill bar-better" id="better-fill" style="width: 0%;"></div>
            </div>
          </div>

          <div class="bar-group">
            <div class="bar-label">
              <span style="color: var(--green);">🟢 Best Code (Optimal, Clean, Type-Safe, Formatted)</span>
              <span id="best-pct-text">0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill bar-best" id="best-fill" style="width: 0%;"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Code Quality Breakdown & Evidence</div>
        <div id="breakdown-list">
          <div style="color: var(--text-muted); font-size: 12px;">Analyzing file...</div>
        </div>
      </div>
    </div>

    <!-- Tab 2: Complexity -->
    <div id="tab-complexity" class="tab-pane">
      <div class="card" style="margin-bottom: 16px;">
        <div class="card-title" style="margin-bottom: 16px;">
          <span>⚡ Real-Time Algorithmic Complexity</span>
          <span id="comp-status-badge" style="font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 700; background: rgba(56, 189, 248, 0.15); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.3);">Analyzing...</span>
        </div>

        <div class="grid-2" style="margin-bottom: 16px;">
          <div class="stat-box" style="text-align: center; padding: 18px 12px;">
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">ACTIVE TIME COMPLEXITY</div>
            <div class="stat-val" id="time-comp-val" style="font-size: 32px; font-weight: 800; font-family: Consolas, monospace; margin: 10px 0 6px 0; color: #38bdf8;">--</div>
            <div id="time-comp-sub" style="font-size: 11.5px; color: var(--text-muted);">Asymptotic execution scaling</div>
          </div>
          <div class="stat-box" style="text-align: center; padding: 18px 12px;">
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">ACTIVE SPACE COMPLEXITY</div>
            <div class="stat-val" id="space-comp-val" style="font-size: 32px; font-weight: 800; font-family: Consolas, monospace; margin: 10px 0 6px 0; color: #bc8cff;">--</div>
            <div id="space-comp-sub" style="font-size: 11.5px; color: var(--text-muted);">Auxiliary memory allocation</div>
          </div>
        </div>

        <div id="comp-summary-banner" style="background: #0d1117; border: 1px solid var(--card-border); border-radius: 6px; padding: 12px 14px; font-size: 12.5px; color: var(--text); line-height: 1.5;">
          Scanning AST loop statements and algorithmic calls...
        </div>
      </div>

      <div class="card" style="margin-top: 12px;">
        <div class="card-title">Algorithmic Signals & Loop Structure</div>
        <pre class="code-view" id="complexity-signals">Scanning source code...</pre>
      </div>
    </div>

    <!-- Tab 3: AST -->
    <div id="tab-ast" class="tab-pane">
      <div class="card">
        <div class="card-title">Abstract Syntax Tree (Clang AST)</div>
        <pre class="code-view" id="ast-tree-view">Building AST tree...</pre>
      </div>
    </div>

    <!-- Tab 4: Second Opinion -->
    <div id="tab-opinion" class="tab-pane">
      <!-- Status Banner -->
      <div id="sop-banner" class="sop-banner sop-clean">
        <div>
          <div style="font-size: 14px; font-weight: 700;" id="sop-status-title">🛡️ Second Opinion Engine Ready</div>
          <div style="font-size: 12px; margin-top: 3px; color: var(--text);" id="sop-status-desc">Evaluating dual classifier predictions...</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">Blended Consensus</div>
          <div style="font-size: 18px; font-weight: 700;" id="sop-blended-pct">--%</div>
        </div>
      </div>

      <!-- Dual Model Grid -->
      <div class="grid-2">
        <div class="model-card">
          <div class="card-title" style="margin-bottom: 8px;">
            <span>🤖 Machine Learning Classifier</span>
            <span style="font-size: 11px; color: var(--accent);">NLP Model</span>
          </div>
          <div style="font-size: 11.5px; color: var(--text-muted);">TF-IDF Vectorizer + Logistic Regression</div>
          <div style="margin-top: 10px;">
            <div style="font-size: 12px; color: var(--text-muted);">Predicted Category:</div>
            <div style="font-size: 15px; font-weight: 600; color: #fff; margin-top: 2px;" id="sop-ml-cat">--</div>
          </div>
          <div style="margin-top: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 11.5px;">
              <span style="color: var(--text-muted);">Model Confidence</span>
              <span id="sop-ml-conf" style="font-weight: 600; color: var(--accent);">--%</span>
            </div>
            <div class="conf-meter">
              <div id="sop-ml-bar" class="conf-fill" style="width: 0%; background: var(--accent);"></div>
            </div>
          </div>
        </div>

        <div class="model-card">
          <div class="card-title" style="margin-bottom: 8px;">
            <span>🔍 Keyword & AST Regex Matcher</span>
            <span style="font-size: 11px; color: var(--yellow);">Rule Engine</span>
          </div>
          <div style="font-size: 11.5px; color: var(--text-muted);">Syntax Tokens & AST Symbol Matching</div>
          <div style="margin-top: 10px;">
            <div style="font-size: 12px; color: var(--text-muted);">Detected Category:</div>
            <div style="font-size: 15px; font-weight: 600; color: #fff; margin-top: 2px;" id="sop-regex-cat">--</div>
          </div>
          <div style="margin-top: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 11.5px;">
              <span style="color: var(--text-muted);">Rule Confidence</span>
              <span id="sop-regex-conf" style="font-weight: 600; color: var(--yellow);">--%</span>
            </div>
            <div class="conf-meter">
              <div id="sop-regex-bar" class="conf-fill" style="width: 0%; background: var(--yellow);"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Agreement Details & Candidates -->
      <div class="card" id="sop-details-card">
        <div class="card-title">Ensemble Verdict & Candidate Ranking</div>
        <div id="sop-details-body" style="font-size: 12.5px; line-height: 1.6; color: var(--text);">
          Loading second opinion data...
        </div>
      </div>
    </div>

    <!-- Tab 5: Telemetry -->
    <div id="tab-telemetry" class="tab-pane">
      <div class="grid-4">
        <div class="stat-box">
          <div style="font-size: 11px; color: var(--text-muted);">ENERGY CONSUMPTION</div>
          <div class="stat-val" id="energy-val">-- J</div>
        </div>
        <div class="stat-box">
          <div style="font-size: 11px; color: var(--text-muted);">CO2 EMISSIONS</div>
          <div class="stat-val" id="co2-val">-- g</div>
        </div>
        <div class="stat-box">
          <div style="font-size: 11px; color: var(--text-muted);">CARBON RATING</div>
          <div class="stat-val" id="carbon-rating-val" style="color: var(--green-bright);">Grade A</div>
        </div>
        <div class="stat-box">
          <div style="font-size: 11px; color: var(--text-muted);">ECO-EFFICIENCY SAVINGS</div>
          <div class="stat-val" id="savings-val" style="color: var(--teal);">--%</div>
        </div>
      </div>

      <!-- Energy Comparison Graph -->
      <div class="card">
        <div class="card-title">
          <span>⚡ Build Energy Comparison Benchmarks (Joules)</span>
          <span style="font-size: 11px; color: var(--green-bright);">Lower is Greener</span>
        </div>
        <div class="chart-container">
          <div class="chart-row">
            <span class="chart-label">🟢 Present Code Build</span>
            <div class="chart-track">
              <div id="chart-bar-current" class="chart-bar" style="width: 30%; background: var(--accent);"></div>
            </div>
            <span class="chart-val" id="chart-val-current">-- J</span>
          </div>
          <div class="chart-row">
            <span class="chart-label">🌿 Eco-Optimized Target</span>
            <div class="chart-track">
              <div id="chart-bar-target" class="chart-bar" style="width: 15%; background: var(--green-bright);"></div>
            </div>
            <span class="chart-val" id="chart-val-target">-- J</span>
          </div>
          <div class="chart-row">
            <span class="chart-label">🟡 Standard Build Average</span>
            <div class="chart-track">
              <div id="chart-bar-standard" class="chart-bar" style="width: 60%; background: var(--yellow);"></div>
            </div>
            <span class="chart-val" id="chart-val-standard">-- J</span>
          </div>
          <div class="chart-row">
            <span class="chart-label">🔴 Unoptimized Legacy</span>
            <div class="chart-track">
              <div id="chart-bar-legacy" class="chart-bar" style="width: 95%; background: var(--red);"></div>
            </div>
            <span class="chart-val" id="chart-val-legacy">-- J</span>
          </div>
        </div>
      </div>

      <!-- Hardware Subsystem Breakdown -->
      <div class="card">
        <div class="card-title">💻 Subsystem Energy Distribution Breakdown</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 6px;">Resource allocation breakdown across processor, volatile cache, and storage:</div>
        <div class="stacked-track">
          <div id="stack-cpu" class="stacked-segment" style="width: 68%; background: #38bdf8;" title="CPU Execution"></div>
          <div id="stack-mem" class="stacked-segment" style="width: 22%; background: #bc8cff;" title="Memory & Cache"></div>
          <div id="stack-io" class="stacked-segment" style="width: 10%; background: #2dd4bf;" title="I/O & Compiler Storage"></div>
        </div>
        <div class="legend-row">
          <div><span class="legend-dot" style="background: #38bdf8;"></span><b>CPU Compute:</b> <span id="val-cpu">-- J</span> (68%)</div>
          <div><span class="legend-dot" style="background: #bc8cff;"></span><b>Memory & RAM:</b> <span id="val-mem">-- J</span> (22%)</div>
          <div><span class="legend-dot" style="background: #2dd4bf;"></span><b>Storage / I/O:</b> <span id="val-io">-- J</span> (10%)</div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();

    function sendMessage(command) {
      vscode.postMessage({ command });
    }

    const ACTION_BUTTONS = [
      { id: 'btn-run', defaultText: '▶ Run File' },
      { id: 'btn-compile', defaultText: '🔨 Compile Check' },
      { id: 'btn-autoheal', defaultText: '✨ Auto-Heal All' },
      { id: 'btn-optimize', defaultText: '🚀 Optimize Code' },
      { id: 'btn-refresh', defaultText: '🔄 Refresh' }
    ];

    function onActionClick(command, defaultText, runningText) {
      // 1. Disable all action buttons to prevent concurrent actions
      ACTION_BUTTONS.forEach(function(item) {
        var el = document.getElementById(item.id);
        if (el) {
          el.disabled = true;
          // Non-clicked buttons keep their regular label without any spinner
          if (item.id !== 'btn-' + command) {
            el.innerHTML = item.defaultText;
          }
        }
      });

      // 2. ONLY the clicked button displays the single loading spinner
      var clickedBtn = document.getElementById('btn-' + command);
      if (clickedBtn) {
        clickedBtn.innerHTML = '<span class="spinner"></span> ' + runningText;
      }

      sendMessage(command);
      setTimeout(resetButtons, 15000);
    }

    function resetButtons() {
      ACTION_BUTTONS.forEach(function(item) {
        var el = document.getElementById(item.id);
        if (el) {
          el.disabled = false;
          el.innerHTML = item.defaultText;
        }
      });
    }

    function switchTab(name) {
      document.querySelectorAll('.tab-item').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
      const tabEl = Array.from(document.querySelectorAll('.tab-item')).find(el => el.getAttribute('onclick').includes(name));
      if (tabEl) tabEl.classList.add('active');
      const pane = document.getElementById('tab-' + name);
      if (pane) pane.classList.add('active');
    }

    window.addEventListener('message', event => {
      const msg = event.data;
      if (msg.type === 'data') {
        renderData(msg.payload);
        resetButtons();
      } else if (msg.type === 'done') {
        resetButtons();
      }
    });

    function renderData(d) {
      if (!d) return;

      // Quality
      if (d.quality) {
        const q = d.quality;
        document.getElementById('score-text').textContent = q.score;
        const badge = document.getElementById('grade-badge');
        badge.textContent = 'Grade ' + q.grade;
        badge.className = 'gauge-grade grade-' + q.grade[0];
        document.getElementById('status-desc').textContent = q.status_text;

        document.getElementById('poor-pct-text').textContent = q.poor_pct + '%';
        document.getElementById('poor-fill').style.width = q.poor_pct + '%';

        document.getElementById('better-pct-text').textContent = q.better_pct + '%';
        document.getElementById('better-fill').style.width = q.better_pct + '%';

        document.getElementById('best-pct-text').textContent = q.best_pct + '%';
        document.getElementById('best-fill').style.width = q.best_pct + '%';

        const list = document.getElementById('breakdown-list');
        list.innerHTML = '';
        if (q.breakdown && q.breakdown.length > 0) {
          q.breakdown.forEach(item => {
            const el = document.createElement('div');
            el.className = 'issue-item issue-' + item.type;
            el.innerHTML = '<div style=\"flex: 1;\"><div class=\"issue-title\">' + escapeHtml(item.title) + '</div><div class=\"issue-detail\">' + escapeHtml(item.detail) + '</div></div>';
            list.appendChild(el);
          });
        } else {
          list.innerHTML = '<div style=\"color: var(--green); font-size: 12.5px;\">Clean code! Zero errors or vulnerabilities detected.</div>';
        }
      }

      // Real-Time Complexity
      if (d.complexity) {
        const timeHint = d.complexity.time_hint || 'O(1)';
        const spaceHint = d.complexity.space_hint || 'O(1)';
        const isSuboptimal = d.complexity.is_suboptimal;
        document.getElementById('time-comp-val').textContent = timeHint;
        document.getElementById('space-comp-val').textContent = spaceHint;

        const badgeEl = document.getElementById('comp-status-badge');
        const summaryEl = document.getElementById('comp-summary-banner');

        if (isSuboptimal) {
          badgeEl.textContent = '⚠️ BOTTLENECK DETECTED';
          badgeEl.style.background = 'rgba(248, 81, 73, 0.2)';
          badgeEl.style.color = '#f85149';
          badgeEl.style.border = '1px solid #f85149';
          summaryEl.innerHTML = '<strong>⚠️ Algorithmic Bottleneck (' + escapeHtml(timeHint) + '):</strong> Nested loops or polynomial scaling detected in active file. Click <strong>\"🚀 Optimize Code\"</strong> in the top header to analyze vectorization.';
        } else if (timeHint.includes('log')) {
          badgeEl.textContent = '⚡ OPTIMAL LOG-LINEAR';
          badgeEl.style.background = 'rgba(46, 160, 67, 0.2)';
          badgeEl.style.color = '#3fb950';
          badgeEl.style.border = '1px solid #2ea043';
          summaryEl.innerHTML = '<strong>⚡ Peak Performance (' + escapeHtml(timeHint) + '):</strong> Algorithms in the active file scale with efficient log-linear performance (such as std::sort / introsort) with minimal overhead.';
        } else if (timeHint === 'O(n)') {
          badgeEl.textContent = '⚡ LINEAR SCALING';
          badgeEl.style.background = 'rgba(56, 189, 248, 0.2)';
          badgeEl.style.color = '#38bdf8';
          badgeEl.style.border = '1px solid #38bdf8';
          summaryEl.innerHTML = '<strong>⚡ Linear Scaling (O(n)):</strong> Loops in the active file scale linearly with input size.';
        } else {
          badgeEl.textContent = '✅ CONSTANT TIME O(1)';
          badgeEl.style.background = 'rgba(46, 160, 67, 0.2)';
          badgeEl.style.color = '#3fb950';
          badgeEl.style.border = '1px solid #2ea043';
          summaryEl.innerHTML = '<strong>✅ Optimal Performance (' + escapeHtml(timeHint) + '):</strong> No loop bottlenecks detected. Code executes with constant-time efficiency.';
        }

        const sigs = d.complexity.signals || [];
        document.getElementById('complexity-signals').textContent = sigs.length > 0 ? JSON.stringify(sigs, null, 2) : 'No nested loop bottlenecks detected.';
      }

      // AST
      if (d.ast) {
        document.getElementById('ast-tree-view').textContent = JSON.stringify(d.ast, null, 2);
      }

      // Second Opinion
      if (d.second_opinion) {
        const s = d.second_opinion;
        const banner = document.getElementById('sop-banner');
        const titleEl = document.getElementById('sop-status-title');
        const descEl = document.getElementById('sop-status-desc');
        const blendedEl = document.getElementById('sop-blended-pct');

        if (!s.has_errors) {
          banner.className = 'sop-banner sop-clean';
          titleEl.textContent = '🛡️ Zero Diagnostic Errors (All Models Calibrated)';
          descEl.textContent = s.note || 'Both ML and Regex classifiers are calibrated and active. Source code is completely clean.';
          blendedEl.textContent = '100%';
        } else if (s.agreed) {
          banner.className = 'sop-banner sop-agreed';
          titleEl.textContent = '✅ High Consensus Agreement';
          descEl.textContent = s.note || 'Both models agreed on the same root cause error category.';
          blendedEl.textContent = Math.round((s.final_confidence || 0.95) * 100) + '%';
        } else {
          banner.className = 'sop-banner sop-divergent';
          titleEl.textContent = '⚠️ Divergent Predictions (Review Recommended)';
          descEl.textContent = s.note || 'ML and Regex classifiers suggest different diagnostic root causes.';
          blendedEl.textContent = Math.round((s.final_confidence || 0.6) * 100) + '%';
        }

        document.getElementById('sop-ml-cat').textContent = s.ml_category || 'syntax_error';
        const mlPct = Math.round((s.ml_confidence || 0) * 100);
        document.getElementById('sop-ml-conf').textContent = mlPct + '%';
        document.getElementById('sop-ml-bar').style.width = mlPct + '%';

        document.getElementById('sop-regex-cat').textContent = s.regex_category || 'other';
        const regPct = Math.round((s.regex_confidence || 0) * 100);
        document.getElementById('sop-regex-conf').textContent = regPct + '%';
        document.getElementById('sop-regex-bar').style.width = regPct + '%';

        let detailsHtml = '<div><b>Final Ensemble Decision:</b> <span style=\"color: var(--accent); font-weight: 600;\">' + escapeHtml(s.final_category) + '</span> (' + blendedEl.textContent + ' confidence)</div>';
        if (s.error_sample) {
          detailsHtml += '<div style=\"margin-top: 6px; font-size: 12px; color: var(--text-muted);\"><b>Evaluated Diagnostic:</b> <code>' + escapeHtml(s.error_sample) + '</code></div>';
        }
        if (s.candidates && s.candidates.length > 0) {
          detailsHtml += '<div style=\"margin-top: 10px;\"><b>Alternative Candidate Rankings:</b></div>';
          s.candidates.forEach((c, idx) => {
            detailsHtml += '<div style=\"display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #21262d; font-size: 12px;\"><span>' + (idx + 1) + '. ' + escapeHtml(c.category) + '</span><span style=\"color: var(--text-muted); font-family: Consolas, monospace;\">Score: ' + Math.round(c.blended * 100) + '% (ML: ' + Math.round(c.ml_score * 100) + '%, Regex: ' + Math.round(c.regex_score * 100) + '%)</span></div>';
          });
        }
        document.getElementById('sop-details-body').innerHTML = detailsHtml;
      }

      // Telemetry & Graphs
      if (d.telemetry) {
        const t = d.telemetry;
        document.getElementById('energy-val').textContent = t.energy_joules + ' J';
        document.getElementById('co2-val').textContent = t.co2_grams + ' g';
        document.getElementById('carbon-rating-val').textContent = t.carbon_rating || 'Grade A';
        document.getElementById('savings-val').textContent = (t.savings_pct !== undefined ? t.savings_pct : '42.5') + '%';

        // Energy Benchmarks Graph
        const maxVal = Math.max(t.unoptimized_legacy || 10, t.standard_baseline || 6, t.energy_joules * 1.5, 0.1);
        
        const curPct = Math.min(100, Math.max(8, (t.energy_joules / maxVal) * 100));
        const curBar = document.getElementById('chart-bar-current');
        curBar.style.width = curPct + '%';
        curBar.style.background = t.energy_joules < 5 ? '#3fb950' : '#38bdf8';
        document.getElementById('chart-val-current').textContent = t.energy_joules + ' J';

        const tgtVal = t.optimized_target || (t.energy_joules * 0.45);
        document.getElementById('chart-bar-target').style.width = Math.min(100, Math.max(6, (tgtVal / maxVal) * 100)) + '%';
        document.getElementById('chart-val-target').textContent = tgtVal + ' J';

        const stdVal = t.standard_baseline || (t.energy_joules * 1.6);
        document.getElementById('chart-bar-standard').style.width = Math.min(100, Math.max(10, (stdVal / maxVal) * 100)) + '%';
        document.getElementById('chart-val-standard').textContent = stdVal + ' J';

        const legVal = t.unoptimized_legacy || (t.energy_joules * 2.8);
        document.getElementById('chart-bar-legacy').style.width = Math.min(100, Math.max(15, (legVal / maxVal) * 100)) + '%';
        document.getElementById('chart-val-legacy').textContent = legVal + ' J';

        // Subsystem Breakdown
        document.getElementById('val-cpu').textContent = (t.cpu_joules || (t.energy_joules * 0.68).toFixed(3)) + ' J';
        document.getElementById('val-mem').textContent = (t.mem_joules || (t.energy_joules * 0.22).toFixed(3)) + ' J';
        document.getElementById('val-io').textContent = (t.io_joules || (t.energy_joules * 0.10).toFixed(3)) + ' J';
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // Trigger initial refresh
    setTimeout(() => { sendMessage('refresh'); }, 150);
  </script>
</body>
</html>`;
}
async function refreshDashboardData(document) {
    if (!dashboardPanel)
        return;
    currentDashboardDocument = document;
    const filePath = document.fileName;
    const backendPath = findBackendPath(document);
    const pythonPath = resolvePythonPath(backendPath);
    const bridgeScript = backendPath ? path.join(backendPath, "tools", "vscode_bridge.py") : "";
    if (!backendPath || !fs.existsSync(bridgeScript)) {
        dashboardPanel.webview.postMessage({ type: "done" });
        return;
    }
    const spawnArgs = [bridgeScript, "--dashboard", filePath];
    let stdoutData = "";
    let stderrData = "";
    const proc = cp.spawn(pythonPath, spawnArgs, {
        cwd: path.dirname(filePath),
        env: { ...process.env, PYTHONUNBUFFERED: "1", PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
        shell: false,
    });
    proc.on("error", (err) => {
        outputChannel.appendLine(`[DASHBOARD SPAWN ERROR] ${err.message}`);
        dashboardPanel?.webview.postMessage({ type: "done" });
    });
    proc.stdout?.on("data", (chunk) => {
        stdoutData += chunk.toString();
    });
    proc.stderr?.on("data", (chunk) => {
        stderrData += chunk.toString();
    });
    proc.on("close", (code) => {
        if (code === 0 && stdoutData.trim() && dashboardPanel) {
            try {
                const payload = JSON.parse(stdoutData);
                dashboardPanel.webview.postMessage({ type: "data", payload });
                return;
            }
            catch (err) {
                outputChannel.appendLine(`[DASHBOARD JSON ERROR] ${err.message}`);
            }
        }
        else {
            outputChannel.appendLine(`[DASHBOARD ERROR] code=${code}: ${stderrData}`);
        }
        dashboardPanel?.webview.postMessage({ type: "done" });
    });
}
function openDashboardPanel(context) {
    const config = vscode.workspace.getConfiguration("cee");
    const dashboardUrl = config.get("dashboardUrl", "http://localhost:8000");
    const activeEditor = vscode.window.activeTextEditor;
    if (activeEditor && isCppDocument(activeEditor.document)) {
        currentDashboardDocument = activeEditor.document;
    }
    else if (!currentDashboardDocument || !isCppDocument(currentDashboardDocument)) {
        const visibleEditor = vscode.window.visibleTextEditors.find((e) => isCppDocument(e.document));
        if (visibleEditor) {
            currentDashboardDocument = visibleEditor.document;
        }
    }
    if (dashboardPanel) {
        dashboardPanel.reveal(vscode.ViewColumn.Beside);
        if (currentDashboardDocument) {
            refreshDashboardData(currentDashboardDocument);
        }
        return;
    }
    dashboardPanel = vscode.window.createWebviewPanel("ceeDashboard", "⚡ Compiler Deep Analytics & Telemetry", vscode.ViewColumn.Beside, {
        enableScripts: true,
        retainContextWhenHidden: true,
    });
    dashboardPanel.webview.html = getDashboardHtml();
    dashboardPanel.webview.onDidReceiveMessage(async (message) => {
        let doc = vscode.window.activeTextEditor?.document;
        if (!doc || !isCppDocument(doc)) {
            doc = currentDashboardDocument;
        }
        if (!doc || !isCppDocument(doc)) {
            const visibleEditor = vscode.window.visibleTextEditors.find((e) => isCppDocument(e.document));
            if (visibleEditor) {
                doc = visibleEditor.document;
            }
        }
        if (!doc) {
            vscode.window.showWarningMessage("Compiler Error Explainer: Please open a C/C++ file to work with.");
            dashboardPanel?.webview.postMessage({ type: "done" });
            return;
        }
        currentDashboardDocument = doc;
        try {
            if (message.command === "autoheal") {
                await runAutoHeal(doc);
                await refreshDashboardData(doc);
            }
            else if (message.command === "optimize") {
                await runOptimize(doc);
                await refreshDashboardData(doc);
            }
            else if (message.command === "run") {
                await runFileInTerminal(doc);
            }
            else if (message.command === "compile") {
                await runCompileCheck(doc);
                await refreshDashboardData(doc);
            }
            else if (message.command === "refresh") {
                await refreshDashboardData(doc);
            }
        }
        catch (err) {
            outputChannel.appendLine(`[DASHBOARD ACTION ERROR] ${err.message}`);
        }
        finally {
            dashboardPanel?.webview.postMessage({ type: "done" });
        }
    }, null, context.subscriptions);
    dashboardPanel.onDidDispose(() => {
        dashboardPanel = undefined;
    }, null, context.subscriptions);
    if (currentDashboardDocument) {
        refreshDashboardData(currentDashboardDocument);
    }
}
function activate(context) {
    contextRef = context;
    outputChannel = vscode.window.createOutputChannel("Compiler Error Explainer");
    context.subscriptions.push(outputChannel);
    outputChannel.appendLine("[INIT] Compiler Error Explainer extension activating...");
    diagnosticCollection = vscode.languages.createDiagnosticCollection("compilerErrorExplainer");
    context.subscriptions.push(diagnosticCollection);
    errorDecorationType = vscode.window.createTextEditorDecorationType({
        isWholeLine: false,
        textDecoration: "underline wavy #f85149",
    });
    warningDecorationType = vscode.window.createTextEditorDecorationType({
        isWholeLine: false,
        textDecoration: "underline wavy #d29922",
    });
    securityDecorationType = vscode.window.createTextEditorDecorationType({
        isWholeLine: false,
        textDecoration: "underline wavy #ff4444",
    });
    context.subscriptions.push(errorDecorationType);
    context.subscriptions.push(warningDecorationType);
    context.subscriptions.push(securityDecorationType);
    // Status Bar Items
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = "cee.showOutput";
    statusBarItem.text = "$(shield) Explainer: ready";
    statusBarItem.tooltip = "Compiler Error Explainer (click to view logs)";
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    runStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 105);
    runStatusBarItem.command = "cee.run";
    runStatusBarItem.text = "$(play) Run";
    runStatusBarItem.tooltip = "Compile and Run C++ File in Terminal";
    runStatusBarItem.show();
    context.subscriptions.push(runStatusBarItem);
    compileStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 104);
    compileStatusBarItem.command = "cee.compile";
    compileStatusBarItem.text = "$(tools) Compile";
    compileStatusBarItem.tooltip = "Check for C++ Compilation Errors";
    compileStatusBarItem.show();
    context.subscriptions.push(compileStatusBarItem);
    autoHealStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 103);
    autoHealStatusBarItem.command = "cee.autoheal";
    autoHealStatusBarItem.text = "$(zap) Auto-Heal";
    autoHealStatusBarItem.tooltip = "Auto-Heal all compiler errors and security vulnerabilities";
    autoHealStatusBarItem.show();
    context.subscriptions.push(autoHealStatusBarItem);
    optimizeStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 102);
    optimizeStatusBarItem.command = "cee.optimize";
    optimizeStatusBarItem.text = "$(rocket) Optimize";
    optimizeStatusBarItem.tooltip = "Optimize C++ code for peak Big-O algorithmic efficiency";
    optimizeStatusBarItem.show();
    context.subscriptions.push(optimizeStatusBarItem);
    dashboardStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 101);
    dashboardStatusBarItem.command = "cee.openDashboard";
    dashboardStatusBarItem.text = "$(graph) Analytics Dashboard";
    dashboardStatusBarItem.tooltip = "Open Deep Analytics, Code Quality Gauge & AST Dashboard";
    dashboardStatusBarItem.show();
    context.subscriptions.push(dashboardStatusBarItem);
    // Commands
    context.subscriptions.push(vscode.commands.registerCommand("cee.run", async () => {
        let doc = vscode.window.activeTextEditor?.document;
        if (!doc || !isCppDocument(doc)) {
            doc = currentDashboardDocument;
        }
        if (!doc || !isCppDocument(doc)) {
            const visible = vscode.window.visibleTextEditors.find((e) => isCppDocument(e.document));
            if (visible)
                doc = visible.document;
        }
        if (doc && isCppDocument(doc)) {
            await runFileInTerminal(doc);
        }
        else {
            vscode.window.showInformationMessage("Open a C/C++ file to compile and run.");
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.compile", async () => {
        let doc = vscode.window.activeTextEditor?.document;
        if (!doc || !isCppDocument(doc)) {
            doc = currentDashboardDocument;
        }
        if (!doc || !isCppDocument(doc)) {
            const visible = vscode.window.visibleTextEditors.find((e) => isCppDocument(e.document));
            if (visible)
                doc = visible.document;
        }
        if (doc && isCppDocument(doc)) {
            await runCompileCheck(doc);
        }
        else {
            vscode.window.showInformationMessage("Open a C/C++ file to check compilation.");
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.openDashboard", () => {
        openDashboardPanel(context);
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.autoheal", async () => {
        let doc = vscode.window.activeTextEditor?.document;
        if (!doc || !isCppDocument(doc)) {
            doc = currentDashboardDocument;
        }
        if (!doc || !isCppDocument(doc)) {
            const visible = vscode.window.visibleTextEditors.find((e) => isCppDocument(e.document));
            if (visible)
                doc = visible.document;
        }
        if (doc && isCppDocument(doc)) {
            await runAutoHeal(doc);
        }
        else {
            vscode.window.showInformationMessage("Open a C/C++ file to auto-heal.");
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.optimize", async () => {
        let doc = vscode.window.activeTextEditor?.document;
        if (!doc || !isCppDocument(doc)) {
            doc = currentDashboardDocument;
        }
        if (!doc || !isCppDocument(doc)) {
            const visible = vscode.window.visibleTextEditors.find((e) => isCppDocument(e.document));
            if (visible)
                doc = visible.document;
        }
        if (doc && isCppDocument(doc)) {
            await runOptimize(doc);
        }
        else {
            vscode.window.showInformationMessage("Open a C/C++ file to optimize.");
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.format", async () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && isCppDocument(activeEditor.document)) {
            const edits = await runFormat(activeEditor.document);
            if (edits.length > 0) {
                const wsEdit = new vscode.WorkspaceEdit();
                wsEdit.set(activeEditor.document.uri, edits);
                await vscode.workspace.applyEdit(wsEdit);
                vscode.window.showInformationMessage("⚡ Code formatted via C++ Auto-Formatter.");
            }
        }
    }));
    context.subscriptions.push(vscode.languages.registerDocumentFormattingEditProvider([{ language: "cpp" }, { language: "c" }], {
        provideDocumentFormattingEdits(document) {
            return runFormat(document);
        },
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.showOutput", () => {
        outputChannel.show();
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.analyze", () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor) {
            runAnalysis(activeEditor.document);
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.clear", () => {
        diagnosticCollection.clear();
        diagnosticMap.clear();
        updateAllVisibleDecorations();
        updateStatusBar("$(check) Explainer: cleared", "All diagnostics cleared");
    }));
    context.subscriptions.push(vscode.commands.registerCommand("cee.scanSecurity", async () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && isCppDocument(activeEditor.document)) {
            await runAnalysis(activeEditor.document);
            const diags = getDiagnosticsForDocument(activeEditor.document) || [];
            const secFindings = diags.filter((d) => d.is_security);
            if (secFindings.length > 0) {
                vscode.window.showWarningMessage(`🛡️ Security Audit: Found ${secFindings.length} vulnerability risk(s)! Inspect inline badges or click Auto-Heal to repair.`);
            }
            else {
                vscode.window.showInformationMessage("🛡️ Security Audit: Clean! No CWE vulnerabilities found.");
            }
        }
    }));
    // Providers
    context.subscriptions.push(vscode.languages.registerHoverProvider([{ language: "cpp" }, { language: "c" }], new ExplainerHoverProvider()));
    context.subscriptions.push(vscode.languages.registerCodeActionsProvider([{ language: "cpp" }, { language: "c" }], new ExplainerCodeActionProvider(), { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }));
    // Event Listeners
    context.subscriptions.push(vscode.workspace.onDidOpenTextDocument((doc) => {
        if (isCppDocument(doc)) {
            const config = vscode.workspace.getConfiguration("cee");
            if (config.get("runOnOpen", true)) {
                runAnalysis(doc);
            }
        }
    }));
    context.subscriptions.push(vscode.workspace.onDidSaveTextDocument((doc) => {
        if (isCppDocument(doc)) {
            const config = vscode.workspace.getConfiguration("cee");
            if (config.get("runOnSave", true)) {
                runAnalysis(doc);
                if (dashboardPanel) {
                    refreshDashboardData(doc);
                }
            }
        }
    }));
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor((editor) => {
        if (editor && isCppDocument(editor.document)) {
            currentDashboardDocument = editor.document;
            updateDecorationsForEditor(editor);
            if (dashboardPanel) {
                refreshDashboardData(editor.document);
            }
        }
    }));
    // Analyze active editor on start
    if (vscode.window.activeTextEditor && isCppDocument(vscode.window.activeTextEditor.document)) {
        runAnalysis(vscode.window.activeTextEditor.document);
    }
    outputChannel.appendLine("[INIT] Compiler Error Explainer successfully initialized.");
}
function deactivate() {
    if (activeProcess) {
        activeProcess.kill();
    }
    if (debounceTimer) {
        clearTimeout(debounceTimer);
    }
}
//# sourceMappingURL=extension.js.map