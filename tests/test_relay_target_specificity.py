from __future__ import annotations

import pandas as pd

from analysis.relay_target_specificity import rank_target_specific_signals


def test_rank_target_specific_signals_penalizes_baseline_locomotor_families() -> None:
    target = pd.DataFrame(
        [
            {
                "family": "RelayA",
                "super_class": "visual_projection",
                "corr_target_bearing": 0.8,
                "corr_drive_asymmetry": 0.1,
                "corr_forward_speed": 0.1,
                "sampled_fraction": 0.0,
            },
            {
                "family": "RelayB",
                "super_class": "visual_projection",
                "corr_target_bearing": 0.85,
                "corr_drive_asymmetry": 0.2,
                "corr_forward_speed": 0.2,
                "sampled_fraction": 0.0,
            },
        ]
    )
    baseline = pd.DataFrame(
        [
            {
                "family": "RelayA",
                "super_class": "visual_projection",
                "corr_drive_asymmetry": 0.1,
                "corr_forward_speed": 0.1,
            },
            {
                "family": "RelayB",
                "super_class": "visual_projection",
                "corr_drive_asymmetry": 0.8,
                "corr_forward_speed": 0.6,
            },
        ]
    )

    ranked = rank_target_specific_signals(
        target_table=target,
        baseline_table=baseline,
        group_column="family",
    )

    assert ranked.iloc[0]["family"] == "RelayA"
    assert ranked.iloc[0]["target_specificity_score"] > ranked.iloc[1]["target_specificity_score"]
