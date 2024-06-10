import csv
import os
from tqdm import tqdm
from tap import Tap
from typing_extensions import Literal
from columns import (
    BoTIoTColumns,
    IntegerFeatures,
    NumberFeatures,
    DummieFeatures,
    FeaturesToRemove,
)
from headers import (
    no_feature_selection_header,
    balanced_feature_selection_header,
    unbalanced_feature_selection_header,
)


class ArgumentParser(Tap):
    """Class defines arguments typing"""

    folder: str  # folder with CSV files to process and where ARFF files will be stored
    processing_type: Literal[
        "unbalanced_fs", "balanced_fs", "no_fs"
    ]  # type of processing


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
    if "x" in (feature):
        return int(feature, 16)

    return int(feature)


def get_dummies(feature_value, feature_idx):
    """Replace feature by its dummies using one-hot encoding"""

    if feature_idx == BoTIoTColumns.FLGS:
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

    if feature_idx == BoTIoTColumns.PROTO:
        return [
            (1 if feature_value == "icmp" else 0),
            (1 if feature_value == "igmp" else 0),
            (1 if feature_value == "udp" else 0),
            (1 if feature_value == "arp" else 0),
            (1 if feature_value == "tcp" else 0),
            (1 if feature_value == "ipv6-icmp" else 0),
            (1 if feature_value == "rarp" else 0),
        ]

    if feature_idx == BoTIoTColumns.STATE:
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


def get_no_feature_selection_instance(row):
    """Function returns instance with no feature selection"""
    # Creates the instance with the final features/data. Main changes:
    # - Replaces flgs, proto and state by its dummies using one-hot encoding
    # - Removes saddr and daddr, that were already converted to 24 new features
    # - Removes category and subcategory since they will not be considered
    instance = []

    for idx, col in enumerate(row):
        if idx in IntegerFeatures:
            instance.append(replace_by_int(col))
        elif idx in NumberFeatures:
            instance.append(float(col))
        elif idx in DummieFeatures:
            instance = instance + get_dummies(col, idx)
        elif idx == BoTIoTColumns.ATTACK:
            # Establishes the label as the only categorical feature
            # since this is required by some of the algorithms used in MOA
            label = "attack" if int(col) == 1 else "normal"
        elif idx not in FeaturesToRemove:
            instance.append(float(col))

    # label must be the last feature
    instance.append(label)

    return instance


def get_unbalanced_feature_selection_instance(row):
    """Function returns instance with feature selection for unbalanced dataset"""
    return [
        # Creates the feature CON as a dummy from the feature state
        (1 if row[BoTIoTColumns.STATE] == "CON" else 0),
        # Establishes the label as the only categorical feature
        # since this is required by some of the algorithms used in MOA
        ("attack" if int(row[BoTIoTColumns.ATTACK]) == 1 else "normal"),
    ]


def get_balanced_feature_selection_instance(row):
    """Function returns instance with feature selection for balanced dataset"""
    return [
        float(row[BoTIoTColumns.STIME]),
        int(row[BoTIoTColumns.SEQ]),
        # Creates the feature CON as a dummy from the feature state
        (1 if row[BoTIoTColumns.STATE] == "CON" else 0),
        # Establishes the label as the only categorical feature
        # since this is required by some of the algorithms used in MOA
        ("attack" if int(row[BoTIoTColumns.ATTACK]) == 1 else "normal"),
    ]


def get_processed_instance(row, processing_type):
    """Function processes data and returns the adjusted instance based on the processing type"""
    if processing_type == "unbalanced_fs":
        return get_unbalanced_feature_selection_instance(row)

    if processing_type == "balanced_fs":
        return get_balanced_feature_selection_instance(row)

    return get_no_feature_selection_instance(row)


def get_normalized_instance(row, processing_type, max_values, min_values):
    """Function returns instance with normalized values"""
    instance = get_processed_instance(row, processing_type)

    # Normalizes features by MIN-MAX scaling
    for idx, _value in enumerate(instance):
        is_last_column = idx == len(instance) - 1
        if is_last_column:
            continue
        instance[idx] = (
            0
            if ((max_values[idx] - min_values[idx]) == 0)
            else (instance[idx] - min_values[idx]) / (max_values[idx] - min_values[idx])
        )

    return instance


def contains_nullable_values(row):
    """Function returns True if row contains nullable values and False otherwise"""
    for idx, value in enumerate(row):
        if value == "" and idx not in FeaturesToRemove:
            return True

    return False


def compute_instances(csv_filename, processing_type):
    """Function computes instances, min values and max values"""
    min_values = []
    max_values = []
    is_first_iteration = True

    with open(csv_filename, encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")

        is_header = True

        for row in reader:
            if is_header:
                is_header = False
                continue

            if contains_nullable_values(row):
                continue

            instance = get_processed_instance(row, processing_type)

            for idx, value in enumerate(instance):
                is_last_column = idx == len(instance) - 1
                if is_last_column:
                    continue
                if is_first_iteration:
                    min_values.append(float(value))
                    max_values.append(float(value))
                else:
                    min_values[idx] = min(min_values[idx], float(value))
                    max_values[idx] = max(max_values[idx], float(value))

            is_first_iteration = False

    csv_file.close()

    return min_values, max_values


def get_csv_files(folder):
    """Function returns all csv files from folder"""
    csv_files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".csv"):
                csv_files.append(file_path)

    return csv_files


def execute(folder, processing_type):
    """Function further processes subset features and generates ARFF files"""

    csv_files = get_csv_files(folder)

    print("\nAdvanced processing started...\n")

    for csv_filename in tqdm(csv_files):
        min_values, max_values = compute_instances(csv_filename, processing_type)

        arff_filename = os.path.join(
            os.path.dirname(csv_filename),
            os.path.splitext(os.path.basename(csv_filename))[0] + ".arff",
        )

        with open(arff_filename, "w", newline="", encoding="utf-8") as arff_file:
            writer = csv.writer(
                arff_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )

            header = (
                balanced_feature_selection_header
                if processing_type == "balanced_fs"
                else (
                    unbalanced_feature_selection_header
                    if processing_type == "unbalanced_fs"
                    else no_feature_selection_header
                )
            )

            arff_file.writelines(header)

            with open(csv_filename, encoding="utf-8") as csv_file:
                csv_file.seek(0)
                reader = csv.reader(csv_file, delimiter=",")

                is_header = True

                for row in reader:
                    if is_header:
                        is_header = False
                        continue

                    if contains_nullable_values(row):
                        continue

                    normalized_instance = get_normalized_instance(
                        row, processing_type, max_values, min_values
                    )
                    writer.writerow(normalized_instance)

            csv_file.close()
        arff_file.close()

    print("\n...Advanced processing finished\n")


if __name__ == "__main__":
    args = parse()

    execute(args.folder, args.processing_type)
