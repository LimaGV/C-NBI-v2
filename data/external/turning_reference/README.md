# Historical VRF decisions, eligible only after current-RSM reevaluation

`vrf_historical_decisions.csv` contains66 literal decision-coordinate strings
from the identified historical VRF export, plus original row IDs. The source
columns cs/f/md map in order to coded x1/x2/x3 (cutting speed, feed, depth).
No objective values, inferred decisions, inverse coding or new VRF search.

Source export and extraction hashes, repository/submodule context and processing
limitations are recorded in `references/metadata/phase_07_v1/source_provenance.json`
and `docs/mathematics/reference_source_audit.md`. The historical export had already
been sanitized and ND-filtered under older models. Only the retained66 decisions
are available through this export; no claim of complete original VRF population.

Do not treat this CSV as experimental observations or a source of RSM fitting.
Canonical responses are produced by reevaluating the current frozen nominal
eight RSMs in Phase7. The experimental workbook and all prior scientific results
remain separate and immutable.
