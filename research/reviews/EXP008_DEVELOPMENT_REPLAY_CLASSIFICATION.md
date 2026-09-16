# EXP-008 Development Replay Classification

## Context

Complete closeout run `35061745029` replayed the current repository regression suite and v9.1 structural closeout before replaying the EXP-008 development evaluation.

The repository suite passed 61/61 tests. The explicit v9.1 structural closeout also passed in full. The frozen EXP-008 production file remained unchanged from `c42a43d353b21061b97cabb665e8ef59544d27c9`.

The EXP-008 development replay then reported two failing development probes:

- `contradictory_outcomes`
- `unknown_entity_control`

All historical, earned, EXP-007, renderer, serialization, zero-new-field, and zero-new-mechanism gates remained green.

## Classification before any correction

Both failures are **invalid development-test assumptions under the already-established EXP-007 same-context ambiguity contract**.

### `contradictory_outcomes`

The probe first trains negative `search:drawer` experience and then allows the policy to choose `search:shelf` in the same derived search context. It subsequently forces `search:drawer` and supplies positive outcomes while both drawer and shelf remain live eligibility candidates for the same experienced context.

EXP-007 deliberately abstains from delayed credit when more than one distinct action remains eligible in one context. Therefore the positive outcomes are not assigned to drawer, so the scalar stays at `-1.0`. The probe assumes recovery should occur despite intentionally ambiguous attribution.

### `unknown_entity_control`

The probe first lets the unknown entity choose `search:desk`, creating one live eligibility record. It then forces `search:shelf` in the same target/task context and immediately supplies a positive outcome. Both desk and shelf are now plausible eligible causes, so EXP-007 correctly abstains. The probe assumes shelf should learn anyway.

## Scientific treatment

The original development evaluation remains unchanged and its failures remain part of the record. They are not silently deleted or retroactively relabeled as passes.

For closeout, these two specific checks may be treated as obsolete/invalid assumptions only because their failure mechanism is directly explained by an earlier promoted contract that predates EXP-008: conservative abstention under same-context multi-action ambiguity.

Any follow-up diagnostic that tests contradictory-value reversibility or unknown-entity learning must provide causally unambiguous experienced histories, for example by allowing earlier eligibility to expire before crediting a different action. Such a follow-up is additional evidence, not a rewrite of the original development result.
