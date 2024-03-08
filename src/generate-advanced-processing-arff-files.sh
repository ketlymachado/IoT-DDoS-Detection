unset -v foldername
unset -v option

while getopts 'f:o:' flag; do
    case "${flag}" in
    f) foldername="${OPTARG}" ;;
    o) option="${OPTARG}" ;;
    *)
        echo 'Error in command line parsing' >&2
        exit 1
        ;;
    esac
done

if [ -z "$foldername" ] || [ -z "$option" ]; then
    echo 'Missing -f or -o flag' >&2
    exit 1
fi

for file in ../processed-data/CSV/$foldername/*; do
    $(python ./advanced-processing-$option.py \
        -p1 $file \
        -p2 ../processed-data/ARFF/$foldername/botiot-${file:54:6}.arff)
done
