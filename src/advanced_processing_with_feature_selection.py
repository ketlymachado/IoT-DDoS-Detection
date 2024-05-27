import csv
import os
from tqdm import tqdm
from tap import Tap


COLUMNS = {"sipv4_pos4": 38, "state": 10, "label": 32}
HEADER = [
    "@relation botiot\n",
    "@attribute 'sipv4_pos4' numeric\n",
    "@attribute 'CON' numeric\n",
    "@attribute 'attack' {normal, attack}\n",
    "@data\n",
]


class ArgumentParser(Tap):
    """Class defines arguments typing"""

    folder: str  # folder with CSV files to process and where ARFF files will be stored


def parse() -> ArgumentParser:
    """Function parses arguments"""

    parser = ArgumentParser(
        description="Advanced Processing",
        usage="""This program can be used to perform advanced processing
        to CSV files containing BoT-IoT subsets, tranforming them into ARFF files
        and performing the feature selection technique.""",
    )

    arguments = parser.parse_args()

    return arguments


def execute(folder):
    """Function processes subset features, performs feature selection and generates ARFF files"""

    csv_files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".csv"):
                csv_files.append(file_path)

    print("\nAdvanced processing with feature selection started...\n")

    for csv_filename in tqdm(csv_files):
        with open(csv_filename, encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=",")

            arff_filename = os.path.join(
                os.path.dirname(csv_filename),
                os.path.splitext(os.path.basename(csv_filename))[0] + ".arff",
            )

            with open(arff_filename, "w", newline="", encoding="utf-8") as arff_file:
                writer = csv.writer(
                    arff_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
                )

                is_first_row = True

                for row in reader:
                    if is_first_row:
                        # Ignores CSV header and adjusts ARFF header for feature treatment
                        arff_file.writelines(HEADER)
                        is_first_row = False
                    else:
                        # Creates the instance with the final features/data
                        instance = [
                            row[COLUMNS["sipv4_pos4"]],
                            # Creates the feature CON as a dummy from the feature state
                            (1 if row[COLUMNS["state"]] == "CON" else 0),
                            # Establishes the label as the only categorical feature
                            # since this is required by some of the algorithms used in MOA
                            ("attack" if int(row[COLUMNS["label"]]) == 1 else "normal"),
                        ]

                        writer.writerow(instance)

                arff_file.close()
            csv_file.close()

    print("\n...Advanced processing with feature selection finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
