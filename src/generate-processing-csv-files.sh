###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : generate-processing-csv-files.sh                 #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      : Generates several CSV files containing           #
#                percentages of the BoT-IoT dataset, accordingly  #
#                to start, finish and interval parameters. To     #
#                generate the CSV files uses the preprocessing.py #
#                program.                                         #
#                                                                 #
###################################################################

unset -v start
unset -v finish
unset -v interval
unset -v folder
unset -v decimals

while getopts 's:f:i:p:d:' flag; do
    case "${flag}" in
    s) start="${OPTARG}" ;;
    f) finish="${OPTARG}" ;;
    i) interval="${OPTARG}" ;;
    p) folder="${OPTARG}" ;;
    d) decimals="${OPTARG}" ;;
    *)
        echo 'Error in command line parsing' >&2
        exit 1
        ;;
    esac
done

if [ -z "$start" ] || [ -z "$finish" ] ||
    [ -z "$interval" ] || [ -z "$folder" ] ||
    [ -z "$decimals" ]; then
    echo 'Missing -s or -f or -i or -p or -d flag' >&2
    exit 1
fi

if [ $(bc <<<"$start < 0") -eq 1 ] || [ $(bc <<<"$start > 100") -eq 1 ] ||
    [ $(bc <<<"$finish < 0") -eq 1 ] || [ $(bc <<<"$finish > 100") -eq 1 ] ||
    [ $(bc <<<"$interval <= 0") -eq 1 ] || [ $(bc <<<"$interval > 100") -eq 1 ] ||
    [ $(bc <<<"$decimals <= 0") -eq 1 ] || [ $(bc <<<"$decimals > 6") -eq 1 ]; then
    echo 'Invalid values for arguments:
    -s, -f and -i must be between 0 and 100
    -d must be between 0 and 6' >&2
    exit 1
fi

counter=$(bc <<<"$start")

while :; do
    echo $(bc <<<"$counter" | awk '{printf "%0.3f", $0}')
    $(python ./preprocessing.py \
        -p $(bc <<<"$counter" | awk '{printf "%0.'$decimals'f", $0}') \
        -csvpath '../processed-data/CSV/'$folder'/' \
        -infopath '../processed-data/INFO/'$folder'/')
    counter=$(bc <<<"$counter+$interval")
    [ $(bc <<<"$counter <= $finish") -eq 0 ] && break
done
