import argparse
import csv
import random
import re
import os
from pathlib import Path
from tap import Tap
from p_tqdm import p_map
from tqdm import tqdm

DATASET_FOLDER = os.path.join(Path(__file__).absolute().parent, "../raw-data/BoT-IoT/")
DATASET_FILE_PREFIX = "UNSW_2018_IoT_Botnet_Dataset_"


def restricted_float(x):
    """Function validates restricted float"""
    try:
        x = float(x)
    except TypeError as e:
        raise argparse.ArgumentTypeError(f"{x} not a floating-point literal") from e

    if x < 0.0 or x > 100.0:
        raise argparse.ArgumentTypeError(f"{x} not in range [0.0, 100.0]")
    return x


class ArgumentParser(Tap):
    """Class defines arguments typing"""

    percentage: float | None = None  # percentage of attack instances
    start: float | None = None  # the range start
    finish: float | None = None  # the range finish
    interval: float | None = None  # the range interval
    folder: str  # folder to store resulting files
    decimals: int = 4  # number of decimals digits to consider


def parse() -> ArgumentParser:
    """Function parses arguments"""
    parser = ArgumentParser(
        description="BoT-IoT Preprocessing",
        usage="""This program can be used to preprocess the BoT-IoT dataset.
        A percentage or a range, defined by start, finish and interval, 
        must be informed to define the amount of attack instances that will
        be included in the final resulting CSV file.""",
    )

    arguments = parser.parse_args()

    if arguments.percentage is None and (
        arguments.start is None
        or arguments.finish is None
        or arguments.interval is None
    ):
        parser.error("a percentage or a range of percentages must be informed")

    if not arguments.percentage is None:
        restricted_float(arguments.percentage)
    else:
        restricted_float(arguments.start)
        restricted_float(arguments.finish)
        restricted_float(arguments.interval)

    return arguments


def create_info_file(file, normal_instances, attack_instances):
    """Function creates info file about the processed data"""
    with open(file, "w", encoding="utf-8") as info_file:
        info_file.write("Total normal instances = " + str(normal_instances) + "\n")
        info_file.write("Total DDoS attack instances = " + str(attack_instances) + "\n")
        total = normal_instances + attack_instances
        info_file.write(
            "Final number of instances (normal + attack) = " + str(total) + "\n"
        )
    info_file.close()


# Splits IPv6 into 8 new features, one per part of the address
# Sets IPv4 features to -1
def handle_ipv6(row, index):
    """Function handles IPv6 conversion"""
    ipv6 = row[index].split(":")

    for idx, element in enumerate(ipv6):
        if element == "":
            ipv6.remove("")
            for i in range(0, 8 - len(ipv6)):
                ipv6.insert(idx + i, "0")
            break

    for idx, element in enumerate(ipv6):
        ipv6[idx] = int(element, 16)

    if len(ipv6) < 8:
        for _ in range(0, 8 - len(ipv6)):
            ipv6.append(-1)

    for i in range(4):
        row.append(-1)

    for element in ipv6:
        row.append(element)


# Splits IPv4 into 4 new features, one per part of the address
# Sets IPv6 features to -1
def handle_ipv4(row, index):
    """Function handles IPv4 conversion"""
    ipv4 = row[index].split(".")
    for element in ipv4:
        row.append(element)
    for _ in range(8):
        row.append(-1)


def handle_ip(instance):
    """Function handles IP conversion"""
    ip_columns = {"source": 4, "destination": 6}
    ipv4_pattern = re.compile("^(\\d{1,3}\\.){3}\\d{1,3}$")

    # Convert source and destination IP addresses from categorical to numerical
    # Done at this point to avoid a possible future use of memory to process it
    if ipv4_pattern.match(instance[ip_columns["source"]]):
        handle_ipv4(instance, ip_columns["source"])
    else:
        handle_ipv6(instance, ip_columns["source"])

    if ipv4_pattern.match(instance[ip_columns["destination"]]):
        handle_ipv4(instance, ip_columns["destination"])
    else:
        handle_ipv6(instance, ip_columns["destination"])


def add_header(file):
    """Function adds header to processed file"""
    features_file_name = "Feature_Names.csv"

    with open(
        os.path.join(DATASET_FOLDER, DATASET_FILE_PREFIX + features_file_name),
        encoding="utf-8",
    ) as features:
        header = features.read()[:-1]
    features.close()

    # Source and destination IP addresses extra features
    header = (
        header
        + ","
        + "sipv4_pos1,sipv4_pos2,sipv4_pos3,sipv4_pos4,"
        + "sipv6_pos1,sipv6_pos2,sipv6_pos3,sipv6_pos4,"
        + "sipv6_pos5,sipv6_pos6,sipv6_pos7,sipv6_pos8,"
        + "dipv4_pos1,dipv4_pos2,dipv4_pos3,dipv4_pos4,"
        + "dipv6_pos1,dipv6_pos2,dipv6_pos3,dipv6_pos4,"
        + "dipv6_pos5,dipv6_pos6,dipv6_pos7,dipv6_pos8\n"
    )

    with open(file, "w", encoding="utf-8") as processed_file:
        processed_file.write(header)
    processed_file.close()


def create_folder(folder, percentage):
    """Function creates the destination folder"""

    folder_name = os.path.join(folder, percentage)

    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    except OSError as e:
        raise OSError("Error while creating destination folder") from e

    return folder_name


def create_processed_file(data):
    """Function creates the processed file"""

    category_columns = {"category": 33, "subcategory": 34}

    count_normal = 0
    count_ddos = 0

    folder_name = create_folder(data["folder"], data["percentage"])
    filename = os.path.join(folder_name, "botiot-subset.csv")

    add_header(filename)

    with open(filename, "a", newline="", encoding="utf-8") as processed_file:
        spamwriter = csv.writer(
            processed_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        for i in tqdm(range(1, 75)):
            original_file = os.path.join(
                DATASET_FOLDER,
                DATASET_FILE_PREFIX + str(i) + ".csv",
            )

            with open(original_file, encoding="utf-8") as subset_file:
                subset = csv.reader(subset_file, delimiter=",")

                for instance in subset:
                    # It considers the instance only if it is either normal
                    # or DDoS attack traffic (except HTTP)
                    if instance[category_columns["category"]] == "Normal":
                        handle_ip(instance)
                        spamwriter.writerow(instance)
                        count_normal = count_normal + 1
                    elif (
                        instance[category_columns["category"]] == "DDoS"
                        and instance[category_columns["subcategory"]] != "HTTP"
                    ):
                        # Randomly chooses to include or not the attack instance
                        if random.random() < (float(data["percentage"]) / 100.00):
                            handle_ip(instance)
                            spamwriter.writerow(instance)
                            count_ddos = count_ddos + 1

                subset_file.close()
        processed_file.close()

    create_info_file(
        os.path.join(folder_name, "botiot-subset-info.txt"),
        count_normal,
        count_ddos,
    )


def execute(start, finish, interval, decimals, folder):
    """Function preprocesses dataset files"""
    print("\nPreprocessing started...\n")

    data = []
    counter = start

    while counter <= finish:
        percentage = format(counter, f".{decimals}f")
        data.append({"percentage": percentage, "folder": folder})
        counter = counter + interval

    p_map(create_processed_file, data)

    print("\n...Preprocessing finished\n")


if __name__ == "__main__":
    args = parse()

    if not args.percentage is None:
        execute(args.percentage, args.percentage, 100, args.decimals, args.folder)
    elif not args.start is None and not args.finish is None and args.interval:
        execute(args.start, args.finish, args.interval, args.decimals, args.folder)
