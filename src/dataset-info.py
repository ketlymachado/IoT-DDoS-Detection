#########################################################################
#                                                                       #
# Project           :                                                   #
#                                                                       #
# Program name      : dataset-info.py                                   #
#                                                                       #
# Authors           : Kétly Gonçalves Machado, Daniel Macêdo Batista    #
#                                                                       #
# Purpose           :                                                   #
#                                                                       #
#########################################################################

import csv
from progress.bar import Bar

count_normal = 0
count_ddos = 0
count_tnormal = 0
count_tddos = 0
    
# Processing bar to follow the execution status
bar = Bar("Processing", max = 74)
# Reads each one of the files from the original dataset
for i in range(1, 75):
    with open("../raw-data/UNSW_2018_IoT_Botnet_Dataset_" + str(i) + ".csv") as data:

        csv_reader = csv.reader(data, delimiter=",")

        for row in csv_reader:
            if row[33] == "Normal":
                count_normal = count_normal + 1
            if (row[33] == "DDoS" and row[34] != "HTTP"):
                count_ddos = count_ddos + 1

        print(f"Total normal instances from file {i} = {count_normal}")
        print(f"Total DDoS attack instances from file {i} = {count_ddos}")
        print("\n\n")
        count_tnormal = count_tnormal + count_normal
        count_tddos = count_tddos + count_ddos
        count_normal = 0
        count_ddos = 0
                    
    bar.next()
bar.finish()

print(f"Total normal instances = {count_tnormal}")
print(f"Total DDoS attack instances = {count_tddos}")
print("\n")