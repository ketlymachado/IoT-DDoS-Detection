###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : advanced-processing-with-feature-selection.py    #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Performs an advanced processing of the CSV files #
#                passed through parameter "-c" to treat or remove #
#                features and deal with null values, aiming to    #
#                produce ARFF files that will be used to perform  #
#                the experiments at Massive Online Analysis (MOA) #
#                                                                 #
#                This advanced processing is performed            #
#                considering the results obtained through the     #
#                Exploratory Data Analysis (EDA) of the BoT-IoT   #
#                dataset and, therefore, only includes the        #
#                features that best represent the data            #
#                                                                 #
###################################################################

import argparse
import csv
import os


def parse():
    parser = argparse.ArgumentParser(
        description="Advanced Processing",
        usage="This program can be used to perform advanced processing to CSV files containing BoT-IoT subsets, tranforming them into ARFF files. Also performs feature selection to improve data quality.",
    )

    parser.add_argument(
        "-c",
        action="store",
        dest="csv_path",
        required=True,
        help="Path to the folder that contains the target CSV files to be further processed.",
    )

    parser.add_argument(
        "-a",
        action="store",
        dest="arff_path",
        required=True,
        help="Path to the folder to store the generated ARFF files.",
    )

    return parser.parse_args()


state_col = 10
label_col = 32

header = [
    "@relation botiot\n",
    "@attribute 'sipv4_pos4' numeric\n",
    "@attribute 'CON' numeric\n",
    "@attribute 'attack' {normal, attack}\n",
    "@data\n",
]

args = parse()

files = [
    f
    for f in os.listdir(args.csv_path)
    if os.path.isfile(os.path.join(args.csv_path, f))
]

for filename in files:
    print("Processing...")

    csv_file = os.path.join(args.arff_path, filename)

    with open(csv_file) as CSV_botiot:
        reader = csv.reader(CSV_botiot, delimiter=",")

        arff_file = os.path.join(args.arff_path, filename[:-3] + "arff")

        with open(arff_file, "w", newline="") as ARFF_botiot:
            writer = csv.writer(
                ARFF_botiot, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )

            flag = True

            for row in reader:
                if flag:
                    # Ignores the CSV header and includes the ARFF header accordingly to the features treatment
                    ARFF_botiot.writelines(header)
                    flag = False
                else:
                    # Creates the instance with the final features/data
                    instance = [
                        # sipv4_pos4
                        row[38],
                        # Creates the feature CON as a dummy from the feature state
                        (1 if row[state_col] == "CON" else 0),
                        # Establishes the label - feature "attack" - as the only categorical feature
                        # since this is required by some of the algorithms used in MOA
                        ("attack" if int(row[label_col]) == 1 else "normal"),
                    ]

                    writer.writerow(instance)

        ARFF_botiot.close()
    CSV_botiot.close()
