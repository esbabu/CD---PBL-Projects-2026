from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # ---- Step 1 ----
    spec_model: str = os.getenv("OPT_SPEC_MODEL", "ollama_chat/qwen2.5-coder:7b")
    predictor_model: str = os.getenv("OPT_PREDICTOR_MODEL", "ollama_chat/llama3.1:8b")
    ollama_base: str = os.getenv("OPT_API_BASE", "http://localhost:11434")
    num_ctx: int = 8192
    temperature: float = 0.0
    llm_timeout_s: int = 240
    llm_max_repairs: int = 3
    exec_timeout_s: float = 5.0
    exec_mem_mb: int = 1024
    max_sample_inputs: int = 12
    max_predictor_inputs: int = 8
    agreement_threshold: float = 0.8
    max_refine_rounds: int = 3
    runs_dir: str = "runs"
    # ---- Step 2: sandbox ----
    sandbox_backend: str = os.getenv("OPT_SANDBOX", "auto")      # auto | docker | local
    docker_image: str = os.getenv("OPT_DOCKER_IMAGE", "python:3.12-slim")
    docker_mem: str = "1g"
    docker_cpus: str = "1"
    case_timeout_s: float = 2.0
    batch_size: int = 256
    workers: int = max(1, (os.cpu_count() or 2) // 2)
    rand_seed: int = 20240607
    # ---- Step 2: corpus ----
    n_family: int = 120
    n_hypothesis: int = 300
    n_probe: int = 24
    n_adversarial: int = 20
    max_collection_len: int = 40
    fuzz_budget_s: float = 90.0
    fuzz_batch: int = 128
    fuzz_patience: int = 5
    fuzz_max_rounds: int = 40
    holdout_pct: int = 30
    strict_probes: bool = False        # True: failures on type-confusion probes fail the check
    fresh_default: int = 200
    # ---- Step 2: mutation testing ----
    max_mutants: int = 60
    mutant_case_timeout_s: float = 2.0
    hunt_inputs_per_survivor: int = 384
    hunt_max_survivors: int = 12
    # ---- Step 2: scaling set ----
    scale_sizes: tuple = (10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000)
    scale_timeout_s: float = 10.0
    scale_budget_s: float = 3.0
    # ---- Step 3: complexity analyzer ----
    empirical_budget_s: float = float(os.getenv("OPT_EMPIRICAL_BUDGET_S", "5.0"))
    empirical_min_r2: float = float(os.getenv("OPT_EMPIRICAL_MIN_R2", "0.85"))
    profile_case_count: int = int(os.getenv("OPT_PROFILE_CASE_COUNT", "10"))
    # ---- Step 5: verification ladder ----
    ladder_fresh_inputs: int = int(os.getenv("OPT_LADDER_FRESH_INPUTS", "10000"))
    ladder_fuzz_budget_s: float = float(os.getenv("OPT_LADDER_FUZZ_BUDGET_S", "3.0"))
    diffcov_min_ratio: float = float(os.getenv("OPT_DIFFCOV_MIN_RATIO", "1.0"))
    enable_symbolic: bool = os.getenv("OPT_ENABLE_SYMBOLIC", "0") == "1"
    enable_formal: bool = os.getenv("OPT_ENABLE_FORMAL", "0") == "1"
    enable_llm_reviewer: bool = os.getenv("OPT_ENABLE_LLM_REVIEWER", "0") == "1"
    # ---- Step 6: benchmarking & search ----
    bench_warmups: int = int(os.getenv("OPT_BENCH_WARMUPS", "2"))
    bench_reps: int = int(os.getenv("OPT_BENCH_REPS", "5"))
    bench_noise_threshold: float = float(os.getenv("OPT_BENCH_NOISE_THRESHOLD", "0.05"))
    search_beam_width: int = int(os.getenv("OPT_SEARCH_BEAM_WIDTH", "3"))
    search_max_depth: int = int(os.getenv("OPT_SEARCH_MAX_DEPTH", "3"))
    search_max_candidates: int = int(os.getenv("OPT_SEARCH_MAX_CANDIDATES", "15"))
    search_budget_s: float = float(os.getenv("OPT_SEARCH_BUDGET_S", "60.0"))
    # ---- Step 7: reporter & memory ----
    memory_db_path: str = os.getenv("OPT_MEMORY_DB", "runs/memory.db")
    # ---- Multi-language support (JS, C, C++) ----
    js_docker_image: str = os.getenv("OPT_JS_DOCKER_IMAGE", "optagent-sandbox-js:latest")
    native_docker_image: str = os.getenv("OPT_NATIVE_DOCKER_IMAGE", "optagent-sandbox-native:latest")
    compile_timeout_s: float = float(os.getenv("OPT_COMPILE_TIMEOUT_S", "30.0"))
    c_flags: tuple[str, ...] = ("-std=c11", "-O2", "-g", "-fno-omit-frame-pointer", "-ffp-contract=off", "-fno-fast-math")
    cpp_flags: tuple[str, ...] = ("-std=c++17", "-O2", "-g", "-fno-omit-frame-pointer", "-ffp-contract=off", "-fno-fast-math")
    allow_local_native: bool = os.getenv("OPT_ALLOW_LOCAL_NATIVE", "0") == "1"
    enable_sanitizers: bool = os.getenv("OPT_ENABLE_SANITIZERS", "1") == "1"
    enable_cbmc: bool = os.getenv("OPT_ENABLE_CBMC", "0") == "1"
    cbmc_unwind: int = int(os.getenv("OPT_CBMC_UNWIND", "16"))
    # ---- Repair & Hardening: Ollama Gateway & Robustness ----
    llm_mode: str = os.getenv("OPT_LLM_MODE", "assist")          # off | assist | required
    proposer_model: str = os.getenv("OPT_PROPOSER_MODEL", "qwen2.5-coder:7b")
    judge_model: str = os.getenv("OPT_JUDGE_MODEL", "llama3.1:8b")
    num_ctx_max: int = int(os.getenv("OPT_NUM_CTX_MAX", "16384"))
    llm_connect_timeout_s: float = float(os.getenv("OPT_LLM_CONNECT_TIMEOUT_S", "5.0"))
    llm_read_timeout_s: float = float(os.getenv("OPT_LLM_READ_TIMEOUT_S", "600.0"))
    llm_concurrency: int = int(os.getenv("OPT_LLM_CONCURRENCY", "1"))
    llm_cache: bool = os.getenv("OPT_LLM_CACHE", "1") != "0"
    max_model_gb: float = float(os.getenv("OPT_MAX_MODEL_GB", "16.0"))
    py_images: tuple[str, ...] = tuple(x.strip() for x in os.getenv("OPT_PY_IMAGES", "").split(",") if x.strip())
    max_source_bytes: int = int(os.getenv("OPT_MAX_SOURCE_BYTES", str(512 * 1024)))
    harness_recursion_limit: int = int(os.getenv("OPT_HARNESS_RECURSION_LIMIT", "0"))
    syntax_fix_mode: str = os.getenv("OPT_SYNTAX_FIX", "auto")
    module_mode: bool = os.getenv("OPT_MODULE_MODE", "0") == "1"