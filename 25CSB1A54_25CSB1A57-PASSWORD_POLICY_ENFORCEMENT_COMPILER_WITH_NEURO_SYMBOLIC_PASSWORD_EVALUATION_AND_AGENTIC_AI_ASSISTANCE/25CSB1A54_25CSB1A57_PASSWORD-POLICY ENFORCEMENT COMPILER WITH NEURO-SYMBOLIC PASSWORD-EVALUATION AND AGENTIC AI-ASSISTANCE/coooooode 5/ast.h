#ifndef AST_H
#define AST_H

#include "token.h"
#include <string>
#include <vector>

struct RuleNode {
    std::string name;
    std::string value;
    SourcePos pos;
};

struct ProgramNode {
    std::vector<RuleNode> rules;
};

struct AgentSuggestion {
    int line = 0;
    int col = 0;
    std::string phase;           // "Parser" or "Semantic"
    std::string issue;           // What went wrong
    std::string originalText;    // What was written
    std::string suggestedText;   // Recommended replacement
    std::string explanation;     // AI reasoning for the user
};

struct SecurityThreat {
    std::string type;        // "INJECTION_ATTACK", "POLICY_DOWNGRADE", "RESOURCE_EXHAUSTION", "OVERFLOW_ATTACK"
    std::string payload;     // Malicious input detected
    std::string defense;     // Security guard action taken
    int line = 0;
    int col = 0;
};

#endif
