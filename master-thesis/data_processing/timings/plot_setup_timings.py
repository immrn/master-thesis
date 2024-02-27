import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import tomllib

with open("../config.toml", "rb") as f:
    toml = tomllib.load(f)
    col_blue = toml["col"]["blue"]
    col_trad = toml["col"]["trad"]
    linewidth = toml["linewidth"]
    linecolor = toml["linecolor"]
    dpi = toml["dpi"]
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300


plot_filepath = "./results/setup_timings_boxplot.png"
plot_values_filepath = "./results/setup_timings_boxplot.csv"

df = pd.read_csv("./raw_data/setup_time.csv")

# Distribution
plot = sns.displot(df["setup_time"], binwidth=30, color=col_blue, linewidth=linewidth)
plot.set(
    ylabel="Anzahl",
    xlabel="Einrichtungszeit [s]"
)
plot.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title('Verteilung der Einrichtungszeit (Blue TOTP)', pad=15)
plot.figure.savefig("./results/distribution_of_setup_data.png", bbox_inches="tight")
del plot
plt.figure()  # reset plot

# Boxplot
sns.set_style("whitegrid")
plt.figure(figsize=(3.4,4.8))  # reset plot
# plt.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)

plot = sns.boxplot(data=df["setup_time"], color=col_blue, linewidth=linewidth, linecolor=linecolor, widths = 0.6)
plot.set(
    ylabel="Zeit [s]"
)
plot.set_xticklabels(["Blue TOTP"])
plot.set_title('Einrichtungszeit (Blue TOTP)', pad=15)
plot.get_figure().savefig(plot_filepath)
print(f"\nRendered boxplot of setup times and stored it at {plot_filepath}")

table = df["setup_time"].describe()
table.to_csv(plot_values_filepath)
print(f"Stored related values of boxplot at {plot_values_filepath}")