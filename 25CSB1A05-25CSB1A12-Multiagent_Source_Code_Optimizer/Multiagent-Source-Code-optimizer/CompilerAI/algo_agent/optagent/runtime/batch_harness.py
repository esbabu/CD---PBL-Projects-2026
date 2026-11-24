"""argv: pkg_root src_path cases_path out_path cfg_path"""
import asyncio
import builtins
import collections
import contextlib
import copy
import inspect
import io
import itertools
import json
import math
import os
import random
import signal
import sys
import time
import types


class _Timeout(BaseException):
    pass


def _on_alarm(signum, frame):
    raise _Timeout()


def _j(x):
    return json.dumps(x)


def _snap_globals(mod, canon):
    out = {}
    for k, v in list(vars(mod).items()):
        if k.startswith("__") or callable(v) or inspect.ismodule(v):
            continue
        try:
            out[k] = canon.encode(v)
        except Exception:
            out[k] = "<unencodable>"
    return out


def _snap_obj_state(inst, canon):
    if inst is None:
        return {}
    if hasattr(inst, "__dict__"):
        out = {}
        for k, v in list(vars(inst).items()):
            if k.startswith("__"):
                continue
            try:
                out[k] = canon.encode(v)
            except Exception:
                out[k] = "<unencodable>"
        return out
    return {}


def _load_props(path):
    if not path:
        return []
    ns = {"math": math, "copy": copy, "itertools": itertools, "collections": collections}
    exec(compile(open(path).read(), path, "exec"), ns)
    return [(k, v) for k, v in ns.items() if k.startswith("prop_") and callable(v)]


def _resolve_callable(mod, entry, ctor_args=None):
    """Resolve `fn` or `Class.method`, returning `(callable_obj, instance_or_None, is_property)`."""
    if "." not in entry:
        return getattr(mod, entry), None, False
    cls_name, meth_name = entry.split(".", 1)
    cls = getattr(mod, cls_name)
    raw_attr = inspect.getattr_static(cls, meth_name)
    if isinstance(raw_attr, staticmethod):
        return getattr(cls, meth_name), None, False
    if isinstance(raw_attr, classmethod):
        return getattr(cls, meth_name), None, False
    inst = cls(*(ctor_args or []))
    if isinstance(raw_attr, property):
        return (lambda: getattr(inst, meth_name)), inst, True
    return getattr(inst, meth_name), inst, False


def _exec_script_case(res, st, code, src, case, cfg, canon, Tracer):
    """B3: Execute entire module as `__main__` with injected stdin/argv."""
    raw_args = case.get("args") or []
    spec = raw_args[0] if raw_args and isinstance(raw_args[0], dict) else {}
    stdin_text = str(spec.get("stdin", ""))
    argv = [src] + [str(x) for x in (spec.get("argv") or [])]

    mod = types.ModuleType("__main__")
    mod.__file__ = src
    mod.__name__ = "__main__"
    old_stdin, old_argv = sys.stdin, sys.argv
    sys.stdin = io.StringIO(stdin_text)
    sys.argv = argv
    st["stage"] = "call"
    tracer = Tracer(src) if cfg.get("cov") else None
    exit_code = 0
    ok = False
    try:
        if tracer:
            tracer.start()
        t0 = time.perf_counter()
        try:
            exec(code, mod.__dict__)
            ok = True
        except SystemExit as se:
            exit_code = se.code if isinstance(se.code, int) else (0 if se.code is None else 1)
            ok = True
        finally:
            res["elapsed_s"] = time.perf_counter() - t0
            if tracer:
                tracer.stop()
    except _Timeout:
        raise
    except BaseException as e:
        res["status"] = "exception"
        res["exc_type"] = type(e).__name__
        res["exc_msg"] = str(e)[:500]
    finally:
        sys.stdin = old_stdin
        sys.argv = old_argv

    if tracer:
        res["edges"] = tracer.result()
    if ok:
        ret_val = {"exit_code": exit_code}
        res["return_type"] = "script"
        res["alias"] = []
        if cfg.get("digest", "off") == "off":
            res["ret"] = ret_val
        else:
            res["ret_digest"] = canon.digest(ret_val, False)
    res["mut"] = {}
    res["glob"] = {}


def _execute(res, st, code, src, case, cfg, canon, Tracer, props):
    random.seed(cfg["rand_seed"])
    if "numpy" in sys.modules:
        try:
            sys.modules["numpy"].random.seed(cfg["rand_seed"] % 2 ** 32)
        except Exception:
            pass

    if cfg["entry"] == "__script__":
        _exec_script_case(res, st, code, src, case, cfg, canon, Tracer)
        return

    mod = types.ModuleType("target_mod")
    mod.__file__ = src
    sys.modules["target_mod"] = mod

    # Guard against blocking input() at import time (Workstream B6)
    orig_input = builtins.input

    def _blocked_import_input(*a, **kw):
        raise RuntimeError("input() called at module import time")

    builtins.input = _blocked_import_input
    try:
        exec(code, mod.__dict__)  # fresh module state for every case
    finally:
        builtins.input = orig_input

    ctor_args = canon.decode(cfg.get("ctor_args", []), mod.__dict__) if cfg.get("ctor_args") else []
    fn, inst, _ = _resolve_callable(mod, cfg["entry"], ctor_args=ctor_args)
    if hasattr(fn, "cache_clear"):
        try:
            fn.cache_clear()
        except Exception:
            pass

    args = list(canon.decode(case["args"], mod.__dict__))
    kwargs = {k: canon.decode(v, mod.__dict__) for k, v in case["kwargs"].items()}
    before = [_j(canon.encode(a)) for a in args]
    before_kw = {k: _j(canon.encode(v)) for k, v in kwargs.items()}
    self_before = _j(_snap_obj_state(inst, canon)) if inst is not None else None
    g_before = {k: _j(v) for k, v in _snap_globals(mod, canon).items()}
    st["stage"] = "call"
    tracer = Tracer(src) if cfg["cov"] else None
    ret, ok = None, False
    try:
        try:
            if tracer:
                tracer.start()
            t0 = time.perf_counter()
            try:
                ret = fn(*args, **kwargs)
                if inspect.iscoroutine(ret):
                    ret = asyncio.run(ret)
                elif inspect.isgenerator(ret):
                    ret = list(itertools.islice(ret, 10000))
                    res["generator"] = True
                res["elapsed_s"] = time.perf_counter() - t0
                ok = True
            finally:
                if tracer:
                    tracer.stop()
        except _Timeout:
            raise
        except BaseException as e:  # exception raised BY the target
            res["status"] = "exception"
            res["exc_type"] = type(e).__name__
            res["exc_msg"] = str(e)[:500]
    except _Timeout:
        raise
    if tracer:
        res["edges"] = tracer.result()

    digest_mode = cfg["digest"]
    if ok:
        enc = canon.encode(ret)
        res["return_type"] = type(ret).__name__
        res["alias"] = [i for i, a in enumerate(args) if a is ret]
        if digest_mode == "off":
            res["ret"] = enc
        else:
            res["ret_digest"] = canon.digest(enc, digest_mode == "multiset")

    mut = {}
    for i, a in enumerate(args):
        e = canon.encode(a)
        if _j(e) != before[i]:
            mut[f"arg{i}"] = e
    for k, v in kwargs.items():
        e = canon.encode(v)
        if _j(e) != before_kw[k]:
            mut[f"kw:{k}"] = e
    if inst is not None:
        self_after_dict = _snap_obj_state(inst, canon)
        if _j(self_after_dict) != self_before:
            mut["self"] = self_after_dict
    if digest_mode != "off":
        mut = {k: canon.digest(v) for k, v in mut.items()}
    res["mut"] = mut
    g_after = _snap_globals(mod, canon)
    res["glob"] = {k: v for k, v in g_after.items() if g_before.get(k) != _j(v)}

    if ok and props:
        fails = []
        for name, p in props:
            try:
                a2 = list(canon.decode(case["args"], mod.__dict__))
                k2 = {k: canon.decode(v, mod.__dict__) for k, v in case["kwargs"].items()}
                if not p(fn, a2, k2, ret):
                    fails.append(name)
            except _Timeout:
                raise
            except BaseException:
                fails.append(name + "!")
        res["prop_failures"] = fails


def _run_one(code, src, case, cfg, canon, Tracer, props, alarm):
    res = {"status": "ok"}
    st = {"stage": "load"}
    buf = io.StringIO()
    try:
        if alarm:
            signal.setitimer(signal.ITIMER_REAL, cfg["timeout"])
        with contextlib.redirect_stdout(buf):
            _execute(res, st, code, src, case, cfg, canon, Tracer, props)
    except _Timeout:
        res["status"] = "timeout"
    except BaseException as e:
        res["status"] = "exception" if st["stage"] == "call" else "load_error"
        res["exc_type"] = type(e).__name__
        res["exc_msg"] = str(e)[:500]
    finally:
        if alarm:
            signal.setitimer(signal.ITIMER_REAL, 0)
    res["stdout"] = buf.getvalue()[:20000]
    return res


def main():
    pkg_root, src, cases_p, out_p, cfg_p = sys.argv[1:6]
    sys.path.pop(0)
    sys.path.insert(0, pkg_root)
    sys.path.insert(0, os.path.dirname(os.path.abspath(src)))
    from optagent.runtime import canon
    from optagent.runtime.cov import Tracer

    cfg = json.load(open(cfg_p))
    if cfg.get("recursion_limit") and int(cfg["recursion_limit"]) > 0:
        sys.setrecursionlimit(int(cfg["recursion_limit"]))
    code = compile(open(src, encoding="utf-8").read(), src, "exec")
    props = _load_props(cfg.get("props_path"))
    alarm = hasattr(signal, "setitimer")
    if alarm:
        signal.signal(signal.SIGALRM, _on_alarm)
    out = open(out_p, "a", encoding="utf-8")
    with open(cases_p, encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx < cfg["start"]:
                continue
            res = _run_one(code, src, json.loads(line), cfg, canon, Tracer, props, alarm)
            res["idx"] = idx
            try:
                text = json.dumps(res)
            except Exception as e:
                text = json.dumps({"idx": idx, "status": "crash", "exc_msg": f"unserialisable result: {e}"})
            out.write(text + "\n")
            out.flush()
    out.write('{"done": true}\n')
    out.flush()
    out.close()
    os._exit(0)


if __name__ == "__main__":
    main()
