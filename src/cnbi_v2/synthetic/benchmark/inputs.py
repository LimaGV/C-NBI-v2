"""Read only the allowed fields of the Phase10B archives, without refitting."""

from pathlib import Path

import numpy as np

from cnbi_v2.synthetic.rsm.rsm_serialization import load_models

from .contracts import SearchInput


def load_search_inputs(directory: Path) -> dict[str, SearchInput]:
    models = load_models(directory)
    result = {}
    with (np.load(directory/"synthetic_experimental_arrays.npz", allow_pickle=False) as observed,
          np.load(directory/"synthetic_rsm_models.npz", allow_pickle=False) as coefficients,
          np.load(directory/"synthetic_residual_covariance.npz", allow_pickle=False) as residual):
        for key, model in models.items():
            scenario, replica = key.rsplit("__replica", 1)
            result[key] = SearchInput(
                scenario, int(replica), model, observed[f"nx{model.nx}__ccd"],
                observed[key+"__observed"], coefficients[key+"__design_r_factor"],
                residual[key+"__covariance"],
            )
    if len(result) != 135:
        raise ValueError("exactly 135 frozen instances required")
    return result
