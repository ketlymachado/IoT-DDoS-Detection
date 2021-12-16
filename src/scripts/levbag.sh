#!/bin/bash

for file in ../../processed-data/ARFF/threshold-experiments/*; do

    lines=$(wc -l < $file)
    #(wc -l $file)

    ((lines=lines/1000))

    # Leveraging Bagging
    `java -cp ../../moa-release-2021.07.0/lib/moa.jar -javaagent:../../moa-release-2021.07.0/lib/sizeofag-1.0.4.jar moa.DoTask \
        "EvaluateInterleavedTestThenTrain \
            -l meta.LeveragingBag \
            -s (ArffFileStream -f $file) \
            -e (WindowClassificationPerformanceEvaluator -w 1000) \
            -f $lines" \
    > ../../moa-results/threshold-experiments/LevBag/lb-${file:55:6}.csv`;
done