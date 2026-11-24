#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "codegen.h"
#include "ir.h"
#include "ir_analyzer.h"
#include "lexer.h"
#include "neurosymbolic.h"
#include "parser.h"
#include "semantic.h"

using namespace std;

static string readAll(const string &path) {
  ifstream f(path);
  stringstream ss;
  ss << f.rdbuf();
  return ss.str();
}

static void printDiagnostic(const string &msg, const SourcePos &pos,
                            const vector<string> &lines) {
  // Print the error message with location
  cout << "Error at line " << pos.line << ", col " << pos.col << ": " << msg
       << "\n";

  // Print the exact line of code
  if (pos.line > 0 && static_cast<size_t>(pos.line) <= lines.size()) {
    string lineStr = lines[pos.line - 1];
    string prefix = "  " + to_string(pos.line) + " | ";
    cout << prefix << lineStr << "\n";

    // Print the caret pointing to the exact column
    int spaceCount = (int)prefix.length() + pos.col - 1;
    if (spaceCount < 0) spaceCount = 0;
    cout << string(spaceCount, ' ') << "^~~\n";
  }
}

bool validatePassword(const string &password, const PolicyConstraints &c) {
  int upper = 0, lower = 0, digit = 0, special = 0, spaces = 0;

  for (char ch : password) {
    if (isupper((unsigned char)ch))
      upper++;
    else if (islower((unsigned char)ch))
      lower++;
    else if (isdigit((unsigned char)ch))
      digit++;
    else if (isspace((unsigned char)ch))
      spaces++;
    else
      special++;
  }

  if (c.minLength != -1 && (int)password.size() < c.minLength)
    return false;
  if (c.maxLength != -1 && (int)password.size() > c.maxLength)
    return false;

  if (c.requireUpper == 1 && upper == 0)
    return false;
  if (c.requireUpper == 0 && upper > 0)
    return false;

  if (c.requireLower == 1 && lower == 0)
    return false;
  if (c.requireLower == 0 && lower > 0)
    return false;

  if (c.requireDigit == 1 && digit == 0)
    return false;
  if (c.requireDigit == 0 && digit > 0)
    return false;

  if (c.requireSpecial == 1 && special == 0)
    return false;
  if (c.requireSpecial == 0 && special > 0)
    return false;

  if (c.noSpaces == 1 && spaces > 0)
    return false;
  if (c.noSpaces == 0 && spaces == 0)
    return false;

  return true;
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    cout << "Usage: policy_compiler <policyfile>\n";
    return 0;
  }

  string path = argv[1];
  ifstream chk(path);

  if (!chk) {
    cout << "Error: cannot open file: " << path << "\n";
    return 0;
  }

  string input = readAll(path);

  // Split input into lines for diagnostic reporting
  vector<string> sourceLines;
  {
    stringstream ss(input);
    string line;
    while (getline(ss, line)) {
      if (!line.empty() && line.back() == '\r') {
        line.pop_back();
      }
      sourceLines.push_back(line);
    }
  }

  // 1. LEXICAL ANALYSIS (Standard Lexing)

  Lexer lex(input);
  auto tokens = lex.tokenize();

  if (!lex.errors().empty()) {
    cout << "\n--- LEXICAL ERRORS ---\n";
    for (const auto &e : lex.errors()) {
      printDiagnostic(e.message, e.pos, sourceLines);
      cout << "\n";
    }
    return 0;
  }

  // 2. SYNTAX ANALYSIS (with Agentic AI Error Suggestions)

  Parser parser(tokens);
  ProgramNode prog = parser.parse();

  if (!parser.errors().empty()) {
    if (!parser.getThreats().empty()) {
      cout << "\n🛡️  [AGENTIC AI SECURITY SHIELD: THREAT INTERCEPTED] 🛡️\n";
      for (const auto &t : parser.getThreats()) {
        cout << "  • THREAT [" << t.type << "] at line " << t.line << ": " << t.payload << "\n"
             << "    SHIELD DEFENSE: " << t.defense << "\n";
      }
    }

    cout << "\n--- SYNTAX ERRORS ---\n";
    for (const auto &e : parser.errors()) {
      printDiagnostic(e.message, e.pos, sourceLines);
      cout << "\n";
    }

    if (!parser.getSuggestions().empty()) {
      cout << "[AGENTIC AI SYNTAX ASSISTANT] Suggested Corrections:\n";
      for (const auto &s : parser.getSuggestions()) {
        cout << "  - Line " << s.line << ": Replace '" << s.originalText
             << "' with '" << s.suggestedText << "'\n"
             << "    AI Reasoning: " << s.explanation << "\n";
      }
    }
    return 0;
  }

  // 3. SEMANTIC ANALYSIS (with Agentic AI Typo & Conflict Suggestions)

  SemanticAnalyzer sem;
  sem.analyze(prog);

  if (!sem.errors().empty()) {
    if (!sem.getThreats().empty()) {
      cout << "\n🛡️  [AGENTIC AI SECURITY SHIELD: THREAT INTERCEPTED] 🛡️\n";
      for (const auto &t : sem.getThreats()) {
        cout << "  • THREAT [" << t.type << "] at line " << t.line << ": " << t.payload << "\n"
             << "    SHIELD DEFENSE: " << t.defense << "\n";
      }
    }

    cout << "\n--- SEMANTIC ERRORS ---\n";
    for (const auto &e : sem.errors()) {
      printDiagnostic(e.message, e.pos, sourceLines);
      cout << "\n";
    }

    if (!sem.getSuggestions().empty()) {
      cout << "[AGENTIC AI SEMANTIC ASSISTANT] Suggested Corrections:\n";
      for (const auto &s : sem.getSuggestions()) {
        cout << "  - Line " << s.line << ": Replace '" << s.originalText
             << "' with '" << s.suggestedText << "'\n"
             << "    AI Reasoning: " << s.explanation << "\n";
      }
    }
    return 0;
  }

  if (!sem.getThreats().empty()) {
    cout << "\n🛡️  [AGENTIC AI SECURITY SHIELD: ADVISORIES DETECTED & HARDENED] 🛡️\n";
    for (const auto &t : sem.getThreats()) {
      cout << "  • THREAT [" << t.type << "] at line " << t.line << ": " << t.payload << "\n"
           << "    SHIELD DEFENSE: " << t.defense << "\n";
    }
  }

  if (!sem.getAudits().empty()) {
    cout << "\n[SECURE SEMANTIC AGENT] Policy Hardening Audits:\n";
    for (const auto &a : sem.getAudits()) {
      cout << "  - Rule [" << a.rule << "]: " << a.conflict << " -> "
           << a.resolution << "\n";
    }
  }

  cout << "Policy Compiled Successfully!\n";

  const auto &c = sem.getConstraints();

  auto formatBool = [](int val) -> string {
    if (val == 1) return "true";
    if (val == 0) return "false";
    return "not set";
  };

  cout << "\nFinal Policy Constraints:\n";
  cout << "  minLength      : " << c.minLength << "\n";
  cout << "  maxLength      : " << c.maxLength << "\n";
  cout << "  requireUpper   : " << formatBool(c.requireUpper) << "\n";
  cout << "  requireLower   : " << formatBool(c.requireLower) << "\n";
  cout << "  requireDigit   : " << formatBool(c.requireDigit) << "\n";
  cout << "  requireSpecial : " << formatBool(c.requireSpecial) << "\n";
  cout << "  noSpaces       : " << formatBool(c.noSpaces) << "\n";

  // 4. IR GENERATION

  PolicyIR ir = buildIR(c);

  // 5. CODE GENERATION PHASE
  cout << "\nGenerating Target C++ Validation Program...\n";
  CodeGenerator::generate(c, "generated_validator.cpp");
  cout << "Target C++ code generated at: generated_validator.cpp\n";

  // 6. IR ANALYSIS

  auto warnings = IRAnalyzer::analyze(ir);

  if (!warnings.empty()) {
    cout << "\nIR ANALYSIS WARNINGS:\n";
    for (const auto &w : warnings) {
      cout << "  - " << w.message << "\n";
    }
  }

  // 7. NEURO-SYMBOLIC EVALUATION

  string password;
  cout << "\nEnter password to evaluate: ";
  cin >> password;

  // Step 1: Validate
  if (!validatePassword(password, c)) {
    cout << "\nPassword does NOT satisfy policy rules ❌\n";
    return 0;
  }

  // Step 2: Evaluate
  NSResult result = NeuroSymbolicEvaluator::evaluate(password, c);

  cout << "\nNeuro-Symbolic Password Evaluation:\n";
  cout << "  Score  : " << result.score << "\n";
  cout << "  Level  : " << result.level << "\n";

  return 0;
}
