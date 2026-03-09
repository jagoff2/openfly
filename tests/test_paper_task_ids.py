from __future__ import annotations

from brain.paper_task_ids import FEEDING_TASK, GROOMING_TASK, MN9_LEFT, MN9_RIGHT, aBN1, aDN1_LEFT, aDN1_RIGHT
from brain.paper_task_probes import output_group_means


def test_feeding_and_grooming_specs_have_grounded_inputs_and_outputs() -> None:
    assert FEEDING_TASK.input_groups["sugar_right"]
    assert FEEDING_TASK.input_groups["sugar_left"]
    assert FEEDING_TASK.output_groups["mn9_left"] == (MN9_LEFT,)
    assert FEEDING_TASK.output_groups["mn9_right"] == (MN9_RIGHT,)

    assert GROOMING_TASK.input_groups["jon_ce"]
    assert GROOMING_TASK.input_groups["jon_f"]
    assert GROOMING_TASK.input_groups["jon_dm"]
    assert GROOMING_TASK.output_groups["adn1_left"] == (aDN1_LEFT,)
    assert GROOMING_TASK.output_groups["adn1_right"] == (aDN1_RIGHT,)
    assert GROOMING_TASK.output_groups["abn1"] == (aBN1,)


def test_output_group_means_averages_task_outputs() -> None:
    rates = {
        MN9_LEFT: 11.0,
        MN9_RIGHT: 13.0,
        aDN1_LEFT: 17.0,
        aDN1_RIGHT: 19.0,
        aBN1: 23.0,
    }

    feeding = output_group_means(rates, FEEDING_TASK.output_groups)
    grooming = output_group_means(rates, GROOMING_TASK.output_groups)

    assert feeding["mn9_left"] == 11.0
    assert feeding["mn9_right"] == 13.0
    assert grooming["adn1_left"] == 17.0
    assert grooming["adn1_right"] == 19.0
    assert grooming["abn1"] == 23.0
