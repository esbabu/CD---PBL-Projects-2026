// OptAgent JavaScript profiler harness (Node 22 built-ins only).
// Measures execution time, V8 heap peak delta, and GC-isolated warm timings.
import fs from "node:fs";
import v8 from "node:v8";
import vm from "node:vm";

function prepareSource(rawSource, entry) {
  let src = rawSource
    .replace(/^\s*export\s+default\s+function\s+/gm, "function ")
    .replace(/^\s*export\s+function\s+/gm, "function ")
    .replace(/^\s*export\s+(const|let|var)\s+/gm, "$1 ")
    .replace(/^\s*export\s*\{[^}]*\}\s*;?/gm, "");
  return `${src}
;globalThis.__optagent_entry__ = (typeof ${entry} !== "undefined")
  ? ${entry}
  : (module.exports && typeof module.exports === "function"
      ? module.exports
      : (module.exports && module.exports[${JSON.stringify(entry)}]));
`;
}

async function main() {
  const [, , targetPath, casesPath, outPath, cfgPath] = process.argv;
  const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf-8"));
  const rawSource = fs.readFileSync(targetPath, "utf-8");
  const prepared = prepareSource(rawSource, cfg.entry);
  const cases = fs.readFileSync(casesPath, "utf-8").split(/\r?\n/).filter(Boolean).map((l) => JSON.parse(l));
  const fd = fs.openSync(outPath, "a");

  try {
    for (let idx = 0; idx < cases.length; idx++) {
      const c = cases[idx];
      const mod = { exports: {} };
      const ctx = vm.createContext({
        console: { log() {}, warn() {}, error() {}, info() {} },
        module: mod,
        exports: mod.exports,
        Buffer,
      });
      vm.runInContext(prepared, ctx, { timeout: 5000 });
      if (typeof global.gc === "function") global.gc();
      const heapBefore = v8.getHeapStatistics().used_heap_size;
      ctx.__args__ = JSON.parse(JSON.stringify(c.args || []));
      const t0 = process.hrtime.bigint();
      let status = "ok";
      try {
        const ret = vm.runInContext(`__optagent_entry__.apply(undefined, __args__)`, ctx, { timeout: 5000 });
        if (ret && typeof ret.then === "function") await ret;
      } catch {
        status = "exception";
      }
      const elapsed_s = Number(process.hrtime.bigint() - t0) / 1e9;
      const heapAfter = v8.getHeapStatistics().used_heap_size;
      const peak_memory_bytes = Math.max(0, heapAfter - heapBefore);
      fs.writeSync(
        fd,
        JSON.stringify({ idx, status, elapsed_s, peak_memory_bytes, line_counts: {} }) + "\n"
      );
    }
    fs.writeSync(fd, JSON.stringify({ done: true }) + "\n");
  } finally {
    fs.closeSync(fd);
  }
}

main().catch((err) => {
  process.stderr.write(String(err) + "\n");
  process.exit(1);
});
