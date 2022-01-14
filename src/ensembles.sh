#!/bin/bash

while getopts 'i:o:e:' flag; do
    case "${flag}" in
        i) inputfiles="${OPTARG}" ;;
        o) outputfolder="${OPTARG}" ;;
        e) ensemble="${OPTARG^^}" ;;
    esac
done

if [ "$ensemble" == "ADACC" ]; then
# Anticipative Dynamic Adaptation to Concept Changes
    efolder="ADACC"
    name="adacc"
    learner="meta.ADACC"
elif [ "$ensemble" == "DWM" ]; then
# Dynamic Weighted Majority
    efolder="DWM"
    name="dwm"
    learner="meta.DynamicWeightedMajority"
elif [ "$ensemble" == "LEVBAG" ]; then
# Leveraging Bagging
    efolder="LevBag"
    name="lb"
    learner="meta.LeveragingBag"
elif [ "$ensemble" == "OAUE" ]; then
# Online Accuracy Updated Ensemble
    efolder="OAUE"
    name="oaue"
    learner="meta.OnlineAccuracyUpdatedEnsemble"
elif [ "$ensemble" == "OZABAG" ]; then
# Online Bagging
    efolder="OzaBag"
    name="ob"
    learner="meta.OzaBag"
elif [ "$ensemble" == "OZABAGADWIN" ]; then
# Online Bagging with ADWIN drift detector
    efolder="OzaBagADWIN"
    name="obadwin"
    learner="meta.OzaBagAdwin"
elif [ "$ensemble" == "OZABAGASHT" ]; then
# Online Bagging with Adaptive-Size Hoeffding Trees
    efolder="OzaBagASHT"
    name="obasht"
    learner="(meta.OzaBagASHT -l ASHoeffdingTree)"
elif [ "$ensemble" == "OZABOOST" ]; then
# Online Boosting
    efolder="OzaBoost"
    name="obst"
    learner="meta.OzaBoost"
else
    exit 1
fi

for file in $inputfiles; do    

    lines=$(wc -l < $file)

    ((lines=lines/1000))

    output="$outputfolder$efolder/$name-${file:(-11):6}.csv"

    `java -cp ../moa-release-2021.07.0/lib/moa.jar -javaagent:../moa-release-2021.07.0/lib/sizeofag-1.0.4.jar moa.DoTask \
        "EvaluateInterleavedTestThenTrain \
            -l $learner \
            -s (ArffFileStream -f $file) \
            -e WindowClassificationPerformanceEvaluator \
            -f $lines" \
    > $output 2> /dev/null`;
done