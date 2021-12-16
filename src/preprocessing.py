#########################################################################
#                                                                       #
# Project           : IoT DDoS Detection Based on Ensemble Methods for  #
#                     Evolving Data Stream Classification               #
#                                                                       #
# Program name      : preprocessing.py                                  #
#                                                                       #
# Authors           : Kétly Gonçalves Machado, Daniel Macêdo Batista    #
#                                                                       #
# Purpose           : Preprocesses the data from BoT-IoT dataset and    #
#                     generates a CSV file containing all the normal    #
#                     traffic instances and a sample (or all, depending #
#                     on the percentage inputed) of the DDoS attack     #
#                     (except HTTP) traffic instances.                  #
#                                                                       #
#########################################################################

import argparse
import csv
import random
import re
from progress.bar import Bar

# Splits IPv4 into 4 new features, one per part of the address
# Sets IPv6 features to -1
def ipv4(row, index):
    ipv4 = row[index].split(".")
    for e in ipv4:
        row.append(e)
    for _ in range(8):
        row.append(-1)

# Splits IPv6 into 8 new features, one per part of the address
# Sets IPv4 features to -1
def ipv6(row, index):
    ipv6 = row[index].split(":")
    for i, e in enumerate(ipv6):
        if e == "":
            ipv6.remove("")
            for j in range(0, 8 - len(ipv6)):
                ipv6.insert(i + j, "0")
            break
    for i, e in enumerate(ipv6):
        ipv6[i] = int(e, 16)
    if len(ipv6) < 8:
        for j in range(0, 8 - len(ipv6)):
            ipv6.append(-1)
    for i in range(4):
        row.append(-1)
    for e in ipv6:
        row.append(e)

# Parser to argument p, which determines the percentage of attack instances 
# to be considered in the preprocessing of the BoT-IoT dataset
parser = argparse.ArgumentParser(description = "Preprocessing")
parser.add_argument("-p", action = "store", dest = "p", 
                    default = "100", required = True,
                    help = "Percentage of attack instances to be considered.")
# Parser to argument path, which determines the path to store the generated CSV file
parser.add_argument("-path", action = "store", dest = "path", 
                    default = "../processed-data/CSV/", required = False,
                    help = "Path (folder) to store the generated CSV file.")
# Parser to argument i, which determines the path to store info about the generated CSV file
parser.add_argument("-i", action = "store", dest = "i", 
                    default = "../processed-data/INFO/", required = False,
                    help = "Path (folder) to store info about the generated CSV file.")

args = parser.parse_args()

# Adds the header to the data
with open("../raw-data/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv") as features:
    with open(args.path + "botiot-" + args.p + ".csv", "w") as botiot:
        header = features.read()[:-1]
        # Source and destination IP addresses extra features
        header = header + ",sipv4_pos1,sipv4_pos2,sipv4_pos3,sipv4_pos4,sipv6_pos1,sipv6_pos2,sipv6_pos3,sipv6_pos4,sipv6_pos5,sipv6_pos6,sipv6_pos7,sipv6_pos8"
        header = header + ",dipv4_pos1,dipv4_pos2,dipv4_pos3,dipv4_pos4,dipv6_pos1,dipv6_pos2,dipv6_pos3,dipv6_pos4,dipv6_pos5,dipv6_pos6,dipv6_pos7,dipv6_pos8\n"
        botiot.write(header)
    botiot.close()
features.close()

with open(args.path + "botiot-" + args.p + ".csv", "a", newline="") as botiot:

    spamwriter = csv.writer(botiot, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

    print("\n")

    count_normal = 0
    count_ddos = 0
    
    # Defines the pattern for IPv4
    pattern = re.compile("^(\d{1,3}\.){3}\d{1,3}$")

    # Processing bar to follow the execution status
    bar = Bar("Processing", max = 74)

    # Reads each one of the files from the original dataset
    for i in range(1, 75):
        with open("../raw-data/UNSW_2018_IoT_Botnet_Dataset_" + str(i) + ".csv") as data:

            csv_reader = csv.reader(data, delimiter=",")

            for row in csv_reader:
                # Source and destination IP addresses technique to convert from categorical to numerical
                    # Done at this point to avoid deal with it in the memory while performing the EDA
                if (pattern.match(row[4])):
                    ipv4(row, 4)
                else:
                    ipv6(row, 4)
                if (pattern.match(row[6])):
                    ipv4(row, 6)
                else:
                    ipv6(row, 6)
                # We consider the instance only if it is either normal or DDoS attack traffic (except HTTP)
                if row[33] == "Normal":
                    spamwriter.writerow(row)
                    count_normal = count_normal + 1
                elif (row[33] == "DDoS" and row[34] != "HTTP"):
                    # Randomly chooses to include or not the attack instance based on the chosen percentage
                    x = random.random()
                    if x < (float(args.p) / 100.00):
                        spamwriter.writerow(row)
                        count_ddos = count_ddos + 1

        data.close()
        bar.next()
    bar.finish()

    with open(args.i + "info-botiot-" + args.p, "w") as info:
        info.write("Total normal instances = " + str(count_normal) + "\n")
        info.write("Total DDoS attack instances = " + str(count_ddos) + "\n")
        total = count_normal + count_ddos
        info.write("Final number of instances (normal + attack) = " + str(total) + "\n")
    info.close()

botiot.close()