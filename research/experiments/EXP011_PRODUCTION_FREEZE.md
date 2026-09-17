# EXP-011 production freeze

Production challenger: `src/lifelike_min/exp011_challenger.py`

Production implementation commit: `359682f463393dadeef53c8fc7a8c65eef5be8b4`

Frozen production blob SHA: `4238680bb78c21dd71b55cf279b2e4e2ce0e03a8`

Development evidence commit: `6563f8dde7838a7585edc3fef0a6905cffe3799e`

Development workflow: `35275738887`

Status: development gate passed on Python 3.11 and 3.12 after preserving and correcting the evaluator-only failure recorded in `research/reviews/EXP011_DEVELOPMENT_FAILURE_1.md`.

Frozen production mutation remains exactly:

`max_prospective = 3`

No production repair has occurred since the first challenger implementation. Reviewers generated after this record must treat the production blob above as frozen. Any later production change requires explicit failure classification, a new production freeze, unchanged replay of prior reviewers, and full regression before a second reviewer generation.
