###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : advanced_processing_without_feature_selection.py #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Performs an advanced processing of the CSV files #
#                inside the folder passed through parameter       #
#                "-folder" to treat and remove features, and also #
#                deal with null values, aiming to produce ARFF    #
#                files that will be used to perform the           #
#                experiments at Massive Online Analysis (MOA)     #
#                                                                 #
###################################################################

import csv
import os
import enum
from tap import Tap


COLUMNS = {
    "int_validation": [0, 5, 7, 8, 9, 12, 25, 26, 27, 28],
    "float_validation": [
        1,
        11,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        29,
        30,
        31,
    ],
    "flgs_col": 2,
    "proto_col": 3,
    "state_col": 10,
    "label_col": 32,
}
HEADER = [
    "@relation botiot\n",
    "@attribute 'pkseqid' numeric\n",
    "@attribute 'stime' numeric\n",
    # flgs
    "@attribute 'e*' numeric\n",
    "@attribute 'e' numeric\n",
    "@attribute 'eF' numeric\n",
    "@attribute 'es' numeric\n",
    "@attribute 'eU' numeric\n",
    "@attribute 'eg' numeric\n",
    "@attribute 'e&' numeric\n",
    "@attribute 'ed' numeric\n",
    "@attribute 'er' numeric\n",
    # proto
    "@attribute 'icmp' numeric\n",
    "@attribute 'igmp' numeric\n",
    "@attribute 'udp' numeric\n",
    "@attribute 'arp' numeric\n",
    "@attribute 'tcp' numeric\n",
    "@attribute 'ipv6-icmp' numeric\n",
    "@attribute 'rarp' numeric\n",
    #
    "@attribute 'sport' numeric\n",
    "@attribute 'dport' numeric\n",
    "@attribute 'pkts' numeric\n",
    "@attribute 'bytes' numeric\n",
    # state
    "@attribute 'RSP' numeric\n",
    "@attribute 'CON' numeric\n",
    "@attribute 'FIN' numeric\n",
    "@attribute 'REQ' numeric\n",
    "@attribute 'ACC' numeric\n",
    "@attribute 'NRS' numeric\n",
    "@attribute 'URP' numeric\n",
    "@attribute 'RST' numeric\n",
    "@attribute 'INT' numeric\n",
    #
    "@attribute 'ltime' numeric\n",
    "@attribute 'seq' numeric\n",
    "@attribute 'dur' numeric\n",
    "@attribute 'mean' numeric\n",
    "@attribute 'stddev' numeric\n",
    "@attribute 'smac' numeric\n",
    "@attribute 'dmac' numeric\n",
    "@attribute 'sum' numeric\n",
    "@attribute 'min' numeric\n",
    "@attribute 'max' numeric\n",
    "@attribute 'soui' numeric\n",
    "@attribute 'doui' numeric\n",
    "@attribute 'sco' numeric\n",
    "@attribute 'dco' numeric\n",
    "@attribute 'spkts' numeric\n",
    "@attribute 'dpkts' numeric\n",
    "@attribute 'sbytes' numeric\n",
    "@attribute 'dbytes' numeric\n",
    "@attribute 'rate' numeric\n",
    "@attribute 'srate' numeric\n",
    "@attribute 'drate' numeric\n",
    "@attribute 'sipv4_pos1' numeric\n",
    "@attribute 'sipv4_pos2' numeric\n",
    "@attribute 'sipv4_pos3' numeric\n",
    "@attribute 'sipv4_pos4' numeric\n",
    "@attribute 'sipv6_pos1' numeric\n",
    "@attribute 'sipv6_pos2' numeric\n",
    "@attribute 'sipv6_pos3' numeric\n",
    "@attribute 'sipv6_pos4' numeric\n",
    "@attribute 'sipv6_pos5' numeric\n",
    "@attribute 'sipv6_pos6' numeric\n",
    "@attribute 'sipv6_pos7' numeric\n",
    "@attribute 'sipv6_pos8' numeric\n",
    "@attribute 'dipv4_pos1' numeric\n",
    "@attribute 'dipv4_pos2' numeric\n",
    "@attribute 'dipv4_pos3' numeric\n",
    "@attribute 'dipv4_pos4' numeric\n",
    "@attribute 'dipv6_pos1' numeric\n",
    "@attribute 'dipv6_pos2' numeric\n",
    "@attribute 'dipv6_pos3' numeric\n",
    "@attribute 'dipv6_pos4' numeric\n",
    "@attribute 'dipv6_pos5' numeric\n",
    "@attribute 'dipv6_pos6' numeric\n",
    "@attribute 'dipv6_pos7' numeric\n",
    "@attribute 'dipv6_pos8' numeric\n",
    "@attribute 'attack' {normal, attack}\n",
    "@data\n",
]


def replace_by_int(feature: str) -> int:
    """Assures that feature is an integer."""
    if feature == "":
        return -1

    if "x" in (feature):
        return int(feature, 16)

    return int(feature)


def replace_by_number(feature: str) -> float:
    """Assures that feature is a number."""
    if feature == "":
        return -1

    return float(feature)


class DummieFeatures(enum.Enum):
    "Features that should be replaced by its dummies"
    FLGS = "flgs"
    PROTO = "proto"
    STATE = "state"


def get_dummies(feature: str, feature_name: DummieFeatures) -> "list[int]":
    """Replace feature by its dummies using one-hot encoding."""

    if feature_name == DummieFeatures.FLGS:
        return [
            (1 if feature == "e *" else 0),
            (1 if feature == "e" else 0),
            (1 if feature == "e    F" else 0),
            (1 if feature == "e s" else 0),
            (1 if feature == "eU" else 0),
            (1 if feature == "e g" else 0),
            (1 if feature == "e &" else 0),
            (1 if feature == "e d" else 0),
            (1 if feature == "e r" else 0),
        ]

    if feature_name == DummieFeatures.PROTO:
        return [
            (1 if feature == "icmp" else 0),
            (1 if feature == "igmp" else 0),
            (1 if feature == "udp" else 0),
            (1 if feature == "arp" else 0),
            (1 if feature == "tcp" else 0),
            (1 if feature == "ipv6-icmp" else 0),
            (1 if feature == "rarp" else 0),
        ]

    if feature_name == DummieFeatures.STATE:
        return [
            (1 if feature == "RSP" else 0),
            (1 if feature == "CON" else 0),
            (1 if feature == "FIN" else 0),
            (1 if feature == "REQ" else 0),
            (1 if feature == "ACC" else 0),
            (1 if feature == "NRS" else 0),
            (1 if feature == "URP" else 0),
            (1 if feature == "RST" else 0),
            (1 if feature == "INT" else 0),
        ]

    raise TypeError("Feature name is invalid")


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
        to CSV files containing BoT-IoT subsets, tranforming them into ARFF files.""",
    )

    arguments = parser.parse_args()

    return arguments


args = parse()

csv_folder_path = os.path.join(args.folder, "CSV")
arff_folder_path = os.path.join(args.folder, "ARFF")

create_folder()

csv_files = [
    file
    for file in os.listdir(csv_folder_path)
    if os.path.isfile(os.path.join(csv_folder_path, file))
]

print("Process started...")

for csv_filename in csv_files:

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
                    # Creates the instance with the final features/data. Main changes:
                    # - Checks for null values and replaces it by -1
                    # - Replaces flgs, proto and state by its dummies using one-hot encoding
                    # - Removes saddr and daddr, that were already converted to 24 new features
                    # - Removes category and subcategory since they will not be considered
                    instance = []

                    for idx, col in enumerate(row):
                        if idx in COLUMNS["int_validation"]:
                            instance.append(replace_by_int(col))
                        elif idx in COLUMNS["float_validation"]:
                            instance.append(replace_by_number(col))
                        elif idx == COLUMNS["flgs_col"]:
                            instance = instance + get_dummies(col, DummieFeatures.FLGS)
                        elif idx == COLUMNS["proto_col"]:
                            instance = instance + get_dummies(col, DummieFeatures.PROTO)
                        elif idx == COLUMNS["state_col"]:
                            instance = instance + get_dummies(col, DummieFeatures.STATE)
                        elif idx == COLUMNS["label_col"]:
                            # Establishes the label as the only categorical feature
                            # since this is required by some of the algorithms used in MOA
                            instance.append("attack" if int(col) == 1 else "normal")
                        else:
                            # nem todos tem que entrar aqui, precisa validar as colunas
                            instance.append(col)

                    writer.writerow(instance)

        arff_file.close()
    csv_file.close()

print("...Process finished")
