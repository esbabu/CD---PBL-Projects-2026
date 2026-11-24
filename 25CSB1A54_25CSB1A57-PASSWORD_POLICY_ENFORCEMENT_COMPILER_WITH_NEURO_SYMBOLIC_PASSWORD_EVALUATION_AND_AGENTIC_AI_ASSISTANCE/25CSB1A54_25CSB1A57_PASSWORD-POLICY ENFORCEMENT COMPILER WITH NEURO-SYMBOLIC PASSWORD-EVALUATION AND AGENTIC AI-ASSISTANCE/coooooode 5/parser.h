#ifndef PARSER_H
#define PARSER_H

#include "ast.h"
#include "token.h"
#include <string>
#include <vector>

struct ParseError {
  std::string message;
  SourcePos pos;
};

class Parser {
public:
  explicit Parser(std::vector<Token> tokens);
  ProgramNode parse();
  const std::vector<ParseError> &errors() const { return errs; }
  const std::vector<AgentSuggestion> &getSuggestions() const { return suggestions; }
  const std::vector<SecurityThreat> &getThreats() const { return threats; }

private:
  std::vector<Token> ts;
  size_t k = 0;
  std::vector<ParseError> errs;
  std::vector<AgentSuggestion> suggestions;
  std::vector<SecurityThreat> threats;

  const Token &cur() const;
  const Token &peekAhead(size_t offset) const;
  bool match(TokenType t);
  const Token &consume(TokenType t, const std::string &msg);
  void skipNewlines();

  RuleNode parseRule();
  std::string parseValue(const std::string &ruleName, const SourcePos &rulePos);
  bool isBooleanRule(const std::string &name) const;
  bool isNumericRule(const std::string &name) const;
  bool detectAndNeutralizeInjection(const std::string &input, const SourcePos &pos);
};

#endif
