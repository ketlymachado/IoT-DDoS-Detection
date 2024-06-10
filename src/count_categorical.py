import csv
import os
from tqdm import tqdm
from tap import Tap
from columns import BoTIoTColumns


class ArgumentParser(Tap):
    """Class defines arguments typing"""

    folder: str  # folder with CSV data files


def parse() -> ArgumentParser:
    """Function parses arguments"""

    parser = ArgumentParser(
        description="Count Categorical",
        usage="""This program can be used to perform the count of categorical features.""",
    )

    arguments = parser.parse_args()

    return arguments


def get_csv_files(folder):
    """Function returns all csv files from folder"""
    csv_files = []

    for subfolder in os.listdir(folder):
        for file in os.listdir(os.path.join(folder, subfolder)):
            file_path = os.path.join(folder, subfolder, file)
            if os.path.isfile(file_path) and file_path.endswith(".csv"):
                csv_files.append(file_path)

    return csv_files


def execute(folder):
    """Function counts categorical features distinct values"""

    csv_files = get_csv_files(folder)

    distinct_values = {
        "flgs": {},
        "proto": {},
        "state": {},
    }

    for csv_filename in tqdm(csv_files):
        with open(csv_filename, encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            is_header = True

            for row in tqdm(reader):
                if is_header:
                    is_header = False
                    continue
                if row[BoTIoTColumns.FLGS] in distinct_values["flgs"]:
                    distinct_values["flgs"][row[BoTIoTColumns.FLGS]] += 1
                else:
                    distinct_values["flgs"][row[BoTIoTColumns.FLGS]] = 1

                if row[BoTIoTColumns.PROTO] in distinct_values["proto"]:
                    distinct_values["proto"][row[BoTIoTColumns.PROTO]] += 1
                else:
                    distinct_values["proto"][row[BoTIoTColumns.PROTO]] = 1

                if row[BoTIoTColumns.STATE] in distinct_values["state"]:
                    distinct_values["state"][row[BoTIoTColumns.STATE]] += 1
                else:
                    distinct_values["state"][row[BoTIoTColumns.STATE]] = 1

        csv_file.close()

    print("Distinct values of flgs:")
    print(f"{'Value':<15}{'Occurences':>10}")
    for key, value in distinct_values["flgs"].items():
        print(f"{key:<15}{value:>10}")

    print("Distinct values of proto:")
    print(f"{'Value':<15}{'Occurences':>10}")
    for key, value in distinct_values["proto"].items():
        print(f"{key:<15}{value:>10}")

    print("Distinct values of state:")
    print(f"{'Value':<15}{'Occurences':>10}")
    for key, value in distinct_values["state"].items():
        print(f"{key:<15}{value:>10}")


if __name__ == "__main__":
    args = parse()

    execute(args.folder)
