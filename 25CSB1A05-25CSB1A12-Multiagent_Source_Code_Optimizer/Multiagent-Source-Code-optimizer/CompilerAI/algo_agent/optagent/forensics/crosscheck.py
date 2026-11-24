"""Static-vs-dynamic crosscheck: detects discrepancies between static analysis and runtime execution."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field
from .probe import DynamicFacts
from .decompose import UnitSpec, ModuleDecomposition


class AnalyzerBlindSpot(BaseModel):
    kind: str
    unit: str
    static_said: str
    dynamic_saw: str
    severity: Literal["low", "medium", "high", "critical"] = "medium"


class StaticVsDynamicCrossCheck:
    """Compares static decomposition/facts against dynamic execution to identify blind spots."""

    @classmethod
    def check_unit(
        cls,
        unit: UnitSpec,
        dyn: DynamicFacts,
        module_decomp: ModuleDecomposition | None = None,
    ) -> list[AnalyzerBlindSpot]:
        spots: list[AnalyzerBlindSpot] = []

        # 1. Global mutation check
        for g in dyn.globals_written:
            expected_tag = f"global:{g}"
            if expected_tag not in unit.implicit_outputs:
                spots.append(AnalyzerBlindSpot(
                    kind="unreported_global_mutation",
                    unit=unit.name,
                    static_said=f"implicit_outputs: {unit.implicit_outputs}",
                    dynamic_saw=f"Global variable '{g}' was mutated at runtime",
                    severity="high",
                ))

        # 2. Side-effect check (file, db, system)
        dyn_effects = {eff.kind for eff in dyn.effects}
        if "os.system" in dyn_effects and "system:command" not in unit.implicit_outputs:
            spots.append(AnalyzerBlindSpot(
                kind="unreported_system_command",
                unit=unit.name,
                static_said=f"implicit_outputs: {unit.implicit_outputs}",
                dynamic_saw="os.system called at runtime",
                severity="critical",
            ))

        if "open" in dyn_effects and "file:read" not in unit.implicit_inputs:
            spots.append(AnalyzerBlindSpot(
                kind="unreported_file_access",
                unit=unit.name,
                static_said=f"implicit_inputs: {unit.implicit_inputs}",
                dynamic_saw="open() called at runtime",
                severity="medium",
            ))

        # 3. Check import-time side effect
        if module_decomp and module_decomp.import_side_effects:
            # If unit is 'module' or runs at top level
            if unit.name == "module":
                for eff in module_decomp.import_side_effects:
                    spots.append(AnalyzerBlindSpot(
                        kind="import_time_side_effect",
                        unit="module",
                        static_said="Module level variable assignment treated as inert",
                        dynamic_saw=f"{eff.sink_type}: {eff.detail} at line {eff.lineno}",
                        severity="high",
                    ))

        return spots
