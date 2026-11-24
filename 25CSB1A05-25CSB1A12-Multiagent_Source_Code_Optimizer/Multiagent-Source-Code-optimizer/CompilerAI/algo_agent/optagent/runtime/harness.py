"""Runs ONE call of the target function/method/script. argv: pkg_root src_path payload_path out_path"""
import asyncio
import builtins
import contextlib
import importlib.util
import inspect
import io
import itertools
import json
import os
import sys
import time
import types


def _snap_globals(mod, canon):
    out = {}
    for k, v in vars(mod).items():
        if k.startswith("__") or callable(v) or inspect.ismodule(v):
            continue
        try:
            out[k] = canon.encode(v)
        except Exception:
            out[k] = "<unencodable>"
    return out


def _snap_obj_state(inst, canon):
    if inst is None or not hasattr(inst, "__dict__"):
        return {}
    out = {}
    for k, v in vars(inst).items():
        if k.startswith("__"):
            continue
        try:
            out[k] = canon.encode(v)
        except Exception:
            out[k] = "<unencodable>"
    return out


def _resolve_callable(mod, entry, ctor_args=None):
    if "." not in entry:
        return getattr(mod, entry), None
    cls_name, meth_name = entry.split(".", 1)
    cls = getattr(mod, cls_name)
    raw_attr = inspect.getattr_static(cls, meth_name)
    if isinstance(raw_attr, (staticmethod, classmethod)):
        return getattr(cls, meth_name), None
    inst = cls(*(ctor_args or []))
    if isinstance(raw_attr, property):
        return (lambda: getattr(inst, meth_name)), inst
    return getattr(inst, meth_name), inst


def main():
    pkg_root, src, payload_p, out_p = sys.argv[1:5]
    sys.path.pop(0)  # drop harness dir
    sys.path.insert(0, pkg_root)
    sys.path.insert(0, os.path.dirname(os.path.abspath(src)))
    from optagent.runtime import canon

    payload = json.load(open(payload_p, encoding="utf-8"))
    res = {"status": "ok"}
    buf = io.StringIO()
    args = kwargs = before = before_kw = before_g = mod = inst = self_before = None

    if payload["entry"] == "__script__":
        raw_args = payload.get("args") or []
        spec = raw_args[0] if raw_args and isinstance(raw_args[0], dict) else {}
        stdin_text = str(spec.get("stdin", ""))
        argv = [src] + [str(x) for x in (spec.get("argv") or [])]
        old_stdin, old_argv = sys.stdin, sys.argv
        sys.stdin = io.StringIO(stdin_text)
        sys.argv = argv
        try:
            code = compile(open(src, encoding="utf-8").read(), src, "exec")
            script_mod = types.ModuleType("__main__")
            script_mod.__file__ = src
            script_mod.__name__ = "__main__"
            exit_code = 0
            with contextlib.redirect_stdout(buf):
                t0 = time.perf_counter()
                try:
                    exec(code, script_mod.__dict__)
                except SystemExit as se:
                    exit_code = se.code if isinstance(se.code, int) else (0 if se.code is None else 1)
                except BaseException as e:
                    res["status"] = "exception"
                    res["exc_type"] = type(e).__name__
                    res["exc_msg"] = str(e)[:500]
                res["elapsed_s"] = time.perf_counter() - t0
            if res["status"] == "ok":
                res["return"] = {"exit_code": exit_code}
                res["return_type"] = "script"
                res["returns_input_alias"] = []
        except BaseException as e:
            res["status"] = "load_error"
            res["exc_type"] = type(e).__name__
            res["exc_msg"] = str(e)[:500]
        finally:
            sys.stdin = old_stdin
            sys.argv = old_argv
    else:
        try:
            spec = importlib.util.spec_from_file_location("target_mod", src)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["target_mod"] = mod
            orig_input = builtins.input

            def _blocked_input(*a, **kw):
                raise RuntimeError("input() called at module import time")

            with contextlib.redirect_stdout(buf):
                builtins.input = _blocked_input
                try:
                    spec.loader.exec_module(mod)
                finally:
                    builtins.input = orig_input

                fn, inst = _resolve_callable(mod, payload["entry"])
                if hasattr(fn, "cache_clear"):
                    try:
                        fn.cache_clear()
                    except Exception:
                        pass
                args = list(canon.decode(payload["args"], mod.__dict__))
                kwargs = canon.decode(payload["kwargs"], mod.__dict__)
                before = [canon.encode(a) for a in args]
                before_kw = {k: canon.encode(v) for k, v in kwargs.items()}
                self_before = _snap_obj_state(inst, canon) if inst is not None else None
                before_g = _snap_globals(mod, canon)
                t0 = time.perf_counter()
                try:
                    ret = fn(*args, **kwargs)
                    if inspect.iscoroutine(ret):
                        ret = asyncio.run(ret)
                    elif inspect.isgenerator(ret):
                        ret = list(itertools.islice(ret, 10000))
                        res["generator"] = True
                    res["elapsed_s"] = time.perf_counter() - t0
                    res["return"] = canon.encode(ret)
                    res["return_type"] = type(ret).__name__
                    res["returns_input_alias"] = [i for i, a in enumerate(args) if a is ret]
                except BaseException as e:  # exception from the TARGET call
                    res["status"] = "exception"
                    res["exc_type"] = type(e).__name__
                    res["exc_msg"] = str(e)[:500]
        except BaseException as e:  # import / setup failure
            res["status"] = "load_error"
            res["exc_type"] = type(e).__name__
            res["exc_msg"] = str(e)[:500]

    if before is not None:
        try:
            after = [canon.encode(a) for a in args]
            after_kw = {k: canon.encode(v) for k, v in kwargs.items()}
            mutated = [f"arg{i}" for i, (a, b) in enumerate(zip(before, after)) if a != b] + [
                f"kw:{k}" for k in before_kw if before_kw[k] != after_kw.get(k)
            ]
            if inst is not None and _snap_obj_state(inst, canon) != self_before:
                mutated.append("self")
            res["mutated_args"] = mutated
            after_g = _snap_globals(mod, canon)
            res["globals_changed"] = sorted(
                k for k in set(before_g) | set(after_g) if before_g.get(k) != after_g.get(k)
            )
        except Exception:
            pass
    res["stdout"] = buf.getvalue()[:20000]
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(res, f)
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
