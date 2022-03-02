###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : advanced-processing-post-eda-balanced.py         #
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
#                processing, particularly, it is interested at    #
#                balancing the data, meaning that it will use     #
#                random over and under-sampling techniques to     #
#                balance the distribution of instances per class  #
#                in the final generated ARFF file.                #
#                                                                 #
#                Final result will have 50% of the new size of    #
#                the majority class as the number of instances    #
#                in the minority class and 70% of the original    #
#                size of the majority class as the new number of  #
#                instances in the majority class.                 #
#                                                                 #
###################################################################

import argparse
import csv
from random import randrange
from tabnanny import check

def parse():
    parser = argparse.ArgumentParser(description = "Advanced Processing")

    parser.add_argument("-csv", action = "store", dest = "csv", 
                        default = "../processed-data/CSV/botiot-complete.csv", required = False,
                        help = "Path to the target file to be further processed.")

    parser.add_argument("-arff", action = "store", dest = "arff", 
                        default = "../processed-data/ARFF/experiments/botiot.arff", required = False,
                        help = "Path (file) to store the generated ARFF file.")

    parser.add_argument("-info", action = "store", dest = "info", required = True, 
                        help = "Path (file) to store info about the generated ARFF file.")

    return parser.parse_args()

def random_oversampling(instances, check_instances, minority, majority_size):
    # We choose to make the new size of the minority class equal to 50% of the new size of the majority class
    # Since we choose to make the new size of the majority class equal to 70% of its original size 
    # this means that the new size of the minority class will be 35% of the original size
    # The oversampled instances will be placed at the end of the data structure
    max = int(majority_size * 0.35)
    minority_size = len(minority)
    while max >= 0:
        sort = randrange(0, minority_size)
        instances.append(minority[sort])
        check_instances.append(1)
        max = max - 1

def random_undersampling(check_instances, majority):
    # We choose to make the new size of the majority class equal to 70% of its original size 
    # As so, we remove 30% of the original instances that belong to the majority class
    majority_size = len(majority)
    min = int(majority_size * 0.3)
    while min >= 0:
        sort = randrange(0, majority_size)
        while check_instances[majority[sort][3]] == 0:
            sort = randrange(0, majority_size)
        check_instances[majority[sort][3]] = 0
        min = min - 1

args = parse()

normal = [] # Stores the normal instances
attack = [] # Stores the attack instances
instances = [] # Stores all instances, including oversampling
check_instances = [] # Binary list that indicates if an instance should or should not be included in the final dataset

with open(args.csv) as CSV_botiot:

    reader = csv.reader(CSV_botiot, delimiter=",")

    first = True

    index = -1

    print("Processing...")

    for row in reader:
        
        if first:
            first = False
            continue

        # Creates the instance with the final features/data
        instance = [(1 if row[10] == "CON" else 0), # Creates the feature CON as a dummy from the feature state
                    row[38], # sipv4_pos4
                    ("attack" if int(row[32]) == 1 else "normal")
                    # Establishes the label - feature "attack" - as the only categorical feature 
                    # since this is required by some of the algorithms used in MOA
                    ]
        
        if (int(row[32]) == 1):
            attack.append(instance)
            attack[-1].append(index)
        else:
            normal.append(instance)
            normal[-1].append(index)

        instances.append(instance)
        check_instances.append(1)
        index = index + 1

CSV_botiot.close()

normal_size = len(normal)
attack_size = len(attack)

if (min(normal_size, attack_size) / max(normal_size, attack_size)) >= 0.5:
    print("The minority class has a size equivalent to 50% or more of the size of the majority class.")
else:
    if (normal_size > attack_size):
        random_oversampling(instances, check_instances, attack, normal_size)
        random_undersampling(check_instances, normal)
    elif (attack_size > normal_size):
        random_oversampling(instances, check_instances, normal, attack_size)
        random_undersampling(check_instances, attack)

header = ["@relation botiot\n",
          "@attribute 'sipv4_pos4' numeric\n",
          "@attribute 'CON' numeric\n",
          "@attribute 'attack' {normal, attack}\n",
          "@data\n"]

with open(args.arff, "w", newline="") as ARFF_botiot:

    writer = csv.writer(ARFF_botiot, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
    
    ARFF_botiot.writelines(header)

    instances_size = len(instances)
    count_ddos = 0
    count_normal = 0

    for i in range(0, instances_size):
        if (check_instances[i] == 1):
            writer.writerow(instances[i])
            if (instances[i][2] == "attack"):
                count_ddos = count_ddos + 1
            elif (instances[i][2] == "normal"):
                count_normal = count_normal + 1

    with open(args.info, "w") as info:
        info.write("Total normal instances = " + str(count_normal) + "\n")
        info.write("Total DDoS attack instances = " + str(count_ddos) + "\n")
        total = count_normal + count_ddos
        info.write("Final number of instances (normal + attack) = " + str(total) + "\n")
    info.close()

ARFF_botiot.close()