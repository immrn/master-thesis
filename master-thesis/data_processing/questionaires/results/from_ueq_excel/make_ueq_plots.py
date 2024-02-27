import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tomllib


with open("../../../config.toml", "rb") as f:
    toml = tomllib.load(f)
    col_blue = toml["col"]["blue"]
    col_blue_sec = toml["col"]["blue_sec"]
    col_trad = toml["col"]["trad"]
    linewidth = toml["linewidth"]
    linecolor = toml["linecolor"]
    dpi = toml["dpi"]
plt.rcParams['figure.dpi'] = dpi
plt.rcParams['savefig.dpi'] = dpi


# Load data
ov_bt = pd.read_csv("./usage_bt_ueq.csv", encoding='utf8')
ov_trad = pd.read_csv("./usage_trad_ueq.csv", encoding='utf8')
si_bt = pd.read_csv("./usage_bt_ueq_single.csv", encoding='utf8')
si_trad = pd.read_csv("./usage_trad_ueq_single.csv", encoding='utf8')

ov_bt["kind"] = "Blue TOTP"
ov_trad["kind"] = "Trad. TOTP"
ov = pd.concat([ov_bt, ov_trad])

si_bt["kind"] = "Blue TOTP"
si_trad["kind"] = "Trad. TOTP"
si = pd.concat([si_bt, si_trad])
si["comb"] = si["left"] + "/" + si["right"]

# ---------------------- Overview -------------------- #
sns.set_theme(style="whitegrid")
plt.figure(figsize=(8,4.8))
# plt.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)
plot = sns.barplot(
    data=ov,
    x="scale",
    y="mean",
    hue="kind",
    width=0.7,
    palette={"Blue TOTP": col_blue, "Trad. TOTP": col_trad},
    alpha=1
)
plot.set(
    ylim=(-0.4,1.4),
    ylabel="Mittelwert",
    xlabel="",
)
# plot.set_yticks([i for i in range(0,101,10)])
plot.set_title("UEQ-Skalen der Authentisierung (Blue TOTP vs. Trad. TOTP)", pad=15)
plt.xticks(rotation=20)
plt.legend(title="", bbox_to_anchor=(0.008, 0.015), loc='lower left', borderaxespad=0)
plot.figure.savefig("./ueq_overview_bt_trad.png", bbox_inches="tight")
sns.set_theme()


# ----------------------- Single Item Means ------------------------ #
sns.set_theme(style="whitegrid")
plt.figure(figsize=(5,10))
# plt.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)

supp = pd.DataFrame()
my_palette = {}
for i in range(0,27,1):
    tmp = pd.DataFrame()
    tmp["x"] = [-0.5, 2.0]
    tmp["y"] = [i-0.5, i-0.5]
    tmp["kind"] = str(i)
    my_palette[str(i)] = "grey"
    if supp.empty:
        supp = tmp.copy()
        continue
    supp = pd.concat([supp, tmp])

plot = sns.lineplot(
    data=supp,
    x="x",
    y="y",
    hue="kind",
    palette=my_palette,
    alpha=0.3,
    linewidth=0.6,
    legend=None
)

plot = sns.barplot(
    data=si,
    x="mean",
    y="comb",
    hue="kind",
    dodge=0.7,
    palette={"Blue TOTP": col_blue, "Trad. TOTP": col_trad},
    orient="h"
)
plot.set(
    xlim=(-0.5,2),
    ylabel="",
    xlabel="Mittelwert",
)
plot.set_title("Mittelwerte der UEQ-Items zur Authentisierung (Blue TOTP vs. Trad. TOTP)", pad=15, x=0.26)
plt.legend(title="", bbox_to_anchor=(-0.41, -0.01), loc='upper left', borderaxespad=0)
plot.figure.savefig("./ueq_single_means_bt_trad.png", bbox_inches="tight")
sns.set_theme()