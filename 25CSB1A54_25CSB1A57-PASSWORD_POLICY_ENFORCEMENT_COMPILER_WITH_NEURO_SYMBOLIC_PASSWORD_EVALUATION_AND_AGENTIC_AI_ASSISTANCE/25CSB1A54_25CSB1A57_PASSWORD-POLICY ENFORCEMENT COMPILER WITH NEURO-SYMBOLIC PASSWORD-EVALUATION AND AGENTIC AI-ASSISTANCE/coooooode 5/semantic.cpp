#include "semantic.h"
#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

// Levenshtein Distance for Typo Correction
static int levenshteinDistance(const string &s1, const string &s2) {
  const size_t len1 = s1.size(), len2 = s2.size();
  vector<vector<int>> d(len1 + 1, vector<int>(len2 + 1));
  for (size_t i = 0; i <= len1; ++i)
    d[i][0] = (int)i;
  for (size_t j = 0; j <= len2; ++j)
    d[0][j] = (int)j;

  for (size_t i = 1; i <= len1; ++i) {
    for (size_t j = 1; j <= len2; ++j) {
      int cost = (tolower((unsigned char)s1[i - 1]) == tolower((unsigned char)s2[j - 1])) ? 0 : 1;
      d[i][j] = min({d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost});
    }
  }
  return d[len1][len2];
}

static string suggestRule(const string &typo) {
  // Security Guard: Prevent ReDoS / quadratic compute exhaustion on oversized identifiers
  if (typo.size() > 32) {
    return "";
  }

  vector<string> validRules = {"minLength",    "maxLength",    "requireUpper",
                               "requireLower", "requireDigit", "requireSpecial",
                               "noSpaces"};

  string bestMatch = "";
  int minDistance = 4; // Tolerance threshold

  for (const auto &rule : validRules) {
    int dist = levenshteinDistance(typo, rule);
    if (dist < minDistance) {
      minDistance = dist;
      bestMatch = rule;
    }
  }
  return bestMatch;
}

void SemanticAnalyzer::analyze(const ProgramNode &prog) {
  unordered_map<string, SourcePos> seenRules;

  // Pre-scan to discover explicit maxLength if defined
  int explicitMax = -1;
  for (const auto &r : prog.rules) {
    if (r.name == "maxLength") {
      try {
        if (r.value.size() <= 6) {
          explicitMax = stoi(r.value);
        }
      } catch (...) {}
    }
  }

  int duplicateCount = 0;

  for (const auto &rule : prog.rules) {
    // Check for duplicate rules with circuit breaker
    if (seenRules.count(rule.name)) {
      duplicateCount++;
      if (duplicateCount > 5) {
        threats.push_back({"RESOURCE_EXHAUSTION", "Excessive duplicate rules",
                           "Circuit breaker: Suppressed duplicate rule flood to prevent DoS",
                           rule.pos.line, rule.pos.col});
        continue;
      }
      errs.push_back({"Duplicate rule definition: '" + rule.name + "'", rule.pos});
      audits.push_back({rule.name, "Duplicate rule definition",
                        "Flagged conflict with previous definition at line " +
                            to_string(seenRules[rule.name].line)});
      suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                             "Duplicate rule definition for '" + rule.name + "'",
                             rule.name + " " + rule.value,
                             "",
                             "Remove redundant re-definition on line " + to_string(rule.pos.line)});
      continue;
    }
    seenRules[rule.name] = rule.pos;

    if (rule.name == "minLength") {
      // Security Check: Integer overflow / underflow defense
      if (rule.value.size() > 5 || (!rule.value.empty() && rule.value[0] == '-')) {
        threats.push_back({"OVERFLOW_ATTACK", rule.name + " " + rule.value,
                           "Sanitized integer overflow/underflow; clamped to NIST baseline [8, 128]",
                           rule.pos.line, rule.pos.col});
        errs.push_back({"[SECURITY SHIELD] Integer overflow/underflow detected in minLength", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Integer overflow/underflow in minLength: '" + rule.value + "'",
                               rule.name + " " + rule.value,
                               "minLength 8",
                               "Security Guard: Clamped integer to NIST baseline 8 to prevent memory corruption"});
        constraints.minLength = 8;
        continue;
      }

      int val = 0;
      try {
        val = stoi(rule.value);
      } catch (...) {
        errs.push_back({"minLength must be a valid integer", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "minLength must be an integer",
                               rule.name + " " + rule.value,
                               "minLength 8",
                               "Set minLength to an integer (e.g. 8)"});
        continue;
      }

      if (val < 8) {
        if (explicitMax != -1 && explicitMax < 8) {
          threats.push_back({"POLICY_DOWNGRADE", "minLength " + to_string(val),
                             "Zero-Trust Guardrail: Prevented policy weakening below NIST 800-63B standard (8 chars)",
                             rule.pos.line, rule.pos.col});
          audits.push_back(
              {"minLength", "Value (" + to_string(val) + ") < 8 NIST floor",
               "Zero-Trust Advisory: Retained " + to_string(val) +
                   " to preserve consistency with maxLength (" +
                   to_string(explicitMax) + ")"});
          constraints.minLength = val;
        } else {
          threats.push_back({"POLICY_DOWNGRADE", "minLength " + to_string(val),
                             "Zero-Trust Guardrail: Prevented policy weakening below NIST 800-63B standard (8 chars)",
                             rule.pos.line, rule.pos.col});
          errs.push_back({"[SECURITY SHIELD] Insecure minimum password length (" + to_string(val) + " < 8) violates NIST SP 800-63B", rule.pos});
          suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                                 "Insecure minimum password length (" + to_string(val) + " < 8)",
                                 rule.name + " " + rule.value,
                                 "minLength 8",
                                 "Security Guard: Upgrade minLength to 8 to satisfy NIST SP 800-63B"});
          constraints.minLength = 8;
        }
      } else {
        constraints.minLength = val;
      }
    } else if (rule.name == "maxLength") {
      // Security Check: Integer overflow / underflow defense
      if (rule.value.size() > 5 || (!rule.value.empty() && rule.value[0] == '-')) {
        threats.push_back({"OVERFLOW_ATTACK", rule.name + " " + rule.value,
                           "Sanitized integer overflow/underflow; clamped maxLength to 128",
                           rule.pos.line, rule.pos.col});
        errs.push_back({"[SECURITY SHIELD] Integer overflow/underflow detected in maxLength", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Integer overflow/underflow in maxLength: '" + rule.value + "'",
                               rule.name + " " + rule.value,
                               "maxLength 64",
                               "Security Guard: Clamped integer to safe buffer limit 64"});
        constraints.maxLength = 64;
        continue;
      }

      int val = 0;
      try {
        val = stoi(rule.value);
      } catch (...) {
        errs.push_back({"maxLength must be a valid integer", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "maxLength must be an integer",
                               rule.name + " " + rule.value,
                               "maxLength 32",
                               "Set maxLength to an integer (e.g. 32)"});
        continue;
      }

      if (val > 128) {
        audits.push_back({"maxLength", "Value (" + to_string(val) + ") > 128",
                          "Capped to 128 for buffer security"});
        constraints.maxLength = 128;
      } else {
        constraints.maxLength = val;
      }
    }

    else if (rule.name == "requireUpper") {
      if (rule.value == "false") {
        threats.push_back({"POLICY_DOWNGRADE", "requireUpper false",
                           "Adversarial weakening: Attempted to disable uppercase entropy requirement",
                           rule.pos.line, rule.pos.col});
        errs.push_back({"[SECURITY SHIELD] Disabling 'requireUpper' violates Zero-Trust entropy standards", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Adversarial weakening: requireUpper disabled",
                               rule.name + " false",
                               rule.name + " true",
                               "Security Advisory: Enable requireUpper to comply with Zero-Trust entropy standards"});
      }
      constraints.requireUpper = (rule.value == "true" ? 1 : 0);
    }

    else if (rule.name == "requireLower") {
      if (rule.value == "false") {
        threats.push_back({"POLICY_DOWNGRADE", "requireLower false",
                           "Adversarial weakening: Attempted to disable lowercase entropy requirement",
                           rule.pos.line, rule.pos.col});
        errs.push_back({"[SECURITY SHIELD] Disabling 'requireLower' violates Zero-Trust entropy standards", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Adversarial weakening: requireLower disabled",
                               rule.name + " false",
                               rule.name + " true",
                               "Security Advisory: Enable requireLower to comply with Zero-Trust entropy standards"});
      }
      constraints.requireLower = (rule.value == "true" ? 1 : 0);
    }

    else if (rule.name == "requireDigit") {
      if (rule.value == "false") {
        threats.push_back({"POLICY_DOWNGRADE", "requireDigit false",
                           "Adversarial weakening: Attempted to disable numeric digit requirement",
                           rule.pos.line, rule.pos.col});
        errs.push_back({"[SECURITY SHIELD] Disabling 'requireDigit' violates Zero-Trust entropy standards", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Adversarial weakening: requireDigit disabled",
                               rule.name + " false",
                               rule.name + " true",
                               "Security Advisory: Enable requireDigit to comply with Zero-Trust entropy standards"});
      }
      constraints.requireDigit = (rule.value == "true" ? 1 : 0);
    }

    else if (rule.name == "requireSpecial") {
      if (rule.value == "false") {
        threats.push_back({"POLICY_DOWNGRADE", "requireSpecial false",
                           "Adversarial weakening: Attempted to disable special character requirement",
                           rule.pos.line, rule.pos.col});
        errs.push_back({"[SECURITY SHIELD] Disabling 'requireSpecial' violates Zero-Trust entropy standards", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Adversarial weakening: requireSpecial disabled",
                               rule.name + " false",
                               rule.name + " true",
                               "Security Advisory: Enable requireSpecial to comply with Zero-Trust entropy standards"});
      }
      constraints.requireSpecial = (rule.value == "true" ? 1 : 0);
    }

    else if (rule.name == "noSpaces") {
      if (rule.value == "false") {
        threats.push_back({"POLICY_DOWNGRADE", "noSpaces false",
                           "Adversarial weakening: Allowed spaces in passwords",
                           rule.pos.line, rule.pos.col});
      }
      constraints.noSpaces = (rule.value == "true" ? 1 : 0);
    }

    else {
      if (rule.name.size() > 32) {
        threats.push_back({"RESOURCE_EXHAUSTION", "Oversized identifier: '" + rule.name.substr(0, 16) + "...' (" + to_string(rule.name.size()) + " chars)",
                           "Shed compute load: skipped quadratic distance evaluation; truncated ReDoS token",
                           rule.pos.line, rule.pos.col});
        string targetRule = "requireDigit";
        string lower = rule.name;
        for (char &c : lower) c = (char)tolower((unsigned char)c);
        if (lower.find("upper") != string::npos) targetRule = "requireUpper";
        else if (lower.find("lower") != string::npos) targetRule = "requireLower";
        else if (lower.find("digit") != string::npos) targetRule = "requireDigit";
        else if (lower.find("special") != string::npos) targetRule = "requireSpecial";
        else if (lower.find("length") != string::npos) targetRule = "minLength";

        errs.push_back({"[SECURITY SHIELD] Oversized identifier token (" + to_string(rule.name.size()) + " chars) intercepted (ReDoS defense)", rule.pos});
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Oversized ReDoS token (" + to_string(rule.name.size()) + " chars)",
                               rule.name + " " + rule.value,
                               targetRule + " " + rule.value,
                               "Security Guard: Truncated oversized ReDoS token and restored canonical rule '" + targetRule + "'"});
        continue;
      }

      string msg = "Unknown rule: '" + rule.name + "'";
      string suggestion = suggestRule(rule.name);
      if (!suggestion.empty()) {
        msg += ". Did you mean '" + suggestion + "'?";
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Unrecognized rule name with likely typo: '" + rule.name + "'",
                               rule.name + " " + rule.value,
                               suggestion + " " + rule.value,
                               "Correct typo to nearest valid rule '" + suggestion + "'"});
      } else {
        suggestions.push_back({rule.pos.line, rule.pos.col, "Semantic",
                               "Unrecognized policy keyword '" + rule.name + "'",
                               rule.name + " " + rule.value,
                               "# " + rule.name + " " + rule.value,
                               "Comment out unrecognized policy rule"});
      }
      errs.push_back({msg, rule.pos});
    }
  }

  // Auto-harden noSpaces if omitted
  if (constraints.noSpaces == -1) {
    audits.push_back(
        {"noSpaces", "Omitted rule", "Auto-hardened: noSpaces = true"});
    constraints.noSpaces = 1;
  }

  // Logical conflict check
  if (constraints.minLength != -1 && constraints.maxLength != -1 &&
      constraints.minLength > constraints.maxLength) {
    errs.push_back({"minLength cannot be greater than maxLength", {0, 0}});
    suggestions.push_back({0, 0, "Semantic",
                           "Logical conflict: minLength (" + to_string(constraints.minLength) +
                               ") cannot exceed maxLength (" + to_string(constraints.maxLength) + ")",
                           "minLength " + to_string(constraints.minLength),
                           "minLength " + to_string(min(8, constraints.maxLength)),
                           "Adjust minLength <= maxLength"});
  }
}
