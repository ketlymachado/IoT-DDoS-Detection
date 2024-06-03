import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tap import Tap
from tqdm import tqdm
from typing_extensions import Literal

ensemble_algorithms = [
    "ADACC",
    "DWM",
    "LEVBAG",
    "OAUE",
    "OZABAG",
    "OZABAGADWIN",
    "OZABAGASHT",
    "OZABOOST",
]

ensemble_algorithms_config = {
    "ADACC": {"name": "adacc"},
    "DWM": {"name": "dwm"},
    "LEVBAG": {"name": "lb"},
    "OAUE": {"name": "oaue"},
    "OZABAG": {"name": "ob"},
    "OZABAGADWIN": {"name": "obadwin"},
    "OZABAGASHT": {"name": "obasht"},
    "OZABOOST": {"name": "obst"},
}

translator = {
    "xAxis": {"PT-BR": "Instâncias", "EN": "Instances"},
    "yAxis": {"PT-BR": "Acurácia (%)", "EN": "Accuracy (%)"},
}


class ArgumentParser(Tap):
    """Class defines arguments typing"""

    identifier: str  # experiment identifier that names the data and results folder
    language: Literal["PT-BR", "EN"]  # plot language


def parse() -> ArgumentParser:
    """Function parses arguments"""

    parser = ArgumentParser(
        description="Plot Experiments",
        usage="""This program can be used to plot the experiments.""",
    )

    arguments = parser.parse_args()

    return arguments


def plot(result_folder, plot_folder, language):
    """Function plots result"""

    if not os.path.exists(plot_folder):
        os.makedirs(plot_folder)

    sns.set_theme(
        context="paper",
        style="darkgrid",
        palette=sns.color_palette("colorblind"),
        font="Liberation Serif",
        font_scale=1.5,
    )

    initial_ensemble = pd.read_csv(
        os.path.join(
            result_folder,
            ensemble_algorithms_config["ADACC"]["name"] + ".csv",
        )
    )
    result = initial_ensemble[["classified instances"]]
    result = result.rename(columns={"classified instances": translator["xAxis"][language]})

    for ensemble in ensemble_algorithms:
        algorithm = ensemble_algorithms_config[ensemble]["name"]
        ensemble_results = pd.read_csv(os.path.join(result_folder, algorithm + ".csv"))

        accuracy_column = "classifications correct (percent)"

        result = pd.concat([result, ensemble_results[[accuracy_column]]], axis=1)
        result = result.rename(columns={accuracy_column: algorithm})

    # Adjusts the DataFrame to make it possible to plot all ensemble methods at once
    melted_result = result.melt(
        translator["xAxis"][language],
        var_name="Ensemble",
        value_name=translator["yAxis"][language],
    )

    # Lineplot
    sns.lineplot(
        x=translator["xAxis"][language],
        y=translator["yAxis"][language],
        hue="Ensemble",
        data=melted_result,
    )

    figure = plt.gcf()
    figure.set_size_inches(12, 6)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_folder, "lineplot.pdf"), format="pdf")

    # Facetgrid
    ax = sns.FacetGrid(data=melted_result, col="Ensemble", hue="Ensemble", col_wrap=2)
    ax.map(sns.lineplot, translator["xAxis"][language], translator["yAxis"][language])

    figure = plt.gcf()
    figure.set_size_inches(12, 15)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_folder, "facetgrid.pdf"), format="pdf")

    plt.clf()
    plt.close("all")


def execute(identifier, language):
    """Function performs experiments plots"""
    results_folder = os.path.join(
        Path(__file__).absolute().parent, "../results/moa", identifier
    )
    plots_folder = os.path.join(
        Path(__file__).absolute().parent, "../results/plots", identifier
    )

    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)

    subfolders = []

    for subfolder in os.listdir(results_folder):
        if os.path.isdir(os.path.join(results_folder, subfolder)):
            subfolders.append(subfolder)

    print("\nPlotting experiments...\n")

    for folder in tqdm(subfolders):
        plot(
            os.path.join(results_folder, folder),
            os.path.join(plots_folder, folder),
            language,
        )

    print("\nExperiments plotted...\n")


if __name__ == "__main__":
    args = parse()

    execute(args.identifier, args.language)
