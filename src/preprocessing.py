###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : preprocessing.py                                 #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Preprocesses the data from the original files of #
#                the BoT-IoT dataset and generates CSV files      #
#                containing all the normal traffic instances and  #
#                a percentage of the DDoS attack (except HTTP)    #
#                traffic instances. If the parameter -p is        #
#                informed, it generates a single file with the    #
#                given percentage. Otherwise, if the parameters   #
#                -s, -f and -i are informed, it generates         #
#                multiple files, each containing the percentage   #
#                given by the range from -s to -f, based on -i    #
#                interval. Also generates TXT files with          #
#                information about the generated subset of data.  #
#                Furthermore, it splits IPv4 and IPv6 features    #
#                into 4 or 8 new dummy features, respectively.    #
#                                                                 #
###################################################################

import argparse
import csv
import random
import re
import os
from multiprocessing import Pool
from tap import Tap


def restricted_float(x) -> float:
    """Function validates restricted float."""
    try:
        x = float(x)
    except TypeError as e:
        raise argparse.ArgumentTypeError(f"{x} not a floating-point literal") from e

    if x < 0.0 or x > 100.0:
        raise argparse.ArgumentTypeError(f"{x} not in range [0.0, 100.0]")
    return x


class ArgumentParser(Tap):
    """Class defines arguments typing."""

    percentage: float | None = None  # percentage of attack instances
    start: float | None = None  # the range start
    finish: float | None = None  # the range finish
    interval: float | None = None  # the range interval
    folder: str  # folder to store resulting files
    decimals: int = 4  # number of decimals digits to consider


def parse():
    """Function parses arguments."""
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


# Splits IPv4 into 4 new features, one per part of the address
# Sets IPv6 features to -1
def handle_ipv4(row: "list[str]", index: int) -> None:
    """Function handles IPv4 conversion."""
    ipv4 = row[index].split(".")
    for element in ipv4:
        row.append(element)
    for _ in range(8):
        row.append(-1)


# Splits IPv6 into 8 new features, one per part of the address
# Sets IPv4 features to -1
def handle_ipv6(row: "list[str]", index: int) -> None:
    """Function handles IPv6 conversion."""
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


def add_header(file: str) -> None:
    """Function adds header to processed file."""
    with open(
        "../raw-data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv",
        encoding="utf-8",
    ) as features:
        with open(file, "w", encoding="utf-8") as processed_file:
            header = features.read()[:-1]
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
            processed_file.write(header)
        processed_file.close()
    features.close()


def create_info_file(file: str, normal_instances: int, attack_instances: int) -> None:
    """Function creates info file about the processed data."""
    with open(file, "w", encoding="utf-8") as info_file:
        info_file.write("Total normal instances = " + str(normal_instances) + "\n")
        info_file.write("Total DDoS attack instances = " + str(attack_instances) + "\n")
        total = normal_instances + attack_instances
        info_file.write(
            "Final number of instances (normal + attack) = " + str(total) + "\n"
        )
    info_file.close()


def create_processed_file(percentage: str) -> None:
    """Function creates the processed file."""

    columns = {"source_ip": 4, "destination_ip": 6, "category": 33, "subcategory": 34}

    count_normal = 0
    count_ddos = 0

    # Defines the pattern for IPv4
    pattern = re.compile("^(\\d{1,3}\\.){3}\\d{1,3}$")

    filepath = os.path.join(csvpath, "botiot-" + percentage + ".csv")

    add_header(filepath)

    with open(filepath, "w", newline="", encoding="utf-8") as processed_file:
        spamwriter = csv.writer(
            processed_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        # Reads each one of the files from the original dataset
        for i in range(1, 75):
            original_file = os.path.join(
                "../raw-data/BoT-IoT/",
                "UNSW_2018_IoT_Botnet_Dataset_" + str(i) + ".csv",
            )

            with open(original_file, encoding="utf-8") as subset_file:
                data = csv.reader(subset_file, delimiter=",")

                for instance in data:
                    # Convert source and destination IP addresses from categorical to numerical
                    # Done at this point to avoid a possible future use of memory to process it
                    if pattern.match(instance[columns["source_ip"]]):
                        handle_ipv4(instance, columns["source_ip"])
                    else:
                        handle_ipv6(instance, columns["source_ip"])

                    if pattern.match(instance[columns["destination_ip"]]):
                        handle_ipv4(instance, columns["destination_ip"])
                    else:
                        handle_ipv6(instance, columns["destination_ip"])

                    # It considers the instance only if it is either normal
                    # or DDoS attack traffic (except HTTP)
                    if instance[columns["category"]] == "Normal":
                        spamwriter.writerow(instance)
                        count_normal = count_normal + 1
                    elif (
                        instance[columns["category"]] == "DDoS"
                        and instance[columns["subcategory"]] != "HTTP"
                    ):
                        # Randomly chooses to include or not the attack instance
                        if random.random() < (float(percentage) / 100.00):
                            spamwriter.writerow(instance)
                            count_ddos = count_ddos + 1

            subset_file.close()
    processed_file.close()

    create_info_file(
        os.path.join(infopath, "info-botiot-" + percentage + ".txt"),
        count_normal,
        count_ddos,
    )


def create_folders() -> None:
    """Function creates the destination folders."""
    try:
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)

        if not os.path.exists(infopath):
            os.makedirs(infopath)
    except OSError as e:
        raise OSError("Error while creating destination folders") from e


args = parse()

csvpath = os.path.join(args.folder, "CSV")
infopath = os.path.join(args.folder, "INFO")

if not args.percentage is None:
    create_processed_file(str(args.percentage))
elif not args.start is None and not args.finish is None and args.interval:
    percentages: "list[str]" = []
    COUNTER = args.start

    while COUNTER <= args.finish:
        percentages.append(format(COUNTER, f".{args.decimals}f"))
        COUNTER = COUNTER + args.interval

    print(f"Percentages considered: {percentages}\n")

    print("Process started...")

    with Pool(len(percentages)) as pool:
        pool.map(create_processed_file, percentages)

    print("...Process finished")
