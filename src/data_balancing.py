import csv
from random import choice, random
import os
from math import ceil, floor
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
from tap import Tap

header = []
SYNTHETIC_INSTANCES_FILENAME = ""


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


def create_info_file(
    filename, minority_class_length, majority_class_length, minority_class_label
):
    """Function creates info file about the balanced data"""
    info_filename = os.path.join(
        os.path.dirname(filename),
        os.path.splitext(os.path.basename(filename))[0] + "-balanced-info.txt",
    )

    normal_instances = (
        majority_class_length
        if minority_class_label == "attack"
        else minority_class_length
    )
    attack_instances = (
        majority_class_length
        if minority_class_label == "normal"
        else minority_class_length
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


def create_balanced_file(filename):
    """Function creates the balanced data file"""

    os.rename(filename, filename + ".old")

    with open(filename, "w", newline="", encoding="utf-8") as balanced_file:
        balanced_file.writelines(header)

        spamwriter = csv.writer(
            balanced_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )

        with open(filename + ".old", encoding="utf-8") as instances_file:
            reader = csv.reader(instances_file, delimiter=",")

            for row in reader:
                if row[0][0] == "@":
                    continue

                spamwriter.writerow(row)
        instances_file.close()

        with open(
            SYNTHETIC_INSTANCES_FILENAME, encoding="utf-8"
        ) as synthetic_instances_file:
            reader = csv.reader(synthetic_instances_file, delimiter=",")
            spamwriter.writerows(reader)
        synthetic_instances_file.close()

    balanced_file.close()
    os.remove(SYNTHETIC_INSTANCES_FILENAME)


def nearest_neighbour(x):
    """Function calculates nearest neighbours"""
    nbs = NearestNeighbors(n_neighbors=5, metric="euclidean", algorithm="kd_tree").fit(
        x
    )
    _euclidean, indices = nbs.kneighbors(x)
    return indices


def populate(smote_amount, idx, neighbours, minority_class, label):
    """Function to generate the synthetic samples"""
    with open(
        SYNTHETIC_INSTANCES_FILENAME, "a", encoding="utf-8"
    ) as synthetic_instances_file:
        spamwriter = csv.writer(
            synthetic_instances_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )

        while smote_amount > 0:
            neighbour = choice(neighbours)
            synthetic_instance = []

            for column_idx, value in enumerate(minority_class[idx]):
                dif = minority_class[neighbour][column_idx] - value
                gap = random()
                synthetic_instance.append(value + gap * dif)

            synthetic_instance.append(label)
            spamwriter.writerow(synthetic_instance)
            smote_amount = smote_amount - 1
    synthetic_instances_file.close()


def smote(minority_class, smote_percentage, label):
    """Function performs Synthetic Minority Over-sampling TEchnique"""
    smote_amount = (
        ceil(smote_percentage / 100)
        if smote_percentage % 100 >= 50
        else floor(smote_percentage / 100)
    )
    neighbour_indices = nearest_neighbour(minority_class)

    for idx, neighbours in tqdm(enumerate(neighbour_indices)):
        populate(
            smote_amount,
            idx,
            neighbours,
            minority_class,
            label,
        )

    return smote_amount * len(minority_class)


def get_minority_class(filename):
    """Function calculates minority class and returns information on it"""
    normal = []
    attack = []

    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")

        for row in tqdm(reader):
            if row[0][0] == "@":
                header.append("".join(row) + "\n")
                continue

            if row[-1] == "attack":
                attack.append([float(column) for column in row[:-1]])
            else:
                normal.append([float(column) for column in row[:-1]])
    file.close()

    if len(attack) > len(normal):
        return normal, "normal", len(normal) / len(attack), len(attack)

    return attack, "attack", len(attack) / len(normal), len(normal)


def get_files(folder):
    """Function returns all arff files from folder"""
    files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".arff"):
                files.append(file_path)

    return files


def execute(folder):
    """Function uses SMOTE techinique to balance class distribution"""

    files = get_files(folder)

    print("\nData balancing started...\n")

    for filename in tqdm(files):
        # pylint: disable=global-statement
        global SYNTHETIC_INSTANCES_FILENAME
        SYNTHETIC_INSTANCES_FILENAME = os.path.join(
            os.path.dirname(filename), "synthetic_instances.arff"
        )

        minority_class, minority_class_label, scale, majority_class_length = (
            get_minority_class(filename)
        )

        if scale < 0.5:
            synthetic_instances_length = smote(
                minority_class, 100 / scale, minority_class_label
            )
            create_balanced_file(filename)
            create_info_file(
                filename,
                majority_class_length,
                len(minority_class) + synthetic_instances_length,
                minority_class_label,
            )

    print("\n...Data balancing finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
