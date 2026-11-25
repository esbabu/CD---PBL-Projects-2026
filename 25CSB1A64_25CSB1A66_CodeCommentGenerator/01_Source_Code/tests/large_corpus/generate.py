"""
Generate the large-file test corpus
====================================
    python -m tests.large_corpus.generate

Writes 50 Python files of roughly 1,800-2,400 lines to ``tests/large_corpus/cases/``
and the ground truth to ``tests/large_corpus/manifest.json``.

Each file = a header + ordinary application code (``filler.TEMPLATES``) + 10
planted vulnerable snippets + 10 safe twins (``snippets``), shuffled with a
fixed seed. Rule coverage is balanced: file *i* plants rules
``(10*(i-1) + k) mod 50`` for k = 0..9, so every one of the 50 rules is planted
in exactly 10 files (500 planted vulnerabilities in total), and every rule also
appears 10 times as a safe twin.

The expected (rule, line) pairs are the ``#!`` markers in the hand-written
snippets; the analyzer is never consulted. Output is deterministic.
"""
from __future__ import annotations

import json
import os
import random
import re

from .filler import TEMPLATES
from .snippets import HEADER, SAFE, VULN

HERE = os.path.dirname(os.path.abspath(__file__))
CASES_DIR = os.path.join(HERE, "cases")
MANIFEST = os.path.join(HERE, "manifest.json")
RULE_IDS = [f"SEC{n:03d}" for n in range(1, 51)]
MARKER = re.compile(r"\s*#!\s*$")

DOMAINS = [
    ("inventory_service", "Inventory"), ("billing_engine", "Invoice"), ("customer_portal", "Customer"),
    ("shipping_tracker", "Shipment"), ("payroll_system", "Payslip"), ("library_catalog", "Book"),
    ("clinic_scheduler", "Appointment"), ("fleet_manager", "Vehicle"), ("event_ticketing", "Ticket"),
    ("hotel_booking", "Reservation"), ("course_registry", "Enrollment"), ("warehouse_robotics", "Pallet"),
    ("restaurant_orders", "Order"), ("gym_membership", "Member"), ("parking_lots", "Permit"),
    ("energy_meter", "Reading"), ("insurance_claims", "Claim"), ("loan_origination", "Loan"),
    ("crm_pipeline", "Lead"), ("helpdesk_tickets", "Incident"), ("survey_builder", "Survey"),
    ("recipe_planner", "Recipe"), ("music_streaming", "Track"), ("photo_gallery", "Album"),
    ("news_publisher", "Article"), ("job_board", "Posting"), ("real_estate", "Listing"),
    ("airline_checkin", "Boarding"), ("pharmacy_stock", "Medicine"), ("lab_results", "Sample"),
    ("school_grades", "Grade"), ("voting_portal", "Ballot"), ("charity_donations", "Donation"),
    ("car_rental", "Rental"), ("farm_sensors", "Sensor"), ("bike_sharing", "Bike"),
    ("dental_records", "Visit"), ("museum_collection", "Exhibit"), ("legal_cases", "Matter"),
    ("travel_expenses", "Expense"), ("marketplace_reviews", "Review"), ("podcast_host", "Episode"),
    ("smart_home", "Device"), ("print_shop", "PrintJob"), ("vet_clinic", "Patient"),
    ("tax_filing", "Return"), ("game_leaderboard", "Score"), ("conference_talks", "Talk"),
    ("cloud_billing", "UsageRecord"), ("city_permits", "Application"),
]
assert len(DOMAINS) == 50


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def fill(text: str, entity: str, number: str, ip_last: int) -> str:
    return (text.replace("__E__", entity).replace("__e__", snake(entity))
            .replace("__N__", number).replace("__M__", str(ip_last)))


def build_case(index: int):
    """Return (source, expected, safe_twins) for case number ``index`` (1-based)."""
    name, entity = DOMAINS[index - 1]
    rng = random.Random(1000 + index)
    vuln_rules = [RULE_IDS[(10 * (index - 1) + k) % 50] for k in range(10)]
    safe_rules = [RULE_IDS[(10 * (index - 1) + 25 + k) % 50] for k in range(10)]
    target = rng.randint(1800, 2400)

    blocks = []                    # (kind, rule, text)
    counter = 0

    def number():
        nonlocal counter
        counter += 1
        return f"{index:02d}{counter:03d}"

    for rule in vuln_rules:
        blocks.append(("vuln", rule, fill(VULN[rule], entity, number(), (index * 7 + counter) % 250 + 1)))
    for rule in safe_rules:
        blocks.append(("safe", rule, fill(SAFE[rule], entity, number(), 1)))
    lines = HEADER.count("\n") + sum(b[2].count("\n") + 2 for b in blocks)
    while lines < target:
        text = fill(rng.choice(TEMPLATES), entity, number(), 1)
        blocks.append(("filler", None, text))
        lines += text.count("\n") + 2
    rng.shuffle(blocks)

    title = f"{name.replace('_', ' ').title()} — {entity} service module."
    out = [fill(HEADER, entity, "0", 1).replace("__TITLE__", title).replace("__CASE__", f"{index:02d}").rstrip("\n")]
    expected, twins = [], []
    line_no = out[0].count("\n") + 1
    for kind, rule, text in blocks:
        body = text.strip("\n").split("\n")
        out.append("")
        out.append("")
        line_no += 2
        start = line_no + 1
        for offset, raw in enumerate(body):
            if MARKER.search(raw):
                if kind != "vuln":
                    raise AssertionError(f"marker in a {kind} block")
                expected.append({"rule": rule, "line": start + offset})
                raw = MARKER.sub("", raw)
            out.append(raw)
        line_no += len(body)
        if kind == "safe":
            twins.append({"rule": rule, "start": start, "end": start + len(body) - 1})
    source = "\n".join(out) + "\n"
    assert source.count("\n") == line_no
    if sorted(e["rule"] for e in expected) != sorted(vuln_rules):
        raise AssertionError(f"case {index}: every vulnerable snippet needs exactly one marker")
    return f"case_{index:02d}_{name}.py", source, expected, twins


def main() -> None:
    os.makedirs(CASES_DIR, exist_ok=True)
    manifest = {"description": "Large-file corpus: 50 files, 10 planted vulnerabilities and 10 safe "
                               "twins each; expected lines come from the #! markers in snippets.py.",
                "cases": []}
    total_lines = 0
    for i in range(1, 51):
        fname, source, expected, twins = build_case(i)
        with open(os.path.join(CASES_DIR, fname), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(source)
        n = source.count("\n")
        total_lines += n
        manifest["cases"].append({"file": fname, "lines": n, "expected": expected, "safe_twins": twins})
    manifest["total_lines"] = total_lines
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"wrote 50 files, {total_lines} lines, to {CASES_DIR}")


if __name__ == "__main__":
    main()
