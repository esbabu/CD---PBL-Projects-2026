/**
 * transformationLineResolver.ts
 *
 * Accurately resolves the line number in the original source code editor
 * where an optimization was applied.
 *
 * Resolution steps:
 * 1. Explicit line reference in the transformation string (e.g., "Line 14: ...", "at line 22", "[Line 8]")
 * 2. Diff analysis: identifies original code lines replaced or modified in optimizedCode
 * 3. Token / identifier / keyword matching from the transformation against sourceCode
 * 4. Fallback to the first executable code statement in sourceCode (avoiding boilerplate #include / import headers)
 */

export function getTransformationLine(
  transformationText: string,
  sourceCode: string = '',
  optimizedCode?: string,
  transformationIndex: number = 0
): number {
  if (!sourceCode || !sourceCode.trim()) return 1;

  const origLines = sourceCode.split('\n');
  const totalLines = origLines.length;

  // ── 1. Explicit regex match in transformation text ─────────────────────────
  const linePatterns = [
    /(?:line|lines|ln)\s*[:#]?\s*(\d+)/i,
    /(?:at|on|in)\s+line\s*[:#]?\s*(\d+)/i,
    /\[(?:line\s*)?(\d+)\]/i,
    /\bL(\d+)\b/,
    /#(\d+)\b/,
  ];

  for (const pat of linePatterns) {
    const match = transformationText.match(pat);
    if (match && match[1]) {
      const line = parseInt(match[1], 10);
      if (line >= 1 && line <= totalLines) {
        return line;
      }
    }
  }

  // ── 2. Diff analysis between original sourceCode and optimizedCode ────────
  if (optimizedCode && optimizedCode.trim() !== sourceCode.trim()) {
    const optLines = optimizedCode.split('\n');

    // Normalized lines
    const normOrig = origLines.map((l) => l.trim());
    const normOpt = optLines.map((l) => l.trim());

    // Set of lines that exist in optimized code
    const optSet = new Set(normOpt.filter((l) => l.length > 0));

    // Find original lines that were modified or removed
    const changedLineIndices: number[] = [];
    for (let i = 0; i < origLines.length; i++) {
      const line = normOrig[i];
      // Skip empty lines, standalone brackets, and comments
      if (line.length === 0) continue;
      if (line === '{' || line === '}' || line === '};') continue;
      if (line.startsWith('//') || line.startsWith('/*') || line.startsWith('*') || line.startsWith('#include') || line.startsWith('import ') || line.startsWith('using ')) {
        continue;
      }

      if (!optSet.has(line)) {
        changedLineIndices.push(i + 1);
      }
    }

    if (changedLineIndices.length > 0) {
      // Group contiguous lines into distinct hunks
      const hunks: number[] = [];
      let lastLine = -100;
      for (const lineNo of changedLineIndices) {
        if (lineNo > lastLine + 2) {
          hunks.push(lineNo);
        }
        lastLine = lineNo;
      }

      if (hunks.length > 0) {
        const targetHunk = hunks[Math.min(transformationIndex, hunks.length - 1)];
        if (targetHunk && targetHunk >= 1 && targetHunk <= totalLines) {
          return targetHunk;
        }
      }
    }
  }

  // ── 3. Token / identifier / keyword matching ──────────────────────────────
  const normTrans = transformationText.toLowerCase();

  // If transformation mentions loops
  if (normTrans.includes('loop') || normTrans.includes('for') || normTrans.includes('while') || normTrans.includes('iteration')) {
    for (let l = 0; l < origLines.length; l++) {
      const lineTrim = origLines[l].trim();
      if (lineTrim.startsWith('for') || lineTrim.startsWith('while') || lineTrim.includes('for (') || lineTrim.includes('while (')) {
        return l + 1;
      }
    }
  }

  // If transformation mentions recursion
  if (normTrans.includes('recurs') || normTrans.includes('call')) {
    for (let l = 0; l < origLines.length; l++) {
      const lineTrim = origLines[l].trim();
      if (lineTrim.includes('(') && lineTrim.includes(')') && !lineTrim.startsWith('//')) {
        return l + 1;
      }
    }
  }

  // Extract identifiers / code words from transformation
  const codeWordMatches = transformationText.match(/`([^`]+)`|'([^']+)'|"([^"]+)"|\b([a-zA-Z_][a-zA-Z0-9_]{3,})\b/g);
  if (codeWordMatches) {
    const stopWords = new Set([
      'line', 'lines', 'loop', 'with', 'from', 'into', 'code', 'made', 'time', 'space',
      'applied', 'using', 'replace', 'replaced', 'constant', 'memory', 'algorithm', 'instead',
      'function', 'variable', 'nested', 'check', 'avoid', 'reduce', 'reduced', 'remove', 'removed',
      'approach', 'technique', 'implement', 'implemented', 'order', 'return', 'input', 'output'
    ]);

    for (const rawWord of codeWordMatches) {
      const word = rawWord.replace(/[`'"]/g, '').trim();
      if (word.length >= 3 && !stopWords.has(word.toLowerCase())) {
        for (let l = 0; l < origLines.length; l++) {
          if (origLines[l].includes(word)) {
            return l + 1;
          }
        }
      }
    }
  }

  // ── 4. Intelligent fallback: first non-header, non-comment executable line ──
  for (let l = 0; l < origLines.length; l++) {
    const lineTrim = origLines[l].trim();
    if (
      lineTrim.length > 0 &&
      !lineTrim.startsWith('//') &&
      !lineTrim.startsWith('/*') &&
      !lineTrim.startsWith('*') &&
      !lineTrim.startsWith('#') &&
      !lineTrim.startsWith('import ') &&
      !lineTrim.startsWith('package ') &&
      !lineTrim.startsWith('using ')
    ) {
      return l + 1;
    }
  }

  return 1;
}
