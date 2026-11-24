# ParC

Securing an AI Code Explanation Agent with Compiler Proven Facts

Pranav Napolean, 25CSB1A69
CS2201 Theory of Automata and Compiler Design
Department of Computer Science and Engineering (AI and DS), NIT Warangal

## Overview

ParC is a teaching compiler for a small C like language with built in parallel loops. Every phase of the compiler is written from scratch in C++20, and each one explains what it found and why. When the compiler reports a bug, it attaches a proof, a weakness class and the exact condition under which the program fails.

On top of the compiler sits an AI agent that explains each finding in plain language and proposes fixes. The agent never has the final word. Every explanation is checked against what the compiler proved, and every fix must pass a compiler gate before anyone sees it. The gate recompiles the rewrite, confirms the bug is gone, rejects new warnings and runs the function on 40 generated inputs to make sure its behaviour has not changed.

Because the agent reads code written by other people, it can be attacked. A comment in the code can carry hidden instructions telling the model to call unsafe code safe. ParC includes a security layer that detects these attacks, scores their risk, blocks them and logs every event. The layer has been tested with simulated attacks, an adaptive red team and a second AI playing the attacker.

## The Compiler

The compiler runs eight phases in order. A phase only runs when the phases before it found no errors.

1. The **scanner** turns source text into tokens with a hand written finite automaton that always takes the longest match.
2. The **parser** builds a syntax tree by recursive descent, using precedence climbing for expressions and recovering after an error so that one mistake produces one message.
3. The **semantic routines** check scopes and types, then analyse the control flow graph for unreachable code, missing returns, variables used before they are assigned and dead stores. A value analysis tracks the range of every integer and whether each array can be null. This is how the compiler proves division by zero, overflow, null access and out of range indexing.
4. The **loop dependence test** decides whether a parallel loop is safe to run in parallel.
5. The **IR builder** produces three address code in basic blocks, along with the control flow graph, dominators and loops.
6. The **optimizer** runs eight passes on a shared data flow framework, among them constant folding, copy propagation, common subexpression elimination, dead code elimination, loop invariant code motion and strength reduction. Every change is logged with its reason.
7. The **code generator** allocates registers by linear scan and emits instructions for the virtual machine.
8. The **register virtual machine** runs the program, including parallel loops on simulated threads under a repeatable scheduler, and it can step through a run one instruction at a time.

The compiler also reports a vulnerability percentage. It counts every operation that can fail at run time and shows the share it could not prove safe.

A separate metrics module measures what a program costs. It records compile time per phase, run time, energy from the processor's own power meter and memory use. It also builds the same program natively with Clang for comparison and estimates the time and space complexity of each function, suggesting a rewrite whenever a known pattern can lower it. This module is the only part of the project that uses Clang. The compiler phases themselves depend on no outside library.

## The Explorer

The explorer is a local web page that makes every phase visible. Programs are typed or chosen from the examples on the left, and the tabs on the right show the tokens, syntax tree, symbol table, findings, IR with its control flow graph, data flow sets, optimizer log, virtual machine code, a run with a step debugger, the metrics and the security view. Clicking an item highlights the source code it came from.

The Security tab shows the program's vulnerability percentage and lets anyone try attacks on the agent with one click, with the security layer switched off and on side by side.

## Project Structure

The **compiler** folder holds one subfolder per phase, each with its own tests, plus the metrics module and the command line tool.

The **explorer** folder holds the web application written in Python with Flask, the agent, its compiler gate and its security layer.

The **examples** folder holds twenty ParC programs together with the output each one is expected to print.

The **evaluation** folder holds the scripts that compare ParC with Clang, generate random test programs, measure the agent and run the attacks on it.

## Requirements

Windows 10 or 11 with Visual Studio 2022, which provides the C++ compiler and CMake. Python 3.13 with Flask for the explorer. LLVM and Clang 23 are optional and needed only for the metrics module. A Google Gemini API key is optional. Without one the agent uses its built in templates.

## Building and Testing

Run these commands from the project folder.

```bat
cmake -S . -B build\msvc
cmake --build build\msvc --config Release
ctest --test-dir build\msvc -C Release
```

This builds the parc command and nine test programs containing 209 tests.

## Running the Explorer

```bat
pip install -r explorer\requirements.txt
python explorer\app.py
```

Then open <http://127.0.0.1:5000> in a browser. To let a language model write the explanations, put the key in a file named .env in the project folder as GEMINI_API_KEY. The explorer's own tests run with the command below.

```bat
python -m unittest discover -s explorer\tests
```

## Using the Compiler Directly

```bat
build\msvc\Release\parc.exe check examples\04_cwe369_divzero.parc
build\msvc\Release\parc.exe ir examples\19_bubble_sort.parc
build\msvc\Release\parc.exe run examples\06_dot_parallel.parc
build\msvc\Release\parc.exe metrics examples\09_fibonacci.parc
```

Running parc with no arguments lists every command and option.

## Results

All 17 examples that run to completion and 300 randomly generated programs print exactly what the same programs print when built with Clang. A further 500 random programs print the same output whether the optimizer is on or off, with fewer registers and with one to four threads.

On the project's 40 simulated attacks, the security layer detected injected instructions with 95 percent precision and 97.5 percent recall. With only the compiler gate, 22 of the 40 attacks succeeded. With the full security layer, none did.

Against attacks phrased in ways the layer had never seen, the input word filter caught only 45 percent, mostly missing attacks written in other languages. A filter that matches wordings is the weakest part of the design, which is why the later checks compare the agent's answers with the compiler's proofs instead.

When Google Gemini played the attacker over 32 rounds, every one of its comments slipped past the word filter, and none of them got through the full layer. Against the real Gemini model, 0 of 37 attack attempts manipulated an explanation and 0 of 6 harmful fixes were accepted.

Native code built by Clang ran about 5.5 times faster than the virtual machine on average across the examples.

The full method and every measurement are described in the project report.
