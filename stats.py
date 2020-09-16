from constants import EXPANSION_RARITY_STATS
from mtga_set_completion import mtg_set
import pandas as pd
import numpy as np


def experiment(num_trials, verbose=False):
    col_names = [
        "Expansion Code",
        "Packs Purchased",
        "Packs Opened",
        "Standard Dev",
        "min",
        "5%",
        "median",
        "95%",
        "max",
    ]

    data = {}
    for col_name in col_names:
        data[col_name] = []

    for expansion_code in EXPANSION_RARITY_STATS:
        packs_purchased = []
        packs_opened = []
        for t in range(num_trials):
            if verbose and t % 100 == 0:
                print("Running trial {} out of {}".format(t, num_trials))
            mtg_set_instance = mtg_set(EXPANSION_RARITY_STATS[expansion_code])
            packs_purchased.append(mtg_set_instance.complete_set())
            packs_opened.append(mtg_set_instance.packs_opened)

        data["Expansion Code"].append(expansion_code)
        data["Packs Purchased"].append(np.average(packs_purchased))
        data["Standard Dev"].append(np.std(packs_purchased))
        data["min"].append(np.min(packs_purchased))
        data["5%"].append(np.percentile(packs_purchased, 5))
        data["median"].append(np.percentile(packs_purchased, 50))
        data["95%"].append(np.percentile(packs_purchased, 95))
        data["max"].append(np.max(packs_purchased))
        data["Packs Opened"].append(np.average(packs_opened))

    pd.DataFrame(data, columns=col_names).to_csv(
        "{}k.csv".format(num_trials // 1000)
    )

def rare_experiment(num_trials, verbose=False):
    col_names = [
        "Expansion Code",
        "Packs Purchased",
        "Packs Opened",
        "Standard Dev",
        "min",
        "5%",
        "median",
        "95%",
        "max",
        "mythics"
    ]

    data = {}
    for col_name in col_names:
        data[col_name] = []

    for expansion_code in EXPANSION_RARITY_STATS:
        packs_purchased = []
        packs_opened = []
        mythics = []
        for t in range(num_trials):
            if verbose and t % 100 == 0:
                print("Running trial {} out of {}".format(t, num_trials))
            mtg_set_instance = mtg_set(EXPANSION_RARITY_STATS[expansion_code])
            packs_purchased.append(mtg_set_instance.complete_rare_set())
            packs_opened.append(mtg_set_instance.packs_opened)
            mythics.append(sum(mtg_set_instance.preexisting[3]) + mtg_set_instance.wildcards[3])

        data["Expansion Code"].append(expansion_code)
        data["Packs Purchased"].append(np.average(packs_purchased))
        data["Standard Dev"].append(np.std(packs_purchased))
        data["min"].append(np.min(packs_purchased))
        data["5%"].append(np.percentile(packs_purchased, 5))
        data["median"].append(np.percentile(packs_purchased, 50))
        data["95%"].append(np.percentile(packs_purchased, 95))
        data["max"].append(np.max(packs_purchased))
        data["Packs Opened"].append(np.average(packs_opened))
        data["mythics"].append(np.average(mythics))

    pd.DataFrame(data, columns=col_names).to_csv(
        "rare{}k.csv".format(num_trials // 1000)
    )


if __name__ == "__main__":
    rare_experiment(10000)