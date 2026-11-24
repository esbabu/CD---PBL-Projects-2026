#ifndef SEMANTIC_H
#define SEMANTIC_H

#include "ast.h"
#include <string>
#include <vector>

struct SemanticError {
  std::string message;
  SourcePos pos;
};

struct PolicyConstraints {
  int minLength = -1;
  int maxLength = -1;
  int requireUpper = -1;
  int requireLower = -1;
  int requireDigit = -1;
  int requireSpecial = -1;
  int noSpaces = -1;
};

struct AgentSemanticAudit {
  std::string rule;
  std::string conflict;
  std::string resolution;
};

class SemanticAnalyzer {
  std::vector<SemanticError> errs;
  PolicyConstraints constraints;
  std::vector<AgentSemanticAudit> audits;
  std::vector<AgentSuggestion> suggestions;
  std::vector<SecurityThreat> threats;

public:
  const std::vector<AgentSemanticAudit> &getAudits() const { return audits; }
  const std::vector<AgentSuggestion> &getSuggestions() const { return suggestions; }
  const std::vector<SecurityThreat> &getThreats() const { return threats; }
  void analyze(const ProgramNode &prog);

  const std::vector<SemanticError> &errors() const { return errs; }
  const PolicyConstraints &getConstraints() const { return constraints; }
};

#endif
