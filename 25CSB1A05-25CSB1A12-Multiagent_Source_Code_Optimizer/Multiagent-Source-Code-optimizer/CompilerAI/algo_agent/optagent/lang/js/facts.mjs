// Babel-based JavaScript semantic fact extractor emitting ModuleFacts JSON.
// Used when Node + @babel/parser + @babel/traverse are available (e.g. inside sandbox-js image).
import fs from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const parser = require("@babel/parser");
const traverseMod = require("@babel/traverse");
const traverse = traverseMod.default || traverseMod;

const MUTATING_ARRAY_METHODS = new Set([
  "push", "pop", "shift", "unshift", "splice", "sort", "reverse", "fill", "copyWithin",
]);

function extractFacts(source) {
  const ast = parser.parse(source, {
    sourceType: "unambiguous",
    plugins: ["jsx", "classProperties", "optionalChaining", "nullishCoalescingOperator"],
  });

  const functions = {};
  const moduleVars = [];
  const mutableModuleVars = [];
  const imports = {};

  traverse(ast, {
    ImportDeclaration(p) {
      imports[p.node.source.value] = p.node.source.value;
    },
    VariableDeclaration(p) {
      if (p.parent.type === "Program") {
        for (const d of p.node.declarations) {
          if (d.id && d.id.type === "Identifier") {
            const isFn = d.init && (d.init.type === "ArrowFunctionExpression" || d.init.type === "FunctionExpression");
            if (!isFn) {
              moduleVars.push(d.id.name);
              if (p.node.kind !== "const") mutableModuleVars.push(d.id.name);
            }
          }
        }
      }
    },
  });

  function analyzeFn(name, path) {
    const node = path.node;
    const params = (node.params || []).map((p) => {
      if (p.type === "Identifier") return { name: p.name, annotation: null, default: null, kind: "positional" };
      if (p.type === "AssignmentPattern" && p.left.type === "Identifier") {
        return { name: p.left.name, annotation: null, default: "...", kind: "positional" };
      }
      if (p.type === "RestElement" && p.argument.type === "Identifier") {
        return { name: p.argument.name, annotation: null, default: null, kind: "vararg" };
      }
      return { name: "_", annotation: null, default: null, kind: "positional" };
    });
    const paramNames = new Set(params.map((p) => p.name));
    const mutated = new Set();
    const effects = [];
    const raises = new Set();
    const sortUses = [];
    const costPatterns = [];
    const callees = new Set();
    let loopCount = 0;
    let maxLoopDepth = 0;
    let curDepth = 0;
    let isRecursive = false;
    let branchingSelf = 0;
    let mayAlias = false;

    const loopHooks = {
      enter() { loopCount++; curDepth++; if (curDepth > maxLoopDepth) maxLoopDepth = curDepth; },
      exit() { curDepth--; },
    };

    path.traverse({
      ForStatement: loopHooks,
      ForInStatement: loopHooks,
      ForOfStatement: loopHooks,
      WhileStatement: loopHooks,
      DoWhileStatement: loopHooks,
      ThrowStatement(p) {
        if (p.node.argument && p.node.argument.type === "NewExpression" && p.node.argument.callee.type === "Identifier") {
          raises.add(p.node.argument.callee.name);
        } else {
          raises.add("Error");
        }
      },
      ReturnStatement(p) {
        if (p.node.argument && p.node.argument.type === "Identifier" && paramNames.has(p.node.argument.name)) {
          mayAlias = true;
        }
      },
      AssignmentExpression(p) {
        const l = p.node.left;
        if (l.type === "MemberExpression" && l.object.type === "Identifier" && paramNames.has(l.object.name)) {
          mutated.add(l.object.name);
          effects.push({ kind: "arg_mutation", line: p.node.loc?.start.line || 1, detail: `${l.object.name}[...] = ...`, certainty: "definite" });
        }
      },
      CallExpression(p) {
        const line = p.node.loc?.start.line || 1;
        const callee = p.node.callee;
        if (callee.type === "Identifier") {
          callees.add(callee.name);
          if (callee.name === name) { isRecursive = true; branchingSelf++; }
        } else if (callee.type === "MemberExpression" && callee.property.type === "Identifier") {
          const prop = callee.property.name;
          const objName = callee.object.type === "Identifier" ? callee.object.name : "";
          if (MUTATING_ARRAY_METHODS.has(prop) && paramNames.has(objName)) {
            mutated.add(objName);
            effects.push({ kind: "arg_mutation", line, detail: `${objName}.${prop}(...)`, certainty: "definite" });
          }
          if (prop === "sort") {
            const hasCmp = (p.node.arguments || []).length > 0;
            sortUses.push({ kind: "array_sort", line, in_loop: curDepth > 0, detail: hasCmp ? "custom comparator" : "default lexicographic sort" });
          }
          if (curDepth > 0 && (prop === "includes" || prop === "indexOf")) {
            costPatterns.push({ kind: "linear_membership", line, in_loop: true, detail: `.${prop}() inside loop` });
          }
          if (curDepth > 0 && (prop === "shift" || prop === "unshift" || prop === "splice")) {
            costPatterns.push({ kind: "linear_shift", line, in_loop: true, detail: `.${prop}() inside loop` });
          }
          if (objName === "console") {
            effects.push({ kind: "print", line, detail: `console.${prop}`, certainty: "definite" });
          }
          if (objName === "Math" && prop === "random") {
            effects.push({ kind: "random", line, detail: "Math.random()", certainty: "definite" });
          }
          if (objName === "Date" && prop === "now") {
            effects.push({ kind: "time", line, detail: "Date.now()", certainty: "definite" });
          }
        }
      },
    });

    functions[name] = {
      name,
      lineno: node.loc?.start.line || 1,
      end_lineno: node.loc?.end.line || 1,
      params,
      returns_annotation: null,
      docstring: null,
      decorators: [],
      is_generator: Boolean(node.generator),
      is_async: Boolean(node.async),
      is_recursive: isRecursive,
      in_recursive_cycle: false,
      branching_self_calls: branchingSelf,
      callees_local: [],
      callees_external: Array.from(callees),
      call_sites: [],
      effects,
      transitive_effect_kinds: Array.from(new Set(effects.map((e) => e.kind))),
      mutated_params: Array.from(mutated).sort(),
      reads_globals: [],
      raises: Array.from(raises).sort(),
      handled_exceptions: [],
      implicit_raises: [],
      loop_count: loopCount,
      max_loop_depth: maxLoopDepth,
      float_reasons: [],
      sort_uses: sortUses,
      unordered_iterations: [],
      cost_patterns: costPatterns,
      uses_hash_or_id: false,
      may_return_input_alias: mayAlias,
      extra: { language: "javascript" },
    };
  }

  traverse(ast, {
    FunctionDeclaration(p) {
      if (p.node.id) analyzeFn(p.node.id.name, p);
    },
    VariableDeclarator(p) {
      if (p.node.id?.type === "Identifier" && p.node.init &&
          (p.node.init.type === "ArrowFunctionExpression" || p.node.init.type === "FunctionExpression")) {
        analyzeFn(p.node.id.name, p.get("init"));
      }
    },
  });

  const fnNames = new Set(Object.keys(functions));
  for (const fn of Object.values(functions)) {
    fn.callees_local = fn.callees_external.filter((c) => fnNames.has(c) && c !== fn.name);
    fn.callees_external = fn.callees_external.filter((c) => !fnNames.has(c));
  }
  const called = new Set(Object.values(functions).flatMap((f) => f.callees_local));
  const roots = Object.keys(functions).filter((n) => !called.has(n));

  return {
    functions,
    imports,
    module_vars: moduleVars,
    mutable_module_vars: mutableModuleVars,
    module_side_effects: [],
    root_functions: roots.length ? roots : Object.keys(functions),
  };
}

const srcPath = process.argv[2];
const src = fs.readFileSync(srcPath, "utf-8");
process.stdout.write(JSON.stringify(extractFacts(src)));
