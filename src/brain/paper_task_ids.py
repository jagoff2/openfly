from __future__ import annotations

from dataclasses import dataclass

from brain.public_ids import JON_CE_IDS, JON_DM_IDS, JON_F_IDS

# Public task-specific outputs from the Shiu et al. Nature 2024 notebook:
# `external/fly-brain/code/paper-phil-drosophila/example.ipynb`
MN9_LEFT = 720575940660219265
MN9_RIGHT = 720575940618238523
aDN1_RIGHT = 720575940616185531
aDN1_LEFT = 720575940624319124

# Public grooming readout from the same notebook family:
# `external/fly-brain/code/paper-phil-drosophila/figures.ipynb`
aBN1 = 720575940630907434

# Public labellar sugar GRNs from:
# `external/fly-brain/code/paper-phil-drosophila/example.ipynb`
SUGAR_GRNS_RIGHT = [
    720575940616885538,
    720575940630233916,
    720575940639332736,
    720575940632889389,
    720575940617000768,
    720575940632425919,
    720575940637568838,
    720575940629176663,
    720575940621502051,
    720575940638202345,
    720575940612670570,
    720575940611875570,
    720575940621754367,
    720575940633143833,
    720575940613601698,
    720575940630797113,
    720575940639198653,
    720575940639259967,
    720575940624963786,
    720575940640649691,
    720575940610788069,
    720575940623172843,
    720575940628853239,
]

# Public left-hemisphere sugar GRNs from:
# `external/fly-brain/code/paper-phil-drosophila/figures.ipynb`
SUGAR_GRNS_LEFT = [
    720575940620589838,
    720575940631147148,
    720575940608305161,
    720575940629388135,
    720575940630968335,
    720575940606801282,
    720575940617398502,
    720575940616167218,
    720575940620296641,
    720575940627961104,
]


@dataclass(frozen=True)
class PaperTaskSpec:
    name: str
    input_groups: dict[str, tuple[int, ...]]
    output_groups: dict[str, tuple[int, ...]]
    frequencies_hz: tuple[float, ...]
    default_duration_ms: float


FEEDING_TASK = PaperTaskSpec(
    name="feeding",
    input_groups={
        "sugar_right": tuple(SUGAR_GRNS_RIGHT),
        "sugar_left": tuple(SUGAR_GRNS_LEFT),
    },
    output_groups={
        "mn9_left": (MN9_LEFT,),
        "mn9_right": (MN9_RIGHT,),
    },
    frequencies_hz=(20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0),
    default_duration_ms=100.0,
)

GROOMING_TASK = PaperTaskSpec(
    name="grooming",
    input_groups={
        "jon_ce": tuple(JON_CE_IDS),
        "jon_f": tuple(JON_F_IDS),
        "jon_dm": tuple(JON_DM_IDS),
        "jon_all": tuple(JON_CE_IDS + JON_F_IDS + JON_DM_IDS),
    },
    output_groups={
        "adn1_left": (aDN1_LEFT,),
        "adn1_right": (aDN1_RIGHT,),
        "abn1": (aBN1,),
    },
    frequencies_hz=(20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0, 220.0),
    default_duration_ms=100.0,
)


def all_output_ids() -> list[int]:
    output_ids: set[int] = set()
    for spec in (FEEDING_TASK, GROOMING_TASK):
        for ids in spec.output_groups.values():
            output_ids.update(int(neuron_id) for neuron_id in ids)
    return sorted(output_ids)
