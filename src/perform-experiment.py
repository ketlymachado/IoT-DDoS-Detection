###################################################################
#                                                                 #
# Project      : IoT DDoS Detection Based on Ensemble Methods for #
#                Evolving Data Stream Classification              #
#                                                                 #
# Program name : perform-experiment.py                            #
#                                                                 #
# Authors      : Kétly Gonçalves Machado, Daniel Macêdo Batista   #
#                                                                 #
# Purpose      :                                                  #
#                                                                 #
###################################################################

import argparse
import os
import subprocess as sp


def restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < 0.0 or x > 100.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 100.0]" % (x,))
    return x


def parse():
    parser = argparse.ArgumentParser(
        description="Perform Experiments",
        usage="This program can be used to perform ensemble learning experiments to the BoT-IoT dataset.\nThe argument -t informs the experiment's type, which must be 'single' for experiments that aim to test a single percentage of attacking data, or 'range', for experiments that aim to test the threshold from multiple percentages of attacking data.\nIf the experiment's type is 'single' then the parameter -p must be informed. Otherwise, the parameters -s, -f and -i must be informed. All number parameters must be between 0 and 100.",
    )

    parser.add_argument(
        "-t",
        action="store",
        dest="type",
        required=True,
        choices=["single", "range"],
        help="the experiment's type",
    )

    parser.add_argument(
        "-p",
        action="store",
        dest="percentage",
        required=False,
        type=restricted_float,
        help="the percentage of attacking data",
    )

    parser.add_argument(
        "-s",
        action="store",
        dest="start",
        required=False,
        type=restricted_float,
        help="the range start",
    )

    parser.add_argument(
        "-f",
        action="store",
        dest="finish",
        required=False,
        type=restricted_float,
        help="the range finish",
    )

    parser.add_argument(
        "-i",
        action="store",
        dest="interval",
        required=False,
        type=restricted_float,
        help="the range interval",
    )

    parser.add_argument(
        "-fs",
        action="store",
        dest="feature_selection",
        required=True,
        choices=["y", "n"],
        help="apply feature selection technique or not",
    )

    parser.add_argument(
        "-b",
        action="store",
        dest="balance",
        required=True,
        choices=["y", "n"],
        help="balance data distribution or not",
    )

    parser.add_argument(
        "-shuffle",
        action="store",
        dest="shuffle",
        required=True,
        choices=["y", "n"],
        help="shuffle the data instances or not",
    )

    args = parser.parse_args()

    if args.type == "single" and (args.percentage is None):
        parser.error("-type equals 'single' requires -p to be informed")

    if args.type == "range" and (
        args.start is None or args.finish is None or args.interval is None
    ):
        parser.error("-type equals 'range' requires -s, -f and -i to be informed")

    return args


def get_preprocessing_arguments(args):
    if args.type == "single":
        return "-p " + str(args.percentage)
    else:
        return (
            "-s "
            + str(args.start)
            + " -f "
            + str(args.finish)
            + " -i "
            + str(args.interval)
        )

args = parse()

paths = ["../processed-data/ARFF", "../processed-data/CSV", "../processed-data/INFO"]

for path in paths:
    if not os.path.exists(path):
        os.makedirs(path)

os.system("python preprocessing.py " + get_preprocessing_arguments(args))

# for i in range(0, 8):
#     path = args.output + ensemble(i)
#     if not os.path.exists(path):
#         os.makedirs(path)

# commands = []

# for i in range(0, 8):
#     # Invokes the "ensembles.sh" script, that instantiate MOA's task
#     commands.append("./ensembles.sh -i \"" + args.input + "*\" -o " + args.output + " -e " + ensemble(i))

# procs = [ sp.Popen(i, shell = True) for i in commands ]

# for p in procs:
#     p.wait()
