# Champion Lineage

The champion lineage records only experimentally earned champions. A system is not entered as Champion 0 because it is famous, theoretically attractive, recently implemented, or convenient to modify.

## Current state

**Champion:** Unassigned  
**Reason:** No candidate has yet completed the common baseline qualification battery in this repository.  
**Frozen reference:** None  
**Promotion experiment:** None

## Promotion requirements

A proposed champion must have a preserved, versioned implementation reference; an adapter that does not rewrite its decision architecture; common scenario traces; longitudinal behavioral measures; old-school performance measurements; and a documented artificiality attack.

For later challengers, promotion additionally requires paired comparison against the frozen champion under identical experiences and an ablation when the challenger introduces or replaces a mechanism.

A challenger can be rejected for meaningful regressions even if its aggregate score rises. Essential behavioral dimensions are not freely exchangeable.

## Lineage table

| Champion | System/version | Promoted by | Target improvement | Regressions accepted | Status |
| --- | --- | --- | --- | --- | --- |
| C0 | Unassigned | None | Baseline qualification | None | Pending |

## Freeze rule

Once a champion is named for an experiment series, its code, configuration, adapter, scenario mappings, and dependency environment are frozen for that series. Bug fixes or configuration changes create a new candidate reference. They are not silently applied to the champion during comparison.
