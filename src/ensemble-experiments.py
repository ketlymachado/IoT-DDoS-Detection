###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : ensemble-experiments.py                          #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Performs the ensemble experiments, instantiating #
#                MOA's tasks (in parallel) for each algorithm to  #
#                be evaluated (ADACC, DWM, LevBag, OAUE, OzaBag,  #
#                OzaBagADWIN, OzaBagASHT & Ozaboost). It receives # 
#                the folder that contains the ARFF data files     #
#                that will be used as input for the experiments   #
#                and produces one CSV file for each algorithm     #
#                that contains the results of its evaluation.     #
#                                                                 #
###################################################################

import argparse
import os
import subprocess as sp

parser = argparse.ArgumentParser(description = "Ensemble Experiments")

parser.add_argument("-input", action = "store", dest = "input", required = True,
                    help = "Path to the folder that contains the ARFF files that will be the input for the ensemble experiments.")

parser.add_argument("-output", action = "store", dest = "output", required = True,
                    help = "Path to the folder that will store the results from the ensemble experiments performed.")

args = parser.parse_args()

def ensemble(i):
    if i == 0: return "ADACC"
    elif i == 1: return "DWM"
    elif i == 2: return "LevBag"
    elif i == 3: return "OAUE"
    elif i == 4: return "OzaBag"
    elif i == 5: return "OzaBagADWIN"
    elif i == 6: return "OzaBagASHT"
    elif i == 7: return "OzaBoost"

if (args.input[-1] != "/"):
    args.input = args.input + "/"

if (args.output[-1] != "/"):
    args.output = args.output + "/"

for i in range(0, 8):
    path = args.output + ensemble(i)
    if not os.path.exists(path):
        os.makedirs(path)

commands = []

for i in range(0, 8):
    # Invokes the "ensembles.sh" script, that instantiate MOA's task
    commands.append("./ensembles.sh -i \"" + args.input + "*\" -o " + args.output + " -e " + ensemble(i))

procs = [ sp.Popen(i, shell = True) for i in commands ]

for p in procs:
    p.wait()