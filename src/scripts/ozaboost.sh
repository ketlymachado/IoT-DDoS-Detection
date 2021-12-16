#!/bin/bash

for file in ../../processed-data/ARFF/threshold-experiments/*; do

    lines=$(wc -l < $file)
    #(wc -l $file)

    ((lines=lines/1000))

    # Online Boosting
    `java -cp ../../moa-release-2021.07.0/lib/moa.jar -javaagent:../../moa-release-2021.07.0/lib/sizeofag-1.0.4.jar moa.DoTask \
        "EvaluateInterleavedTestThenTrain \
            -l meta.OzaBoost \
            -s (ArffFileStream -f $file) \
            -e (WindowClassificationPerformanceEvaluator -w 1000) \
            -f $lines" \
    > ../../moa-results/threshold-experiments/OzaBoost/obst-${file:55:6}.csv`;
done