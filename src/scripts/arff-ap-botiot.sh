for file in ../../processed-data/CSV/threshold-experiments/*; do
    `python ../advanced-processing.py \
    -p1 $file \
    -p2 ../../processed-data/ARFF/threshold-experiments/botiot-${file:54:6}.arff`;
done