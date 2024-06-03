import csv

COUNT_NORMAL = 0
COUNT_DDOS = 0
COUNT_TNORMAL = 0
COUNT_TDDOS = 0

LABEL_COLUMN = 33
CATEGORY_COLUMN = 34

# Reads each one of the files from the original dataset
for i in range(1, 75):
    with open(
        "../raw-data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_" + str(i) + ".csv",
        encoding="utf-8",
    ) as data:
        csv_reader = csv.reader(data, delimiter=",")

        for row in csv_reader:
            if row[LABEL_COLUMN] == "Normal":
                COUNT_NORMAL = COUNT_NORMAL + 1
            if row[LABEL_COLUMN] == "DDoS" and row[CATEGORY_COLUMN] != "HTTP":
                COUNT_DDOS = COUNT_DDOS + 1

        print(f"{i:0.2d}/74")
        print(f"Total normal instances from file {i} = {COUNT_NORMAL}")
        print(f"Total DDoS attack instances from file {i} = {COUNT_DDOS}")
        print()
        COUNT_TNORMAL = COUNT_TNORMAL + COUNT_NORMAL
        COUNT_TDDOS = COUNT_TDDOS + COUNT_DDOS
        COUNT_NORMAL = 0
        COUNT_DDOS = 0

print(f"Total normal instances = {COUNT_TNORMAL}")
print(f"Total DDoS attack instances = {COUNT_TDDOS}")
print("\n")
