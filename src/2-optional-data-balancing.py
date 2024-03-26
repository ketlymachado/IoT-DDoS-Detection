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
import os


def parse():
    parser = argparse.ArgumentParser(
        description="Data Balancing",
        usage="This program can be used to perform data balancing to ARFF files containing BoT-IoT subsets.",
    )

    parser.add_argument(
        "-a",
        action="store",
        dest="arff_path",
        required=True,
        help="Path to the folder that contains the target ARFF files whose data will be balanced.",
    )

    parser.add_argument(
        "-i",
        action="store",
        dest="info_path",
        required=True,
        help="Path to the folder that will store information about the generated ARFF files whose data is balanced.",
    )

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
    idx_position = 3
    not_include = 0
    while min >= 0:
        sort = randrange(0, majority_size)
        while check_instances[majority[sort][idx_position]] == not_include:
            sort = randrange(0, majority_size)
        check_instances[majority[sort][idx_position]] = not_include
        min = min - 1


args = parse()

normal = []  # Stores the normal instances
attack = []  # Stores the attack instances
instances = []  # Stores all instances, including oversampling
check_instances = (
    []
)  # Binary list that indicates if an instance should or should not be included in the final data set

files = [
    f
    for f in os.listdir(args.arff_path)
    if os.path.isfile(os.path.join(args.arff_path, f))
]

for filename in files:

    print("Processing...")

    arff_file = os.path.join(args.arff_path, filename)

    header = []

    with open(arff_file) as ARFF_botiot:
        reader = csv.reader(ARFF_botiot, delimiter=",")

        index = -1

        for row in reader:
            if row[0][0] == "@":
                header.append("".join(row) + "\n")
                continue

            if row[-1] == "attack":
                attack.append(row)
                attack[-1].append(index)
            else:
                normal.append(row)
                normal[-1].append(index)

            instances.append(row)
            check_instances.append(1)
            index = index + 1

    ARFF_botiot.close()

    print(header)

    normal_size = len(normal)
    attack_size = len(attack)

    minority_class = normal if attack_size > normal_size else attack
    majority_class = normal if normal_size > attack_size else attack

    if (len(minority_class) / len(majority_class)) >= 0.5:
        print(
            "The minority class has a size equivalent to 50% or more of the size of the majority class."
        )
    else:
        random_oversampling(
            instances,
            check_instances,
            minority_class,
            len(majority_class),
        )
        random_undersampling(check_instances, majority_class)

    balanced_data_folder = os.path.join(args.arff_path, "balanced-data/")

    if not os.path.exists(balanced_data_folder):
        os.makedirs(balanced_data_folder)

    with open(balanced_data_folder + filename, "w", newline="") as ARFF_balanced_botiot:
        writer = csv.writer(
            ARFF_balanced_botiot,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )

        ARFF_balanced_botiot.writelines(header)

        include_instance = 1
        instances_size = len(instances)
        count_ddos = 0
        count_normal = 0

        for i in range(0, instances_size):
            if check_instances[i] == include_instance:
                writer.writerow(instances[i][:-1])
                if instances[i][2] == "attack":
                    count_ddos = count_ddos + 1
                elif instances[i][2] == "normal":
                    count_normal = count_normal + 1

    ARFF_balanced_botiot.close()

    balanced_data_info_folder = os.path.join(args.info_path, "balanced-data/")

    if not os.path.exists(balanced_data_info_folder):
        os.makedirs(balanced_data_info_folder)

    with open(
        balanced_data_info_folder + "info-" + filename[:-4] + "txt", "w"
    ) as balanced_info:
        balanced_info.write("Total normal instances = " + str(count_normal) + "\n")
        balanced_info.write("Total DDoS attack instances = " + str(count_ddos) + "\n")
        total = count_normal + count_ddos
        balanced_info.write(
            "Final number of instances (normal + attack) = " + str(total) + "\n"
        )
    balanced_info.close()
