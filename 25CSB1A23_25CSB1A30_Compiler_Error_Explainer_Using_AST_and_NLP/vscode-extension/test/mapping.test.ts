import { describe, it } from "node:test";
import * as assert from "node:assert";
import {
  mapRawDiagnostic,
  parseBridgeOutput,
  escapeMarkdown,
  buildHoverMarkdown,
  RawBridgeDiagnostic,
} from "../src/diagnosticMapper";

describe("JSON-to-Diagnostic Mapping Tests", () => {
  const dummyFileLines = [
    "#include <iostream>", // line 0
    "    int x = 10",      // line 1 (indented)
    "    int y = 20;",     // line 2
    "    return 0;",       // line 3
  ];

  const getLineText = (lineIndex: number): string => {
    return dummyFileLines[lineIndex] || "";
  };

  it("handles null column by underlining the whole trimmed line", () => {
    const raw: RawBridgeDiagnostic = {
      line: 2, // 1-based (corresponds to line 1: "    int x = 10")
      column: null,
      severity: "error",
      category: "syntax_error",
      message: "expected ';' at end of declaration",
      what: "Compiler expected a semicolon",
      why: "Grammar syntax rule violated",
      how: "Add a semicolon",
      suggestion: "Add ';'",
      confidence: 0.95,
    };

    const mapped = mapRawDiagnostic(raw, getLineText);

    assert.strictEqual(mapped.range.startLine, 1);
    assert.strictEqual(mapped.range.endLine, 1);
    // Line 1 is "    int x = 10". First non-whitespace is index 4.
    assert.strictEqual(mapped.range.startCharacter, 4);
    assert.strictEqual(mapped.range.endCharacter, 14); // length of "    int x = 10"
    assert.strictEqual(mapped.severity, "error");
    assert.strictEqual(mapped.category, "syntax_error");
  });

  it("handles null line (linker errors) by placing diagnostic on line 1 with clear message", () => {
    const raw: RawBridgeDiagnostic = {
      line: null,
      column: null,
      severity: "error",
      category: "linker_error",
      message: "undefined reference to 'computeArea(int, int)'",
      what: "Linker error: undefined reference",
      why: "Symbol declared but not linked",
      how: "Compile and link the implementation",
      suggestion: "Ensure source file is compiled",
      confidence: 0.98,
    };

    const mapped = mapRawDiagnostic(raw, getLineText);

    // Mapped to line 1 (0-based index 0)
    assert.strictEqual(mapped.range.startLine, 0);
    assert.strictEqual(mapped.range.endLine, 0);
    assert.strictEqual(mapped.range.startCharacter, 0);
    assert.ok(mapped.message.startsWith("[Linker Error]"));
    assert.strictEqual(mapped.severity, "error");
    assert.strictEqual(mapped.category, "linker_error");
  });

  it("correctly maps all three severities: error, warning, and information", () => {
    const rawError: RawBridgeDiagnostic = {
      line: 1,
      column: 1,
      severity: "error",
      category: "type_error",
      message: "Type mismatch",
      what: "Incompatible types",
      why: "Cannot cast",
      how: "Use static_cast",
      suggestion: "Cast explicitly",
      confidence: 0.9,
    };

    const rawWarning: RawBridgeDiagnostic = {
      line: 2,
      column: 5,
      severity: "warning",
      category: "unused_var",
      message: "unused variable 'x'",
      what: "Variable declared but unused",
      why: "Dead code",
      how: "Remove or use it",
      suggestion: "Remove variable",
      confidence: 0.85,
    };

    const rawInfo: RawBridgeDiagnostic = {
      line: 3,
      column: 1,
      severity: "information",
      category: "style_note",
      message: "Consider const qualification",
      what: "Variable not modified",
      why: "Improves safety",
      how: "Add const",
      suggestion: "Add const keyword",
      confidence: 0.8,
    };

    assert.strictEqual(mapRawDiagnostic(rawError, getLineText).severity, "error");
    assert.strictEqual(mapRawDiagnostic(rawWarning, getLineText).severity, "warning");
    assert.strictEqual(mapRawDiagnostic(rawInfo, getLineText).severity, "information");
  });

  it("handles malformed JSON gracefully", () => {
    assert.throws(() => parseBridgeOutput("{ broken json"), /Malformed JSON output/);
    assert.throws(() => parseBridgeOutput(""), /Empty bridge output/);
    assert.throws(() => parseBridgeOutput("null"), /Bridge output is not an object/);
    assert.throws(() => parseBridgeOutput("12345"), /Bridge output is not an object/);

    const validJson = JSON.stringify({
      ok: true,
      compiler: "clang",
      diagnostics: [],
    });
    const parsed = parseBridgeOutput(validJson);
    assert.strictEqual(parsed.ok, true);
    assert.strictEqual(parsed.compiler, "clang");
    assert.deepStrictEqual(parsed.diagnostics, []);
  });

  it("properly escapes Markdown and HTML in hover card generation", () => {
    const raw: RawBridgeDiagnostic = {
      line: 1,
      column: 1,
      severity: "error",
      category: "syntax_error",
      message: "expected '<' or '>' in template",
      what: "Template parameter error: std::vector<int>",
      why: "Missing closing `>` tag or *pointer* dereference",
      how: "Use `static_cast<int>(x)`",
      suggestion: "Fix syntax",
      confidence: 0.95,
    };

    const mapped = mapRawDiagnostic(raw, getLineText);
    const hoverMd = buildHoverMarkdown(mapped);

    // Angle brackets must be escaped
    assert.ok(hoverMd.includes("&lt;int&gt;"));
    assert.ok(!hoverMd.includes("<int>"));
    // Markdown characters escaped
    assert.ok(hoverMd.includes("\\*pointer\\*"));
    assert.ok(hoverMd.includes("\\`&gt;\\`"));
  });

  it("correctly maps fix metadata and includes Quick Fix notice in hover markdown", () => {
    const raw: RawBridgeDiagnostic = {
      line: 2,
      column: 10,
      severity: "error",
      category: "syntax_error",
      message: "expected ';'",
      what: "Missing semicolon",
      why: "Syntax rule",
      how: "Add semicolon",
      suggestion: "Add ';'",
      confidence: 0.95,
      fix: {
        available: true,
        title: "Auto-fix syntax error",
        tier_name: "Tier 1: Compiler Fix-It",
        safety_level: "S0",
        patched_source: "int x = 10;\n",
      },
    };

    const mapped = mapRawDiagnostic(raw, getLineText);
    assert.ok(mapped.fix);
    assert.strictEqual(mapped.fix.available, true);
    assert.strictEqual(mapped.fix.safety_level, "S0");
    assert.strictEqual(mapped.fix.title, "Auto-fix syntax error");

    const hoverMd = buildHoverMarkdown(mapped);
    assert.ok(hoverMd.includes("Auto-Heal:"));
    assert.ok(hoverMd.includes("S0"));
    assert.ok(hoverMd.includes("Cmd + ."));
  });

  it("correctly maps security vulnerabilities with CWE badges and security hover card", () => {
    const raw: RawBridgeDiagnostic = {
      line: 3,
      column: null,
      severity: "warning",
      category: "Use After Free",
      message: "Memory appears to be accessed after it was freed.",
      what: "Memory appears to be accessed after it was freed.",
      why: "Heap pointer reused",
      how: "Reset pointer to nullptr",
      suggestion: "Reset pointer",
      confidence: 1.0,
      is_security: true,
      cwe: "CWE-416",
      security_risk: "High",
      recommendation: "Do not use pointer after delete.",
    };

    const mapped = mapRawDiagnostic(raw, getLineText);
    assert.strictEqual(mapped.is_security, true);
    assert.strictEqual(mapped.cwe, "CWE-416");
    assert.strictEqual(mapped.security_risk, "High");
    assert.ok(mapped.message.includes("[Security CWE-416]"));

    const hoverMd = buildHoverMarkdown(mapped);
    assert.ok(hoverMd.includes("Security Vulnerability: `CWE-416`"));
    assert.ok(hoverMd.includes("High"));
    assert.ok(hoverMd.includes("Static Security Analysis"));
    assert.ok(hoverMd.includes("Remediation:"));
  });
});
