# AGentic_C 2.0 — Plain English Guide
> **No jargon. Just analogies. Everything we built (and how we upgraded our seniors' v1.0) explained from scratch.**

---

## 1. What is AGentic_C 2.0?

**One-line answer:** AGentic_C 2.0 is a **safe, smart AI compiler assistant** that takes your C/C++ code, makes the critical parts run faster using real Clang/LLVM tools, and **proves** it didn't break your output or delete your security protections.

### The recipe analogy 🍕 (v1.0 vs. v2.0)
* **Normal Compiler (`clang -O3`):** A regular oven that bakes every dish at the exact same temperature for the exact same time.
* **Seniors' AGentic_C 1.0:** A Michelin-star chef who reads your recipe and suggests faster steps — *but mostly practices on a whiteboard without actually turning on the real oven or tasting the final dish.*
* **Our AGentic_C 2.0:** A Michelin-star chef **plus a food-safety inspector and a bouncer at the kitchen door**. It checks your ingredients for poison first (Prompt Injection / Trojan Guard), fixes spelling mistakes in your recipe with 1 click (Syntax Fixer), cooks in the **real oven** (Clang/LLVM 23), stops the chef from throwing away safety steps like washing hands (CWE-14 Key-Wipe Protection), **taste-tests the real dish 6 times** before serving (6-Fixture Validator), and hands you a sealed receipt (SHA-256 Provenance).

---

## 2. Who is it built for?

While v1.0 focused only on **High-Frequency Trading (HFT)**, AGentic_C 2.0 is built for **all ultra-low-latency and safety-critical C/C++ systems** (tested across **7 real benchmark suites**):

1. **High-Frequency Trading (HFT)** (`hft_strategy.cpp`, `market_maker.cpp`, `order_book_engine.cpp`, `enterprise_hft_engine.cpp`) — where 1 nanosecond can decide a million-dollar trade.
2. **Cryptographic Key Vaults** (`crypto_constant_time_vault.cpp`) — fast encryption where secret keys *must* be wiped from RAM.
3. **Autonomous Flight Controllers** (`autonomous_flight_controller.cpp`) — 1 kHz drone/aircraft sensor & PID loops that must fit inside the CPU's tiny 32 KB cache.
4. **Linux eBPF / XDP DDoS Packet Filters** (`ebpf_ddos_packet_filter.cpp`) — network firewalls dropping attack packets at wire speed.

### The race-car analogy 🏎️
A normal app is a family sedan. These systems are **Formula 1 cars carrying locked briefcases**. They don't just need to go 300 km/h — they also can't lose a wheel (broken output) or drop the briefcase on the track (leaked crypto keys).

---

## 3. Why does it exist? (What Problems We Solved)

Standard compilers (`-O2` / `-O3`) have three big problems:
1. **One-size-fits-all:** Like a gym trainer giving an Olympic sprinter and a 70-year-old grandma the exact same workout — optimizing rarely-used startup/logging code bloats the binary and kicks hot code out of the CPU's fast **32 KB L1 instruction cache**.
2. **Black box:** They never tell you *why* your C++ code is slow (virtual functions, mutexes, heap allocations).
3. **Dangerous "too-clever" optimizations (CWE-14):** Standard passes delete `std::memset()` secret-key wipes at the end of a function because they think nobody reads that memory again!

### And what was missing in our seniors' AGentic_C 1.0?
When we tested v1.0, we found **6 real gaps** we needed to fix:
1. It mostly ran on **fake/simulated LLVM IR stubs** instead of real `clang++` and LLVM `opt`.
2. It had **no Policy Gate** (agents could suggest any pass unchecked).
3. It had **no Critic Feedback loop** to swap in a safe fallback pass when a pass failed.
4. Its security scanner wasn't connected to the optimizer and **couldn't map IR warnings back to C++ line numbers**.
5. It had **no CWE-14 key-wipe protection** and **no Prompt-Injection / Trojan Unicode guard**.
6. It **never compiled and ran the real binary** on test inputs to verify that program outputs stayed identical.

---

## 4. How AGentic_C 2.0 Actually Works (8-Stage Guarded Assembly Line)

Think of AGentic_C 2.0 as an **8-stage high-security race-car factory**.

---

### 🛡️ Stage 0 — The Bouncer & Grammar Tutor (Entrance Guard + Pre-IR Syntax Fixer)
**What:** Before any AI agent touches your file, Stage 0 checks two things:
1. **Entrance Guard:** Scans the raw file (including comments!) for **prompt-injection tricks** (like `// IGNORE SECURITY POLICY`) and invisible **Trojan Source Unicode characters** (CVE-2021-42574) that make code look different to humans than to the compiler. If caught, it **locks the door immediately (fail-closed)**.
2. **Pre-IR Syntax Fixer:** Runs a quick Clang syntax check. If you forgot a semicolon `;` on Line 4, it highlights the exact line and column in plain English and gives you a **1-click "Auto-Fix & Compile" button** in the dashboard!

**Analogy:** A security guard at the factory gate checking IDs for fake badges *and* a receptionist fixing typos on your order form before sending it to the factory floor.

---

### 🏭 Stage 1 — The Real Translator (`clang++` + `!dbg` Footnotes)
**What:** Runs the **real** Homebrew `clang++` (LLVM 23) to convert your C++ file into real LLVM IR (`.ll`) using two special flags:
* `-Xclang -disable-O0-optnone` — unlocks the IR so our agents can run custom LLVM `opt` passes.
* `-gline-tables-only` — stamps a tiny `!dbg` footnote on every IR instruction pointing back to its exact C++ line number (`!DILocation`).

**Analogy:** Translating a 10-page recipe into a 50-page factory manual, where every single step has a footnote saying *"from Line 341 of the original recipe."*

---

### 🔎 Stage 2 — The Safety Inspector & Memory Lookup (Source/IR Scanner + 256-dim Encoder)
**What:**
1. Scans **both** the C++ code and the LLVM IR for dangerous C functions (`gets`, `strcpy`, `sprintf`, `scanf("%s")`, `memcpy`) — tracing IR warnings straight back to exact C++ lines via `!dbg` in **under 2.3 milliseconds**.
2. **Connected to the Planner:** If it finds an unsafe buffer (`CWE-120` / `CWE-242`), it warns the tuners to prefer safe register passes (`sroa`, `mem2reg`) and **avoid** risky `loop-unroll` / `loop-vectorize`.
3. Encodes the IR into a **256-number vector** and checks our **persistent SQLite Experience Store** to see what worked on similar code before.

**Analogy:** A car's wet-road sensor that doesn't just flash a warning light — it is actually wired into the cruise control so the car slows down on slippery curves.

---

### 🧠 Stage 3 — The Boss Agent (Factory Manager)
**What:** Scores every function from 0 to 100 and splits them into:
* **🔴 HOT functions** (score ≥ 50 — trading loops, crypto blocks, 1 kHz flight ticks) → strict **150–400 ns** budgets, heavy targeted optimization.
* **🔵 COLD functions** (score < 50 — config loading, startup logging) → light optimization only, keeping the `.text` machine code tiny (**16–24 KB**, comfortably inside the **32 KB L1i cache**).

**Analogy:** The factory manager saying *"Tune the F1 engine to perfection, but don't waste money turbocharging the windshield wipers."*

---

### 🔧 Stage 4 — The Fixer Agent (Race-Car Mechanic)
**What:** Scans every HOT function for **11 HFT Latency Anti-Patterns (`LAP-001` to `LAP-011`)** — expanding seniors' 10 patterns by adding **C++20 Coroutines (`LAP-011`)** — and gives exact C++ fix suggestions.

| Code | Code Problem | Real-World Analogy |
|---|---|---|
| `LAP-001` | Heap allocation (`new` / `malloc`) | Stopping mid-race to buy new tyres |
| `LAP-002` | Virtual dispatch (`virtual`) | Calling a middleman instead of talking directly |
| `LAP-003` | Exceptions (`try` / `catch`) | Bolting heavy scaffolding onto an F1 car |
| `LAP-004` | Mutex locks (`std::mutex`) | A red traffic light in the middle of a racetrack |
| `LAP-005` | Syscalls / I/O (`printf` / `cout`) | Pulling over mid-race to write in your diary |
| `LAP-006` | `std::function` indirect call | Mailing a letter instead of walking across the room |
| `LAP-007` | Heavy atomics (`seq_cst`) | Stopping every lane on the highway just to change lanes |
| `LAP-008` | `dynamic_cast` (RTTI) | Checking a driver's birth certificate at every corner |
| `LAP-009` | Unaligned memory (`#pragma pack(1)`) | Parking across two parking spots — takes twice the effort |
| `LAP-010` | Deep branches (`if`/`switch`) | Too many blind forks in the road (CPU guesses wrong) |
| `LAP-011` | Coroutines (`co_await`) *(NEW in 2.0!)* | Pausing the car to pack its state into a storage locker |

---

### ⚙️ Stage 5 — The IR Tuner & Hardware Tuner (Blueprint Engineer + Chip Specialist)
**What:** Builds an ordered queue of LLVM passes (`mem2reg`, `sroa`, `inline`, `instcombine`, `gvn`, `dce`, `loop-vectorize`) tailored to both the code's anti-patterns and your physical CPU (**128-bit ARM64 NEON** on Apple Silicon or **x86 AVX2**), while obeying any safety warnings from Stage 2.

---

### 🚧 Stage 6 — Closed-Loop Policy Gate, CWE-14 Bodyguard & Critic Fallback *(BIGGEST UPGRADE IN 2.0!)*
**What:** Instead of blindly trusting the agents, our `SafeOptimizationController` puts **three locks** on every single pass:

1. **17-Pass Allowlist Policy Gate:** Only 17 vetted, safe LLVM middle-end passes are allowed. Unknown flags or shell injection tricks are blocked immediately.
2. **Real LLVM `opt` + Verifier:** Runs the pass using the real LLVM `opt` tool and verifies the IR with `opt -passes=verify`.
3. **CWE-14 Key-Wipe Bodyguard:** Compares the LLVM IR before and after every pass. If a pass like `sroa` or `mem2reg` deletes a `std::memset` secret-key wipe, it gets **REJECTED**!
   * **Whiteboard Analogy:** Imagine writing your secret ATM PIN on a whiteboard, doing your math, and wiping the board clean before leaving. An overly "efficient" assistant says *"Nobody uses the board after you leave, let's skip wiping it to save 2 seconds!"* Our CWE-14 Bodyguard stops them at the door: *"No! Wipe the board or you're rejected!"*
4. **Closed-Loop Critic Fallback:** Whenever a pass is rejected by the Policy Gate or CWE-14 check, the controller keeps the last safe IR and **automatically inserts a safe fallback pass** (like `inline` or `instcombine`) so optimization still succeeds safely!

---

### ✅ Stage 7 — The Taste-Tester & Receipt Printer (Candidate Validator + SHA-256 Provenance)
**What:**
1. **Real Compilation:** Compiles **both** the baseline IR and optimized IR into real native binaries using `clang++`.
2. **6-Fixture Taste Test:** Runs both binaries on **6 sample test inputs**. If exit codes, `stdout`, or `stderr` differ by even a single character (for example, `enterprise_hft_engine.cpp` prints live changing CPU timestamps), it **reverts fail-closed** to the baseline!
3. **Real Stopwatch Timing + 32 KB L1i Check:** Times the real executable across **5 runs** (reporting true median & P99 ms — kept **100% separate** from theoretical cost-model estimates!) and measures `.text` code size via `llvm-size` to ensure it fits in the **32 KB L1i cache**.
4. **SHA-256 Build Receipt (`.provenance.json`):** Fingerprints the source file, final LLVM IR, and executable binary with SHA-256 hashes so the dashboard can prove nothing was tampered with, and saves the run in the **persistent SQLite Experience Store**.

---

## 5. The Reward System (How It Grades Each Run)

```
Score (R) = 50% × Latency Reduction
          + 20% × Instruction Reduction
          + 15% × Anti-Patterns Addressed
          − 10% × Retry Penalty
          +  5% × Stability Bonus
```

**Analogy:** Grading an F1 pit crew — 50% for lap time improvement, 20% for lighter parts, 15% for fixing mechanical flaws, −10% penalty for wasted pit stops, and +5% for consistent lap times.

---

## 6. The Web Dashboard & Standalone Attack Lab

Open **`http://localhost:5050`** for the Compiler Dashboard and **`http://localhost:5050/attack_lab.html`** for the Attack Lab:

| Panel | What You See |
|---|---|
| **8-Stage Pipeline Bar** | Live status of every stage from Clang IR to Verifier |
| **Interactive C/C++ Editor & 1-Click Auto-Fix** | Edit any of the 7 examples or type broken C++ and click **Auto-Fix & Compile** |
| **Function Classification & Latency Bars** | HOT vs. COLD table + Baseline vs. AGentic_C 2.0 vs. Clang `-O3` chart |
| **Anti-Pattern Cards & Pass Timeline** | Every `LAP-001`..`LAP-011` issue + exact order of applied passes |
| **Safety Checks & Policy Gate** *(NEW!)* | Source/IR findings with `!dbg` C++ line numbers + CWE-14 rejections + Critic Fallbacks |
| **Build Integrity Panel** *(NEW!)* | One-click **Verify artifacts** button checking SHA-256 hashes in `.provenance.json` |
| **Standalone Attack Lab** *(NEW!)* | Test the scanner on **48 visible + 8 held-out** attack scenarios with Precision/Recall/F1 charts |

---

## 7. Honest Remaining Limitations (Great for Viva Questions!)

We fixed all 6 major gaps from v1.0, and we are transparent about what is left for **Future Work**:

1. **Regex Scanner vs. Obfuscated Attacks in Attack Lab:** Our fast regex scanner finishes in **0.69–2.27 ms** and catches 50% of direct prompt injections, credential leaks, and path traversals (31.2% overall recall on 48 scenarios), but misses Base64-encoded or split payloads. Catching those needs deeper **AST data-flow and taint analysis**.
2. **Non-Deterministic `stdout` Programs Revert Fail-Closed:** Because `enterprise_hft_engine.cpp` prints live CPU clock timestamps to `stdout`, its output changes between runs, so our strict validator safely reverts it. Deterministic test harnesses (checking return values instead of live timestamps) solve this.
3. **Single-File Compilation Only:** Currently optimizes one `.cpp` translation unit at a time; multi-file CMake/LTO whole-program builds are future work.
4. **Heuristic + Experience Store Planning (No Trained Deep RL Yet):** Pass selection uses rule-guided heuristics + SQLite 256-dim cosine similarity lookup rather than an offline-trained deep PPO neural network or live hardware `perf` PGO counters.
5. **Unsigned Provenance Receipts:** `.provenance.json` verifies file integrity via SHA-256 hashes (detecting accidental changes), but adding cryptographic digital signatures (like Sigstore/cosign) is planned for full supply-chain security.

---

## 8. Quick Comparison: Seniors' v1.0 vs. Our AGentic_C 2.0

| Feature | Seniors' AGentic_C 1.0 | Our AGentic_C 2.0 |
|---|---|---|
| **Clang++ & LLVM `opt` execution** | ⚠️ Mostly stub IR | ✅ **Real Clang++ & LLVM 23 (`opt`, `llvm-size`)** |
| **Stage 0 Prompt & Trojan Unicode Guard** | ❌ Not present | ✅ **100% blocks prompt overrides & Bidi Unicode** |
| **Pre-IR Syntax Error 1-Click Auto-Fix** | ❌ Not present | ✅ **Works live in Web UI** |
| **Source + IR Security Scanner (`!dbg` lines)** | ❌ Not connected | ✅ **Maps IR calls to exact C++ lines & guides planner** |
| **HOT/COLD classification** | ✅ Rule-based | ✅ **Security-aware (97.3% accuracy, 72/74 funcs)** |
| **HFT Anti-pattern detection** | ✅ 10 patterns | ✅ **11 patterns (`LAP-001` to `LAP-011`)** |
| **17-Pass Allowlist & Critic Fallback** | ❌ Open-loop | ✅ **Fail-closed gate + automatic safe fallbacks** |
| **CWE-14 Key-Wipe Protection** | ❌ Not present | ✅ **100% blocks `memset` key-wipe removal** |
| **6-Fixture Validation & Real Timing** | ❌ Estimates only | ✅ **6 fixtures + 5-run real median/P99 + 32 KB L1i** |
| **Persistent Experience Store** | ⚠️ Lost on restart | ✅ **Persistent SQLite 256-dim store** |
| **SHA-256 Build Provenance & Attack Lab** | ❌ Not present | ✅ **`.provenance.json` + 56-case Attack Lab** |
| **Automated Unit Tests** | ❌ None | ✅ **12/12 passing (100%)** |

---

> **Team:** Haamiz Suhail Hakeem (`25CSB1A70`) & Shrot Amish Parekh (`25CSB1A62`) · NIT Warangal CSE
