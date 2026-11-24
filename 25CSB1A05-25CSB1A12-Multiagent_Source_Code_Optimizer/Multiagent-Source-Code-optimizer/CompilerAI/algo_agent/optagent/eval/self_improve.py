"""Self-improvement module: Harvesting preference data for DPO/RLHF fine-tuning."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from ..report.schemas import Report
from ..search.schemas import SearchResult
from .schemas import PreferencePair


def reward_from_candidate(tier: str, speedup: float, passed: bool) -> float:
    """Compute verification-grounded reward for RL fine-tuning."""
    if not passed or tier == "REJECTED":
        return 0.0
    tier_mult = {"T0": 0.5, "T1": 1.0, "T2": 1.5, "T3": 2.0, "T4": 2.5}.get(tier, 1.0)
    return round(math_speedup_reward(speedup) * tier_mult, 3)


def math_speedup_reward(speedup: float) -> float:
    """Logarithmic reward scaling for speedups."""
    if speedup <= 1.0:
        return 0.1
    import math
    return round(math.log2(speedup) + 1.0, 3)


class PreferenceHarvester:
    """Harvests (chosen, rejected) candidate pairs from search trajectories."""

    def harvest_from_search(
        self,
        task_name: str,
        entry_point: str,
        original_code: str,
        search_res: SearchResult,
    ) -> list[PreferencePair]:
        """Generate pairwise preferences comparing verified winners vs rejected/suboptimal candidates."""
        pairs: list[PreferencePair] = []
        if not search_res.best_candidate:
            return pairs

        best = search_res.best_candidate
        # Find best node in evaluated nodes
        best_node = next((n for n in search_res.all_evaluated if n.candidate.id == best.id), None)
        chosen_tier = best_node.evidence.tier if best_node and best_node.evidence else "T2"
        chosen_speedup = (best_node.bench.overall_speedup if best_node and best_node.bench else getattr(best_node, "speedup", 2.0)) if best_node else 2.0
        chosen_reward = reward_from_candidate(chosen_tier, chosen_speedup, passed=True)

        prompt = (
            f"# Task: Optimize Python function `{entry_point}`\n\n"
            f"Original code:\n```python\n{original_code}\n```\n\n"
            "Return the most efficient equivalent algorithm preserving all behavior."
        )

        # Pair chosen against all rejected or strictly slower candidates
        for node in search_res.all_evaluated:
            if node.candidate.id == best.id:
                continue

            rejected_cand = node.candidate
            rejected_tier = node.evidence.tier if node.evidence else "REJECTED"
            rejected_speedup = node.bench.overall_speedup if node.bench else getattr(node, "speedup", 1.0)
            passed = node.status == "verified"
            rejected_reward = reward_from_candidate(rejected_tier, rejected_speedup, passed=passed)

            margin = round(chosen_reward - rejected_reward, 3)
            if margin <= 0.05:
                continue

            rationale = (
                f"Chosen candidate achieved {chosen_speedup:.2f}x speedup at tier {chosen_tier}. "
                f"Rejected candidate had reward {rejected_reward:.2f} (tier {rejected_tier})."
            )
            if node.evidence and node.evidence.feedback:
                rationale += f" Failure feedback: {node.evidence.feedback[:120]}"

            pairs.append(
                PreferencePair(
                    task_name=task_name,
                    entry_point=entry_point,
                    prompt=prompt,
                    original_code=original_code,
                    chosen_code=best.source,
                    rejected_code=rejected_cand.source,
                    reward_chosen=chosen_reward,
                    reward_rejected=rejected_reward,
                    chosen_tier=chosen_tier,
                    rejected_tier=rejected_tier,
                    margin=margin,
                    rationale=rationale,
                )
            )

        return pairs

    @staticmethod
    def export_dpo_jsonl(pairs: Sequence[PreferencePair], output_path: str | Path) -> int:
        """Export preference pairs into standard DPO format JSONL."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with open(out_p, "w", encoding="utf-8") as f:
            for p in pairs:
                record = {
                    "task": p.task_name,
                    "prompt": p.prompt,
                    "chosen": p.chosen_code,
                    "rejected": p.rejected_code,
                    "reward_chosen": p.reward_chosen,
                    "reward_rejected": p.reward_rejected,
                    "margin": p.margin,
                    "tier_chosen": p.chosen_tier,
                    "tier_rejected": p.rejected_tier,
                    "rationale": p.rationale,
                }
                f.write(json.dumps(record) + "\n")
                count += 1
        return count
