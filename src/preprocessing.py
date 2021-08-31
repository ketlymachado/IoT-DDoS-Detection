#########################################################################
#                                                                       #
# Project           :                                                   #
#                                                                       #
# Program name      : preprocessing.py                                  #
#                                                                       #
# Authors           : Kétly Gonçalves Machado, Daniel Macêdo Batista    #
#                                                                       #
# Purpose           : Preprocesses the data from BoT-IoT dataset and    #
#                     generates a CSV file containing all the normal    #
#                     traffic instances and a sample (or all, depending #
#                     on the percentage inputed) of the DDoS attack     #
#                     traffic instances.                                #
#                                                                       #
#########################################################################


import argparse
import csv
import random
from progress.bar import Bar

# Parser to argument p, which determines the percentage of attack instances 
# to be considered in the preprocessing of the BoT-IoT dataset
parser = argparse.ArgumentParser(description = "Preprocessing")
parser.add_argument("-p", action = "store", dest = "p", 
                    default = "100", required = True,
                    help = "Percentage of attack instances to be considered.")

args = parser.parse_args()

# Adds the header to the data
with open("../raw-data/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv") as features:
    with open("../processed-data/botiot-" + args.p + ".csv", "w") as botiot:
        botiot.write(features.read() + "\n")
    botiot.close()

with open("../processed-data/botiot-" + args.p + ".csv", "a", newline="") as botiot:

    spamwriter = csv.writer(botiot, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

    print("\n")

    count_normal = 0
    count_ddos = 0
    
    # Processing bar to follow the execution status
    bar = Bar("Processing", max = 74)
    # Reads each one of the files from the original dataset
    for i in range(1, 75):
        with open("../raw-data/UNSW_2018_IoT_Botnet_Dataset_" + str(i) + ".csv") as data:

            csv_reader = csv.reader(data, delimiter=",")

            for row in csv_reader:
                # We consider the instance only if it is either normal or DDoS attack traffic
                # 08/30 Test - Considering reconnaissance attacks as normal traffic
                #if row[33] == "Normal" or row[33] == "Reconnaissance" or (row[33] == "DDoS" and row[34] != "HTTP"):
                if row[33] == "Normal" or (row[33] == "DDoS" and row[34] != "HTTP"):
                    #if row[33] == "Reconnaissance":
                        #row[32] = "0"
                    if row[33] == "Normal": #or row[33] == "Reconnaissance":
                        spamwriter.writerow(row)
                        count_normal = count_normal + 1
                    else:
                        x = random.random()
                        # Randomly chooses to include or not the attack instance based on the chosen percentage
                        if x < (float(args.p) / 100.00):
                            spamwriter.writerow(row)
                            count_ddos = count_ddos + 1
                    
        bar.next()
    bar.finish()

    print(f"Total normal instances = {count_normal}")
    print(f"Total DDoS attack instances = {count_ddos}")
    print(f"Final number of instances (normal + attack) = {count_normal + count_ddos}")
    print("\n")

botiot.close()