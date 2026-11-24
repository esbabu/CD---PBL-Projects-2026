"""
Language Detector Module - Multilingual Detection (Python, C++, Java)
Phase 3: Multi-signal structural & lexical detection with confidence scoring

Supported Languages:
- 'python'
- 'cpp'
- 'java'

Features:
- Multi-signal pattern matching (structural, lexical, syntax tokens)
- Confidence scoring (high, medium, low, ambiguous)
- Ambiguity & short snippet detection
- Explicit user override handling with advisory warnings
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class LanguageDetectionResult:
    language: str                # 'python', 'cpp', 'java', or 'unknown'
    confidence: float           # 0.0 to 1.0
    confidence_level: str       # 'high', 'medium', 'low', 'ambiguous'
    signals: List[str] = field(default_factory=list)
    reason: str = ""
    ambiguous: bool = False
    user_override: Optional[str] = None
    scores: Dict[str, float] = field(default_factory=dict)

    @property
    def confidence_score(self) -> float:
        return self.confidence


class LanguageDetector:
    """
    Detects whether a source code snippet is Python, C++, or Java.
    Enforces strict 3-language constraint and provides confidence scoring.
    """

    SUPPORTED_LANGUAGES = {"python", "cpp", "java"}

    # --- PYTHON SIGNATURES ---
    PYTHON_STRONG_PATTERNS = [
        (r"\bdef\s+[a-zA-Z_]\w*\s*\(.*\)\s*:", "Python function definition with colon ('def ...:')", 4.0),
        (r"\belif\s+.*:", "Python 'elif' conditional", 4.0),
        (r"\bfrom\s+[a-zA-Z_]\w*\s+import\s+[a-zA-Z_]", "Python 'from ... import ...'", 4.0),
        (r"\bimport\s+[a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)*\s*$", "Python import statement without semicolon", 3.0),
        (r"\bclass\s+[a-zA-Z_]\w*(?:\s*\([^)]*\))?\s*:", "Python class definition with colon", 4.0),
        (r"\b__init__\s*\(", "Python '__init__' constructor", 4.0),
        (r"\b__main__\b", "Python '__main__' dunder", 3.5),
        (r"\bself\.[a-zA-Z_]\w*", "Python 'self.' attribute reference", 3.0),
        (r"\[\s*.*\s+for\s+.*\s+in\s+.*\]", "Python list comprehension", 4.0),
        (r"\bpass\b\s*(?:#.*)?$", "Python 'pass' statement", 3.0),
        (r"\bexcept(?:\s+[A-Za-z_]\w*)?\s*:", "Python 'except:' block", 4.0),
        (r"\braise\s+[A-Za-z_]\w*", "Python 'raise' statement", 3.0),
        (r"\bNone\b", "Python 'None' literal", 2.0),
        (r"\bTrue\b|\bFalse\b", "Python capitalized boolean ('True'/'False')", 2.0),
    ]

    PYTHON_SYNTAX_PATTERNS = [
        (r"^\s*#(?!\s*(?:include|define|pragma))\s*.*$", "Python '#' single-line comment", 1.5),
        (r":\s*$", "Block ending with colon without trailing semicolon", 1.5),
        (r"\bprint\s*\([^;]*\)\s*$", "Python print function call without semicolon", 2.0),
    ]

    # --- C++ SIGNATURES ---
    CPP_STRONG_PATTERNS = [
        (r"#include\s*<[a-zA-Z0-9_\./]+>", "C++ #include <header>", 4.5),
        (r"#include\s*\"[a-zA-Z0-9_\./]+\"", "C++ #include \"header\"", 4.0),
        (r"\busing\s+namespace\s+std\s*;", "C++ 'using namespace std;' directive", 4.5),
        (r"\bstd::", "C++ 'std::' namespace qualifier", 4.0),
        (r"\bcout\s*<<", "C++ stream output ('cout <<')", 4.5),
        (r"\bcin\s*>>", "C++ stream input ('cin >>')", 4.5),
        (r"\bendl\b", "C++ 'endl' stream manipulator", 3.5),
        (r"\bnullptr\b", "C++ 'nullptr' keyword", 4.0),
        (r"\btemplate\s*<", "C++ template declaration", 4.5),
        (r"\bint\s+main\s*\(\s*(?:int\s+argc|\s*void\s*|\s*)\)", "C++ int main() signature", 4.0),
        (r"\bvector\s*<", "C++ std::vector template instantiation", 3.5),
        (r"->\s*[a-zA-Z_]\w*", "C++ arrow operator pointer member access ('->')", 3.0),
        (r"::\s*[a-zA-Z_]\w*", "C++ scope resolution operator ('::')", 3.0),
        (r"\bdelete\s+(?:\[\]\s*)?[a-zA-Z_]", "C++ 'delete' memory deallocation", 3.5),
    ]

    CPP_SYNTAX_PATTERNS = [
        (r"\b#define\b", "C/C++ preprocessor macro '#define'", 2.5),
        (r"\bbool\b", "C++ 'bool' type (lowercase)", 1.5),
        (r"\bprintf\s*\(|\bscanf\s*\(", "C/C++ stdio functions (printf/scanf)", 2.5),
        (r"\bNULL\b", "C/C++ 'NULL' macro", 2.0),
    ]

    # --- JAVA SIGNATURES ---
    JAVA_STRONG_PATTERNS = [
        (r"\bpublic\s+class\s+[A-Za-z_]\w*", "Java 'public class' declaration", 4.5),
        (r"\bpublic\s+static\s+void\s+main\s*\(\s*String\s*(?:\[\s*\]|\.\.\.)\s*\w*\s*\)", "Java main method ('public static void main(String[] args)')", 5.0),
        (r"\bSystem\.(?:out|err)\.(?:println|print|printf)\b", "Java 'System.out.println' stream call", 4.5),
        (r"\bimport\s+java\.[a-zA-Z0-9_\.\*]+\s*;", "Java 'import java.*' package import", 4.5),
        (r"\bpackage\s+[a-zA-Z0-9_\.]+\s*;", "Java 'package ...;' statement", 4.5),
        (r"@Override\b", "Java '@Override' annotation", 4.0),
        (r"\bimplements\s+[A-Za-z_]\w*", "Java 'implements' keyword", 4.0),
        (r"\bextends\s+[A-Za-z_]\w*", "Java 'extends' keyword", 3.5),
        (r"\bboolean\b", "Java 'boolean' primitive keyword", 2.5),
        (r"\bString\s+[a-zA-Z_]\w*\s*=", "Java 'String' class type declaration", 3.0),
        (r"\bnew\s+Scanner\s*\(", "Java 'new Scanner' instantiation", 4.0),
        (r"\bnew\s+ArrayList\s*<", "Java 'new ArrayList<>' instantiation", 4.0),
        (r"\bthrows\s+[A-Za-z_]\w*Exception\b", "Java 'throws Exception' method clause", 4.0),
        (r"\bpublic\s+(?:int|void|boolean|String|double|float|long|char)\s+[a-zA-Z_]\w*\s*\(", "Java method declaration", 3.5),
        (r"\bprivate\s+(?:int|void|boolean|String|double|float|long|char)\s+[a-zA-Z_]\w*\s*\(", "Java private method declaration", 3.5),
    ]

    JAVA_SYNTAX_PATTERNS = [
        (r"\bnull\b", "Java/C 'null' keyword (lowercase)", 1.5),
        (r"\bfinal\s+[a-zA-Z_]\w*", "Java 'final' keyword modifier", 2.0),
        (r"\bthis\.[a-zA-Z_]\w*", "Java 'this.' reference", 2.0),
    ]

    def __init__(self):
        pass

    def detect_language(
        self,
        code: str,
        user_override: Optional[str] = None
    ) -> LanguageDetectionResult:
        """
        Analyze code snippet and identify whether it is Python, C++, or Java.

        Args:
            code: Source code string to evaluate.
            user_override: Optional user-specified language ('python', 'cpp', 'java').
                           If given, result.language will be user_override, with any
                           contradicting signals clearly noted.

        Returns:
            LanguageDetectionResult with detected language, confidence, and signals.
        """
        # If user explicitly overrode language and it is valid
        if user_override:
            normalized_override = user_override.strip().lower()
            if normalized_override in self.SUPPORTED_LANGUAGES:
                # Still analyze signals to inform user if code conflicts with their choice
                raw_result = self._score_code(code)
                signals = raw_result["signals"].get(normalized_override, [])
                contradiction = ""
                if raw_result["best_lang"] != normalized_override and raw_result["best_score"] >= 4.0:
                    contradiction = (
                        f" (Note: Code contains strong indicators for {raw_result['best_lang'].upper()} "
                        f"[score={raw_result['best_score']:.1f}])"
                    )

                return LanguageDetectionResult(
                    language=normalized_override,
                    confidence=1.0,
                    confidence_level="high",
                    signals=signals,
                    reason=f"User override applied: '{normalized_override}'{contradiction}",
                    ambiguous=False,
                    user_override=normalized_override,
                    scores=raw_result["scores"]
                )

        if not code or not code.strip():
            return LanguageDetectionResult(
                language="python",
                confidence=0.0,
                confidence_level="ambiguous",
                signals=[],
                reason="Empty or whitespace-only code snippet.",
                ambiguous=True,
                scores={"python": 0.0, "cpp": 0.0, "java": 0.0}
            )

        analysis = self._score_code(code)
        best_lang = analysis["best_lang"]
        scores = analysis["scores"]
        signals = analysis["signals"]
        best_score = analysis["best_score"]
        second_score = analysis["second_score"]
        second_lang = analysis["second_lang"]

        # Ambiguity checks
        # 1. Total score is 0 or extremely low (e.g. `x = 5`, `print`)
        if best_score <= 1.0:
            return LanguageDetectionResult(
                language="python",  # default fallback
                confidence=0.25,
                confidence_level="ambiguous",
                signals=signals.get("python", []),
                reason="Snippet is too brief or lacks distinct language signatures. Defaulting to Python.",
                ambiguous=True,
                scores=scores
            )

        # 2. Tie or very close margin between top two contenders
        diff = best_score - second_score
        is_close_tie = (diff < 1.5 and best_score < 6.0) or (diff < 0.5)

        if is_close_tie and second_score > 1.5:
            return LanguageDetectionResult(
                language=best_lang,
                confidence=0.45,
                confidence_level="ambiguous",
                signals=signals.get(best_lang, []) + [f"Ambiguous with {second_lang} (score diff {diff:.1f})"],
                reason=f"Ambiguous snippet: features found for both {best_lang} ({best_score:.1f}) and {second_lang} ({second_score:.1f}).",
                ambiguous=True,
                scores=scores
            )

        # Confidence level computation
        if best_score >= 7.0 and diff >= 3.5:
            conf_level = "high"
            confidence = min(0.99, 0.85 + (diff / 20.0))
        elif best_score >= 3.5 and diff >= 1.5:
            conf_level = "medium"
            confidence = min(0.85, 0.70 + (diff / 15.0))
        else:
            conf_level = "low"
            confidence = min(0.69, 0.50 + (diff / 10.0))

        detected_signals = signals.get(best_lang, [])
        reason = f"Detected {best_lang.upper()} with {conf_level} confidence based on {len(detected_signals)} distinct signal(s)."

        return LanguageDetectionResult(
            language=best_lang,
            confidence=round(confidence, 2),
            confidence_level=conf_level,
            signals=detected_signals,
            reason=reason,
            ambiguous=False,
            scores=scores
        )

    def _score_code(self, code: str) -> Dict[str, Any]:
        """Calculates evidence weights for Python, C++, and Java."""
        scores: Dict[str, float] = {"python": 0.0, "cpp": 0.0, "java": 0.0}
        signals: Dict[str, List[str]] = {"python": [], "cpp": [], "java": []}

        # Check Python patterns
        for pattern, desc, weight in self.PYTHON_STRONG_PATTERNS + self.PYTHON_SYNTAX_PATTERNS:
            matches = re.findall(pattern, code, re.MULTILINE)
            if matches:
                scores["python"] += weight * min(len(matches), 3)
                signals["python"].append(desc)

        # Check C++ patterns
        for pattern, desc, weight in self.CPP_STRONG_PATTERNS + self.CPP_SYNTAX_PATTERNS:
            matches = re.findall(pattern, code, re.MULTILINE)
            if matches:
                scores["cpp"] += weight * min(len(matches), 3)
                signals["cpp"].append(desc)

        # Check Java patterns
        for pattern, desc, weight in self.JAVA_STRONG_PATTERNS + self.JAVA_SYNTAX_PATTERNS:
            matches = re.findall(pattern, code, re.MULTILINE)
            if matches:
                scores["java"] += weight * min(len(matches), 3)
                signals["java"].append(desc)

        # Lexical heuristics: Semicolons & Curly Braces vs Colons & Indentation
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        lines_with_semicolon = sum(1 for line in lines if line.endswith(";"))
        lines_with_colon = sum(1 for line in lines if line.endswith(":") or ":" in line)
        lines_with_braces = sum(1 for line in lines if "{" in line or "}" in line)

        if lines:
            semicolon_ratio = lines_with_semicolon / len(lines)
            if semicolon_ratio > 0.4:
                scores["cpp"] += 2.0
                scores["java"] += 2.0
            elif semicolon_ratio == 0 and lines_with_colon > 0:
                scores["python"] += 2.0
                signals["python"].append("Absence of trailing semicolons with colon block syntax")

            if lines_with_braces > 0:
                scores["cpp"] += 1.5
                scores["java"] += 1.5

        # Sort scores descending
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_lang, best_score = sorted_scores[0]
        second_lang, second_score = sorted_scores[1]

        return {
            "best_lang": best_lang,
            "best_score": best_score,
            "second_lang": second_lang,
            "second_score": second_score,
            "scores": {k: round(v, 2) for k, v in scores.items()},
            "signals": signals
        }

def detect_language(code: str, user_override: Optional[str] = None) -> LanguageDetectionResult:
    """Convenience function for detecting the language of a code snippet."""
    detector = LanguageDetector()
    return detector.detect_language(code, user_override=user_override)