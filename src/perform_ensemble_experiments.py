import csv
import os
from pathlib import Path
from tqdm import tqdm
from tap import Tap

ensemble_algorithms = [
    "OZABOOST",
    "OZABAGASHT",
    "OZABAGADWIN",
    "OZABAG",
    "OAUE",
    "LEVBAG",
    # "DWM",
    "ADACC",
]

ensemble_algorithms_config = {
    # Anticipative Dynamic Adaptation to Concept Changes
    "ADACC": {"name": "adacc", "learner": "meta.ADACC"},
    # Dynamic Weighted Majority
    "DWM": {"name": "dwm", "learner": "meta.DynamicWeightedMajority"},
    # Leveraging Bagging
    "LEVBAG": {"name": "lb", "learner": "meta.LeveragingBag"},
    # Online Accuracy Updated Ensemble
    "OAUE": {
        "name": "oaue",
        "learner": "meta.OnlineAccuracyUpdatedEnsemble",
    },
    # Online Bagging
    "OZABAG": {"name": "ob", "learner": "meta.OzaBag"},
    # Online Bagging with ADWIN drift detector
    "OZABAGADWIN": {
        "name": "obadwin",
        "learner": "meta.OzaBagAdwin",
    },
    # Online Bagging with Adaptive-Size Hoeffding Trees
    "OZABAGASHT": {
        "name": "obasht",
        "learner": "(meta.OzaBagASHT -l ASHoeffdingTree)",
    },
    # Online Boosting
    "OZABOOST": {
        "name": "obst",
        "learner": "meta.OzaBoost",
    },
}


class ArgumentParser(Tap):
    """Class defines arguments typing"""

    folder: (
        str  # folder with ARFF files whose data will be considered for the experiments
    )


def parse() -> ArgumentParser:
    """Function parses arguments"""

    parser = ArgumentParser(
        description="Ensemble Experiments",
        usage="""This program can be used to perform the ensemble experiments.""",
    )

    arguments = parser.parse_args()

    return arguments


def get_experiment_command(lines, algorithm, stream, output_file):
    """Function creates and returns the command line to perform an experiment"""
    moa_path = os.path.join(
        Path(__file__).absolute().parent, "../moa-release-2023.04.0/lib"
    )

    learner = ensemble_algorithms_config[algorithm]["learner"]
    evaluator = "(WindowClassificationPerformanceEvaluator -o -p -r -f)"
    sample_frequency = int(lines / 1000)

    return (
        f'java -cp {os.path.join(moa_path, "moa.jar")} '
        f'-javaagent:{os.path.join(moa_path, "sizeofag-1.0.4.jar")} '
        f'moa.DoTask "EvaluateInterleavedTestThenTrain -l {learner} -s '
        f'(ArffFileStream -f {stream}) -e {evaluator} -f {str(sample_frequency)}"'
        f"2>&1 > {output_file}"
    )


def perform_experiment(experiment_data):
    """Function performs a single experiment"""
    lines = 0

    with open(experiment_data["data_file"], encoding="utf-8") as arff_file:
        reader = csv.reader(arff_file, delimiter=",")

        for row in reader:
            # ignore header
            if row[0][0] == "@":
                continue

            lines = lines + 1

    arff_file.close()

    experiment_command = get_experiment_command(
        lines,
        experiment_data["algorithm"],
        experiment_data["data_file"],
        experiment_data["result_file"],
    )

    os.system(experiment_command)


def execute(folder):
    """Function performs ensemble experiments"""
    experiment_folder = os.path.basename(folder)
    results_folder = os.path.join(
        Path(__file__).absolute().parent, "../results/moa", experiment_folder
    )

    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".arff"):
                files.append(file_path)

    print("\nEnsemble experiments started...\n")

    for filename in tqdm(files):
        experiment_subfolder = os.path.join(
            results_folder, os.path.basename(os.path.dirname(filename))
        )

        if not os.path.exists(experiment_subfolder):
            os.makedirs(experiment_subfolder)

        for ensemble in tqdm(ensemble_algorithms):
            print(f"\n## {ensemble} ##\n")
            perform_experiment(
                {
                    "algorithm": ensemble,
                    "data_file": filename,
                    "result_file": os.path.join(
                        experiment_subfolder,
                        ensemble_algorithms_config[ensemble]["name"] + ".csv",
                    ),
                }
            )

    print("\n...Ensemble experiments finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
