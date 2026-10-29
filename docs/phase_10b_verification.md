# Phase10B — verification record

Branch:feature/10b-synthetic-rsm-generation.
Input Phase10A:489aa0e2b4703c0e39b0bff2623209e5a177a94b.
Integrated by merge d68aef72532ed0e39bd256b3e9dcb75f30c6a76b,identical tree;
main CI40906784465 SUCCESS Ubuntu/Windows.30 input checksums and three archive
tests passed before integration. No prior conflicting validated95% noise protocol
found in docs/src/scripts/tests. Current definition is explicitly owner-specified.

## Stage A — implementation and small tests

56 tests passed,including all27 noiseless certificates,full135-instance count
check under a separate test seed,CCD geometry,independent centers,reverse order,
three workers,existing OLS/LOOCV/ANOVA APIs,raw singular covariance,external
validation,predefined grid-free figures and lossless oracle-free reload.
Ruff and strict mypy passed;1150 preexisting main files verified byte-for-byte.

Stages B–E will be recorded after the source/protocol commit and official run.
No official noisy result has been selected or used to tune the protocol.
