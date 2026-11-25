from src.agent.agent import SecurityAgent


def test_agent_accepts_c_cpp_java_js_and_typescript_sources():
    samples = [
        ("c", "demo.c", "int add(int a, int b) { return a+b; }"),
        ("cpp", "demo.cpp", "class Calc { public: int add(int a,int b) { return a+b; } };"),
        ("java", "Demo.java", "public class Demo { public int add(int a,int b) { return a+b; } }"),
        ("javascript", "demo.js", "function add(a,b) { return a+b; }"),
        ("typescript", "demo.ts", "function add(a:number,b:number):number { return a+b; }"),
    ]
    agent = SecurityAgent()
    for language, filename, source in samples:
        result = agent.analyze(source, language=language, filename=filename)
        assert result["success"], (language, result.get("error"))
        assert result["report"]["language"] == language
        assert result["report"]["malware_assessment"]["status"] == "no_indicators"


def test_agent_includes_malware_evidence_in_report():
    source = "import base64\npayload = base64.b64decode('YQ==')\nexec(payload)\n"
    result = SecurityAgent().analyze(source, language="python", filename="sample.py")
    assert result["success"]
    report = result["report"]
    assert report["malware_assessment"]["status"] == "high_risk"
    assert "MAL001" in report["text"]
    assert "line" in report["text"].lower()
