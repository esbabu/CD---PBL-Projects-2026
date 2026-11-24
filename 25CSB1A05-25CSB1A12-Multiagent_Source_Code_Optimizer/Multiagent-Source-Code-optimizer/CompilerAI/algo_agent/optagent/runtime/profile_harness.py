"""argv: pkg_root src_path cases_path out_path cfg_path

Step 3 profile harness: runs cases with cProfile + tracemalloc + line profiling.
STDLIB-ONLY: executes inside the sandbox.
"""
import collections
import contextlib
import cProfile
import io
import inspect
import itertools
import json
import os
import pstats
import random
import signal
import sys
import time
import tracemalloc
import types


class _Timeout(BaseException):
    pass


def _on_alarm(signum, frame):
    raise _Timeout()


class LineProfiler:
    __slots__ = ("fn", "line_hits", "line_times", "last_line", "last_time")

    def __init__(self, filename):
        self.fn = os.path.abspath(filename)
        self.line_hits = collections.defaultdict(int)
        self.line_times = collections.defaultdict(float)
        self.last_line = {}
        self.last_time = {}

    def _global(self, frame, event, arg):
        if os.path.abspath(frame.f_code.co_filename) == self.fn:
            fid = id(frame)
            self.last_line[fid] = frame.f_lineno
            self.last_time[fid] = time.perf_counter()
            return self._local
        return None

    def _local(self, frame, event, arg):
        fid = id(frame)
        now = time.perf_counter()
        if fid in self.last_line and fid in self.last_time:
            prev_ln = self.last_line[fid]
            dt = now - self.last_time[fid]
            if dt > 0:
                self.line_times[prev_ln] += dt
            self.line_hits[prev_ln] += 1
        if event == "line":
            self.last_line[fid] = frame.f_lineno
            self.last_time[fid] = now
        elif event in ("return", "exception"):
            self.last_line.pop(fid, None)
            self.last_time.pop(fid, None)
        return self._local


def _execute_profile(res, code, src, case, cfg, canon):
    mod = types.ModuleType("target_mod")
    mod.__file__ = src
    sys.modules["target_mod"] = mod
    exec(code, mod.__dict__)

    fn = getattr(mod, cfg["entry"])
    args = list(canon.decode(case["args"]))
    kwargs = {k: canon.decode(v) for k, v in case.get("kwargs", {}).items()}

    profiler = LineProfiler(src)
    cp = cProfile.Profile()

    tracemalloc.start()
    sys.settrace(profiler._global)
    cp.enable()
    t0 = time.perf_counter()
    ok = False
    try:
        try:
            ret = fn(*args, **kwargs)
            if inspect.isgenerator(ret):
                ret = list(itertools.islice(ret, 10000))
            ok = True
        except _Timeout:
            raise
        except BaseException as e:
            res["status"] = "exception"
            res["exc_type"] = type(e).__name__
            res["exc_msg"] = str(e)[:500]
    finally:
        t1 = time.perf_counter()
        cp.disable()
        sys.settrace(None)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    res["elapsed_s"] = t1 - t0
    res["peak_mem_bytes"] = peak
    res["line_hits"] = {str(k): v for k, v in profiler.line_hits.items()}
    res["line_times"] = {str(k): round(v, 8) for k, v in profiler.line_times.items()}

    # Extract function stats from cProfile
    stream = io.StringIO()
    stats = pstats.Stats(cp, stream=stream)
    func_stats = {}
    for (filename, lineno, func_name), (cc, nc, tt, ct, _) in stats.stats.items():
        if os.path.abspath(filename) == os.path.abspath(src):
            func_stats[f"{func_name}@{lineno}"] = {
                "ncalls": nc,
                "tottime": round(tt, 6),
                "cumtime": round(ct, 6),
            }
    res["func_stats"] = func_stats
    if ok:
        res["status"] = "ok"


def _run_one(code, src, case, cfg, canon, alarm):
    res = {"status": "ok"}
    buf = io.StringIO()
    try:
        if alarm:
            signal.setitimer(signal.ITIMER_REAL, cfg["timeout"])
        with contextlib.redirect_stdout(buf):
            _execute_profile(res, code, src, case, cfg, canon)
    except _Timeout:
        res["status"] = "timeout"
    except BaseException as e:
        res["status"] = "crash"
        res["exc_type"] = type(e).__name__
        res["exc_msg"] = str(e)[:500]
    finally:
        if alarm:
            signal.setitimer(signal.ITIMER_REAL, 0)
    res["stdout"] = buf.getvalue()[:10000]
    return res


def main():
    pkg_root, src, cases_p, out_p, cfg_p = sys.argv[1:6]
    sys.path.pop(0)
    sys.path.insert(0, pkg_root)
    sys.path.insert(0, os.path.dirname(os.path.abspath(src)))
    from optagent.runtime import canon

    cfg = json.load(open(cfg_p, encoding="utf-8"))
    code = compile(open(src, encoding="utf-8").read(), src, "exec")
    alarm = hasattr(signal, "setitimer")
    if alarm:
        signal.signal(signal.SIGALRM, _on_alarm)
    out = open(out_p, "a", encoding="utf-8")
    with open(cases_p, encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx < cfg["start"]:
                continue
            res = _run_one(code, src, json.loads(line), cfg, canon, alarm)
            res["idx"] = idx
            try:
                text = json.dumps(res)
            except Exception as e:
                text = json.dumps({"idx": idx, "status": "crash", "exc_msg": f"unserialisable: {e}"})
            out.write(text + "\n")
            out.flush()
    out.write('{"done": true}\n')
    out.flush()
    out.close()
    os._exit(0)


if __name__ == "__main__":
    main()

