#pragma once

#include <string>
#include <string_view>
#include <vector>

#include "common/diagnostic.hpp"
#include "ir/ir.hpp"

// Semantic checks that need the control-flow graph, so they run on the IR
// (before any optimization) using the data-flow framework:
//
//   reachability          code that can never run; a function that can end without returning
//   definite assignment   a variable read before it has a value on some path
//   liveness              a value that is assigned and never read (dead store)
//   call graph            recursion (Tarjan's strongly connected components), functions never called
//   value analysis        the range of every int and whether an array can be null:
//                         overflow, underflow, divide by zero, index out of bounds, null array
//
// The value analysis generalizes the four CWE checks of the earlier VulnHGNN
// project: CWE-190, CWE-191, CWE-369 and CWE-476.
namespace parc::sem {

// How many operations of one kind the value analysis looked at, and how many
// of them it could not prove safe.
struct OpCount {
    int checked = 0;   // operations of this kind in code that can run
    int at_risk = 0;   // with a warning: the compiler can say how it fails
    int possible = 0;  // with only a note: it could fail, but nothing in the code points at it
};

// The operations of one function that can fail when the program runs.
// "1 of 5 checked operations can fail" is what the vulnerability percentage means.
struct CheckedOps {
    std::string function;
    OpCount arithmetic;  // int + - * and unary minus written in the source: overflow, underflow
    OpCount division;    // int / and %: divide by zero
    OpCount access;      // a[i] and len(a): null array, index out of range
    OpCount allocation;  // new T[n]: negative size

    OpCount total() const {
        OpCount sum;
        for (const OpCount* part : {&arithmetic, &division, &access, &allocation}) {
            sum.checked += part->checked;
            sum.at_risk += part->at_risk;
            sum.possible += part->possible;
        }
        return sum;
    }
};

// What the value analysis knew, exported as ranges.json for the agent: the
// gate uses the block facts to find a fix's error path (the blocks where the
// finding's guard holds), and the claim checker uses both to decide claims
// such as "n is never 0 here" or "the caller never passes 0".

// One variable at one point: an int's range, or an array's nullness and length.
struct VarFact {
    std::string name;
    bool array = false;
    bool param = false;  // a parameter (as opposed to a local): pinned to one value, a caller chose it
    long long lo = -2147483648LL, hi = 2147483647LL;
    bool lo_widened = false, hi_widened = false;  // the bound is only there because the analysis gave up on a loop
    bool nonzero = false;                         // known not to be 0 even though [lo, hi] spans 0
    std::string null = "no";                      // arrays: "no", "yes" or "maybe"
    long long len_lo = 0, len_hi = 2147483647LL;  // arrays: the length
};

// Something a block does that a fix must not add on its error path.
struct Effect {
    std::string kind;     // "print", "call", "store", "alloc" or "return"
    int line = 0;
    std::string callee;   // call
    std::string subject;  // what is printed, stored, allocated or returned, as source text
    // return: the value is one value known when compiling (a literal, no value at all, or a
    // variable the analysis pins to a single value), so it carries nothing from the inputs.
    bool constant = false;
};

struct BlockFacts {
    int block = 0;
    std::string label;
    int line = 0;  // the first source line in the block, 0 if none
    bool reachable = false;
    std::vector<VarFact> vars;  // at the start of the block: parameters and locals of type int or array
    std::vector<Effect> effects;
};

struct FunctionFacts {
    std::string function;
    std::vector<BlockFacts> blocks;  // in block order, the same numbering as cfg.json
};

// One argument at one call: what the callee's parameter can receive from here.
struct ArgFact {
    std::string caller, callee, param, text;  // text: the argument as written
    int line = 0, col = 0, index = 0;
    VarFact value;  // value.name is the parameter's name
};

struct RangeFacts {
    std::vector<FunctionFacts> functions;
    std::vector<ArgFact> calls;  // every call to a ParC function in code that can run
};

// ranges.json: {"file", "functions": [{"name", "blocks": [...]}], "calls": [...]}
std::string ranges_json(const RangeFacts& facts, std::string_view file);

// 'checked', if given, receives one entry per function from the value analysis;
// 'ranges', if given, what it knew at each block and each call.
std::vector<Diagnostic> check_flow(const ir::Program& program, std::vector<CheckedOps>* checked = nullptr,
                                   RangeFacts* ranges = nullptr);

// The individual checks, for tests.
std::vector<Diagnostic> check_reachability(const ir::Program& program);
std::vector<Diagnostic> check_definite_assignment(const ir::Program& program);
std::vector<Diagnostic> check_dead_stores(const ir::Program& program);
std::vector<Diagnostic> check_call_graph(const ir::Program& program);
std::vector<Diagnostic> check_values(const ir::Program& program, std::vector<CheckedOps>* checked = nullptr,
                                     RangeFacts* ranges = nullptr);

}  // namespace parc::sem
