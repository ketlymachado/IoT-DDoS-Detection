###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : generate-advanced-processing-arff-files.sh       #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Generates advanced processing on CSV files that  #
#                contain BoT-IoT data, accordingly to option      #
#                parameter, that defines which type of processing #
#                will be performed. Also converts CSV files to    #
#                ARFF files, that can be used to perform          #
#                experiments at Massive Online Analysis (MOA).    #
#                To do so, uses the proper advanced-processing    #
#                program.                                         #
#                                                                 #
###################################################################

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
