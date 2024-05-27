import csv
from random import sample
import os
import numpy as np
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


def create_balanced_file(filename, header, instances, included):
    """Function creates the balanced data file"""

    os.rename(filename, filename + ".old")

    with open(filename, "w", newline="", encoding="utf-8") as balanced_file:
        writer = csv.writer(
            balanced_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )

        balanced_file.writelines(header)

        instances_size = len(instances)
        count_ddos = 0
        count_normal = 0

        for i in range(0, instances_size):
            if included[i]:
                instance = instances[i][:-1]
                writer.writerow(instance)

                if instance[-1] == "attack":
                    count_ddos = count_ddos + 1
                else:
                    count_normal = count_normal + 1

        balanced_file.close()

    return count_normal, count_ddos


def random_oversampling(minority, majority_size, instances, included):
    """Function performs random oversampling."""
    minority_size = len(minority)
    number_of_instances_to_include = int(majority_size * 0.35)

    sorted_instances_to_include = np.random.choice(
        range(0, minority_size), size=number_of_instances_to_include, replace=True
    )

    for sorted_idx in sorted_instances_to_include:
        instances.append(minority[sorted_idx])
        included.append(True)


def random_undersampling(majority, included):
    """Function performs random undersampling."""
    majority_size = len(majority)
    number_of_instances_to_remove = int(majority_size * 0.3)

    sorted_instances_to_remove = sample(
        range(0, majority_size), number_of_instances_to_remove
    )

    for sorted_idx in sorted_instances_to_remove:
        included[majority[sorted_idx][-1]] = False


def initial_compute(filename):
    """Function initializes control variables and returns it"""
    normal = []  # Stores the normal instances
    attack = []  # Stores the attack instances
    instances = []  # Stores all instances, including oversampling
    included = []  # Binary list indicating if an instance is included
    header = []  # ARFF header

    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")

        idx = 0

        for row in reader:
            if row[0][0] == "@":
                header.append("".join(row) + "\n")
                continue

            if row[-1] == "attack":
                attack.append(row)
                attack[-1].append(idx)
            else:
                normal.append(row)
                normal[-1].append(idx)

            instances.append(row)
            included.append(True)
            idx = idx + 1
        file.close()

    return normal, attack, instances, included, header


def execute(folder):
    """Function uses random over and under-sampling to balance class distribution"""

    files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".arff"):
                files.append(file_path)

    print("\nData balancing started...\n")

    for filename in tqdm(files):
        print("\nperforming initial computation...\n")
        normal, attack, instances, included, header = initial_compute(filename)

        minority_class = normal if len(attack) > len(normal) else attack
        majority_class = normal if len(normal) > len(attack) else attack

        if (len(minority_class) / len(majority_class)) >= 0.5:
            print("The minority class is at least 50% the size of the majority class")
        else:
            print("\nperforming oversampling...\n")
            random_oversampling(
                minority_class, len(majority_class), instances, included
            )
            print("\nperforming undersampling...\n")
            random_undersampling(majority_class, included)

        print("\ncreating balanced file...\n")
        count_normal, count_ddos = create_balanced_file(
            filename, header, instances, included
        )

        create_info_file(filename, count_normal, count_ddos)

    print("\n...Data balancing finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
