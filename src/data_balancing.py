import csv
from random import choice, random
import os
from math import ceil, floor
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
from tap import Tap


class ArgumentParser(Tap):
    """Class defines arguments typing."""

    folder: str  # folder with ARFF files whose data will be balanced


def parse() -> ArgumentParser:
    """Function parses arguments."""

    parser = ArgumentParser(
        description="Data Balancing",
        usage="""This program can be used to perform data balancing to ARFF files
                containing BoT-IoT subsets.""",
    )

    arguments = parser.parse_args()

    return arguments


def create_info_file(filename, normal_instances, attack_instances):
    """Function creates info file about the balanced data"""
    info_filename = os.path.join(
        os.path.dirname(filename),
        os.path.splitext(os.path.basename(filename))[0] + "-balanced-info.txt",
    )

    with open(info_filename, "w", encoding="utf-8") as balanced_info_file:
        balanced_info_file.write(
            "Total normal instances = " + str(normal_instances) + "\n"
        )
        balanced_info_file.write(
            "Total DDoS attack instances = " + str(attack_instances) + "\n"
        )
        total = normal_instances + attack_instances
        balanced_info_file.write(
            "Final number of instances (normal + attack) = " + str(total) + "\n"
        )
    balanced_info_file.close()


def create_balanced_file(filename, header, instances, systhetic_instances):
    """Function creates the balanced data file"""

    os.rename(filename, filename + ".old")

    with open(filename, "w", newline="", encoding="utf-8") as balanced_file:
        balanced_file.writelines(header)
        balanced_file.writelines(
            "\n".join([",".join(instance) for instance in instances]) + "\n"
        )
        balanced_file.writelines(
            "\n".join([",".join(instance) for instance in systhetic_instances]) + "\n"
        )

    balanced_file.close()


def nearest_neighbour(x):
    """Function calculates nearest neighbours"""
    nbs = NearestNeighbors(n_neighbors=5, metric="euclidean", algorithm="kd_tree").fit(
        x
    )
    _euclidean, indices = nbs.kneighbors(x)
    return indices


def populate(smote_amount, idx, neighbours, minority_class, number_of_columns):
    """Function to generate the synthetic samples"""
    synthetic_instances = []
    while smote_amount > 0:
        neighbour = choice(neighbours)
        synthetic_instances.append([])
        for column_idx in range(number_of_columns):
            dif = (
                minority_class[neighbour][column_idx] - minority_class[idx][column_idx]
            )
            gap = random()
            synthetic_instances[-1].append(
                str(minority_class[idx][column_idx] + gap * dif)
            )
        smote_amount = smote_amount - 1

    return synthetic_instances


def smote(minority_class, smote_percentage, label):
    """Function performs Synthetic Minority Over-sampling TEchnique"""
    smote_amount = (
        ceil(smote_percentage / 100)
        if smote_percentage % 100 >= 50
        else floor(smote_percentage / 100)
    )
    number_of_columns = len(minority_class[0])
    neighbour_indices = nearest_neighbour(minority_class)
    synthetic_instances = []

    for idx, neighbours in enumerate(neighbour_indices):
        synthetic_instances.extend(
            populate(
                smote_amount,
                idx,
                neighbours,
                minority_class,
                number_of_columns,
            )
        )

    for instance in synthetic_instances:
        instance.append(label)

    return synthetic_instances


def initial_compute(filename):
    """Function initializes control variables and returns it"""
    normal = []
    attack = []
    instances = []
    header = []

    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")

        for row in reader:
            if row[0][0] == "@":
                header.append("".join(row) + "\n")
                continue

            instances.append(row)
            instance = []

            for idx, value in enumerate(row):
                is_last_column = idx == len(row) - 1
                if is_last_column:
                    continue
                instance.append(float(value))

            if row[-1] == "attack":
                attack.append(instance)
            else:
                normal.append(instance)
    file.close()

    return normal, attack, instances, header


def execute(folder):
    """Function uses SMOTE techinique to balance class distribution"""

    files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".arff"):
                files.append(file_path)

    print("\nData balancing started...\n")

    for filename in tqdm(files):
        normal, attack, instances, header = initial_compute(filename)

        minority_class = normal if len(attack) > len(normal) else attack
        majority_class = normal if len(normal) > len(attack) else attack
        minority_class_label = "normal" if len(attack) > len(normal) else "attack"
        scale = len(minority_class) / len(majority_class)

        if scale < 0.5:
            synthetic_instances = smote(
                minority_class, 100 / scale, minority_class_label
            )
            create_balanced_file(filename, header, instances, synthetic_instances)
            create_info_file(
                filename,
                (
                    len(normal) + len(synthetic_instances)
                    if minority_class_label == "normal"
                    else len(normal)
                ),
                (
                    len(attack) + len(synthetic_instances)
                    if minority_class_label == "attack"
                    else len(attack)
                ),
            )

    print("\n...Data balancing finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
