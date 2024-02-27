import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import tomllib
import pingouin as pg

with open("../../config.toml", "rb") as f:
    toml = tomllib.load(f)
    col_blue = toml["col"]["blue"]
    col_blue_sec = toml["col"]["blue_sec"]
    col_trad = toml["col"]["trad"]
    linewidth = toml["linewidth"]
    linecolor = toml["linecolor"]
    dpi = toml["dpi"]
plt.rcParams['figure.dpi'] = dpi
plt.rcParams['savefig.dpi'] = dpi


pd.options.display.max_columns = None
pd.options.display.width = None

add_output_str = ""

# Load:
setup = pd.read_csv("setup_sus_with_inversions.csv", index_col="id")
setup_11 = pd.read_csv("setup_sus_11.csv", index_col="id")

usage_bt = pd.read_csv("usage_bt_sus_with_inversions.csv", index_col="id")
usage_bt_11 = pd.read_csv("usage_bt_sus_11.csv", index_col="id")

usage_trad = pd.read_csv("usage_trad_sus_with_inversions.csv", index_col="id")
usage_trad_11 = pd.read_csv("usage_trad_sus_11.csv", index_col="id")

# remove row of id == 9 in usage_bt, because this participant didn't use blue totp how it was meant to be used
usage_bt = usage_bt[~(usage_bt.index == 9)]
usage_bt_11 = usage_bt_11[~(usage_bt_11.index == 9)]
usage_trad = usage_trad[~(usage_trad.index == 9)]
usage_trad_11 = usage_trad_11[~(usage_trad_11.index == 9)]

# ----------- Setup -----------
filepath_plot = "../results/setup_sus_boxplot.png"
filepath_values = "../results/setup_sus_boxplot.csv"
setup['score'] = setup.sum(axis=1) * 2.5

# score 11
setup["score_11"] = setup_11["11"].astype(float)
setup["score_diff"] = setup["score_11"] - setup["score"]
setup["score_diff_abs"] = setup["score_diff"].abs()
add_output_str += "----- Setup -----\n\n"
add_output_str += str(setup) + "\n\n"
add_output_str +=  "Means and medians per question (columns):\n"
add_output_str +=  str(setup[[str(i) for i in range(1,11)]].describe().loc[["mean", '50%']].round(2)) + "\n\n"
add_output_str += "Description of all differences (score_11 - score):\n"
add_output_str += str(setup["score_diff_abs"].describe()) + "\n\n"

# Distribution
plot = sns.displot(setup["score"], color=col_blue, linewidth=linewidth)
plot.set(
    ylabel="Anzahl",
    xlabel="SUS-Punktzahl",
    xlim=(None, 100)
)
plot.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Verteilung der SUS-Bewertung zur Einrichtung (Blue TOTP)", pad=15)
plot.figure.savefig("../results/setup_sus_distribution.png", bbox_inches="tight")
del plot
plt.figure()  # reset plot

# Diff of score_11 - score as bar chart + table
sns.set_theme(style="whitegrid")
plt.figure()
# plt.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)
setup_melt = pd.melt(setup, ignore_index=False, value_vars=["score", "score_11"], var_name="score_kind")
score_name = "SUS-Bewertung"
score_11_name = "empfundene\nNutzerfreundl."
setup_melt = setup_melt.replace("score", score_name)
setup_melt = setup_melt.replace("score_11", score_11_name)
plot = sns.barplot(
    setup_melt,
    x="id", y="value",
    hue="score_kind",
    width=0.7,
    palette={score_name: col_blue, score_11_name: col_blue_sec},
    alpha=1
)
plot.set(
    ylim=(0,100),
    ylabel="Punktzahl",
    xlabel="Proband",
)
plot.set_yticks([i for i in range(0,101,10)])
plot.set_title("SUS-Bewertung und empfundene Nutzerfreundlichkeit zur Einrichtung (Blue TOTP)", pad=15)
plt.legend(title="", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plot.figure.savefig("../results/setup_sus_vs_sus11.png", bbox_inches="tight")

# Boxplot
plt.figure(figsize=(4.5,4))  # reset plot
plt.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)
plot = sns.boxplot(data=setup["score"], color=col_blue, linewidth=linewidth, linecolor=linecolor, widths = 0.6)
plot.set(
    ylabel="SUS-Bewertung",
    ylim=(None, 100)
)
plot.set_xticklabels(["Blue TOTP"])
plot.set_title("SUS-Bewertung der Einrichtung (Blue TOTP)", pad=15)
plot.get_figure().savefig(filepath_plot)
print(f"\n- rendered boxplot of setup sus score and stored it at {filepath_plot}")
del plot
plt.figure()  # reset plot

# Table of boxplot
table = setup["score"].describe()
table.to_csv(filepath_values)
print(f"- stored related values of boxplot at {filepath_values}")

# ----------- Usage bt and trad in one plot -----------
filepath_plot = "../results/usage_sus_boxplot.png"
filepath_values = "../results/usage_sus_boxplot.csv"
usage_bt['score'] = usage_bt.sum(axis=1) * 2.5
usage_trad['score'] = usage_trad.sum(axis=1) * 2.5

# score 11 bt
usage_bt["score_11"] = usage_bt_11["11"].astype(float)
usage_bt["score_diff"] = usage_bt["score_11"] - usage_bt["score"]
usage_bt["score_diff_abs"] = usage_bt["score_diff"].abs()
add_output_str += "----- Usage bt -----\n\n"
add_output_str += str(usage_bt) + "\n\n"
add_output_str +=  "Means and medians per question (columns):\n"
add_output_str +=  str(usage_bt[[str(i) for i in range(1,11)]].describe().loc[["mean", '50%']].round(2)) + "\n\n"
add_output_str += "Description of all differences (score_11 - score):\n"
add_output_str += str(usage_bt["score_diff_abs"].describe()) + "\n\n"

# score 11 trad
usage_trad["score_11"] = usage_trad_11["11"].astype(float)
usage_trad["score_diff"] = usage_trad["score_11"] - usage_trad["score"]
usage_trad["score_diff_abs"] = usage_trad["score_diff"].abs()
add_output_str += "----- Usage trad -----\n\n"
add_output_str += str(usage_trad) + "\n\n"
add_output_str +=  "Means and medians per question (columns):\n"
add_output_str +=  str(usage_trad[[str(i) for i in range(1,11)]].describe().loc[["mean", '50%']].round(2)) + "\n\n"
add_output_str += "Description of all differences (score_11 - score):\n"
add_output_str += str(usage_trad["score_diff_abs"].describe()) + "\n\n"

# Dist bt and trad
dist_plot_x_min = max(min(usage_trad["score"].min(),usage_bt["score"].min()) - 5, 0)
dist_bin_w = 6

# Distribution bt
plot = sns.displot(usage_bt["score"], binwidth=dist_bin_w, color=col_blue, linewidth=linewidth)
plot.set(
    ylabel="Anzahl",
    xlabel="SUS-Punktzahl",
    xlim=(dist_plot_x_min, 100)
)
plot.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Verteilung der SUS-Bewertung zur Authentisierung (Blue TOTP)", pad=15)
plot.figure.savefig("../results/usage_bt_sus_distribution.png", bbox_inches="tight")
del plot
plt.figure()  # reset plot

# Distribution trad
plot = sns.displot(usage_trad["score"], binwidth=dist_bin_w, color=col_trad, linewidth=linewidth)
plot.set(
    ylabel="Anzahl",
    xlabel="SUS-Punktzahl",
    xlim=(dist_plot_x_min, 100),
    ylim=(None, 4)
)
plot.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title('Verteilung der SUS-Bewertung zur Authentisierung (trad. TOTP)', pad=15)
plot.figure.savefig("../results/usage_trad_sus_distribution.png", bbox_inches="tight")
del plot
plt.figure()  # reset plot


# Boxplot
usage = pd.DataFrame()
usage.index = usage_trad.index
usage["bt"] = usage_bt["score"]
usage["trad"] = usage_trad["score"]
usage.reset_index(inplace=True, drop=True)

plt.figure(figsize=(6,4))  # reset plot
plt.subplots_adjust(left=0.1, right=.9, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)
plot = sns.boxplot(data=usage, palette={"bt": col_blue, "trad": col_trad}, linewidth=linewidth, linecolor=linecolor, widths=0.7)
plot.set(
    ylabel="SUS-Bewertung",
    ylim=(None, 100)
)
plot.set_xticklabels(["Blue TOTP", "trad. TOTP"])
plot.set_title("SUS-Bewertung der Authentisierung (Blue TOTP vs. Trad. TOTP)", pad=15)
plot.get_figure().savefig(filepath_plot)
print(f"\n- rendered boxplot of usage sus score and stored it at {filepath_plot}")
del plot
plt.figure()  # reset plot

# Table of boxplot
table = usage.describe()
table.to_csv(filepath_values)
print(f"- stored related values of boxplot at {filepath_values}")



# Statistical significance:
plt.figure()
plot = sns.displot(usage["trad"] - usage["bt"], color="black", linewidth=linewidth)
plot.set(
    ylabel="Anzahl",
    xlabel="Differenz in der SUS-Punktzahl (Trad. TOTP - Blue TOTP)",
    # xlim=(0, 100),
    # ylim=(None, 4)
)
plot.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title('Verteilung der SUS-Differenzen (trad. TOTP - Blue TOTP)', pad=15)
plot.figure.savefig("../results/usage_trad_minus_bt_sus_diff_distribution.png", bbox_inches="tight")
del plot
add_output_str += "\nShapiro-Wilk test to determine if sus diffs are normally distriuted:\n" + str(pg.normality(usage["trad"] - usage["bt"])) + "\n"
stat_significance = pg.ttest(x=usage["bt"], y=usage["trad"], paired=True)
add_output_str += "\nSUS BT vs Trad T test:\n" + str(stat_significance) + "\n\n"



# Diff of score_11 - score as bar chart
plt.figure(figsize=(10,4.8))
# plt.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)
sus_vs_11 = usage_bt[["score", "score_11"]]
sus_vs_11["kind"] = "Blue TOTP"
sus_vs_11 = pd.concat([sus_vs_11, usage_trad[["score", "score_11"]]])
sus_vs_11["kind"] = sus_vs_11["kind"].fillna("Trad. TOTP")
sus_vs_11 = sus_vs_11.melt(ignore_index=False, id_vars="kind", value_vars=["score", "score_11"], var_name="score_type")
score_name = "SUS"
score_11_name = "empf."
sus_vs_11 = sus_vs_11.replace("score", score_name)
sus_vs_11 = sus_vs_11.replace("score_11", score_11_name)
sus_vs_11["hue"] = sus_vs_11["kind"] + " " + sus_vs_11["score_type"]
sus_vs_11 = sus_vs_11[["value", "hue"]]
sus_vs_11 = sus_vs_11.sort_values("hue")
plot = sns.barplot(
    sus_vs_11,
    x="id",
    y="value",
    hue="hue",
    width=0.8,
    palette={
        f"Blue TOTP {score_name}": col_blue,
        f"Blue TOTP {score_11_name}": col_blue_sec,
        f"Trad. TOTP {score_name}": col_trad,
        f"Trad. TOTP {score_11_name}": toml["col"]["trad_sec"]},
    alpha=1
)
plot.set(
    ylim=(0,94),
    ylabel="Punktzahl",
    xlabel="Proband",
)
plot.set_yticks([i for i in range(0,91,10)])
plot.set_title("SUS-Bewertung und empfundene Nutzerfreundlichkeit der Authentisierung (Blue TOTP vs. Trad. TOTP)", pad=15)
plt.legend(title="", ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.23), fontsize=10)
# plt.legend(title="", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plot.figure.savefig("../results/usage_sus_vs_sus11.png", bbox_inches="tight")

# store additional data:
with open("../results/sus_score_vs_11.txt", "w") as file:
    file.write(add_output_str)
    print("\n- saved some result of sus score vs. sus 11 in results/sus_score_vs_11.txt")