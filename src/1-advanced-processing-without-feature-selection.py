###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : advanced-processing-without-feature-selection.py #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Performs an advanced processing of the CSV files #
#                passed through parameter "-c" to treat or remove #
#                features and deal with null values, aiming to    #
#                produce ARFF files that will be used to perform  #
#                the experiments at Massive Online Analysis (MOA) #
#                                                                 #
###################################################################

import argparse
import csv
import os


def parse():
    parser = argparse.ArgumentParser(
        description="Advanced Processing",
        usage="This program can be used to perform advanced processing to CSV files containing BoT-IoT subsets, tranforming them into ARFF files.",
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


def check_null_int(feature):
    if feature == "":
        return -1
    elif "x" in (feature):
        return int(feature, 16)
    else:
        return int(feature)


def check_null_float(feature):
    if feature == "":
        return -1
    else:
        return float(feature)


def get_flgs_dummies(flgs):
    return [
        (1 if flgs == "e *" else 0),
        (1 if flgs == "e" else 0),
        (1 if flgs == "e    F" else 0),
        (1 if flgs == "e s" else 0),
        (1 if flgs == "eU" else 0),
        (1 if flgs == "e g" else 0),
        (1 if flgs == "e &" else 0),
        (1 if flgs == "e d" else 0),
        (1 if flgs == "e r" else 0),
    ]


def get_proto_dummies(proto):
    return [
        (1 if proto == "icmp" else 0),
        (1 if proto == "igmp" else 0),
        (1 if proto == "udp" else 0),
        (1 if proto == "arp" else 0),
        (1 if proto == "tcp" else 0),
        (1 if proto == "ipv6-icmp" else 0),
        (1 if proto == "rarp" else 0),
    ]


def get_state_dummies(state):
    return [
        (1 if state == "RSP" else 0),
        (1 if state == "CON" else 0),
        (1 if state == "FIN" else 0),
        (1 if state == "REQ" else 0),
        (1 if state == "ACC" else 0),
        (1 if state == "NRS" else 0),
        (1 if state == "URP" else 0),
        (1 if state == "RST" else 0),
        (1 if state == "INT" else 0),
    ]


no_validation_cols = [
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
]
int_validation_cols = [0, 5, 7, 8, 9, 12, 25, 26, 27, 28]
float_validation_cols = [
    1,
    11,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    29,
    30,
    31,
]
flgs_col = 2
proto_col = 3
state_col = 10
label_col = 32

header = [
    "@relation botiot\n",
    "@attribute 'pkseqid' numeric\n",
    "@attribute 'stime' numeric\n",
    # flgs
    "@attribute 'e*' numeric\n",
    "@attribute 'e' numeric\n",
    "@attribute 'eF' numeric\n",
    "@attribute 'es' numeric\n",
    "@attribute 'eU' numeric\n",
    "@attribute 'eg' numeric\n",
    "@attribute 'e&' numeric\n",
    "@attribute 'ed' numeric\n",
    "@attribute 'er' numeric\n",
    # proto
    "@attribute 'icmp' numeric\n",
    "@attribute 'igmp' numeric\n",
    "@attribute 'udp' numeric\n",
    "@attribute 'arp' numeric\n",
    "@attribute 'tcp' numeric\n",
    "@attribute 'ipv6-icmp' numeric\n",
    "@attribute 'rarp' numeric\n",
    #
    "@attribute 'sport' numeric\n",
    "@attribute 'dport' numeric\n",
    "@attribute 'pkts' numeric\n",
    "@attribute 'bytes' numeric\n",
    # state
    "@attribute 'RSP' numeric\n",
    "@attribute 'CON' numeric\n",
    "@attribute 'FIN' numeric\n",
    "@attribute 'REQ' numeric\n",
    "@attribute 'ACC' numeric\n",
    "@attribute 'NRS' numeric\n",
    "@attribute 'URP' numeric\n",
    "@attribute 'RST' numeric\n",
    "@attribute 'INT' numeric\n",
    #
    "@attribute 'ltime' numeric\n",
    "@attribute 'seq' numeric\n",
    "@attribute 'dur' numeric\n",
    "@attribute 'mean' numeric\n",
    "@attribute 'stddev' numeric\n",
    "@attribute 'smac' numeric\n",
    "@attribute 'dmac' numeric\n",
    "@attribute 'sum' numeric\n",
    "@attribute 'min' numeric\n",
    "@attribute 'max' numeric\n",
    "@attribute 'soui' numeric\n",
    "@attribute 'doui' numeric\n",
    "@attribute 'sco' numeric\n",
    "@attribute 'dco' numeric\n",
    "@attribute 'spkts' numeric\n",
    "@attribute 'dpkts' numeric\n",
    "@attribute 'sbytes' numeric\n",
    "@attribute 'dbytes' numeric\n",
    "@attribute 'rate' numeric\n",
    "@attribute 'srate' numeric\n",
    "@attribute 'drate' numeric\n",
    "@attribute 'sipv4_pos1' numeric\n",
    "@attribute 'sipv4_pos2' numeric\n",
    "@attribute 'sipv4_pos3' numeric\n",
    "@attribute 'sipv4_pos4' numeric\n",
    "@attribute 'sipv6_pos1' numeric\n",
    "@attribute 'sipv6_pos2' numeric\n",
    "@attribute 'sipv6_pos3' numeric\n",
    "@attribute 'sipv6_pos4' numeric\n",
    "@attribute 'sipv6_pos5' numeric\n",
    "@attribute 'sipv6_pos6' numeric\n",
    "@attribute 'sipv6_pos7' numeric\n",
    "@attribute 'sipv6_pos8' numeric\n",
    "@attribute 'dipv4_pos1' numeric\n",
    "@attribute 'dipv4_pos2' numeric\n",
    "@attribute 'dipv4_pos3' numeric\n",
    "@attribute 'dipv4_pos4' numeric\n",
    "@attribute 'dipv6_pos1' numeric\n",
    "@attribute 'dipv6_pos2' numeric\n",
    "@attribute 'dipv6_pos3' numeric\n",
    "@attribute 'dipv6_pos4' numeric\n",
    "@attribute 'dipv6_pos5' numeric\n",
    "@attribute 'dipv6_pos6' numeric\n",
    "@attribute 'dipv6_pos7' numeric\n",
    "@attribute 'dipv6_pos8' numeric\n",
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

    csv_file = os.path.join(args.csv_path, filename)

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
                    # Main changes:
                    # Checks for null values and replaces it by -1
                    # Replaces features flgs, proto and state by its dummies, through one-hot encoding
                    # Removes features saddr and daddr since they were already treated and converted to 24 new features
                    # Removes features category and subcategory since they will not be considered in the classification
                    instance = []

                    for idx, col in enumerate(row):
                        if idx in no_validation_cols:
                            instance.append(col)
                        elif idx in int_validation_cols:
                            instance.append(check_null_int(col))
                        elif idx in float_validation_cols:
                            instance.append(check_null_float(col))
                        elif idx == flgs_col:
                            instance = instance + get_flgs_dummies(col)
                        elif idx == proto_col:
                            instance = instance + get_proto_dummies(col)
                        elif idx == state_col:
                            instance = instance + get_state_dummies(col)
                        elif idx == label_col:
                            # Establishes the label - feature "attack" - as the only categorical feature
                            # since this is required by some of the algorithms used in MOA
                            instance.append("attack" if int(row[32]) == 1 else "normal")

                    writer.writerow(instance)

        ARFF_botiot.close()
    CSV_botiot.close()
