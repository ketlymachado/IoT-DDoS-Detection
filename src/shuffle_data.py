import csv
import random
import os
from tqdm import tqdm
from tap import Tap


class ArgumentParser(Tap):
    """Class defines arguments typing."""

    folder: str  # folder with ARFF files whose data will be shuffled


def parse() -> ArgumentParser:
    """Function parses arguments."""

    parser = ArgumentParser(
        description="Data Shuffle",
        usage="""This program can be used to perform data shuffle to ARFF files
                containing BoT-IoT subsets.""",
    )

    arguments = parser.parse_args()

    return arguments


def execute(folder):
    """Function performs data shuffling"""

    files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".arff"):
                files.append(file_path)

    print("\nData shuffling started...\n")

    for filename in tqdm(files):
        header = []
        instances = []

        with open(filename, encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")

            for row in reader:
                if row[0][0] == "@":
                    header.append("".join(row) + "\n")
                    continue

                instances.append(",".join(row) + "\n")

        file.close()

        random.shuffle(instances)

        with open(filename, "w", newline="", encoding="utf-8") as shuffled_file:
            shuffled_file.writelines(header)
            shuffled_file.writelines(instances)

        shuffled_file.close()

    print("\n...Data shuffling finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
