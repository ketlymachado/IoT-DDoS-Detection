import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

def parse():
    parser = argparse.ArgumentParser(description = "Plot Results")

    parser.add_argument("-input", action = "store", dest = "input", required = True,
                        help = "Path to the folder that contains the files that represent the results of the experiments to be plotted.")

    parser.add_argument("-output", action = "store", dest = "output", required = True,
                        help = "Path to the folder where the generated plots will be stored.")

    arguments = parser.parse_args()

    if (arguments.input[-1] != "/"):
        arguments.input = arguments.input + "/"

    if (arguments.output[-1] != "/"):
        arguments.output = arguments.output + "/"

    return arguments

def ensemble_name(i):
    if i == 0: return "adacc"
    elif i == 1: return "dwm"
    elif i == 2: return "lb"
    elif i == 3: return "oaue"
    elif i == 4: return "ob"
    elif i == 5: return "obadwin"
    elif i == 6: return "obasht"
    elif i == 7: return "obst"

def ensemble_NAME(i):
    if i == 0: return "ADACC"
    elif i == 1: return "DWM"
    elif i == 2: return "LevBag"
    elif i == 3: return "OAUE"
    elif i == 4: return "OzaBag"
    elif i == 5: return "OzaBagADWIN"
    elif i == 6: return "OzaBagASHT"
    elif i == 7: return "OzaBoost"

def plot(input_path, suffix, output_path):

    path = output_path + "facetgrid"
    if not os.path.exists(path):
        os.makedirs(path)

    path = output_path + "lineplot"
    if not os.path.exists(path):
        os.makedirs(path)

    sns.set_theme(context = "paper", 
                  style = "darkgrid",
                  palette = sns.color_palette("colorblind"),
                  font = "Liberation Serif",
                  font_scale = 1.5)

    ensemble = pd.read_csv(input_path + "ADACC/adacc-" + suffix + ".csv")
    result = ensemble[["classified instances"]]
    result = result.rename(columns={"classified instances": "Instâncias"})

    i = 0

    while True:
        result = pd.concat([result, ensemble[["classifications correct (percent)"]]], axis=1)
        result = result.rename(columns={"classifications correct (percent)":ensemble_NAME(i)})
        i = i + 1
        if i >= 8: break
        ensemble = pd.read_csv(input_path + ensemble_NAME(i) + "/" + ensemble_name(i) + "-" + suffix + ".csv")

    resultm = result.melt("Instâncias", var_name = "Ensemble", value_name = "Acurácia (%)")

    sns.lineplot(x = "Instâncias", 
                 y = "Acurácia (%)", 
                 hue = "Ensemble",
                 data = resultm)

    figure = plt.gcf()
    figure.set_size_inches(12, 6)
    plt.tight_layout()
    plt.savefig(output_path + "lineplot/lp-" + suffix + ".eps", format="eps")

    ax = sns.FacetGrid(data = resultm, col = "Ensemble", hue = "Ensemble", col_wrap = 2)
    ax.map(sns.lineplot, "Instâncias", "Acurácia (%)")
    
    figure = plt.gcf()
    figure.set_size_inches(12, 15)
    plt.tight_layout()
    plt.savefig(output_path + "facetgrid/fg-" + suffix + ".eps", format="eps")

    plt.clf()
    plt.close("all")

args = parse()

adacc_dir = args.input + "ADACC/"

for filename in sorted(os.listdir(adacc_dir)):
    file = os.path.join(adacc_dir, filename)
    if os.path.isfile(file):
        suffix = file[-10:-4]
        plot(args.input, suffix, args.output)