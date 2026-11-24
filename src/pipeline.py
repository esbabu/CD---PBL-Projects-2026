"""
Main Pipeline - End-to-end error explanation system
"""

from typing import Optional, Dict
from dataclasses import dataclass
from .pedagogical_agent import PedagogicalAgent

try:
    from .error_capture import ErrorCapture
    from .ast_parser import ASTContextExtractor
    from .model import ErrorExplainerModel, FallbackExplainer
    from .agent import RepairAgent, OptimizationAgent
    from .language_detector import LanguageDetector
    from .cpp_analyzer import CppAnalyzer
    from .java_analyzer import JavaAnalyzer
    from .pedagogical_agent import PedagogicalAgent
except ImportError:
    from error_capture import ErrorCapture
    from ast_parser import ASTContextExtractor
    from model import ErrorExplainerModel, FallbackExplainer
    from agent import RepairAgent, OptimizationAgent
    from language_detector import LanguageDetector
    from cpp_analyzer import CppAnalyzer
    from java_analyzer import JavaAnalyzer
    from pedagogical_agent import PedagogicalAgent


@dataclass
class ExplanationResult:
    """Result from the error explanation pipeline."""
    success: bool
    error_type: Optional[str]
    raw_error: Optional[str]
    friendly_explanation: Optional[str]
    suggested_fix: Optional[str]
    code_context: Optional[str]
    line_number: Optional[int]
    similar_names: list
    security_warnings: list
    candidate_code: Optional[str] = None
    validated: bool = False
    attempts: int = 0
    status: str = "UNVERIFIED"
    language: str = "python"
    confidence: float = 1.0
    compiler_available: bool = True
    diagnostics: Optional[list] = None
    stdout: Optional[str] = None
    column_number: Optional[int] = None
    severity: str = "ERROR"
    underlying_concept: Optional[str] = None
    diagnostic_details: Optional[str] = None
    changes_made: Optional[str] = None
    assumptions: Optional[str] = None
    error_id: Optional[str] = None
    fix_explanation: Optional[str] = None


class AIErrorTutor:
    """Main pipeline for AI-powered error explanations."""

    def __init__(self, model_path: Optional[str] = "./models/error_tutor_model", use_ai: bool = True):
        """
        Initialize the AI Error Tutor.

        Args:
            model_path: Path to fine-tuned model (if available)
            use_ai: Whether to use AI model (False for fallback only)
        """
        self.error_capture = ErrorCapture()
        self.ast_extractor = ASTContextExtractor()
        self.fallback = FallbackExplainer()
        self.pedagogical_agent = PedagogicalAgent()
        self.agent = RepairAgent(self.error_capture)
        self.optimizer = OptimizationAgent(self.error_capture)
        self.language_detector = LanguageDetector()
        self.cpp_analyzer = CppAnalyzer()
        self.java_analyzer = JavaAnalyzer()

        self.use_ai = use_ai
        self.model = None

        if use_ai:
            try:
                import os
                # Verify folder actually exists locally
                if model_path and not os.path.exists(model_path):
                    raise FileNotFoundError(f"Model folder not found at: {model_path}")
                
                # Pass the path directly when initializing!
                self.model = ErrorExplainerModel(model_path=model_path)
                print("[OK] AI model loaded successfully")
            except Exception as e:
                print(f"[NOTE] AI model not available: {e}")
                print("  Using fallback explanations")
                self.use_ai = False

    def analyze_code(self, code: str, language: Optional[str] = None) -> ExplanationResult:
        """
        Analyze code and provide friendly error explanations.
        Supports Python, C++, and Java with automatic detection or user override.

        Args:
            code: Source code to analyze
            language: Optional language override ('python', 'cpp', 'java', or None/'auto')

        Returns:
            ExplanationResult with error details, friendly explanation, and language info
        """
        # Determine language
        confidence = 1.0
        if not language or language.lower() == "auto":
            det_res = self.language_detector.detect_language(code)
            target_lang = det_res.language
            confidence = det_res.confidence
        else:
            target_lang = language.strip().lower()

        # Dispatch C++
        if target_lang == "cpp":
            cpp_res = self.cpp_analyzer.analyze(code)
            sec_warnings = [cpp_res["error_message"]] if cpp_res["status"] == "BLOCKED" else []
            cand = cpp_res.get("candidate_code")
            if not cand or cand == code:
                cand = self.cpp_analyzer.generate_candidate(code, cpp_res.get("error_type") or "")
            
            card = None
            if cpp_res["status"] != "SUCCESS":
                card = self.pedagogical_agent.generate_diagnostic_card(
                    error_type=cpp_res.get("error_type") or "SyntaxError",
                    code=code,
                    raw_message=cpp_res.get("error_message") or "",
                    language="cpp",
                    line_number=cpp_res.get("line_number"),
                    column=cpp_res.get("column", 1)
                )

            ped_exp = card.get("pedagogical_explanation") if card else (cpp_res.get("explanation") or "")

            return ExplanationResult(
                success=(cpp_res["status"] == "SUCCESS"),
                error_type=cpp_res["error_type"],
                raw_error=cpp_res["error_message"],
                friendly_explanation=ped_exp,
                suggested_fix=card.get("illustrative_example") if card else None,
                code_context=cpp_res.get("code_snippet"),
                line_number=cpp_res.get("line_number"),
                column_number=cpp_res.get("column", 1),
                severity=card.get("severity") if card else None,
                underlying_concept=card.get("underlying_concept") if card else None,
                diagnostic_details=card.get("diagnostic_details") if card else None,
                changes_made=card.get("changes_made") if card else None,
                assumptions=card.get("assumptions") if card else None,
                error_id="cpp_err_1" if card else None,
                fix_explanation=card.get("fix_explanation") if card else None,
                similar_names=[],
                security_warnings=sec_warnings,
                candidate_code=cand,
                validated=(cand is not None and cand != code),
                attempts=1 if cand else 0,
                status=cpp_res["status"],
                language="cpp",
                confidence=confidence,
                compiler_available=cpp_res.get("compiler_available", True),
                diagnostics=cpp_res.get("diagnostics", []),
                stdout=cpp_res.get("stdout", "")
            )

        # Dispatch Java
        if target_lang == "java":
            java_res = self.java_analyzer.analyze(code)
            sec_warnings = [java_res["error_message"]] if java_res["status"] == "BLOCKED" else []
            cand = java_res.get("candidate_code")
            if not cand or cand == code:
                cand = self.java_analyzer.generate_candidate(code, java_res.get("error_type") or "")

            card = None
            if java_res["status"] != "SUCCESS":
                card = self.pedagogical_agent.generate_diagnostic_card(
                    error_type=java_res.get("error_type") or "SyntaxError",
                    code=code,
                    raw_message=java_res.get("error_message") or "",
                    language="java",
                    line_number=java_res.get("line_number"),
                    column=java_res.get("column", 1)
                )

            ped_exp = card.get("pedagogical_explanation") if card else (java_res.get("explanation") or "")

            return ExplanationResult(
                success=(java_res["status"] == "SUCCESS"),
                error_type=java_res["error_type"],
                raw_error=java_res["error_message"],
                friendly_explanation=ped_exp,
                suggested_fix=card.get("illustrative_example") if card else None,
                code_context=java_res.get("code_snippet"),
                line_number=java_res.get("line_number"),
                column_number=java_res.get("column", 1),
                severity=card.get("severity") if card else None,
                underlying_concept=card.get("underlying_concept") if card else None,
                diagnostic_details=card.get("diagnostic_details") if card else None,
                changes_made=card.get("changes_made") if card else None,
                assumptions=card.get("assumptions") if card else None,
                error_id="java_err_1" if card else None,
                fix_explanation=card.get("fix_explanation") if card else None,
                similar_names=[],
                security_warnings=sec_warnings,
                candidate_code=cand,
                validated=(cand is not None and cand != code),
                attempts=1 if cand else 0,
                status=java_res["status"],
                language="java",
                confidence=confidence,
                compiler_available=java_res.get("compiler_available", False),
                diagnostics=java_res.get("diagnostics", []),
                stdout=java_res.get("stdout", "") 
            )

        # Step 1: Execute and capture errors (security check happens inside)
        success, error_info = self.error_capture.execute_code(code)

        # Collect any security warnings
        sec_warnings = []
        if error_info and 'security_warnings' in error_info:
            sec_warnings = error_info['security_warnings']

        if success:
            return ExplanationResult(
                success=True,
                error_type=None,
                raw_error=None,
                friendly_explanation="✓ Your code ran successfully! ",
                suggested_fix=None,
                code_context=None,
                line_number=None,
                similar_names=[],
                security_warnings=sec_warnings,
                language="python",
                confidence=confidence,
                stdout=error_info.get("stdout","") if error_info else ""
            )

        # Step 1.5: Handle security blocks separately
        if error_info.get('error_type') == 'SecurityError':
            return ExplanationResult(
                success=False,
                error_type='SecurityError',
                raw_error=error_info['message'],
                friendly_explanation=(
                    "🚫 Your code was blocked because it contains potentially "
                    "dangerous operations. In a learning environment, operations "
                    "like system commands, file deletion, or dynamic code execution "
                    "are not allowed for your safety."
                ),
                suggested_fix=(
                    "Remove the dangerous imports/functions and focus on "
                    "the programming concept you're trying to learn."
                ),
                code_context=error_info.get('code_context', ''),
                line_number=error_info.get('line_number'),
                similar_names=[],
                security_warnings=sec_warnings,
                language="python",
                confidence=confidence
            )

        # Step 2: Extract AST context
        ast_context = self.ast_extractor.analyze_error_context(error_info)

        # Step 3: Generate explanation
        # Force deterministic fallback for V1 reliability to prevent T5 hallucinations
        explanation = self._generate_fallback_explanation(error_info, ast_context)

        # Step 4: Agentic Correction Loop
        # Agent generates a candidate fix and validates it using the execution pipeline
        agent_result = self.agent.attempt_repair(code, error_info, ast_context)
        
        explanation.candidate_code = agent_result.get("candidate_code")
        explanation.validated = agent_result.get("validated", False)
        explanation.attempts = agent_result["attempts"]
        explanation.status = agent_result.get("status", "UNVERIFIED")

        card = self.pedagogical_agent.generate_diagnostic_card(
            error_type=error_info.get('error_type', 'SyntaxError'),
            code=code,
            raw_message=error_info.get('message', ''),
            language="python",
            line_number=error_info.get('line_number'),
            column=error_info.get('column')
        )
        if card:
            explanation.friendly_explanation = card.get("pedagogical_explanation") or explanation.friendly_explanation
            explanation.severity = card.get("severity")
            explanation.underlying_concept = card.get("underlying_concept")
            explanation.diagnostic_details = card.get("diagnostic_details")
            explanation.changes_made = card.get("changes_made")
            explanation.assumptions = card.get("assumptions")
            explanation.error_id = "py_err_1"
            explanation.fix_explanation = card.get("fix_explanation")
            explanation.column_number = error_info.get('column')

        explanation.security_warnings = sec_warnings
        explanation.language = "python"
        explanation.confidence = confidence

        return explanation

    def analyze_all_errors(self, code: str, language: Optional[str] = None) -> list[ExplanationResult]:
        """
        Analyze code to find all errors across Python, C++, and Java.
        Generates individual structured diagnostic cards for every detected error.
        """
        if language is None or language == "AUTO":
            det_res = self.language_detector.detect_language(code)
            target_lang = det_res.language
            confidence = det_res.confidence
        else:
            target_lang = language.strip().lower()
            confidence = 1.0

        if target_lang == "cpp":
            cpp_res = self.cpp_analyzer.analyze(code)
            if cpp_res.get("status") == "SUCCESS":
                return [self.analyze_code(code, language="cpp")]
            diags = cpp_res.get("diagnostics") or []
            if not diags:
                return [self.analyze_code(code, language="cpp")]
            
            card_results = []
            for idx, d in enumerate(diags, 1):
                cat = d.get("category", "SyntaxError")
                line_no = d.get("line")
                col_no = d.get("column", 1)
                cand = self.cpp_analyzer.generate_candidate(code, cat)
                card = self.pedagogical_agent.generate_diagnostic_card(
                    error_type=cat,
                    code=code,
                    raw_message=d.get("message", ""),
                    language="cpp",
                    line_number=line_no,
                    column=col_no
                )
                card_results.append(ExplanationResult(
                    success=False,
                    error_type=cat,
                    raw_error=d.get("message", ""),
                    friendly_explanation=card.get("pedagogical_explanation", ""),
                    suggested_fix=card.get("illustrative_example"),
                    code_context=d.get("code_snippet", ""),
                    line_number=line_no,
                    column_number=col_no,
                    severity=card.get("severity"),
                    underlying_concept=card.get("underlying_concept"),
                    diagnostic_details=card.get("diagnostic_details"),
                    changes_made=card.get("changes_made"),
                    assumptions=card.get("assumptions"),
                    error_id=f"cpp_err_{idx}",
                    fix_explanation=card.get("fix_explanation"),
                    similar_names=[],
                    security_warnings=[cpp_res["error_message"]] if cpp_res.get("status") == "BLOCKED" else [],
                    candidate_code=cand,
                    validated=(cand is not None and cand != code),
                    attempts=1 if cand else 0,
                    status=cpp_res.get("status", "ERROR"),
                    language="cpp",
                    confidence=confidence,
                    compiler_available=cpp_res.get("compiler_available", False),
                    diagnostics=diags,
                    stdout=cpp_res.get("stdout", "")
                ))
            return card_results

        if target_lang == "java":
            java_res = self.java_analyzer.analyze(code)
            if java_res.get("status") == "SUCCESS":
                return [self.analyze_code(code, language="java")]
            diags = java_res.get("diagnostics") or []
            if not diags:
                return [self.analyze_code(code, language="java")]
            
            card_results = []
            for idx, d in enumerate(diags, 1):
                cat = d.get("category", "SyntaxError")
                line_no = d.get("line")
                col_no = d.get("column", 1)
                cand = self.java_analyzer.generate_candidate(code, cat)
                card = self.pedagogical_agent.generate_diagnostic_card(
                    error_type=cat,
                    code=code,
                    raw_message=d.get("message", ""),
                    language="java",
                    line_number=line_no,
                    column=col_no
                )
                card_results.append(ExplanationResult(
                    success=False,
                    error_type=cat,
                    raw_error=d.get("message", ""),
                    friendly_explanation=card.get("pedagogical_explanation", ""),
                    suggested_fix=card.get("illustrative_example"),
                    code_context=d.get("code_snippet", ""),
                    line_number=line_no,
                    column_number=col_no,
                    severity=card.get("severity"),
                    underlying_concept=card.get("underlying_concept"),
                    diagnostic_details=card.get("diagnostic_details"),
                    changes_made=card.get("changes_made"),
                    assumptions=card.get("assumptions"),
                    error_id=f"java_err_{idx}",
                    fix_explanation=card.get("fix_explanation"),
                    similar_names=[],
                    security_warnings=[java_res["error_message"]] if java_res.get("status") == "BLOCKED" else [],
                    candidate_code=cand,
                    validated=(cand is not None and cand != code),
                    attempts=1 if cand else 0,
                    status=java_res.get("status", "ERROR"),
                    language="java",
                    confidence=confidence,
                    compiler_available=java_res.get("compiler_available", False),
                    diagnostics=diags,
                    stdout=java_res.get("stdout", "")
                ))
            return card_results

        # Python iterative multi-error analysis
        results = []
        current_code = code
        patched_lines_set = set()
        for _ in range(10):  # Max 10 errors to avoid infinite loops
            res = self.analyze_code(current_code, language="python")
            
            if res.success:
                if not results:
                    results.append(res)
                break
                
            results.append(res)
            
            if res.error_type == 'SecurityError':
                break
                
            if res.candidate_code:
                patched_lines = res.candidate_code.split('\n')
                orig_lines = code.split('\n')
                for i in range(min(len(patched_lines), len(orig_lines))):
                    if "__AUTO_PATCH__" in patched_lines[i]:
                        patched_lines[i] = orig_lines[i]
                res.candidate_code = '\n'.join(patched_lines)

            if not res.candidate_code or res.candidate_code == current_code:
                err_info = {
                    'error_type': res.error_type,
                    'message': res.raw_error or '',
                    'line_number': res.line_number,
                    'full_code': code,
                    'code_context': res.code_context or ''
                }
                ast_ctx = self.ast_extractor.analyze_error_context(err_info)
                cand = self.agent._generate_candidate_code(code, err_info, ast_ctx)
                if cand and cand != code:
                    res.candidate_code = cand

            if res.line_number and res.line_number not in patched_lines_set:
                patched_lines_set.add(res.line_number)
                lines = current_code.split('\n')
                if 1 <= res.line_number <= len(lines):
                    indent = len(lines[res.line_number - 1]) - len(lines[res.line_number - 1].lstrip())
                    if res.line_number > 1 and lines[res.line_number - 2].rstrip().endswith(':'):
                        indent = len(lines[res.line_number - 2]) - len(lines[res.line_number - 2].lstrip()) + 4
                    lines[res.line_number - 1] = (" " * indent) + "pass  # __AUTO_PATCH__"
                    current_code = '\n'.join(lines)
                else:
                    break
            else:
                if res.line_number and res.line_number in patched_lines_set:
                    lines = current_code.split('\n')
                    if 1 <= res.line_number <= len(lines) and "pass  # __AUTO_PATCH__" in lines[res.line_number - 1]:
                        lines[res.line_number - 1] = "# " + lines[res.line_number - 1]
                        current_code = '\n'.join(lines)
                        continue
                break
                
        unique_results = []
        seen = set()
        for r in results:
            if not r.success and r.line_number:
                key = (r.line_number, r.error_type)
                if key not in seen:
                    seen.add(key)
                    unique_results.append(r)
            else:
                if not any(ur.success for ur in unique_results):
                    unique_results.append(r)

        for idx, r in enumerate(unique_results, 1):
            if not r.success:
                if not r.candidate_code or r.candidate_code == code or "__AUTO_PATCH__" in (r.candidate_code or ""):
                    err_info = {
                        'error_type': r.error_type,
                        'message': r.raw_error or '',
                        'line_number': r.line_number,
                        'full_code': code,
                        'code_context': r.code_context or ''
                    }
                    ast_ctx = self.ast_extractor.analyze_error_context(err_info)
                    cand = self.agent._generate_candidate_code(code, err_info, ast_ctx)
                    if cand and cand != code:
                        r.candidate_code = cand

                card = self.pedagogical_agent.generate_diagnostic_card(
                    error_type=r.error_type or "SyntaxError",
                    code=code,
                    raw_message=r.raw_error or "",
                    language="python",
                    line_number=r.line_number,
                    column=r.column_number
                )
                if card:
                    r.friendly_explanation = card.get("pedagogical_explanation") or r.friendly_explanation
                    r.severity = card.get("severity")
                    r.underlying_concept = card.get("underlying_concept")
                    r.diagnostic_details = card.get("diagnostic_details")
                    r.changes_made = card.get("changes_made")
                    r.assumptions = card.get("assumptions")
                    r.error_id = f"py_err_{idx}"
                    r.fix_explanation = card.get("fix_explanation")

        return unique_results

    def _get_clean_code_context(self, error_info: Dict) -> str:
        """
        Extract clean code context for the AI model (no >>> markers or line numbers).

        Uses the raw source code and error line number to get a clean snippet
        matching the format the model was trained on.
        """
        full_code = error_info.get('full_code', '')
        line_number = error_info.get('line_number')

        if not line_number or not full_code:
            return error_info.get('code_context', '')

        lines = full_code.split('\n')
        # Get up to 3 lines of context around the error
        start = max(0, line_number - 2)
        end = min(len(lines), line_number + 2)
        return '\n'.join(lines[start:end]).strip()

    def _generate_ai_explanation(self, error_info: Dict,
                                 ast_context: Dict) -> ExplanationResult:
        """Generate explanation using AI model."""
        try:
            # Send clean code to the model, not the formatted display context
            clean_context = self._get_clean_code_context(error_info)

            full_explanation = self.model.generate_explanation(
                error_type=error_info['error_type'],
                error_message=error_info['message'],
                code_context=clean_context
            )

            # Parse explanation and fix
            if ' FIX: ' in full_explanation:
                parts = full_explanation.split(' FIX: ', 1)
                explanation = parts[0]
                fix = parts[1] if len(parts) > 1 else None
                
                if error_info.get('error_type') == 'NameError' and fix:
                    import re
                    match = re.search(r"name '([^']+)' is not defined", error_info.get('message', ''))
                    if match:
                        bad_name = match.group(1)
                        if f"Change '{bad_name}' to '{bad_name}'" in fix:
                            fix = self._generate_basic_fix(error_info, ast_context)
            else:
                explanation = full_explanation
                fix = self._generate_basic_fix(error_info, ast_context)

            return ExplanationResult(
                success=False,
                error_type=error_info['error_type'],
                raw_error=error_info['message'],
                friendly_explanation=explanation,
                suggested_fix=fix,
                code_context=error_info['code_context'],
                line_number=error_info['line_number'],
                similar_names=ast_context.get('similar_names', []),
                security_warnings=[]
            )

        except Exception as e:
            print(f"AI generation failed: {e}, using fallback")
            return self._generate_fallback_explanation(error_info, ast_context)

    def _generate_fallback_explanation(self, error_info: Dict,
                                       ast_context: Dict) -> ExplanationResult:
        """Generate explanation using rule-based fallback."""
        explanation = self.pedagogical_agent.generate_explanation(
            error_type=error_info.get('error_type'),
            code=error_info.get('full_code', ''),
            error_msg=error_info.get('message', '')
        )
        # Enhance with AST context
        similar = ast_context.get('similar_names', [])
        if similar:
            explanation += f" Did you mean: {', '.join(similar)}?"

        fix = self._generate_basic_fix(error_info, ast_context)

        return ExplanationResult(
            success=False,
            error_type=error_info['error_type'],
            raw_error=error_info['message'],
            friendly_explanation=explanation,
            suggested_fix=fix,
            code_context=error_info['code_context'],
            line_number=error_info['line_number'],
            similar_names=similar,
            security_warnings=[],
        )

    def _generate_basic_fix(self, error_info: Dict, ast_context: Dict) -> str:
        """Generate basic fix suggestions."""
        error_type = error_info.get('error_type')
        
        if error_type == 'NameError':
            import re
            match = re.search(r"name '([^']+)' is not defined", error_info.get('message', ''))
            if match:
                bad_name = match.group(1)
                node_type = ast_context.get('node_type')
                if node_type == 'For':
                    return f"Define '{bad_name}' before the loop, or replace it with the collection you intended to iterate over."
                else:
                    return f"Define '{bad_name}' before using it."

        suggestions = ast_context.get('suggestions', [])
        if suggestions:
            return suggestions[0]

        fix_templates = {
            'SyntaxError': "Check for missing colons, parentheses, or quotes",
            'NameError': "Verify the variable name is spelled correctly and defined",
            'TypeError': "Check type compatibility and use conversion functions",
            'IndexError': "Verify the index is within the valid range",
            'KeyError': "Use .get() method or verify the key exists"
        }

        return fix_templates.get(error_type, "Review the code at the indicated line")

    def explain_error(self, code: str) -> str:
        """
        Convenience method to get a formatted explanation string.

        Args:
            code: Python code to analyze

        Returns:
            Formatted explanation string
        """
        result = self.analyze_code(code)

        if result.success:
            output = result.friendly_explanation
            # Still show warnings even if code ran successfully
            if result.security_warnings:
                warned = [w for w in result.security_warnings if w.level == 'WARNING']
                if warned:
                    output += "\n\n⚠️  Security Notes:"
                    for w in warned:
                        output += f"\n  Line {w.line_number}: {w.message}"
            return output

        output = []

        # Show security block prominently
        if result.error_type == 'SecurityError':
            output.append("🚫 SECURITY BLOCK")
            output.append("=" * 40)
            output.append(result.friendly_explanation)
            output.append("")
            if result.suggested_fix:
                output.append(f"🔧 {result.suggested_fix}")
            output.append("")
            # Show detailed warnings
            if result.security_warnings:
                for w in result.security_warnings:
                    if w.level == 'BLOCKED':
                        output.append(f"  ❌ Line {w.line_number}: {w.message}")
                        output.append(f"     Code: {w.code_snippet}")
            return '\n'.join(output)

        output.append(f"🔴 Error Type: {result.error_type}")
        output.append(f"📍 Line:  {result.line_number}")
        output.append("")
        output.append(f"💡 Explanation: {result.friendly_explanation}")
        output.append("")

        if result.suggested_fix:
            output.append(f"🔧 Suggested Fix: {result.suggested_fix}")

        if result.similar_names:
            output.append(f"❓ Did you mean: {', '.join(result.similar_names)}?")

        # Show security warnings if any
        if result.security_warnings:
            warned = [w for w in result.security_warnings if w.level == 'WARNING']
            if warned:
                output.append("")
                output.append("⚠️  Security Notes:")
                for w in warned:
                    output.append(f"  Line {w.line_number}: {w.message}")

        output.append("")
        output.append("📄 Code Context:")
        output.append(result.code_context)

        return '\n'.join(output)

    def optimize_code(self, code: str) -> dict:
        """
        Optimize the provided code for time and space complexity.
        Returns detailed algorithmic analysis, candidate optimal code,
        and pedagogical tutoring guidance.
        """
        return self.optimizer.analyze_and_optimize(code)
