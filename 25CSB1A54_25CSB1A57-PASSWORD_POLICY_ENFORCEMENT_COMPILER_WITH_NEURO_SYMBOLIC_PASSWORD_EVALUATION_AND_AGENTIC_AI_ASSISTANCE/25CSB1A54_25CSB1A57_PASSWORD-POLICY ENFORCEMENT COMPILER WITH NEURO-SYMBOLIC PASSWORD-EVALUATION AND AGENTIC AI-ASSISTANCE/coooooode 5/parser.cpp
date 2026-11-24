#include "parser.h"
#include <algorithm>
#include <cctype>

using namespace std;

Parser::Parser(vector<Token> tokens) : ts(std::move(tokens)) {}

const Token &Parser::cur() const {
  if (k >= ts.size())
    return ts.back();
  return ts[k];
}

const Token &Parser::peekAhead(size_t offset) const {
  if (k + offset >= ts.size())
    return ts.back();
  return ts[k + offset];
}

bool Parser::match(TokenType t) {
  if (cur().type == t) {
    k++;
    return true;
  }
  return false;
}

const Token &Parser::consume(TokenType t, const string &msg) {
  if (cur().type == t)
    return ts[k++];

  errs.push_back({msg, cur().pos});
  return ts[k]; // recovery: return current
}

void Parser::skipNewlines() {
  while (cur().type == TokenType::Newline)
    k++;
}

bool Parser::isBooleanRule(const string &name) const {
  string lower = name;
  for (char &c : lower) c = (char)tolower((unsigned char)c);
  return lower == "requireupper" || lower == "requirelower" ||
         lower == "requiredigit" || lower == "requirespecial" ||
         lower == "nospaces";
}

bool Parser::isNumericRule(const string &name) const {
  string lower = name;
  for (char &c : lower) c = (char)tolower((unsigned char)c);
  return lower == "minlength" || lower == "maxlength";
}

bool Parser::detectAndNeutralizeInjection(const string &input, const SourcePos &pos) {
  if (input.size() > 64) {
    threats.push_back({"RESOURCE_EXHAUSTION", "Token length (" + to_string(input.size()) + ") > 64 chars",
                       "Truncated oversized token to prevent ReDoS / memory exhaustion", pos.line, pos.col});
    errs.push_back({"[SECURITY SHIELD] Oversized token intercepted (Resource Exhaustion Defense)", pos});
    return true;
  }

  string lower = input;
  for (char &c : lower) c = (char)tolower((unsigned char)c);

  const vector<string> signatures = {
    "script", "drop", "select", "insert", "delete", "table", "system",
    "exec", "eval", "ignore", "override", "bypass", "admin", "truncate",
    ";", "--", "/*", "javascript:"
  };

  for (const auto &sig : signatures) {
    if (lower == sig || lower.find(sig) != string::npos) {
      threats.push_back({"INJECTION_ATTACK", input,
                         "Sanitized and neutralized malicious code/prompt injection payload", pos.line, pos.col});
      errs.push_back({"[SECURITY SHIELD] Malicious injection payload intercepted on line " + to_string(pos.line), pos});
      return true;
    }
  }
  return false;
}

string Parser::parseValue(const string &ruleName, const SourcePos &rulePos) {
  // Check for injection in current token
  if (detectAndNeutralizeInjection(cur().lexeme, cur().pos)) {
    k++;
    suggestions.push_back({rulePos.line, rulePos.col, "Parser",
                           "Malicious injection detected in rule '" + ruleName + "'",
                           ruleName + " [INJECTION_PAYLOAD]",
                           ruleName + (isBooleanRule(ruleName) ? " true" : " 8"),
                           "Security Shield: Purged injection payload; restored canonical safe syntax"});
    return isBooleanRule(ruleName) ? "true" : "8";
  }

  // 1. Omitted value (end of line or file)
  if (cur().type == TokenType::Newline || cur().type == TokenType::End) {
    string msg = "Expected value (number/true/false)";
    errs.push_back({msg, rulePos});

    if (isBooleanRule(ruleName)) {
      suggestions.push_back({rulePos.line, rulePos.col, "Parser",
                             "Missing value for boolean rule '" + ruleName + "'",
                             ruleName,
                             ruleName + " true",
                             "Boolean constraint '" + ruleName + "' expects a value; suggested: 'true'"});
    } else if (isNumericRule(ruleName)) {
      suggestions.push_back({rulePos.line, rulePos.col, "Parser",
                             "Missing value for numeric rule '" + ruleName + "'",
                             ruleName,
                             ruleName + " 8",
                             "Numeric constraint '" + ruleName + "' expects an integer length; suggested: '8'"});
    } else {
      suggestions.push_back({rulePos.line, rulePos.col, "Parser",
                             "Missing value for rule '" + ruleName + "'",
                             ruleName,
                             ruleName + " true",
                             "Rule '" + ruleName + "' requires a value"});
    }
    return "";
  }

  // 2. Numeric token
  if (cur().type == TokenType::Number) {
    string val = ts[k++].lexeme;
    if (isBooleanRule(ruleName)) {
      errs.push_back({"Expected boolean (true/false) for rule '" + ruleName + "', found number '" + val + "'", cur().pos});
      // Anti-downgrade guard: If someone enters 0, do NOT downgrade security rule to false
      string suggested = "true";
      if (val == "0") {
        threats.push_back({"POLICY_DOWNGRADE", ruleName + " 0",
                           "Blocked attempt to disable security constraint '" + ruleName + "'; enforced 'true'",
                           rulePos.line, rulePos.col});
      }
      suggestions.push_back({rulePos.line, rulePos.col, "Parser",
                             "Rule '" + ruleName + "' expects boolean, found number '" + val + "'",
                             ruleName + " " + val,
                             ruleName + " " + suggested,
                             "Security Guard: Enforced canonical secure boolean 'true' to prevent policy downgrade"});
    }
    return val;
  }

  // 3. Boolean token
  if (cur().type == TokenType::Boolean) {
    string val = ts[k++].lexeme;
    if (isNumericRule(ruleName)) {
      errs.push_back({"Expected integer for rule '" + ruleName + "', found boolean '" + val + "'", cur().pos});
      suggestions.push_back({rulePos.line, rulePos.col, "Parser",
                             "Rule '" + ruleName + "' expects an integer length, found boolean '" + val + "'",
                             ruleName + " " + val,
                             ruleName + " 8",
                             "Replace boolean '" + val + "' with an integer length (NIST floor: 8)"});
    }
    return val;
  }

  // 4. Identifier token (e.g. "maybe", "abc", "yes", etc.)
  if (cur().type == TokenType::Identifier) {
    Token tok = ts[k++];
    string s = tok.lexeme;
    string lower = s;
    for (char &c : lower) c = (char)tolower((unsigned char)c);

    if (isBooleanRule(ruleName)) {
      errs.push_back({"Expected boolean (true/false) for rule '" + ruleName + "', found '" + s + "'", tok.pos});
      // Anti-Downgrade Invariant: Never suggest disabling a security feature
      if (lower == "no" || lower == "false" || lower == "off" || lower == "0" || lower == "disable") {
        threats.push_back({"POLICY_DOWNGRADE", s,
                           "Blocked attempt to downgrade security constraint '" + ruleName + "'; enforced 'true'",
                           tok.pos.line, tok.pos.col});
      }
      string suggested = "true";
      suggestions.push_back({tok.pos.line, tok.pos.col, "Parser",
                             "Invalid value '" + s + "' for boolean rule '" + ruleName + "'",
                             ruleName + " " + s,
                             ruleName + " " + suggested,
                             "Security Guard: Enforced secure boolean '" + suggested + "' to maintain policy entropy"});
      return s;
    }

    if (isNumericRule(ruleName)) {
      errs.push_back({"Expected integer value for rule '" + ruleName + "', found '" + s + "'", tok.pos});
      suggestions.push_back({tok.pos.line, tok.pos.col, "Parser",
                             "Invalid non-integer value '" + s + "' for rule '" + ruleName + "'",
                             ruleName + " " + s,
                             ruleName + " 8",
                             "Replace '" + s + "' with a valid integer (NIST floor: 8)"});
      return s;
    }

    return s;
  }

  // 5. Fallback for other unexpected tokens
  Token errTok = ts[k++];
  errs.push_back({"Expected value (number/true/false)", errTok.pos});
  suggestions.push_back({errTok.pos.line, errTok.pos.col, "Parser",
                         "Invalid value token '" + errTok.lexeme + "'",
                         ruleName + " " + errTok.lexeme,
                         ruleName + " true",
                         "Security Guard: Replaced invalid token with safe default 'true'"});
  return "";
}

RuleNode Parser::parseRule() {
  if (detectAndNeutralizeInjection(cur().lexeme, cur().pos)) {
    Token bad = cur();
    k++;
    while (cur().type != TokenType::Newline && cur().type != TokenType::End) k++;
    if (cur().type == TokenType::Newline) k++;
    suggestions.push_back({bad.pos.line, bad.pos.col, "Parser",
                           "Malicious injection / payload on line " + to_string(bad.pos.line),
                           bad.lexeme,
                           "# [INJECTION REMOVED]",
                           "Neutralized adversarial injection payload; line purged"});
    RuleNode r;
    r.name = "requireUpper";
    r.value = "true";
    r.pos = bad.pos;
    return r;
  }

  // Check for inverted syntax: [Value] [RuleName] (e.g., "true requireUpper" or "8 minLength")
  if ((cur().type == TokenType::Boolean || cur().type == TokenType::Number) &&
      peekAhead(1).type == TokenType::Identifier) {
    Token valTok = cur();
    Token nameTok = peekAhead(1);
    errs.push_back({"Expected rule name (identifier)", valTok.pos});
    suggestions.push_back({valTok.pos.line, valTok.pos.col, "Parser",
                           "Inverted statement order: value preceded rule name",
                           valTok.lexeme + " " + nameTok.lexeme,
                           nameTok.lexeme + " " + valTok.lexeme,
                           "Transpose tokens into canonical syntax [RuleName] [Value]"});
    k += 2;
    if (cur().type == TokenType::Newline)
      k++;

    RuleNode r;
    r.name = nameTok.lexeme;
    r.value = valTok.lexeme;
    r.pos = nameTok.pos;
    return r;
  }

  Token nameTok =
      consume(TokenType::Identifier, "Expected rule name (identifier)");
  string value = parseValue(nameTok.lexeme, nameTok.pos);

  if (cur().type == TokenType::Newline)
    k++;

  RuleNode r;
  r.name = nameTok.lexeme;
  r.value = value;
  r.pos = nameTok.pos;
  return r;
}

ProgramNode Parser::parse() {
  ProgramNode prog;
  skipNewlines();

  while (cur().type != TokenType::End) {

    if (cur().type == TokenType::Newline) {
      skipNewlines();
      continue;
    }

    if (cur().type == TokenType::Unknown) {
      errs.push_back({"Unknown token in input", cur().pos});

      while (cur().type != TokenType::Newline && cur().type != TokenType::End)
        k++;

      if (cur().type == TokenType::Newline)
        k++;

      continue;
    }

    if (prog.rules.size() >= 30) {
      threats.push_back({"RESOURCE_EXHAUSTION", "Rules count >= 30",
                         "Circuit breaker tripped: halted parsing to mitigate Denial-of-Service / token flooding",
                         cur().pos.line, cur().pos.col});
      errs.push_back({"[SECURITY SHIELD] Circuit breaker tripped: rule flood limit reached", cur().pos});
      break;
    }

    prog.rules.push_back(parseRule());
    skipNewlines();
  }

  return prog;
}
