from __future__ import annotations
import argparse, json
from pathlib import Path
from . import mbase001_audit_v2 as v2
from .runtime import Event
MECHANISMS=v2.MECHANISMS; BasisAblationCharacter=v2.BasisAblationCharacter

def probe_ambiguity(enabled):
    control=BasisAblationCharacter(enabled)
    control.step(Event(kind="context",context="control",forced_action="inspect"))
    control.step(Event(kind="outcome",context="control",reward=1.0,forced_action="idle"))
    unambiguous=control.habits.get(("control","inspect"),0.0)>0
    a=BasisAblationCharacter(enabled)
    a.step(Event(kind="context",context="lab",forced_action="inspect")); a.step(Event(kind="context",context="lab",forced_action="wait")); before=dict(a.habits); a.step(Event(kind="outcome",context="lab",reward=1.0,forced_action="idle"))
    return unambiguous and a.habits==before

PROBES=dict(v2.PROBES); PROBES["ambiguity_abstention"]=probe_ambiguity

def evaluate_subset(enabled):
    enabled=tuple(enabled); outcomes={}; errors={}
    for name,probe in PROBES.items():
        try: outcomes[name]=bool(probe(enabled))
        except Exception as exc: outcomes[name]=False; errors[name]=f"{type(exc).__name__}: {exc}"
    sample=BasisAblationCharacter(enabled)
    return {"enabled":list(enabled),"count":len(enabled),"structurally_valid":not errors,"capabilities":outcomes,"coverage":sum(outcomes.values()),"total_capabilities":len(outcomes),"full_coverage":all(outcomes.values()),"fresh_projected_canonical_bytes":sample.audit_canonical_bytes(),"errors":errors}

def run():
    rows=[evaluate_subset([m for i,m in enumerate(MECHANISMS) if mask&(1<<i)]) for mask in range(1<<len(MECHANISMS))]; full=rows[-1]; frontier={}
    for n in range(len(MECHANISMS)+1):
        group=[r for r in rows if r["count"]==n]; best=max(r["coverage"] for r in group); winners=[r for r in group if r["coverage"]==best]; frontier[str(n)]={"best_coverage":best,"total_capabilities":full["total_capabilities"],"best_subsets":[r["enabled"] for r in winners[:20]],"best_subset_count":len(winners)}
    full_rows=[r for r in rows if r["full_coverage"]]; minimum=min((r["count"] for r in full_rows),default=None); allset=set(MECHANISMS); single={}
    for m in MECHANISMS:
        row=next(r for r in rows if set(r["enabled"])==allset-{m}); single[m]={"coverage":row["coverage"],"lost":[k for k,v in row["capabilities"].items() if not v]}
    return {"audit":"MBASE-001","pass":3,"methodology_corrections":["relationship probe isolates global affect decay","ambiguity abstention requires successful unambiguous learning control"],"champion":"v9.3_concern_capacity_three","champion_commit":"a10bc27579bf5bd0ff1a90d6ad6e3f337d8ed7bc","mechanisms":list(MECHANISMS),"fixed_capacities":{"concerns":3,"prospective":2,"eligibility":2},"subset_count":len(rows),"full_reference":full,"minimum_full_coverage_count":minimum,"minimal_full_coverage_subsets":[r["enabled"] for r in full_rows if r["count"]==minimum],"full_coverage_subset_count":len(full_rows),"single_ablation":single,"coverage_frontier":frontier,"rows":rows}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",type=Path); a=p.parse_args(); r=run(); print(json.dumps({k:v for k,v in r.items() if k!="rows"},indent=2,sort_keys=True));
    if a.json: a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
