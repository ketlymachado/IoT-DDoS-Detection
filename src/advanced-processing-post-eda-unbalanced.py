###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : advanced-processing-post-eda-unbalanced.py       #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Performs an advanced processing of the CSV file  #
#                passed through parameter "-csv" to treat or      #
#                remove features and deal with null values aiming #
#                to produce a final ARFF file (passed through     #
#                parameter "-arff") that will be used to perform  #
#                the experiments at Massive Online Analysis (MOA) #
#                                                                 #
#                The advanced processing is performed considering #
#                the results obtained through the Exploratory     #
#                Data Analysis of the BoT-IoT dataset. This       #
#                processing, particularly, it is not interested   #
#                at balancing the data, meaning that the          #
#                distribution of instances per class in the final #
#                generated ARFF file will follow the original     #
#                distribution of the received CSV file.           #
#                                                                 #
###################################################################

import argparse
import csv

def parse():
    parser = argparse.ArgumentParser(description = "Advanced Processing")

    parser.add_argument("-csv", action = "store", dest = "csv", 
                        default = "../processed-data/CSV/botiot-complete.csv", required = False,
                        help = "Path to the target file to be further processed.")

    parser.add_argument("-arff", action = "store", dest = "arff", 
                        default = "../processed-data/ARFF/experiments/botiot.arff", required = False,
                        help = "Path (file) to store the generated ARFF file.")

    return parser.parse_args()

header = ["@relation botiot\n",
          "@attribute 'CON' numeric\n",
          "@attribute 'attack' {normal, attack}\n",
          "@data\n"]

args = parse()

with open(args.arff, "w", newline="") as ARFF_botiot:

    writer = csv.writer(ARFF_botiot, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)

    with open(args.csv) as CSV_botiot:

        reader = csv.reader(CSV_botiot, delimiter=",")

        flag = True

        print("Processing...")

        for row in reader:

            if flag:
                # Ignores the CSV header and includes the appropriate ARFF header
                ARFF_botiot.writelines(header)
                flag = False
            else:
                # Creates the instance with the final features/data
                instance = [(1 if row[10] == "CON" else 0), # Creates the feature CON as a dummy from the feature state
                            ("attack" if int(row[32]) == 1 else "normal")
                            # Establishes the label - feature "attack" - as the only categorical feature 
                            # since this is required by some of the algorithms used in MOA
                            ]
                writer.writerow(instance)

    CSV_botiot.close()
ARFF_botiot.close()