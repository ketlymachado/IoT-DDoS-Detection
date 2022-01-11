import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

start = 0.0125
finish = 1
step = 0.0125

sns.set_theme(context = "paper", 
              #style = "whitegrid",
              style = "darkgrid",
              palette = sns.color_palette("colorblind"),
              font = "Liberation Serif",
              font_scale = 1.5)

while start <= finish:

    ensemble = pd.read_csv("../moa-results/threshold-experiments/ADACC/adacc-" + "{:.4f}".format(start) + ".csv")

    result = ensemble[["classified instances"]]

    result = result.rename(columns={"classified instances": "Instâncias"})

    i = 0
    while True:
        result = pd.concat([result, ensemble[["classifications correct (percent)"]]], axis=1)
        result = result.rename(columns={"classifications correct (percent)":ensemble_NAME(i)})
        i = i + 1
        if i >= 8: break
        ensemble = pd.read_csv("../moa-results/threshold-experiments/" + ensemble_NAME(i) + "/" + ensemble_name(i) + "-" + "{:.4f}".format(start) + ".csv")

    resultm = result.melt("Instâncias", var_name = "Ensemble", value_name = "Acurácia (%)")

    ax = sns.lineplot(x = "Instâncias", 
                      y = "Acurácia (%)", 
                      hue = "Ensemble", 
                      #style = "Ensemble",
                      #dashes = False,
                      #markers = True,
                      data = resultm)

    #plt.show()
    figure = plt.gcf()
    figure.set_size_inches(12, 6)
    plt.tight_layout()
    plt.savefig("../moa-results/plots/threshold-experiments/lineplot/lp-" + "{:.4f}".format(start) + ".eps", format="eps")

    ax = sns.FacetGrid(data = resultm, col = "Ensemble", hue = "Ensemble", col_wrap = 2)
    ax.map(sns.lineplot, "Instâncias", "Acurácia (%)")
    
    #plt.show()
    figure = plt.gcf()
    figure.set_size_inches(12, 15)
    plt.tight_layout()
    plt.savefig("../moa-results/plots/threshold-experiments/facetgrid/fg-" + "{:.4f}".format(start) + ".eps", format="eps")

    plt.clf()
    plt.close("all")
    
    start = start + step