#include "llvm/IR/PassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/GlobalVariable.h"
#include "llvm/IR/CFG.h"
#include "llvm/IR/Dominators.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/ErrorHandling.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/JSON.h"
#include "llvm/Support/Error.h"

#include <cmath>
#include <cctype>
#include <algorithm>
#include <fstream>
#include <queue>
#include <set>
#include <string>
#include <vector>

using namespace llvm;

namespace {

static bool isInList(StringRef Name, std::initializer_list<StringRef> Names) {
    for (StringRef N : Names) {
        if (Name == N) {
            return true;
        }
    }
    return false;
}

static bool isNameMatch(StringRef Name,
                        std::initializer_list<StringRef> AllowedNames) {
    for (StringRef N : AllowedNames) {
        if (Name == N) {
            return true;
        }
    }
    return false;
}

static std::string blockNameOrFallback(const BasicBlock *BB) {
    if (!BB) {
        return "<null-bb>";
    }

    if (BB->hasName()) {
        return BB->getName().str();
    }

    return "<unnamed-bb>";
}

static std::string instructionSite(const Instruction *I) {
    std::string S;
    raw_string_ostream OS(S);

    OS << "bb=" << blockNameOrFallback(I ? I->getParent() : nullptr) << " | inst=";
    if (I) {
        I->print(OS);
    } else {
        OS << "<null-inst>";
    }
    return OS.str();
}

static bool blockReachesTarget(BasicBlock *Start, BasicBlock *Target) {
    if (!Start || !Target) {
        return false;
    }

    if (Start == Target) {
        return true;
    }

    SmallPtrSet<BasicBlock *, 32> Visited;
    std::queue<BasicBlock *> Q;
    Visited.insert(Start);
    Q.push(Start);

    while (!Q.empty()) {
        BasicBlock *BB = Q.front();
        Q.pop();

        for (BasicBlock *Succ : successors(BB)) {
            if (Succ == Target) {
                return true;
            }
            if (Visited.insert(Succ).second) {
                Q.push(Succ);
            }
        }
    }

    return false;
}

static bool valueDerivedFrom(Value *V, const Value *Target,
                             SmallPtrSetImpl<const Value *> &Visited) {
    if (!V) {
        return false;
    }

    V = V->stripPointerCasts();

    if (V == Target) {
        return true;
    }

    if (!Visited.insert(V).second) {
        return false;
    }

    if (auto *LI = dyn_cast<LoadInst>(V)) {
        return valueDerivedFrom(LI->getPointerOperand(), Target, Visited);
    }

    if (auto *GEP = dyn_cast<GetElementPtrInst>(V)) {
        return valueDerivedFrom(GEP->getPointerOperand(), Target, Visited);
    }

    if (auto *Cast = dyn_cast<CastInst>(V)) {
        return valueDerivedFrom(Cast->getOperand(0), Target, Visited);
    }

    if (auto *AI = dyn_cast<AllocaInst>(V)) {
        // At -O0, function args are commonly stored to allocas and later reloaded.
        for (User *U : AI->users()) {
            auto *SI = dyn_cast<StoreInst>(U);
            if (!SI || SI->getPointerOperand() != AI) {
                continue;
            }

            if (valueDerivedFrom(SI->getValueOperand(), Target, Visited)) {
                return true;
            }
        }
    }

    if (auto *PHI = dyn_cast<PHINode>(V)) {
        for (Value *Incoming : PHI->incoming_values()) {
            if (valueDerivedFrom(Incoming, Target, Visited)) {
                return true;
            }
        }
        return false;
    }

    if (auto *Sel = dyn_cast<SelectInst>(V)) {
        return valueDerivedFrom(Sel->getTrueValue(), Target, Visited) ||
               valueDerivedFrom(Sel->getFalseValue(), Target, Visited);
    }

    if (auto *CI = dyn_cast<CallInst>(V)) {
        for (Value *Arg : CI->args()) {
            if (valueDerivedFrom(Arg, Target, Visited)) {
                return true;
            }
        }
    }

    return false;
}

static bool isPkgDerived(Value *V, Value *PkgArg) {
    SmallPtrSet<const Value *, 32> Visited;
    return valueDerivedFrom(V, PkgArg, Visited);
}

static bool isCurrentVersionDerivedImpl(Value *V,
                                        SmallPtrSetImpl<const Value *> &Visited) {

    if (!V) {
        return false;
    }

    V = V->stripPointerCasts();

    if (auto *GV = dyn_cast<GlobalVariable>(V)) {
        StringRef GVName = GV->getName();
        return GVName == "current_version" || GVName.contains("current_version") || GVName == "s_firmware_version";
    }

    if (auto *CI = dyn_cast<CallInst>(V)) {
        Function *Callee = CI->getCalledFunction();
        if (!Callee) {
            Callee = dyn_cast<Function>(CI->getCalledOperand()->stripPointerCasts());
        }
        if (Callee && (Callee->getName() == "get_current_firmware_version" ||
                       Callee->getName() == "get_current_version" ||
                       Callee->getName() == "read_nvram_version")) {
            return true;
        }
    }

    if (!Visited.insert(V).second) {
        return false;
    }

    if (auto *AI = dyn_cast<AllocaInst>(V)) {
        for (User *U : AI->users()) {
            auto *SI = dyn_cast<StoreInst>(U);
            if (!SI || SI->getPointerOperand() != AI) {
                continue;
            }
            if (isCurrentVersionDerivedImpl(SI->getValueOperand(), Visited)) {
                return true;
            }
        }
    }

    if (auto *LI = dyn_cast<LoadInst>(V)) {
        return isCurrentVersionDerivedImpl(LI->getPointerOperand(), Visited);
    }

    if (auto *GEP = dyn_cast<GetElementPtrInst>(V)) {
        return isCurrentVersionDerivedImpl(GEP->getPointerOperand(), Visited);
    }

    if (auto *Cast = dyn_cast<CastInst>(V)) {
        return isCurrentVersionDerivedImpl(Cast->getOperand(0), Visited);
    }

    if (auto *PHI = dyn_cast<PHINode>(V)) {
        for (Value *Incoming : PHI->incoming_values()) {
            if (isCurrentVersionDerivedImpl(Incoming, Visited)) {
                return true;
            }
        }
        return false;
    }

    if (auto *Sel = dyn_cast<SelectInst>(V)) {
        return isCurrentVersionDerivedImpl(Sel->getTrueValue(), Visited) ||
               isCurrentVersionDerivedImpl(Sel->getFalseValue(), Visited);
    }

    return false;
}

static bool isCurrentVersionDerived(Value *V) {
    SmallPtrSet<const Value *, 32> Visited;
    return isCurrentVersionDerivedImpl(V, Visited);
}

static bool hasRollbackGuardBeforeInstall(Function &F, DominatorTree &DT,
                                          Instruction *InstallI) {
    auto *InstallCall = dyn_cast<CallInst>(InstallI);
    if (!InstallCall || InstallCall->arg_size() == 0) {
        return false;
    }

    Value *PkgArg = InstallCall->getArgOperand(0)->stripPointerCasts();
    BasicBlock *InstallBB = InstallI->getParent();

    for (BasicBlock &BB : F) {
        for (Instruction &I : BB) {
            auto *Cmp = dyn_cast<ICmpInst>(&I);
            if (!Cmp) {
                continue;
            }

            if (!DT.dominates(Cmp, InstallI)) {
                continue;
            }

            Value *LHS = Cmp->getOperand(0);
            Value *RHS = Cmp->getOperand(1);

            bool PkgL = isPkgDerived(LHS, PkgArg);
            bool CurR = isCurrentVersionDerived(RHS);
            bool CurL = isCurrentVersionDerived(LHS);
            bool PkgR = isPkgDerived(RHS, PkgArg);

            // Fallback for common IR shapes where compare value traces to another
            // function argument aliasing the package pointer (through allocas).
            if (!PkgL) {
                for (Argument &A : F.args()) {
                    if (A.getType()->isPointerTy() && isPkgDerived(LHS, &A)) {
                        PkgL = true;
                        break;
                    }
                }
            }

            if (!PkgR) {
                for (Argument &A : F.args()) {
                    if (A.getType()->isPointerTy() && isPkgDerived(RHS, &A)) {
                        PkgR = true;
                        break;
                    }
                }
            }

            ICmpInst::Predicate Pred = Cmp->getPredicate();

            for (User *U : Cmp->users()) {
                auto *Br = dyn_cast<BranchInst>(U);
                if (!Br || !Br->isConditional() || Br->getCondition() != Cmp) {
                    continue;
                }

                BasicBlock *TrueSucc = Br->getSuccessor(0);
                BasicBlock *FalseSucc = Br->getSuccessor(1);
                bool TrueReachesInstall = blockReachesTarget(TrueSucc, InstallBB);
                bool FalseReachesInstall = blockReachesTarget(FalseSucc, InstallBB);

                if (PkgL && CurR) {
                    bool DirectStrictGT =
                        (Pred == ICmpInst::ICMP_SGT || Pred == ICmpInst::ICMP_UGT) &&
                        TrueReachesInstall && !FalseReachesInstall;

                    bool RejectLEThenInstall =
                        (Pred == ICmpInst::ICMP_SLE || Pred == ICmpInst::ICMP_ULE) &&
                        FalseReachesInstall && !TrueReachesInstall;

                    if (DirectStrictGT || RejectLEThenInstall) {
                        return true;
                    }
                }

                if (CurL && PkgR) {
                    bool DirectStrictGT =
                        (Pred == ICmpInst::ICMP_SLT || Pred == ICmpInst::ICMP_ULT) &&
                        TrueReachesInstall && !FalseReachesInstall;

                    bool RejectGEThenInstall =
                        (Pred == ICmpInst::ICMP_SGE || Pred == ICmpInst::ICMP_UGE) &&
                        FalseReachesInstall && !TrueReachesInstall;

                    if (DirectStrictGT || RejectGEThenInstall) {
                        return true;
                    }
                }
            }
        }
    }

    return false;
}

struct SecurityPolicy {
    std::string name = "Original Protocol (Full Security)";
    bool checkSignature = true;
    bool checkSource = true;
    bool checkRollback = true;
    bool checkLogging = true;
    bool checkWeakCrypto = true;
    bool checkBannedFunctions = true;
    bool checkSecrets = true;
    bool checkImageHash = true;
    std::vector<std::string> bannedFunctionsList = {
        "strcpy", "strcat", "sprintf", "vsprintf", "gets", "gets_s", "system"
    };

    static SecurityPolicy load() {
        SecurityPolicy Policy;
        const char *PolicyPath = std::getenv("OTA_POLICY_FILE");
        if (!PolicyPath || std::string(PolicyPath).empty()) {
            return Policy;
        }

        std::ifstream File(PolicyPath);
        if (!File.is_open()) {
            return Policy;
        }

        std::string Content((std::istreambuf_iterator<char>(File)),
                            std::istreambuf_iterator<char>());

        auto Parsed = llvm::json::parse(Content);
        if (!Parsed) {
            llvm::consumeError(Parsed.takeError());
            return Policy;
        }

        auto *Obj = Parsed->getAsObject();
        if (!Obj) {
            return Policy;
        }

        if (auto NameVal = Obj->getString("name")) {
            Policy.name = NameVal->str();
        }

        if (auto *Rules = Obj->getObject("rules")) {
            if (auto V = Rules->getBoolean("signature_verification")) {
                Policy.checkSignature = *V;
            }
            if (auto V = Rules->getBoolean("source_trust")) {
                Policy.checkSource = *V;
            }
            if (auto V = Rules->getBoolean("rollback_guard")) {
                Policy.checkRollback = *V;
            }
            if (auto V = Rules->getBoolean("banned_logging")) {
                Policy.checkLogging = *V;
            }
            if (auto V = Rules->getBoolean("weak_crypto")) {
                Policy.checkWeakCrypto = *V;
            }
            if (auto V = Rules->getBoolean("banned_memory_functions")) {
                Policy.checkBannedFunctions = *V;
            }
            if (auto V = Rules->getBoolean("banned_functions")) {
                Policy.checkBannedFunctions = *V;
            }
            if (auto V = Rules->getBoolean("secret_detection")) {
                Policy.checkSecrets = *V;
            }
            if (auto V = Rules->getBoolean("hardcoded_secrets")) {
                Policy.checkSecrets = *V;
            }
            if (auto V = Rules->getBoolean("image_hash_verification")) {
                Policy.checkImageHash = *V;
            }
            if (auto V = Rules->getBoolean("hash_dominance")) {
                Policy.checkImageHash = *V;
            }
            if (auto V = Rules->getBoolean("check_image_hash")) {
                Policy.checkImageHash = *V;
            }
        }

        if (auto *Arr = Obj->getArray("banned_functions_list")) {
            Policy.bannedFunctionsList.clear();
            for (const auto &Val : *Arr) {
                if (auto S = Val.getAsString()) {
                    Policy.bannedFunctionsList.push_back(S->str());
                }
            }
        }

        return Policy;
    }
};

static bool isHexChar(char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

static bool isBase64Char(char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
           c == '+' || c == '/' || c == '=' || c == '-' || c == '_';
}

static double calculateShannonEntropy(StringRef S) {
    if (S.empty()) return 0.0;
    unsigned Freq[256] = {0};
    for (unsigned char c : S) {
        Freq[c]++;
    }
    double Entropy = 0.0;
    double Len = static_cast<double>(S.size());
    for (unsigned count : Freq) {
        if (count > 0) {
            double p = static_cast<double>(count) / Len;
            Entropy -= p * std::log2(p);
        }
    }
    return Entropy;
}

static bool detectSecretInString(StringRef Str, std::string &SecretKind) {
    // 1. PEM Private Key Headers
    static const char *const PemHeaders[] = {
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN RSA PRIVATE KEY-----",
        "-----BEGIN EC PRIVATE KEY-----",
        "-----BEGIN OPENSSH PRIVATE KEY-----",
        "-----BEGIN PGP PRIVATE KEY-----",
        "-----BEGIN ENCRYPTED PRIVATE KEY-----"
    };
    for (const char *H : PemHeaders) {
        if (Str.contains(H)) {
            SecretKind = std::string("private key marker '") + H + "'";
            return true;
        }
    }

    // 2. Known Token & Credential Prefixes (case-insensitive)
    std::string Lower = Str.lower();
    static const char *const Prefixes[] = {
        "ghp_",
        "bearer ",
        "eyjh",
        "api_key=",
        "apikey=",
        "api-key=",
        "secret=",
        "secret_key=",
        "aws_secret_access_key"
    };
    for (const char *P : Prefixes) {
        if (StringRef(Lower).contains(P)) {
            SecretKind = std::string("credential token prefix '") + P + "'";
            return true;
        }
    }

    // 3. Shannon Entropy Check on candidate continuous tokens
    size_t Start = 0;
    while (Start < Str.size()) {
        while (Start < Str.size() && (isspace(Str[Start]) || Str[Start] == '\0' || Str[Start] == '"' || Str[Start] == '\'' ||
                                      Str[Start] == ';' || Str[Start] == ',' || Str[Start] == '=' ||
                                      Str[Start] == '{' || Str[Start] == '}' || Str[Start] == '(' ||
                                      Str[Start] == ')')) {
            Start++;
        }
        if (Start >= Str.size()) break;
        size_t End = Start;
        while (End < Str.size() && !isspace(Str[End]) && Str[End] != '\0' && Str[End] != '"' && Str[End] != '\'' &&
               Str[End] != ';' && Str[End] != ',' && Str[End] != '=' && Str[End] != '{' &&
               Str[End] != '}' && Str[End] != '(' && Str[End] != ')') {
            End++;
        }
        StringRef Token = Str.slice(Start, End).rtrim('\0');
        Start = End;

        if (Token.size() >= 32) {
            bool allHex = true;
            bool allBase64 = true;
            unsigned digitCount = 0;
            unsigned upperCount = 0;
            unsigned lowerCount = 0;

            for (char c : Token) {
                if (!isHexChar(c)) allHex = false;
                if (!isBase64Char(c)) allBase64 = false;
                if (isdigit(c)) digitCount++;
                if (isupper(c)) upperCount++;
                if (islower(c)) lowerCount++;
            }

            double Entropy = calculateShannonEntropy(Token);

            if (allHex && Token.size() >= 32 && digitCount >= 2 && (lowerCount >= 2 || upperCount >= 2)) {
                if (Entropy >= 3.2) {
                    SecretKind = "high-entropy hex secret (entropy=" + std::to_string(Entropy).substr(0, 4) + ")";
                    return true;
                }
            } else if (allBase64 && Token.size() >= 32 && digitCount >= 1 && upperCount >= 1 && lowerCount >= 1) {
                if (Entropy >= 4.4) {
                    SecretKind = "high-entropy credential token (entropy=" + std::to_string(Entropy).substr(0, 4) + ")";
                    return true;
                }
            }
        }
    }

    return false;
}

static void collectStringsFromConstant(const Constant *C,
                                      std::vector<std::string> &Strings,
                                      SmallPtrSetImpl<const Constant *> &Visited) {
    if (!C || !Visited.insert(C).second)
        return;

    if (const auto *CDS = dyn_cast<ConstantDataSequential>(C)) {
        if (CDS->isString()) {
            Strings.push_back(CDS->getAsString().rtrim('\0').str());
            return;
        }
        if (CDS->getElementType()->isIntegerTy(8)) {
            StringRef Raw = CDS->getRawDataValues();
            Strings.push_back(Raw.rtrim('\0').str());
            return;
        }
    }

    if (const auto *CE = dyn_cast<ConstantExpr>(C)) {
        for (unsigned i = 0; i < CE->getNumOperands(); ++i) {
            if (const auto *OpC = dyn_cast<Constant>(CE->getOperand(i))) {
                collectStringsFromConstant(OpC, Strings, Visited);
            }
        }
        return;
    }

    if (const auto *CA = dyn_cast<ConstantAggregate>(C)) {
        for (unsigned i = 0; i < CA->getNumOperands(); ++i) {
            if (const auto *OpC = dyn_cast<Constant>(CA->getOperand(i))) {
                collectStringsFromConstant(OpC, Strings, Visited);
            }
        }
        return;
    }

    if (const auto *GV = dyn_cast<GlobalVariable>(C)) {
        if (GV->hasInitializer()) {
            collectStringsFromConstant(GV->getInitializer(), Strings, Visited);
        }
        return;
    }
}

static std::string getDescriptiveGlobalName(const GlobalVariable &GV) {
    StringRef Name = GV.getName();
    if (Name.starts_with(".str")) {
        for (const User *U : GV.users()) {
            if (const auto *UserGV = dyn_cast<GlobalVariable>(U)) {
                if (!UserGV->getName().starts_with(".str")) {
                    return UserGV->getName().str();
                }
            } else if (const auto *CE = dyn_cast<ConstantExpr>(U)) {
                for (const User *CEU : CE->users()) {
                    if (const auto *UserGV = dyn_cast<GlobalVariable>(CEU)) {
                        if (!UserGV->getName().starts_with(".str")) {
                            return UserGV->getName().str();
                        }
                    }
                }
            } else if (const auto *I = dyn_cast<Instruction>(U)) {
                if (const Function *F = I->getFunction()) {
                    return ".str in function '" + F->getName().str() + "'";
                }
            }
        }
    }
    return Name.str();
}

static void scanModuleSecrets(Module &M, std::vector<std::string> &Violations) {
    SmallPtrSet<const Constant *, 32> VisitedConstants;
    std::set<std::string> ReportedVars;

    for (const GlobalVariable &GV : M.globals()) {
        if (!GV.hasInitializer()) {
            continue;
        }

        const Constant *Init = GV.getInitializer();
        std::vector<std::string> Strings;
        collectStringsFromConstant(Init, Strings, VisitedConstants);

        for (const std::string &S : Strings) {
            std::string SecretKind;
            if (detectSecretInString(S, SecretKind)) {
                std::string VarName = getDescriptiveGlobalName(GV);
                if (ReportedVars.insert(VarName).second) {
                    errs() << "secure-clang error: Hardcoded private key or secret detected in global constant '"
                           << VarName << "'. Secrets must be provisioned via secure hardware storage or runtime environment variables.\n";
                    errs() << "  --> note: detected " << SecretKind << "\n";

                    std::string ViolMsg = "Hardcoded private key or secret detected in global constant '" +
                                          VarName + "': " + SecretKind +
                                          ". Secrets must be provisioned via secure hardware storage or runtime environment variables.";
                    Violations.push_back(ViolMsg);
                }
            }
        }
    }
}

static void scanBannedFunctions(Function &F, const SecurityPolicy &Policy,
                                std::vector<std::string> &Violations) {
    for (BasicBlock &BB : F) {
        for (Instruction &I : BB) {
            auto *CB = dyn_cast<CallBase>(&I);
            if (!CB) {
                continue;
            }

            Function *Callee = CB->getCalledFunction();
            if (!Callee) {
                Callee = dyn_cast<Function>(CB->getCalledOperand()->stripPointerCasts());
            }
            if (!Callee) {
                continue;
            }

            StringRef Name = Callee->getName();
            bool isBanned = false;
            for (const std::string &BF : Policy.bannedFunctionsList) {
                if (Name == BF) {
                    isBanned = true;
                    break;
                }
            }

            if (isBanned) {
                const DebugLoc &Loc = I.getDebugLoc();
                std::string LocStr = "";
                if (Loc && Loc.getLine() > 0) {
                    LocStr = " at line " + std::to_string(Loc.getLine());
                    errs() << "secure-clang error: Banned memory-unsafe function '"
                           << Name << "' detected" << LocStr
                           << ". Replace with bounded alternative (e.g., strncpy_s or snprintf).\n";
                    if (Loc.getCol() > 0) {
                        errs() << "  --> note: call site at column " << Loc.getCol()
                               << " in function '" << F.getName() << "'\n";
                    }
                } else {
                    errs() << "secure-clang error: Banned memory-unsafe function '"
                           << Name << "' detected. Replace with bounded alternative (e.g., strncpy_s or snprintf).\n";
                }

                std::string ViolMsg = "Banned memory-unsafe function '" + Name.str() + "' detected" +
                                      LocStr + " in function '" + F.getName().str() + "' (" +
                                      instructionSite(&I) + "). Replace with bounded alternative (e.g., strncpy_s or snprintf).";
                Violations.push_back(ViolMsg);
            }
        }
    }
}

static bool isDerivedFromCall(Value *V, const CallInst *CI,
                              SmallPtrSetImpl<const Value *> &Visited) {
    if (!V || !CI) {
        return false;
    }
    V = V->stripPointerCasts();
    if (V == CI) {
        return true;
    }
    if (!Visited.insert(V).second) {
        return false;
    }

    if (auto *Cast = dyn_cast<CastInst>(V)) {
        return isDerivedFromCall(Cast->getOperand(0), CI, Visited);
    }

    if (auto *LI = dyn_cast<LoadInst>(V)) {
        Value *Ptr = LI->getPointerOperand()->stripPointerCasts();
        if (auto *AI = dyn_cast<AllocaInst>(Ptr)) {
            for (User *U : AI->users()) {
                if (auto *SI = dyn_cast<StoreInst>(U)) {
                    if (SI->getPointerOperand()->stripPointerCasts() == AI) {
                        if (isDerivedFromCall(SI->getValueOperand(), CI, Visited)) {
                            return true;
                        }
                    }
                }
            }
        }
    }

    if (auto *PHI = dyn_cast<PHINode>(V)) {
        for (Value *Inc : PHI->incoming_values()) {
            if (isDerivedFromCall(Inc, CI, Visited)) {
                return true;
            }
        }
    }

    if (auto *Sel = dyn_cast<SelectInst>(V)) {
        return isDerivedFromCall(Sel->getTrueValue(), CI, Visited) ||
               isDerivedFromCall(Sel->getFalseValue(), CI, Visited);
    }

    return false;
}

static bool isDerivedFromCall(Value *V, const CallInst *CI) {
    SmallPtrSet<const Value *, 32> Visited;
    return isDerivedFromCall(V, CI, Visited);
}

static bool isConditionDerivedFrom(Value *Cond, const Value *Origin,
                                   SmallPtrSetImpl<const Value *> &Visited) {
    if (!Cond || !Origin) {
        return false;
    }
    Cond = Cond->stripPointerCasts();
    if (Cond == Origin) {
        return true;
    }
    if (!Visited.insert(Cond).second) {
        return false;
    }

    if (auto *Cast = dyn_cast<CastInst>(Cond)) {
        return isConditionDerivedFrom(Cast->getOperand(0), Origin, Visited);
    }

    if (auto *LI = dyn_cast<LoadInst>(Cond)) {
        Value *Ptr = LI->getPointerOperand()->stripPointerCasts();
        if (auto *AI = dyn_cast<AllocaInst>(Ptr)) {
            for (User *U : AI->users()) {
                if (auto *SI = dyn_cast<StoreInst>(U)) {
                    if (SI->getPointerOperand()->stripPointerCasts() == AI) {
                        if (isConditionDerivedFrom(SI->getValueOperand(), Origin, Visited)) {
                            return true;
                        }
                    }
                }
            }
        }
    }

    if (auto *PHI = dyn_cast<PHINode>(Cond)) {
        for (Value *Inc : PHI->incoming_values()) {
            if (isConditionDerivedFrom(Inc, Origin, Visited)) {
                return true;
            }
        }
    }

    return false;
}

static bool isConditionDerivedFrom(Value *Cond, const Value *Origin) {
    SmallPtrSet<const Value *, 32> Visited;
    return isConditionDerivedFrom(Cond, Origin, Visited);
}

static bool isHashCheckGuardingInstall(Function &F, DominatorTree &DT,
                                       CallInst *HashCI, CallInst *InstallCI) {
    if (!HashCI || !InstallCI) {
        return false;
    }

    BasicBlock *HashBB = HashCI->getParent();
    BasicBlock *InstallBB = InstallCI->getParent();
    if (!HashBB || !InstallBB) {
        return false;
    }

    // HashBB must strictly dominate InstallBB (cannot be in the same basic block)
    if (HashBB == InstallBB || !DT.dominates(HashBB, InstallBB)) {
        return false;
    }

    // Instruction-level dominance
    if (!DT.dominates(HashCI, InstallCI)) {
        return false;
    }

    for (BasicBlock &BB : F) {
        for (Instruction &I : BB) {
            auto *Cmp = dyn_cast<ICmpInst>(&I);
            if (!Cmp) {
                continue;
            }

            bool Op0Derived = isDerivedFromCall(Cmp->getOperand(0), HashCI);
            bool Op1Derived = isDerivedFromCall(Cmp->getOperand(1), HashCI);
            if (!Op0Derived && !Op1Derived) {
                continue;
            }

            ICmpInst::Predicate Pred = Cmp->getPredicate();
            const ConstantInt *ConstVal = nullptr;

            if (Op0Derived) {
                ConstVal = dyn_cast<ConstantInt>(Cmp->getOperand(1));
            } else {
                ConstVal = dyn_cast<ConstantInt>(Cmp->getOperand(0));
                Pred = Cmp->getSwappedPredicate();
            }

            if (!ConstVal) {
                continue;
            }

            int64_t K = ConstVal->getSExtValue();
            bool isSuccessTrue = false;
            bool recognized = false;

            if (Pred == ICmpInst::ICMP_NE && K == 0) {
                // ret != 0 is success
                isSuccessTrue = true;
                recognized = true;
            } else if (Pred == ICmpInst::ICMP_EQ && K == 0) {
                // ret == 0 is failure
                isSuccessTrue = false;
                recognized = true;
            } else if (Pred == ICmpInst::ICMP_EQ && K == 1) {
                // ret == 1 is success
                isSuccessTrue = true;
                recognized = true;
            } else if (Pred == ICmpInst::ICMP_NE && K == 1) {
                // ret != 1 is failure
                isSuccessTrue = false;
                recognized = true;
            } else if ((Pred == ICmpInst::ICMP_SGT || Pred == ICmpInst::ICMP_UGT) && K == 0) {
                // ret > 0 is success
                isSuccessTrue = true;
                recognized = true;
            } else if ((Pred == ICmpInst::ICMP_SLE || Pred == ICmpInst::ICMP_ULE) && K == 0) {
                // ret <= 0 is failure
                isSuccessTrue = false;
                recognized = true;
            } else if (Pred == ICmpInst::ICMP_SGE && K == 1) {
                // ret >= 1 is success
                isSuccessTrue = true;
                recognized = true;
            }

            if (!recognized) {
                continue;
            }

            for (BasicBlock &BrBB : F) {
                auto *Br = dyn_cast<BranchInst>(BrBB.getTerminator());
                if (!Br || !Br->isConditional()) {
                    continue;
                }

                if (!isConditionDerivedFrom(Br->getCondition(), Cmp)) {
                    continue;
                }

                BasicBlock *SuccessSucc = isSuccessTrue ? Br->getSuccessor(0) : Br->getSuccessor(1);
                BasicBlock *FailureSucc = isSuccessTrue ? Br->getSuccessor(1) : Br->getSuccessor(0);

                bool SuccessReaches = blockReachesTarget(SuccessSucc, InstallBB);
                bool FailureReaches = blockReachesTarget(FailureSucc, InstallBB);

                // Install must reside exclusively on the success branch of verifyImageHash
                if (SuccessReaches && !FailureReaches && DT.dominates(Br->getParent(), InstallBB)) {
                    return true;
                }
            }
        }
    }

    return false;
}

static void scanUpdateFirmware(Function &F, DominatorTree &DT, const SecurityPolicy &Policy,
                               std::vector<std::string> &Violations) {
    std::vector<CallInst *> InstallCalls;
    std::vector<CallInst *> VerifyCalls;
    std::vector<CallInst *> TrustedSourceCalls;
    std::vector<CallInst *> HashVerifyCalls;

    const std::initializer_list<StringRef> InstallNames = {
        "install", "installFirmware", "applyUpdate", "perform_flash_write"
    };
    const std::initializer_list<StringRef> VerifyNames = {
        "verifySignature", "verify_signature", "checkSignature", "verify_cryptographic_signature"
    };
    const std::initializer_list<StringRef> TrustedSourceNames = {
        "sourceTrusted", "isSourceTrusted", "validateSource"
    };
    const std::initializer_list<StringRef> HashVerifyNames = {
        "verifyImageHash", "verify_image_hash", "checkImageHash"
    };

    for (BasicBlock &BB : F) {
        for (Instruction &I : BB) {
            auto *CI = dyn_cast<CallInst>(&I);
            if (!CI) {
                continue;
            }

            Function *Callee = CI->getCalledFunction();
            if (!Callee) {
                Callee = dyn_cast<Function>(CI->getCalledOperand()->stripPointerCasts());
            }
            if (!Callee) {
                continue;
            }

            StringRef Name = Callee->getName();

            if (isNameMatch(Name, InstallNames)) {
                InstallCalls.push_back(CI);
                continue;
            }

            if (isNameMatch(Name, VerifyNames)) {
                VerifyCalls.push_back(CI);
                continue;
            }

            if (isNameMatch(Name, TrustedSourceNames)) {
                TrustedSourceCalls.push_back(CI);
                continue;
            }

            if (isNameMatch(Name, HashVerifyNames)) {
                HashVerifyCalls.push_back(CI);
                continue;
            }

            if (Policy.checkLogging &&
                isInList(Name,
                         {"printf", "puts", "fprintf", "perror", "syslog", "vsyslog", "snprintf"})) {
                Violations.push_back("Sensitive logging API call inside updateFirmware(): " +
                                     Name.str() + " at " + instructionSite(CI));
                continue;
            }

            if (Policy.checkWeakCrypto &&
                isInList(Name,
                         {"MD5", "MD5_Init", "MD5_Update", "MD5_Final", "SHA1", "SHA1_Init", "SHA1_Update", "SHA1_Final", "rand", "srand"})) {
                Violations.push_back("Weak crypto or weak entropy API inside updateFirmware(): " +
                                     Name.str() + " at " + instructionSite(CI));
            }
        }
    }

    std::set<std::string> ReportedHashViolations;

    for (CallInst *InstallCI : InstallCalls) {
        if (Policy.checkSignature) {
            bool VerifyDominates = false;
            for (CallInst *VerifyCI : VerifyCalls) {
                if (DT.dominates(VerifyCI, InstallCI)) {
                    VerifyDominates = true;
                    break;
                }
            }
            if (!VerifyDominates) {
                Violations.push_back("Install call is not dominated by signature verification on all paths at " +
                                     instructionSite(InstallCI));
            }
        }

        if (Policy.checkSource) {
            bool SourceDominates = false;
            for (CallInst *TrustedCI : TrustedSourceCalls) {
                if (DT.dominates(TrustedCI, InstallCI)) {
                    SourceDominates = true;
                    break;
                }
            }
            if (!SourceDominates) {
                Violations.push_back("Install call is not dominated by trusted source validation on all paths at " +
                                     instructionSite(InstallCI));
            }
        }

        if (Policy.checkRollback) {
            if (!hasRollbackGuardBeforeInstall(F, DT, InstallCI)) {
                Violations.push_back("Rollback guard '(new_version > current_version)' does not gate install path at " +
                                     instructionSite(InstallCI));
            }
        }

        if (Policy.checkImageHash) {
            bool HashGuarded = false;
            for (CallInst *HashCI : HashVerifyCalls) {
                if (isHashCheckGuardingInstall(F, DT, HashCI, InstallCI)) {
                    HashGuarded = true;
                    break;
                }
            }

            if (!HashGuarded) {
                StringRef CalleeName = "install";
                if (Function *TargetF = InstallCI->getCalledFunction()) {
                    CalleeName = TargetF->getName();
                } else if (Value *CalledOp = InstallCI->getCalledOperand()) {
                    if (Function *TargetF = dyn_cast<Function>(CalledOp->stripPointerCasts())) {
                        CalleeName = TargetF->getName();
                    }
                }

                if (ReportedHashViolations.insert(CalleeName.str()).second) {
                    errs() << "secure-clang error: Control-flow dominance violation. Function '"
                           << CalleeName << "()' is called without being strictly dominated by 'verifyImageHash()'.\n";
                }

                Violations.push_back("Control-flow dominance violation. Function '" +
                                     CalleeName.str() + "()' is called without being strictly dominated by 'verifyImageHash()' at " +
                                     instructionSite(InstallCI));
            }
        }
    }
}

class TraversalPass : public PassInfoMixin<TraversalPass> {
public:
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &MAM) {
        SecurityPolicy Policy = SecurityPolicy::load();
        std::vector<std::string> Violations;

        // 1. Scan global variables and constant strings for hardcoded secrets
        if (Policy.checkSecrets) {
            scanModuleSecrets(M, Violations);
        }

        FunctionAnalysisManager &FAM =
            MAM.getResult<FunctionAnalysisManagerModuleProxy>(M).getManager();

        for (Function &F : M) {
            if (F.isDeclaration()) {
                continue;
            }

            // 2. Scan function calls for banned memory-unsafe functions
            if (Policy.checkBannedFunctions) {
                scanBannedFunctions(F, Policy, Violations);
            }

            // 3. Scan updateFirmware / flashing dominance & security checks
            bool isUpdateFirmware = (F.getName() == "updateFirmware");
            bool hasInstallCall = false;
            for (BasicBlock &BB : F) {
                for (Instruction &I : BB) {
                    if (auto *CI = dyn_cast<CallInst>(&I)) {
                        Function *Callee = CI->getCalledFunction();
                        if (!Callee) {
                            Callee = dyn_cast<Function>(CI->getCalledOperand()->stripPointerCasts());
                        }
                        if (Callee && isNameMatch(Callee->getName(), {"install", "installFirmware", "applyUpdate", "perform_flash_write"})) {
                            hasInstallCall = true;
                            break;
                        }
                    }
                }
                if (hasInstallCall) {
                    break;
                }
            }

            if (isUpdateFirmware || hasInstallCall) {
                DominatorTree &DT = FAM.getResult<DominatorTreeAnalysis>(F);
                scanUpdateFirmware(F, DT, Policy, Violations);
            }
        }

        if (!Violations.empty()) {
            std::string Message =
                "[OTA Security Pass] Security policy violation(s) [" + Policy.name + "]:\n";
            for (const std::string &V : Violations) {
                Message += " - " + V + "\n";
            }
            report_fatal_error(StringRef(Message), false);
        }

        return PreservedAnalyses::all();
    }
};

} 

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "TraversalPass", LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "traversal-pass" || Name == "secret-detection-pass") {
                        MPM.addPass(TraversalPass());
                        return true;
                    }
                    return false;
                });
        }};
}

