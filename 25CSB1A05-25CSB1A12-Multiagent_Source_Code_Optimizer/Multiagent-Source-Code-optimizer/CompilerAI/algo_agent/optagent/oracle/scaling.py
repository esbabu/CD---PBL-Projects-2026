"""Build the scaling set: run the original on families of inputs at increasing sizes
to record timing and output digests for empirical complexity fitting (Step 3)."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..config import Settings
from ..runtime.sandbox import RunOpts, Sandbox
from .schema_infer import Gen, ParamSchema, scalable
from .schemas import Case, ScalePoint

if TYPE_CHECKING:
    pass


def scale_case(ps: ParamSchema, p: ScalePoint) -> Case:
    """Re-create a Case from a ScalePoint for checking candidate behaviour."""
    return Case(id=f"scale:{p.family}:{p.mode}:{p.n}",
                args=p.args, kwargs=p.kwargs,
                origin="scale", category="scale", kind="valid",
                size=p.n)


def build_scaling(sb: Sandbox, src, entry: str, ps: ParamSchema,
                  multiset: bool, s: Settings, log=print) -> list[ScalePoint]:
    """Run the original on the scaling grid and return ScalePoint records."""
    import random
    import hashlib
    import json

    if not any(scalable(v) for v in ps.args):
        log("[oracle/scaling] no scalable argument found; scaling set skipped")
        return []

    rng = random.Random(s.rand_seed ^ 0xCAFE)
    gen = Gen(ps, rng, s.max_collection_len)
    sizes = list(s.scale_sizes)
    families = ["random", "sorted", "few_unique"]
    modes = ["hit", "miss"] if any(v.derived for v in ps.args) else ["hit"]
    digest_mode = "multiset" if multiset else "exact"

    all_points: list[ScalePoint] = []
    budget_left = s.scale_budget_s
    t_start = time.time()

    for n in sizes:
        if budget_left <= 0:
            log(f"[oracle/scaling] budget exhausted at n={n}")
            break
        for fam in families:
            for mode in modes:
                args, kwargs = gen.scaled(fam, n, mode)
                enc_args = _encode(args)
                enc_kwargs = {k: _encode(v) for k, v in kwargs.items()}
                c = Case(id=f"scale:{fam}:{mode}:{n}",
                         args=enc_args, kwargs=enc_kwargs,
                         origin="scale", category="scale", kind="valid", size=n)
                t0 = time.time()
                res = sb.run_batch(src, entry, [c],
                                   RunOpts(timeout=s.scale_timeout_s, digest=digest_mode))
                elapsed = time.time() - t0
                budget_left -= elapsed
                r = res[0]
                if r.status not in ("ok", "exception"):
                    all_points.append(ScalePoint(
                        family=fam, mode=mode, n=n,
                        args=enc_args, kwargs=enc_kwargs,
                        status=r.status))
                    continue
                # Build digest same way as compare.py::scale_digest
                digest_raw = json.dumps([r.status, r.ret_digest, r.exc_type, r.mut],
                                        sort_keys=True)
                digest = hashlib.sha1(digest_raw.encode()).hexdigest()[:16]
                all_points.append(ScalePoint(
                    family=fam, mode=mode, n=n,
                    args=enc_args, kwargs=enc_kwargs,
                    status=r.status,
                    orig_time_s=r.elapsed_s,
                    digest=digest))
                if budget_left <= 0:
                    break
            if budget_left <= 0:
                break

    total_elapsed = round(time.time() - t_start, 2)
    log(f"[oracle/scaling] {len(all_points)} scale points in {total_elapsed}s")
    return all_points


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _encode(v):
    from ..runtime import canon
    return canon.encode(v)

