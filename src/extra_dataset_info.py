import csv
import os
from pathlib import Path

COUNT_FILE_NORMAL = 0
COUNT_FILE_DDOS = 0
COUNT_TOTAL_NORMAL = 0
COUNT_TOTAL_DDOS = 0

LABEL_COLUMN = 33
CATEGORY_COLUMN = 34

DATASET_FOLDER = os.path.join(Path(__file__).absolute().parent, "../raw-data/BoT-IoT/")
DATASET_FILE_PREFIX = "UNSW_2018_IoT_Botnet_Dataset_"

for i in range(1, 75):
    original_file = os.path.join(
        DATASET_FOLDER,
        DATASET_FILE_PREFIX + str(i) + ".csv",
    )
    with open(original_file, encoding="utf-8") as subset:
        csv_reader = csv.reader(subset, delimiter=",")

        for row in csv_reader:
            if row[LABEL_COLUMN] == "Normal":
                COUNT_FILE_NORMAL = COUNT_FILE_NORMAL + 1
            if row[LABEL_COLUMN] == "DDoS" and row[CATEGORY_COLUMN] != "HTTP":
                COUNT_FILE_DDOS = COUNT_FILE_DDOS + 1

        print(f"Total normal instances from file {i} = {COUNT_FILE_NORMAL}")
        print(f"Total DDoS attack instances from file {i} = {COUNT_FILE_DDOS}")
        print()
        COUNT_TOTAL_NORMAL = COUNT_TOTAL_NORMAL + COUNT_FILE_NORMAL
        COUNT_TOTAL_DDOS = COUNT_TOTAL_DDOS + COUNT_FILE_DDOS
        COUNT_FILE_NORMAL = 0
        COUNT_FILE_DDOS = 0

print(f"Total normal instances = {COUNT_TOTAL_NORMAL}")
print(f"Total DDoS attack instances = {COUNT_TOTAL_DDOS}")
print("\n")
