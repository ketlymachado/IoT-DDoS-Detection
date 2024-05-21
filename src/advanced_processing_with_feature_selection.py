###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : advanced_processing_with_feature_selection.py    #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Performs an advanced processing of the CSV files #
#                inside the folder passed through parameter       #
#                "-folder" to treat and remove features, aiming   #
#                to produce ARFF files that will be used to       #
#                perform the experiments at Massive Online        #
#                Analysis (MOA)                                   #
#                                                                 #
#                This advanced processing is performed            #
#                considering the results obtained through the     #
#                Exploratory Data Analysis (EDA) of the BoT-IoT   #
#                dataset and, therefore, only includes the        #
#                features that best represent the data            #
#                                                                 #
###################################################################

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


def create_folder() -> None:
    """Function creates the destination folder."""
    try:
        if not os.path.exists(arff_folder_path):
            os.makedirs(arff_folder_path)
    except OSError as e:
        raise OSError("Error while creating destination folder") from e


class ArgumentParser(Tap):
    """Class defines arguments typing."""

    folder: str  # folder with CSV files to process and where ARFF files will be stored


def parse() -> ArgumentParser:
    """Function parses arguments."""

    parser = ArgumentParser(
        description="Advanced Processing",
        usage="""This program can be used to perform advanced processing
        to CSV files containing BoT-IoT subsets, tranforming them into ARFF files
        and performing the feature selection technique.""",
    )

    arguments = parser.parse_args()

    return arguments


args = parse()

csv_folder_path = os.path.join(args.folder, "CSV")
arff_folder_path = os.path.join(args.folder, "ARFF-FS")

create_folder()

csv_files = [
    file
    for file in os.listdir(csv_folder_path)
    if os.path.isfile(os.path.join(csv_folder_path, file))
]

print("Process started...")

for csv_filename in tqdm(csv_files):

    csv_path = os.path.join(csv_folder_path, csv_filename)

    with open(csv_path, encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")

        arff_path = os.path.join(arff_folder_path, csv_filename[:-3] + "arff")

        with open(arff_path, "w", newline="", encoding="utf-8") as arff_file:
            writer = csv.writer(
                arff_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )

            IS_FIRST_ROW = True

            for row in reader:
                if IS_FIRST_ROW:
                    # Ignores CSV header and adjusts ARFF header for feature treatment
                    arff_file.writelines(HEADER)
                    IS_FIRST_ROW = False
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

print("...Process finished")
