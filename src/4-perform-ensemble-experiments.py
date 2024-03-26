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

def parse():
    parser = argparse.ArgumentParser(description = "Ensemble Experiments")

    parser.add_argument("-input", action = "store", dest = "input", required = True,
                        help = "Path to the folder that contains the ARFF files that will be the input for the ensemble experiments.")

    parser.add_argument("-output", action = "store", dest = "output", required = True,
                        help = "Path to the folder that will store the results from the ensemble experiments performed.")

    arguments = parser.parse_args()

    if (arguments.input[-1] != "/"):
        arguments.input = arguments.input + "/"

    if (arguments.output[-1] != "/"):
        arguments.output = arguments.output + "/"

    return arguments

def ensemble(i):
    if i == 0: return "ADACC"
    elif i == 1: return "DWM"
    elif i == 2: return "LevBag"
    elif i == 3: return "OAUE"
    elif i == 4: return "OzaBag"
    elif i == 5: return "OzaBagADWIN"
    elif i == 6: return "OzaBagASHT"
    elif i == 7: return "OzaBoost"

args = parse()

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
    



# #!/bin/bash

# while getopts 'i:o:e:' flag; do
#     case "${flag}" in
#         i) inputfiles="${OPTARG}" ;;
#         o) outputfolder="${OPTARG}" ;;
#         e) ensemble="${OPTARG^^}" ;;
#     esac
# done

# if [ "$ensemble" == "ADACC" ]; then
# # Anticipative Dynamic Adaptation to Concept Changes
#     efolder="ADACC"
#     name="adacc"
#     learner="meta.ADACC"
# elif [ "$ensemble" == "DWM" ]; then
# # Dynamic Weighted Majority
#     efolder="DWM"
#     name="dwm"
#     learner="meta.DynamicWeightedMajority"
# elif [ "$ensemble" == "LEVBAG" ]; then
# # Leveraging Bagging
#     efolder="LevBag"
#     name="lb"
#     learner="meta.LeveragingBag"
# elif [ "$ensemble" == "OAUE" ]; then
# # Online Accuracy Updated Ensemble
#     efolder="OAUE"
#     name="oaue"
#     learner="meta.OnlineAccuracyUpdatedEnsemble"
# elif [ "$ensemble" == "OZABAG" ]; then
# # Online Bagging
#     efolder="OzaBag"
#     name="ob"
#     learner="meta.OzaBag"
# elif [ "$ensemble" == "OZABAGADWIN" ]; then
# # Online Bagging with ADWIN drift detector
#     efolder="OzaBagADWIN"
#     name="obadwin"
#     learner="meta.OzaBagAdwin"
# elif [ "$ensemble" == "OZABAGASHT" ]; then
# # Online Bagging with Adaptive-Size Hoeffding Trees
#     efolder="OzaBagASHT"
#     name="obasht"
#     learner="(meta.OzaBagASHT -l ASHoeffdingTree)"
# elif [ "$ensemble" == "OZABOOST" ]; then
# # Online Boosting
#     efolder="OzaBoost"
#     name="obst"
#     learner="meta.OzaBoost"
# else
#     exit 1
# fi

# for file in $inputfiles; do    

#     lines=$(wc -l < $file)

#     ((lines=lines/1000))

#     output="$outputfolder$efolder/$name-${file:(-11):6}.csv"

#     `java -cp ../moa-release-2021.07.0/lib/moa.jar -javaagent:../moa-release-2021.07.0/lib/sizeofag-1.0.4.jar moa.DoTask \
#         "EvaluateInterleavedTestThenTrain \
#             -l $learner \
#             -s (ArffFileStream -f $file) \
#             -e WindowClassificationPerformanceEvaluator \
#             -f $lines" \
#     > $output 2> /dev/null`;
# done