import csv
import os
from enum import IntEnum
from tqdm import tqdm
from tap import Tap


class IntegerFeatures(IntEnum):
    "Features that must be an integer and its indexes"
    PKSEQID = 0
    SPORT = 5
    DPORT = 7
    PKTS = 8
    BYTES = 9
    SEQ = 12
    SPKTS = 25
    DPKTS = 26
    SBYTES = 27
    DBYTES = 28


class NumberFeatures(IntEnum):
    "Features that must be a number and its indexes"
    STIME = 1
    LTIME = 11
    DUR = 13
    MEAN = 14
    STDDEV = 15
    SMAC = 16
    DMAC = 17
    SUM = 18
    MIN = 19
    MAX = 20
    SOUI = 21
    DOUI = 22
    SCO = 23
    DCO = 24
    RATE = 29
    SRATE = 30
    DRATE = 31


class RemovalFeatures(IntEnum):
    "Features that must be removed and its indexes"
    SADDR = 4
    DADDR = 6
    CATEGORY = 33
    SUBCATEGORY = 34


class DummieFeatures(IntEnum):
    "Features that must be replaced by its dummies"
    FLGS = 2
    PROTO = 3
    STATE = 10


LABEL_FEATURE = 32

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


class ArgumentParser(Tap):
    """Class defines arguments typing"""

    folder: str  # folder with CSV files to process and where ARFF files will be stored


def parse() -> ArgumentParser:
    """Function parses arguments"""

    parser = ArgumentParser(
        description="Advanced Processing",
        usage="""This program can be used to perform advanced processing
        to CSV files containing BoT-IoT subsets, tranforming them into ARFF files.""",
    )

    arguments = parser.parse_args()

    return arguments


def replace_by_int(feature):
    """Assures that feature is an integer"""
    if feature == "":
        return -1

    if "x" in (feature):
        return int(feature, 16)

    return int(feature)


def replace_by_number(feature):
    """Assures that feature is a number"""
    if feature == "":
        return -1

    return float(feature)


def get_dummies(feature_value, feature_idx):
    """Replace feature by its dummies using one-hot encoding"""

    if feature_idx == DummieFeatures.FLGS:
        return [
            (1 if feature_value == "e *" else 0),
            (1 if feature_value == "e" else 0),
            (1 if feature_value == "e    F" else 0),
            (1 if feature_value == "e s" else 0),
            (1 if feature_value == "eU" else 0),
            (1 if feature_value == "e g" else 0),
            (1 if feature_value == "e &" else 0),
            (1 if feature_value == "e d" else 0),
            (1 if feature_value == "e r" else 0),
        ]

    if feature_idx == DummieFeatures.PROTO:
        return [
            (1 if feature_value == "icmp" else 0),
            (1 if feature_value == "igmp" else 0),
            (1 if feature_value == "udp" else 0),
            (1 if feature_value == "arp" else 0),
            (1 if feature_value == "tcp" else 0),
            (1 if feature_value == "ipv6-icmp" else 0),
            (1 if feature_value == "rarp" else 0),
        ]

    if feature_idx == DummieFeatures.STATE:
        return [
            (1 if feature_value == "RSP" else 0),
            (1 if feature_value == "CON" else 0),
            (1 if feature_value == "FIN" else 0),
            (1 if feature_value == "REQ" else 0),
            (1 if feature_value == "ACC" else 0),
            (1 if feature_value == "NRS" else 0),
            (1 if feature_value == "URP" else 0),
            (1 if feature_value == "RST" else 0),
            (1 if feature_value == "INT" else 0),
        ]

    raise TypeError("Feature name is invalid")


def get_processed_instance(row):
    """Function processes data and returns the adjusted instance"""
    # Creates the instance with the final features/data. Main changes:
    # - Checks for null values and replaces it by -1
    # - Replaces flgs, proto and state by its dummies using one-hot encoding
    # - Removes saddr and daddr, that were already converted to 24 new features
    # - Removes category and subcategory since they will not be considered
    instance = []

    for idx, col in enumerate(row):
        if idx in iter(IntegerFeatures):
            instance.append(replace_by_int(col))
        elif idx in iter(NumberFeatures):
            instance.append(replace_by_number(col))
        elif idx in iter(DummieFeatures):
            instance = instance + get_dummies(col, idx)
        elif idx == LABEL_FEATURE:
            # Establishes the label as the only categorical feature
            # since this is required by some of the algorithms used in MOA
            label = "attack" if int(col) == 1 else "normal"
        elif idx not in iter(RemovalFeatures):
            instance.append(col)

    # label must be the last feature
    instance.append(label)

    return instance


def execute(folder):
    """Function further processes subset features and generates ARFF files"""

    csv_files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".csv"):
                csv_files.append(file_path)

    print("\nAdvanced processing without feature selection started...\n")

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
                        writer.writerow(get_processed_instance(row))

            arff_file.close()
        csv_file.close()

    print("\n...Advanced processing without feature selection finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
