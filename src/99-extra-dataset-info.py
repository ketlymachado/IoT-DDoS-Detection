###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : dataset-info.py                                  #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Prints information describing the total number   #
#                of instances in the BoT-IoT, detailing the       #
#                number of instances per class in each file that  #
#                constitutes the dataset.                         #
#                                                                 #
###################################################################

import csv
from progress.bar import Bar

count_normal = 0
count_ddos = 0
count_tnormal = 0
count_tddos = 0

# Reads each one of the files from the original dataset
for i in range(1, 75):
    with open("../raw-data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_" + str(i) + ".csv") as data:

        csv_reader = csv.reader(data, delimiter=",")

        for row in csv_reader:
            if row[33] == "Normal":
                count_normal = count_normal + 1
            if (row[33] == "DDoS" and row[34] != "HTTP"):
                count_ddos = count_ddos + 1

        print("%02d/74" % i)
        print(f"Total normal instances from file {i} = {count_normal}")
        print(f"Total DDoS attack instances from file {i} = {count_ddos}")
        print()
        count_tnormal = count_tnormal + count_normal
        count_tddos = count_tddos + count_ddos
        count_normal = 0
        count_ddos = 0

print(f"Total normal instances = {count_tnormal}")
print(f"Total DDoS attack instances = {count_tddos}")
print("\n")