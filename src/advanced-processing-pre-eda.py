###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : advanced-processing-pre-eda.py                   #
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

def check_null_int(feature):
    if feature == "": return -1
    elif "x" in (feature): return int(feature, 16)
    else: return int(feature)

def check_null_float(feature):
    if feature == "": return -1
    else: return float(feature)

header = ["@relation botiot\n",
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
                instance = [check_null_int(row[0]),
                            check_null_float(row[1]),
                            (1 if row[2] == "e *" else 0),
                            (1 if row[2] == "e" else 0),
                            (1 if row[2] == "e    F" else 0),
                            (1 if row[2] == "e s" else 0),
                            (1 if row[2] == "eU" else 0),
                            (1 if row[2] == "e g" else 0),
                            (1 if row[2] == "e &" else 0),
                            (1 if row[2] == "e d" else 0),
                            (1 if row[2] == "e r" else 0),
                            (1 if row[3] == "icmp" else 0),
                            (1 if row[3] == "igmp" else 0),
                            (1 if row[3] == "udp" else 0),
                            (1 if row[3] == "arp" else 0),
                            (1 if row[3] == "tcp" else 0),
                            (1 if row[3] == "ipv6-icmp" else 0),
                            (1 if row[3] == "rarp" else 0),
                            check_null_int(row[5]),
                            check_null_int(row[7]),
                            check_null_int(row[8]),
                            check_null_int(row[9]),
                            (1 if row[10] == "RSP" else 0),
                            (1 if row[10] == "CON" else 0),
                            (1 if row[10] == "FIN" else 0),
                            (1 if row[10] == "REQ" else 0),
                            (1 if row[10] == "ACC" else 0),
                            (1 if row[10] == "NRS" else 0),
                            (1 if row[10] == "URP" else 0),
                            (1 if row[10] == "RST" else 0),
                            (1 if row[10] == "INT" else 0),
                            check_null_float(row[11]),
                            check_null_int(row[12]),
                            check_null_float(row[13]),
                            check_null_float(row[14]),
                            check_null_float(row[15]),
                            check_null_float(row[16]),
                            check_null_float(row[17]),
                            check_null_float(row[18]),
                            check_null_float(row[19]),
                            check_null_float(row[20]),
                            check_null_float(row[21]),
                            check_null_float(row[22]),
                            check_null_float(row[23]),
                            check_null_float(row[24]),
                            check_null_int(row[25]),
                            check_null_int(row[26]),
                            check_null_int(row[27]),
                            check_null_int(row[28]),
                            check_null_float(row[29]),
                            check_null_float(row[30]),
                            check_null_float(row[31]),
                            row[35], row[36], row[37], row[38], # Source IPv4
                            row[39], row[40], row[41], row[42], row[43], row[44], row[45], row[46], # Source IPv6
                            row[47], row[48], row[49], row[50], # Destination IPv4
                            row[51], row[52], row[53], row[54], row[55], row[56], row[57], row[58], # Destination IPv6
                            ("attack" if int(row[32]) == 1 else "normal")
                            # Establishes the label - feature "attack" - as the only categorical feature 
                            # since this is required by some of the algorithms used in MOA
                            ]
                writer.writerow(instance)

    CSV_botiot.close()
ARFF_botiot.close()