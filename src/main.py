import re
import os
from pathlib import Path
import inquirer
from inquirer import errors
from inquirer.themes import GreenPassion
import preprocessing
import advanced_processing_with_feature_selection
import advanced_processing_without_feature_selection
import data_balancing
import shuffle_data
import perform_ensemble_experiments
import plot_results


def validate_identifier(_answers, current):
    """Function validates provided identifier"""
    if not re.search("^([a-z]*-*)*[a-z]+$", current):
        raise errors.ValidationError(
            "",
            reason="Identifier must use only lowercase letters and dashes, ending with a letter",
        )

    return True


def validate_percentage(_answers, current):
    """Function validates provided percentage"""
    try:
        percentage = float(current)
    except ValueError as e:
        raise errors.ValidationError(
            "",
            reason="Must be a floating-point literal",
        ) from e

    if percentage <= 0.0 or percentage > 100.0:
        raise errors.ValidationError(
            "",
            reason=f"{percentage} not in range (0.0, 100.0]",
        )

    return True


def validate_decimals(_answers, current):
    """Function validates provided decimals"""
    try:
        decimals = int(current)
    except ValueError as e:
        raise errors.ValidationError(
            "",
            reason="Must be an integer",
        ) from e

    if decimals < 0 or decimals > 6:
        raise errors.ValidationError(
            "",
            reason=f"{decimals} not in range [0, 6]",
        )

    return True


questions = [
    inquirer.Text(
        "identifier",
        message="Provide an identifier for this experiment (only lowercase and dashes allowed)",
        validate=validate_identifier,
    ),
    inquirer.Confirm(
        "feature_selection", message="Should feature selection be performed?"
    ),
    inquirer.Confirm("data_balancing", message="Should data balancing be performed?"),
    inquirer.Confirm("shuffle", message="Should data be shuffled?"),
    inquirer.List(
        "plot_language",
        message="In which language should data be plotted?",
        choices=["PT-BR", "EN"],
    ),
    inquirer.List(
        "percentage_mode",
        message="The experiments will consider a single percentage or a range of percentages?",
        choices=["range", "single"],
    ),
]

answers = inquirer.prompt(questions, theme=GreenPassion())

if answers["percentage_mode"] == "single":
    additional_questions = [
        inquirer.Text(
            "percentage",
            message="Provide the percentage for the experiments",
            validate=validate_percentage,
        ),
    ]
else:
    additional_questions = [
        inquirer.Text(
            "range_start",
            message="Provide the range start value",
            validate=validate_percentage,
        ),
        inquirer.Text(
            "range_finish",
            message="Provide the range finish value",
            validate=validate_percentage,
        ),
        inquirer.Text(
            "interval",
            message="Provide the interval",
            validate=validate_percentage,
        ),
    ]

additional_questions.append(
    inquirer.Text(
        "decimals",
        message="How many decimals would you like to use to present the percentage(s)?",
        validate=validate_decimals,
    )
)

additional_answers = inquirer.prompt(additional_questions, theme=GreenPassion())

start = (
    float(additional_answers["range_start"])
    if answers["percentage_mode"] == "range"
    else float(additional_answers["percentage"])
)

finish = (
    float(additional_answers["range_finish"])
    if answers["percentage_mode"] == "range"
    else float(additional_answers["percentage"])
)

interval = (
    float(additional_answers["interval"])
    if answers["percentage_mode"] == "range"
    else 100
)

folder = os.path.join(
    Path(__file__).absolute().parent, "../processed-data", answers["identifier"]
)

preprocessing.execute(
    start, finish, interval, int(additional_answers["decimals"]), folder
)

if answers["feature_selection"]:
    advanced_processing_with_feature_selection.execute(folder)
else:
    advanced_processing_without_feature_selection.execute(folder)

if answers["data_balancing"]:
    data_balancing.execute(folder)

if answers["shuffle"]:
    shuffle_data.execute(folder)

perform_ensemble_experiments.execute(folder)

plot_results.execute(answers["identifier"], answers["plot_language"])
