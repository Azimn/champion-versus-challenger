# EXP-008 Reviewer Generation 2

## Frozen production under test

- Production commit: `c42a43d353b21061b97cabb665e8ef59544d27c9`
- Reviewer source was created only after that repair freeze.
- Workflow run: `35061378333`
- Artifact: `exp008-review2`, artifact ID `10432691986`
- The workflow explicitly ran `git diff --exit-code c42a43d353b21061b97cabb665e8ef59544d27c9 -- src/lifelike_min/exp008_challenger.py` before executing the reviewer. The production file was unchanged.

## Result

Nine of ten probes passed. One probe failed:

- `matching_negative_only`

The observed pre-observation habit state contained only:

`('search_task:find_home;entity:book', 'search:drawer') -> -0.7`

There was no learned negative `search:shelf` entry before direct observation. After observation, the drawer entry was correctly absent/neutral and the shelf lookup was also neutral because no shelf habit had ever been learned.

## Failure classification before repair

**Classification: invalid reviewer assumption.**

The reviewer attempted to learn negative values for two different search actions (`search:drawer` and `search:shelf`) in the same derived experienced context (`find_home + book`) without allowing the first eligibility candidate to expire or otherwise disambiguating causal attribution.

EXP-007 established a conservative contract: if more than one live action is eligible in the same experienced context, a later outcome does not infer which action caused it. `EligibilityTraceCharacter._apply_delayed_outcome` therefore abstains when the set of candidate actions has cardinality other than one.

Consequently, the reviewer assumed a second negative learned value existed even though the already-earned temporal-credit semantics deliberately prevented that value from being created. This is a test-assumption failure, not evidence that EXP-008 cleared an unrelated learned location value.

## Preservation rule

The failing reviewer source remains unchanged. It is not deleted or rewritten.

Any follow-up diagnostic for the intended claim, namely that direct observation of location A does not clear a genuinely existing negative search value for location B, must create those learned values under causally unambiguous histories, such as distinct task contexts or sufficient trace separation. That follow-up is additional evidence and does not retroactively convert the original reviewer result into a pass.

## Other reviewer-2 findings

The untouched generation also showed that, under its tested histories:

- positive search experience survived direct observation;
- another entity's negative search experience survived;
- non-search habit state survived;
- hidden-world change did not trigger invalidation;
- percent-encoded Unicode/delimiter-heavy actor identity remained specific;
- same entity/location negative values across two search-task contexts were invalidated;
- one delayed old negative outcome arriving after reobservation remained proportionate and did not immediately overpower the direct-location prior;
- invalidation survived serialization/reconstruction;
- direct observation did not erase a live eligibility record.

These passes do not by themselves justify promotion. Semantic interpretation of the learned scalar remains an open mandatory closeout question.
