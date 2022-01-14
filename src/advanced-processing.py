#########################################################################
#                                                                       #
# Project           : IoT DDoS Detection Based on Ensemble Methods for  #
#                     Evolving Data Stream Classification               #
#                                                                       #
# Program name      : advanced-processing.py                            #
#                                                                       #
# Authors           : Kétly Gonçalves Machado, Daniel Macêdo Batista    #
#                                                                       #
# Purpose           :                                                   #
#                                                                       #
#########################################################################

#This advanced processing is performed taking into account the information obtained from the Exploratory Data Analysis

import argparse
import csv

parser = argparse.ArgumentParser(description = "Advanced Processing")
# Parser to argument p1, which determines the path to the target file
# whose advanced processing will be performed
parser.add_argument("-p1", action = "store", dest = "path_1", 
                    default = "../processed-data/CSV/botiot-complete.csv", required = False,
                    help = "Path to the target file to be further processed.")
# Parser to argument p2, which determines the path to store the generated ARFF file
parser.add_argument("-p2", action = "store", dest = "path_2", 
                    default = "../processed-data/ARFF/botiot.arff", required = False,
                    help = "Path (file) to store the generated ARFF file.")

args = parser.parse_args()

def get_header_row(index):
    if (index == 5):
        return "@relation botiot\n"
    elif (index == 4):
        return "@attribute 'dport' numeric\n"
    elif (index == 3):
        return "@attribute 'CON' numeric\n"
    elif (index == 2):
        return "@attribute 'attack' {normal, attack}\n"
    elif (index == 1):
        return "@data\n"

def get_CON(row):
    return 1 if (row[10] == "CON") else 0

def dport(row):
    if (row[7] == ''):
        ret = -1
    elif "x" in (row[7]):
        ret = int(row[7], 16)
    else:
        ret = int(row[7])
    return ret

with open(args.path_2, "w", newline="") as botiot:

    spamwriter = csv.writer(botiot, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

    # Mudar para o definitivo quando possível
    with open(args.path_1) as data:

        csv_reader = csv.reader(data, delimiter=",")

        first = 1

        for row in csv_reader:

            if first:
                for i in range(5, 0, -1):
                    instance = get_header_row(i)
                    botiot.write(instance)
                first = 0
            else:
                instance = [dport(row), get_CON(row), ("attack" if int(row[32]) == 1 else "normal")]
                spamwriter.writerow(instance)

    data.close()
botiot.close()