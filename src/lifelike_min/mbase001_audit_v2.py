from __future__ import annotations

import argparse, json
from pathlib import Path

from . import mbase001_audit as v1
from .runtime import Event

MECHANISMS=v1.MECHANISMS
BasisAblationCharacter=v1.BasisAblationCharacter

def probe_relationship(enabled):
    a=BasisAblationCharacter(enabled)
    for _ in range(3):
        a.step(Event(kind="hostility", actor="morgan", intensity=1.0, forced_action="idle"))
    # Isolate persistent partner history from the global affect transient.
    for _ in range(35):
        a.step(Event(kind="neutral", forced_action="idle"))
    m=a.step(Event(kind="neutral", actor="morgan", available_actions=("idle","avoid:morgan")))
    s=a.step(Event(kind="neutral", actor="sarah", available_actions=("idle","avoid:sarah")))
    return m=="avoid:morgan" and s=="idle"

PROBES=dict(v1.PROBES)
PROBES["partner_specific_relationship_history"]=probe_relationship

def evaluate_subset(enabled):
    enabled=tuple(enabled); outcomes={}; errors={}
    for name,probe in PROBES.items():
        try: outcomes[name]=bool(probe(enabled))
        except Exception as exc: outcomes[name]=False; errors[name]=f"{type(exc).__name__}: {exc}"
    sample=BasisAblationCharacter(enabled)
    return {"enabled":list(enabled),"count":len(enabled),"structurally_valid":not errors,"capabilities":outcomes,"coverage":sum(outcomes.values()),"total_capabilities":len(outcomes),"full_coverage":all(outcomes.values()),"fresh_projected_canonical_bytes":sample.audit_canonical_bytes(),"errors":errors}

def run():
    rows=[]
    for mask in range(1<<len(MECHANISMS)):
        rows.append(evaluate_subset([m for i,m in enumerate(MECHANISMS) if mask&(1<<i)]))
    full=rows[-1]; frontier={}
    for n in range(len(MECHANISMS)+1):
        group=[r for r in rows if r["count"]==n]; best=max(r["coverage"] for r in group); winners=[r for r in group if r["coverage"]==best]
        frontier[str(n)]={"best_coverage":best,"total_capabilities":full["total_capabilities"],"best_subsets":[r["enabled"] for r in winners[:20]],"best_subset_count":len(winners)}
    full_rows=[r for r in rows if r["full_coverage"]]; minimum=min((r["count"] for r in full_rows),default=None); minimal=[r for r in full_rows if r["count"]==minimum]
    allset=set(MECHANISMS); single={}
    for m in MECHANISMS:
        row=next(r for r in rows if set(r["enabled"])==allset-{m}); single[m]={"coverage":row["coverage"],"lost":[k for k,v in row["capabilities"].items() if not v]}
    return {"audit":"MBASE-001","pass":2,"methodology_correction":"relationship probe waits for global affect decay before partner-specific behavioral comparison","champion":"v9.3_concern_capacity_three","champion_commit":"a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc","mechanisms":list(MECHANISMS),"fixed_capacities":{"concerns":3,"prospective":2,"eligibility":2},"subset_count":len(rows),"full_reference":full,"minimum_full_coverage_count":minimum,"minimal_full_coverage_subsets":[r["enabled"] for r in minimal],"full_coverage_subset_count":len(full_rows),"single_ablation":single,"coverage_frontier":frontier,"rows":rows}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); print(json.dumps({k:v for k,v in r.items() if k!="rows"},indent=2,sort_keys=True));
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
