// OptAgent JavaScript batch harness (Node 22 built-ins only, zero npm deps).
// argv: node batch_harness.mjs <target_path> <cases_path> <out_path> <cfg_path>
import crypto from "node:crypto";
import fs from "node:fs";
import inspector from "node:inspector";
import { createRequire } from "node:module";
import vm from "node:vm";

const ALLOWED_MODULES = new Set([
  "util",
  "assert",
  "events",
  "buffer",
  "string_decoder",
  "path",
  "node:util",
  "node:assert",
  "node:events",
  "node:buffer",
  "node:string_decoder",
  "node:path",
]);

const nodeRequire = createRequire(import.meta.url);

// ---------- Canonical encoder (NEVER uses `instanceof` — safe across vm realms) ----------
function typeTag(v) {
  return Object.prototype.toString.call(v);
}

function encodeValue(v, depth = 0, seen = new Map(), nextId = { n: 1 }) {
  if (depth > 60) {
    return { __object__: { type: typeof v, repr: "<too deep>" } };
  }
  if (v === undefined) return { __undefined__: 1 };
  if (v === null || typeof v === "boolean" || typeof v === "string") return v;
  if (typeof v === "bigint") return { __bigint__: v.toString() };
  if (typeof v === "number") {
    if (Number.isNaN(v)) return { __float__: "nan" };
    if (v === Infinity) return { __float__: "inf" };
    if (v === -Infinity) return { __float__: "-inf" };
    if (Object.is(v, -0)) return { __float__: "-0" };
    return v;
  }
  if (typeof v === "function" || typeof v === "symbol") {
    return { __object__: { type: typeof v, repr: String(v).slice(0, 200) } };
  }

  // Object-like values: cycle detection
  if (seen.has(v)) {
    return { __ref__: seen.get(v) };
  }
  const tag = typeTag(v);
  if (tag === "[object Date]") {
    return { __date__: v.getTime() };
  }
  if (tag === "[object RegExp]") {
    return { __regexp__: [v.source, v.flags] };
  }
  if (tag === "[object ArrayBuffer]") {
    return { __bytes__: Buffer.from(v).toString("hex") };
  }
  if (ArrayBuffer.isView(v)) {
    const ctorName = v.constructor ? v.constructor.name : "TypedArray";
    if (ctorName === "Buffer") {
      return { __bytes__: Buffer.from(v.buffer, v.byteOffset, v.byteLength).toString("hex") };
    }
    const items = [];
    for (let i = 0; i < v.length; i++) {
      items.push(encodeValue(v[i], depth + 1, seen, nextId));
    }
    return { __typed__: [ctorName, items] };
  }

  const myId = nextId.n++;
  seen.set(v, myId);
  let hasCycle = false;

  if (Array.isArray(v)) {
    const out = [];
    for (let i = 0; i < v.length; i++) {
      if (!(i in v)) {
        out.push({ __hole__: 1 });
      } else {
        out.push(encodeValue(v[i], depth + 1, seen, nextId));
      }
    }
    seen.delete(v);
    return out;
  }
  if (tag === "[object Map]") {
    const pairs = [];
    for (const [k, val] of v.entries()) {
      pairs.push([
        encodeValue(k, depth + 1, seen, nextId),
        encodeValue(val, depth + 1, seen, nextId),
      ]);
    }
    seen.delete(v);
    return { __map__: pairs };
  }
  if (tag === "[object Set]") {
    const items = [];
    for (const item of v.values()) {
      items.push(encodeValue(item, depth + 1, seen, nextId));
    }
    seen.delete(v);
    return { __set__: items };
  }
  if (tag === "[object Object]" || tag === "[object Error]") {
    const pairs = [];
    for (const k of Object.keys(v)) {
      pairs.push([k, encodeValue(v[k], depth + 1, seen, nextId)]);
    }
    seen.delete(v);
    return { __dict__: pairs };
  }

  seen.delete(v);
  return { __object__: { type: tag, repr: String(v).slice(0, 200) } };
}

function stableStringify(x) {
  if (x === null || typeof x !== "object") return JSON.stringify(x);
  if (Array.isArray(x)) return "[" + x.map(stableStringify).join(",") + "]";
  const keys = Object.keys(x).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + stableStringify(x[k])).join(",") + "}";
}

function asMultiset(enc) {
  if (Array.isArray(enc)) {
    return [...enc].sort((a, b) => stableStringify(a).localeCompare(stableStringify(b)));
  }
  if (enc && typeof enc === "object") {
    const keys = Object.keys(enc);
    if (keys.length === 1 && ["__tuple__", "__set__", "__dict__", "__map__"].includes(keys[0])) {
      const k = keys[0];
      return { [k]: [...enc[k]].sort((a, b) => stableStringify(a).localeCompare(stableStringify(b))) };
    }
  }
  return enc;
}

function digestOf(enc, multiset) {
  const target = multiset ? asMultiset(enc) : enc;
  return crypto.createHash("sha1").update(stableStringify(target)).digest("hex").slice(0, 16);
}

function jsReturnType(v, wasPromise) {
  let base;
  if (v === null) base = "null";
  else if (v === undefined) base = "undefined";
  else if (Array.isArray(v)) base = "Array";
  else if (typeof v === "object") {
    const tag = typeTag(v);
    base = tag.slice(8, -1); // "[object Map]" -> "Map"
  } else {
    base = typeof v;
  }
  return wasPromise ? `Promise<${base}>` : base;
}

// ---------- Light ESM-to-CJS normalization (no external npm needed) ----------
function prepareSource(rawSource, entry) {
  let src = rawSource;
  // Normalize `export default function ...` / `export function ...` / `export const ...`
  src = src.replace(/^\s*export\s+default\s+function\s+/gm, "function ");
  src = src.replace(/^\s*export\s+default\s+async\s+function\s+/gm, "async function ");
  src = src.replace(/^\s*export\s+function\s+/gm, "function ");
  src = src.replace(/^\s*export\s+async\s+function\s+/gm, "async function ");
  src = src.replace(/^\s*export\s+(const|let|var)\s+/gm, "$1 ");
  src = src.replace(/^\s*export\s*\{[^}]*\}\s*;?/gm, "");
  return `${src}
;globalThis.__optagent_entry__ = (typeof ${entry} !== "undefined")
  ? ${entry}
  : (module.exports && typeof module.exports === "function"
      ? module.exports
      : (module.exports && typeof module.exports[${JSON.stringify(entry)}] === "function"
          ? module.exports[${JSON.stringify(entry)}]
          : undefined));
`;
}

// ---------- Build decoder function INSIDE the VM context so intrinsics match target realm ----------
const IN_CONTEXT_DECODER = `
globalThis.__optagent_decode__ = function(v) {
  if (v === null || typeof v !== "object") return v;
  if (Array.isArray(v)) {
    const arr = new Array(v.length);
    for (let i = 0; i < v.length; i++) {
      if (v[i] && typeof v[i] === "object" && "__hole__" in v[i]) continue;
      arr[i] = globalThis.__optagent_decode__(v[i]);
    }
    return arr;
  }
  const keys = Object.keys(v);
  if (keys.length === 1) {
    const k = keys[0], val = v[k];
    if (k === "__undefined__") return undefined;
    if (k === "__bigint__") return BigInt(val);
    if (k === "__float__") {
      if (val === "nan") return NaN;
      if (val === "inf") return Infinity;
      if (val === "-inf") return -Infinity;
      if (val === "-0") return -0;
      return Number(val);
    }
    if (k === "__date__") return new Date(val);
    if (k === "__regexp__") return new RegExp(val[0], val[1]);
    if (k === "__map__") {
      const m = new Map();
      for (const pair of val) m.set(globalThis.__optagent_decode__(pair[0]), globalThis.__optagent_decode__(pair[1]));
      return m;
    }
    if (k === "__set__") {
      const s = new Set();
      for (const item of val) s.add(globalThis.__optagent_decode__(item));
      return s;
    }
    if (k === "__tuple__") return val.map(globalThis.__optagent_decode__);
    if (k === "__dict__") {
      const o = {};
      for (const pair of val) o[String(globalThis.__optagent_decode__(pair[0]))] = globalThis.__optagent_decode__(pair[1]);
      return o;
    }
    if (k === "__typed__") {
      const Ctor = globalThis[val[0]];
      if (typeof Ctor === "function") return new Ctor(val[1].map(globalThis.__optagent_decode__));
      return val[1].map(globalThis.__optagent_decode__);
    }
    if (k === "__bytes__") {
      const bytes = new Uint8Array(val.length / 2);
      for (let i = 0; i < bytes.length; i++) bytes[i] = parseInt(val.slice(i * 2, i * 2 + 2), 16);
      return bytes.buffer;
    }
  }
  const obj = {};
  for (const k of keys) obj[k] = globalThis.__optagent_decode__(v[k]);
  return obj;
};
`;

function createDeterministicEnv(randSeed, perturbIdx, stdoutBuf) {
  // mulberry32 PRNG seeded by randSeed + perturbIdx
  let state = (Number(randSeed || 0) + Number(perturbIdx || 0) * 9973) >>> 0;
  function seededRandom() {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
  const fixedTime = 1700000000000 + Number(perturbIdx || 0) * 100000;

  function safeRequire(modName) {
    if (!ALLOWED_MODULES.has(modName)) {
      const err = new Error(`Forbidden module require('${modName}') in OptAgent JS sandbox`);
      err.name = "SecurityError";
      throw err;
    }
    return nodeRequire(modName);
  }

  const fmt = (...args) => args.map((a) => (typeof a === "string" ? a : JSON.stringify(a))).join(" ");
  const customConsole = {
    log: (...a) => stdoutBuf.push(fmt(...a) + "\n"),
    info: (...a) => stdoutBuf.push(fmt(...a) + "\n"),
    warn: (...a) => stdoutBuf.push(fmt(...a) + "\n"),
    error: (...a) => stdoutBuf.push(fmt(...a) + "\n"),
  };

  const moduleObj = { exports: {} };
  const sandbox = {
    console: customConsole,
    module: moduleObj,
    exports: moduleObj.exports,
    require: safeRequire,
    Buffer,
    process: {
      stdout: { write: (s) => { stdoutBuf.push(String(s)); return true; } },
      stderr: { write: () => true },
      env: {},
      hrtime: process.hrtime,
    },
    setTimeout,
    clearTimeout,
  };
  const ctx = vm.createContext(sandbox);
  // Override Math.random and Date.now inside the target context
  vm.runInContext(
    `
    Math.random = ${seededRandom.toString()};
    let __optagent_seed_state = ${state};
    Math.random = function() {
      __optagent_seed_state = (__optagent_seed_state + 0x6d2b79f5) >>> 0;
      let t = Math.imul(__optagent_seed_state ^ (__optagent_seed_state >>> 15), 1 | __optagent_seed_state);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    Date.now = function() { return ${fixedTime}; };
    ${IN_CONTEXT_DECODER}
    `,
    ctx
  );
  return ctx;
}

function buildLineOffsets(src) {
  const offsets = [0];
  for (let i = 0; i < src.length; i++) {
    if (src.charCodeAt(i) === 10) offsets.push(i + 1);
  }
  return offsets;
}

function offsetToLine(offsets, off) {
  let lo = 0, hi = offsets.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (offsets[mid] <= off) lo = mid + 1;
    else hi = mid - 1;
  }
  return Math.max(1, hi + 1);
}

async function runCase(idx, rawSource, preparedSource, lineOffsets, c, cfg, covSession) {
  const res = {
    idx,
    status: "ok",
    ret: null,
    ret_digest: null,
    return_type: null,
    exc_type: null,
    exc_msg: null,
    stdout: "",
    mut: {},
    glob: {},
    alias: [],
    edges: [],
    prop_failures: [],
    elapsed_s: null,
    generator: false,
    sanitizer: null,
    signal: null,
  };

  const stdoutBuf = [];
  const perturbIdx = Number(process.env.OPT_PERTURB_IDX ?? cfg.perturb_idx ?? 0);
  const timeoutMs = Math.max(50, Math.round((cfg.timeout || 2.0) * 1000));
  const ctx = createDeterministicEnv(cfg.rand_seed || 0, perturbIdx, stdoutBuf);

  const protoBefore = vm.runInContext(
    `JSON.stringify([Object.getOwnPropertyNames(Object.prototype).sort(), Object.getOwnPropertyNames(Array.prototype).sort()])`,
    ctx
  );

  // Load target module inside fresh VM context
  const scriptUrl = `optagent_target_${idx}.js`;
  try {
    vm.runInContext(preparedSource, ctx, { filename: scriptUrl, timeout: timeoutMs });
  } catch (e) {
    res.status = "load_error";
    res.exc_type = e && e.name ? String(e.name) : "Error";
    res.exc_msg = e && e.message ? String(e.message).slice(0, 500) : String(e).slice(0, 500);
    return res;
  }

  const entryFn = ctx.__optagent_entry__;
  if (typeof entryFn !== "function") {
    res.status = "load_error";
    res.exc_type = "ReferenceError";
    res.exc_msg = `Entry function '${cfg.entry}' not found or not a function`;
    return res;
  }

  // Decode arguments INSIDE the VM context so intrinsics match
  const rawArgs = c.args || [];
  ctx.__optagent_raw_args__ = JSON.stringify(rawArgs);
  const decodedArgs = vm.runInContext(
    `JSON.parse(__optagent_raw_args__).map(__optagent_decode__)`,
    ctx
  );
  const before = decodedArgs.map((a) => stableStringify(encodeValue(a)));

  // Snapshot global variables before call
  const skipGlobals = new Set([
    "console", "module", "exports", "require", "Buffer", "process",
    "setTimeout", "clearTimeout", "__optagent_entry__", "__optagent_decode__",
    "__optagent_raw_args__", "__optagent_seed_state", cfg.entry,
  ]);
  function snapGlobals() {
    const out = {};
    for (const k of Object.keys(ctx)) {
      if (skipGlobals.has(k) || typeof ctx[k] === "function") continue;
      try {
        out[k] = encodeValue(ctx[k]);
      } catch {
        out[k] = "<unencodable>";
      }
    }
    return out;
  }
  const gBefore = {};
  for (const [k, v] of Object.entries(snapGlobals())) gBefore[k] = stableStringify(v);

  if (covSession) {
    await new Promise((resolve) =>
      covSession.post("Profiler.startPreciseCoverage", { callCount: true, detailed: true }, () => resolve())
    );
  }

  let ret = undefined;
  let ok = false;
  let wasPromise = false;
  const t0 = process.hrtime.bigint();
  try {
    ctx.__optagent_call_args__ = decodedArgs;
    let rawRet = vm.runInContext(
      `__optagent_entry__.apply(undefined, __optagent_call_args__)`,
      ctx,
      { timeout: timeoutMs }
    );
    if (rawRet && (typeof rawRet === "object" || typeof rawRet === "function") && typeof rawRet.then === "function") {
      wasPromise = true;
      let timer;
      const racePromise = new Promise((_, reject) => {
        timer = setTimeout(() => {
          const err = new Error("Async execution timed out");
          err.name = "TimeoutError";
          reject(err);
        }, timeoutMs);
      });
      try {
        ret = await Promise.race([rawRet, racePromise]);
      } finally {
        clearTimeout(timer);
      }
    } else {
      ret = rawRet;
    }
    const dtNs = process.hrtime.bigint() - t0;
    res.elapsed_s = Number(dtNs) / 1e9;
    ok = true;
  } catch (e) {
    const dtNs = process.hrtime.bigint() - t0;
    res.elapsed_s = Number(dtNs) / 1e9;
    const msg = e && e.message ? String(e.message) : String(e);
    if (
      (e && e.code === "ERR_SCRIPT_EXECUTION_TIMEOUT") ||
      (e && e.name === "TimeoutError") ||
      msg.includes("Script execution timed out")
    ) {
      res.status = "timeout";
      res.exc_type = "TimeoutError";
      res.exc_msg = msg.slice(0, 500);
    } else {
      res.status = "exception";
      res.exc_type = e && e.name ? String(e.name) : "Error";
      res.exc_msg = msg.slice(0, 500);
    }
  }

  if (covSession) {
    const covData = await new Promise((resolve) =>
      covSession.post("Profiler.takePreciseCoverage", (err, data) => resolve(err ? null : data))
    );
    if (covData && Array.isArray(covData.result)) {
      const edges = new Set();
      for (const script of covData.result) {
        if (script.url !== scriptUrl) continue;
        for (const fn of script.functions || []) {
          for (const range of fn.ranges || []) {
            if (range.count > 0 && range.startOffset < rawSource.length) {
              const startLine = offsetToLine(lineOffsets, range.startOffset);
              const endLine = offsetToLine(lineOffsets, Math.min(range.endOffset, rawSource.length));
              for (let ln = startLine; ln <= endLine; ln++) {
                edges.add(`0>${ln}`);
              }
              edges.add(`blk:${fn.functionName || "anon"}:${range.startOffset}-${range.endOffset}`);
            }
          }
        }
      }
      res.edges = Array.from(edges);
    }
  }

  res.stdout = stdoutBuf.join("");
  const digestMode = cfg.digest || "off";
  if (ok) {
    const enc = encodeValue(ret);
    res.return_type = jsReturnType(ret, wasPromise);
    const aliases = [];
    for (let i = 0; i < decodedArgs.length; i++) {
      if (decodedArgs[i] !== null && typeof decodedArgs[i] === "object" && decodedArgs[i] === ret) {
        aliases.push(i);
      }
    }
    res.alias = aliases;
    if (digestMode === "off") {
      res.ret = enc;
    } else {
      res.ret_digest = digestOf(enc, digestMode === "multiset");
    }
  }

  const mut = {};
  for (let i = 0; i < decodedArgs.length; i++) {
    const enc = encodeValue(decodedArgs[i]);
    if (stableStringify(enc) !== before[i]) {
      mut[`arg${i}`] = digestMode === "off" ? enc : digestOf(enc, false);
    }
  }
  res.mut = mut;

  const gAfter = snapGlobals();
  const glob = {};
  for (const [k, v] of Object.entries(gAfter)) {
    if (gBefore[k] !== stableStringify(v)) glob[k] = v;
  }
  const protoAfter = vm.runInContext(
    `JSON.stringify([Object.getOwnPropertyNames(Object.prototype).sort(), Object.getOwnPropertyNames(Array.prototype).sort()])`,
    ctx
  );
  if (protoAfter !== protoBefore) {
    glob["__prototype__"] = protoAfter;
  }
  res.glob = glob;

  return res;
}

async function main() {
  const [, , targetPath, casesPath, outPath, cfgPath] = process.argv;
  const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf-8"));
  const rawSource = fs.readFileSync(targetPath, "utf-8");
  const preparedSource = prepareSource(rawSource, cfg.entry);
  const lineOffsets = buildLineOffsets(rawSource);
  const lines = fs.readFileSync(casesPath, "utf-8").split(/\r?\n/).filter(Boolean);
  const start = cfg.start || 0;

  let covSession = null;
  if (cfg.cov) {
    try {
      covSession = new inspector.Session();
      covSession.connect();
      await new Promise((resolve) => covSession.post("Profiler.enable", () => resolve()));
    } catch {
      covSession = null;
    }
  }

  const fd = fs.openSync(outPath, "a");
  try {
    for (let i = start; i < lines.length; i++) {
      const c = JSON.parse(lines[i]);
      const r = await runCase(i, rawSource, preparedSource, lineOffsets, c, cfg, covSession);
      fs.writeSync(fd, JSON.stringify(r) + "\n");
      if (r.status === "load_error") break;
    }
    fs.writeSync(fd, JSON.stringify({ done: true }) + "\n");
  } finally {
    fs.closeSync(fd);
    if (covSession) {
      try { covSession.disconnect(); } catch {}
    }
  }
}

main().catch((err) => {
  process.stderr.write(String(err && err.stack ? err.stack : err) + "\n");
  process.exit(1);
});
