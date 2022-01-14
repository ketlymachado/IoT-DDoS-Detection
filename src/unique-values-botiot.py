###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : unique-values-botiot.py                          #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Find the unique values of the features flgs,     #
#                proto and state from BoT-IoT dataset for         #
#                the advanced processing of the data.             #
#                                                                 #
###################################################################

import csv
from progress.bar import Bar 

maxlines = 38522252

with open("../processed-data/CSV/botiot-complete.csv") as botiot:

    reader = csv.reader(botiot, delimiter=",")

    unique_flgs = set()
    unique_proto = set()
    unique_state = set()

    first = True

    bar = Bar("Processing", max = maxlines)

    for row in reader:

        if first:
            first = False
        else:
            unique_flgs.add(row[2])
            unique_proto.add(row[3])
            unique_state.add(row[10])
        
        bar.next()
    bar.finish()

    print(unique_flgs)
    print(unique_proto)
    print(unique_state)

botiot.close()