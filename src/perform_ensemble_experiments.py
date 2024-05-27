###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : ensemble-experiments.py                          #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Performs the ensemble experiments, instantiating #
#                MOA's tasks (in parallel) for each algorithm to  #
#                be evaluated (ADACC, DWM, LevBag, OAUE, OzaBag,  #
#                OzaBagADWIN, OzaBagASHT & Ozaboost). It receives #
#                the folder that contains the ARFF data files     #
#                that will be used as input for the experiments   #
#                and produces one CSV file for each algorithm     #
#                that contains the results of its evaluation.     #
#                                                                 #
###################################################################

import csv
import os
from pathlib import Path
from p_tqdm import p_map
from tap import Tap

ensemble_algorithms = [
    "ADACC",
    "DWM",
    "LEVBAG",
    "OAUE",
    "OAUE",
    "OZABAG",
    "OZABAGASHT",
    "OZABOOST",
]

ensemble_algorithms_config = {
    # Anticipative Dynamic Adaptation to Concept Changes
    "ADACC": {"folder": "ADACC", "name": "adacc", "learner": "meta.ADACC"},
    # Dynamic Weighted Majority
    "DWM": {"folder": "DWM", "name": "dwm", "learner": "meta.DynamicWeightedMajority"},
    # Leveraging Bagging
    "LEVBAG": {"folder": "LevBag", "name": "lb", "learner": "meta.LeveragingBag"},
    # Online Accuracy Updated Ensemble
    "OAUE": {
        "folder": "OAUE",
        "name": "oaue",
        "learner": "meta.OnlineAccuracyUpdatedEnsemble",
    },
    # Online Bagging
    "OZABAG": {"folder": "OzaBag", "name": "ob", "learner": "meta.OzaBag"},
    # Online Bagging with ADWIN drift detector
    "OZABAGADWIN": {
        "folder": "OzaBagADWIN",
        "name": "obadwin",
        "learner": "meta.OzaBagAdwin",
    },
    # Online Bagging with Adaptive-Size Hoeffding Trees
    "OZABAGASHT": {
        "folder": "OzaBagASHT",
        "name": "obasht",
        "learner": "(meta.OzaBagASHT -l ASHoeffdingTree)",
    },
    # Online Boosting
    "OZABOOST": {
        "folder": "OzaBoost",
        "name": "obst",
        "learner": "meta.OzaBoost",
    },
}


def perform_experiment(ensemble_algorithm: str):
    """Function performs experiment."""

    for filename in files:

        lines = 0

        with open(
            os.path.join(args.arff_folder, filename), encoding="utf-8"
        ) as arff_file:
            reader = csv.reader(arff_file, delimiter=",")

            for row in reader:
                # ignore header
                if row[0][0] == "@":
                    continue

                lines = lines + 1

        arff_file.close()

        moa_path = os.path.join(Path(__file__).absolute().parent, "../moa-release-2023.04.0/lib")

        learner = ensemble_algorithms_config[ensemble_algorithm]["learner"]
        stream = os.path.join(args.arff_folder, filename)
        evaluator = "WindowClassificationPerformanceEvaluator"
        sample_frequency = int(lines / 1000)

        percentage_identifier = filename.split("-")[1].split(".")[0]
        output_file = os.path.join(
            os.path.join(
                args.results_folder,
                ensemble_algorithms_config[ensemble_algorithm]["folder"],
            ),
            ensemble_algorithms_config[ensemble_algorithm]["name"]
            + "-"
            + percentage_identifier
            + ".csv",
        )

        experiment_command = (
            f'java -cp {os.path.join(moa_path, "moa.jar")} '
            f'-javaagent:{os.path.join(moa_path, "sizeofag-1.0.4.jar")} '
            f'moa.DoTask "EvaluateInterleavedTestThenTrain -l {learner} -s '
            f'(ArffFileStream -f {stream}) -e {evaluator} -f {str(sample_frequency)}"'
            f"> {output_file} 2> /dev/null"
        )

        os.system(experiment_command)


class ArgumentParser(Tap):
    """Class defines arguments typing."""

    arff_folder: (
        str  # folder with ARFF files whose data will be considered for the experiments
    )
    results_folder: str  # folder that will store the experiments results


def parse() -> ArgumentParser:
    """Function parses arguments."""

    parser = ArgumentParser(
        description="Ensemble Experiments",
        usage="""This program can be used to perform the ensemble experiments.""",
    )

    arguments = parser.parse_args()

    return arguments


args = parse()

for ensemble in ensemble_algorithms:
    path = os.path.join(
        args.results_folder, ensemble_algorithms_config[ensemble]["folder"]
    )
    if not os.path.exists(path):
        os.makedirs(path)

files = [
    file
    for file in os.listdir(args.arff_folder)
    if os.path.isfile(os.path.join(args.arff_folder, file))
]

p_map(perform_experiment, ensemble_algorithms)
