"use strict";
/**
 * diagnosticMapper.ts
 * Pure data transformation and mapping logic between vscode_bridge.py output and VS Code diagnostics.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.escapeMarkdown = escapeMarkdown;
exports.parseBridgeOutput = parseBridgeOutput;
exports.mapRawDiagnostic = mapRawDiagnostic;
exports.buildHoverMarkdown = buildHoverMarkdown;
exports.buildMultiHoverMarkdown = buildMultiHoverMarkdown;
/**
 * Escapes characters that have special meaning in Markdown.
 */
function escapeMarkdown(text) {
    if (!text) {
        return "";
    }
    return text
        .replace(/\\/g, "\\\\")
        .replace(/`/g, "\\`")
        .replace(/\*/g, "\\*")
        .replace(/_/g, "\\_")
        .replace(/\{/g, "\\{")
        .replace(/\}/g, "\\}")
        .replace(/\[/g, "\\[")
        .replace(/\]/g, "\\]")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}
/**
 * Parses raw stdout from vscode_bridge.py safely.
 */
function parseBridgeOutput(jsonString) {
    if (!jsonString || typeof jsonString !== "string") {
        throw new Error("Empty bridge output");
    }
    try {
        const parsed = JSON.parse(jsonString);
        if (typeof parsed !== "object" || parsed === null) {
            throw new Error("Bridge output is not an object");
        }
        return parsed;
    }
    catch (err) {
        throw new Error(`Malformed JSON output from backend bridge: ${err.message || String(err)}`);
    }
}
/**
 * Maps a single raw diagnostic to normalized 0-based range and severity.
 *
 * @param raw Raw diagnostic from bridge
 * @param getLineText Function that returns the full string of a 0-based line index
 */
function mapRawDiagnostic(raw, getLineText) {
    let startLine;
    let startCol;
    let endLine;
    let endCol;
    let displayMessage = raw.message || "Compiler diagnostic";
    // Check for null line (e.g. Linker error) -> line 1 (0-based index 0)
    if (raw.line === null || raw.line === undefined || raw.line < 1) {
        startLine = 0;
        endLine = 0;
        const line0Text = getLineText(0) || "";
        const firstNonWs = line0Text.search(/\S/);
        startCol = firstNonWs >= 0 ? firstNonWs : 0;
        endCol = Math.max(startCol + 1, line0Text.trimEnd().length);
        if (!displayMessage.toLowerCase().startsWith("[linker error]")) {
            displayMessage = `[Linker Error] [Explainer] ${displayMessage}`;
        }
    }
    else {
        // 1-based line to 0-based
        startLine = raw.line - 1;
        endLine = startLine;
        const lineText = getLineText(startLine) || "";
        if (raw.is_security) {
            displayMessage = `[Security ${raw.cwe || "Vulnerability"}] ${raw.category}: ${raw.message}`;
        }
        else if (!displayMessage.startsWith("[Explainer]")) {
            displayMessage = `[Explainer] ${displayMessage}`;
        }
        if (raw.column === null || raw.column === undefined || raw.column < 1) {
            // Underline the whole line, trimmed
            const firstNonWs = lineText.search(/\S/);
            startCol = firstNonWs >= 0 ? firstNonWs : 0;
            endCol = Math.max(startCol + 1, lineText.trimEnd().length);
        }
        else {
            // 1-based column to 0-based
            const targetCol = Math.max(0, raw.column - 1);
            const trimmedLen = lineText.trimEnd().length;
            if (trimmedLen === 0) {
                startCol = 0;
                endCol = 1;
            }
            else if (targetCol >= trimmedLen) {
                // Column is beyond line text (e.g. expected ';' at col 20 on 19-char line)
                endCol = trimmedLen;
                let tokenStart = endCol - 1;
                while (tokenStart > 0 && /[a-zA-Z0-9_]/.test(lineText[tokenStart - 1])) {
                    tokenStart--;
                }
                startCol = Math.min(tokenStart, endCol - 1);
            }
            else {
                startCol = targetCol;
                // Span at least 1 character, or until end of token/line
                let wordEnd = startCol + 1;
                while (wordEnd < lineText.length && /[a-zA-Z0-9_]/.test(lineText[wordEnd])) {
                    wordEnd++;
                }
                endCol = Math.max(startCol + 1, wordEnd);
            }
        }
    }
    // Normalize severity
    let severity = "error";
    const sevLower = (raw.severity || "").toLowerCase();
    if (sevLower === "warning") {
        severity = "warning";
    }
    else if (sevLower === "information" || sevLower === "info" || sevLower === "note") {
        severity = "information";
    }
    else {
        severity = "error";
    }
    return {
        range: {
            startLine,
            startCharacter: startCol,
            endLine,
            endCharacter: endCol,
        },
        severity,
        category: raw.category || "other",
        message: displayMessage,
        what: raw.what || raw.message || "Compiler diagnostic reported.",
        why: raw.why || "Language rules violated.",
        how: raw.how || raw.suggestion || "Inspect and fix code at location.",
        suggestion: raw.suggestion || "",
        confidence: typeof raw.confidence === "number" ? raw.confidence : 1.0,
        rawLine: raw.line,
        rawColumn: raw.column,
        fix: raw.fix,
        is_security: raw.is_security,
        cwe: raw.cwe,
        security_risk: raw.security_risk,
        recommendation: raw.recommendation,
    };
}
/**
 * Builds the MarkdownString content for the hover popup.
 */
function buildHoverMarkdown(diag) {
    const parts = [];
    if (diag.is_security) {
        parts.push(`### 🛡️ Security Vulnerability: \`${diag.cwe || "Security Alert"}\` (${diag.category})`);
        parts.push(`**Risk Level:** \`${diag.security_risk || "High"}\` &nbsp;|&nbsp; *Source:* Static Security Analysis`);
        parts.push(`**Vulnerability:**\n\n${escapeMarkdown(diag.what)}`);
        parts.push(`**Why it is dangerous:**\n\n${escapeMarkdown(diag.why)}`);
        const fixText = diag.recommendation || diag.how;
        parts.push(`**Remediation:**\n\n${escapeMarkdown(fixText)}`);
        if (diag.fix && diag.fix.available) {
            parts.push(`💡 **Auto-Heal:** *Quick Fix available (${diag.fix.safety_level} - ${escapeMarkdown(diag.fix.tier_name)}). Press Cmd + . or click lightbulb to apply.*`);
        }
        parts.push(`---\n*CWE Identifier:* \`${diag.cwe || "CWE-Other"}\` &nbsp;|&nbsp; *Detection Engine:* Compiler Error Explainer`);
        return parts.join("\n\n");
    }
    parts.push(`### ⚡ Compiler Error Explainer: \`${diag.category}\``);
    parts.push(`**What happened:**\n\n${escapeMarkdown(diag.what)}`);
    parts.push(`**Why it happened:**\n\n${escapeMarkdown(diag.why)}`);
    parts.push(`**How to fix it:**\n\n${escapeMarkdown(diag.how)}`);
    if (diag.suggestion && diag.suggestion !== diag.how) {
        parts.push(`**Suggestion:**\n\n${escapeMarkdown(diag.suggestion)}`);
    }
    if (diag.fix && diag.fix.available) {
        parts.push(`💡 **Auto-Heal:** *Quick Fix available (${diag.fix.safety_level} - ${escapeMarkdown(diag.fix.tier_name)}). Press Cmd + . or click lightbulb to apply.*`);
    }
    const confPct = Math.round(diag.confidence * 100);
    parts.push(`---\n*Source:* \`Compiler Error Explainer\` &nbsp;|&nbsp; *Confidence:* ${confPct}%`);
    return parts.join("\n\n");
}
/**
 * Builds markdown content for one or more diagnostics on the hovered line.
 */
function buildMultiHoverMarkdown(diags) {
    if (diags.length === 1) {
        return buildHoverMarkdown(diags[0]);
    }
    return diags
        .map((d, idx) => {
        const header = `### Compiler Issue ${idx + 1} of ${diags.length}: \`${d.category}\``;
        return `${header}\n\n${buildHoverMarkdown(d)}`;
    })
        .join("\n\n---\n\n");
}
//# sourceMappingURL=diagnosticMapper.js.map