# Frozen Phase10C analytical reference

27 scenarios,5000 primary points each,135000 total.
Each reference is shared by five RSM replicas. This finite sample
is not the continuous front.

Primary NPZs have exactly27 scenario keys and5000 rows each.
The nested NPZ stores5000-row extensions and10000-row witnesses.
R2500 is the primary prefix;R10000 concatenates primary+extension.
Coordinates/responses are float64;ID vectors are int64.
Independent probes and every candidate's weights/source are archived.

load_reference verifies hashes and loads without optimization,
recalibration or RSM fitting. load_evaluation_context is offline only.
No oracle is returned to search. Precision limitations are explicit.

Source commit:d982c01f7753152e5961093d0e6de809362c595c. Main integration:47a0e4dc55a22a7d0ad436540c1a305e4078e2ad.

No algorithm results or noisy RSMs are reference inputs.
No search or equalization occurred. Existing data/science/licenses
are unchanged. See LICENSE_SCOPE.md;original-code MIT does not
automatically license scientific artifacts.
