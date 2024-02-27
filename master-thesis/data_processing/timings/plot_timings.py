import pandas as pd
import pingouin as pg
import seaborn as sns
import matplotlib.pyplot as plt
import tomllib

with open("../config.toml", "rb") as f:
    toml = tomllib.load(f)
    col_blue = toml["col"]["blue"]
    col_trad = toml["col"]["trad"]
    linewidth = toml["linewidth"]
    linecolor = toml["linecolor"]
    dpi = toml["dpi"]
plt.rcParams['figure.dpi'] = dpi
plt.rcParams['savefig.dpi'] = dpi


plot_filepath = "./results/totp_timings_boxplot.png"
plot_values_filepath = "./results/totp_timings_boxplot.csv"

inferential_statistic_str = ""
alternative_means_str = ""

df = pd.read_csv("./cleaned_data/totp_times.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["time_totp"] = pd.to_timedelta(df["time_totp"]).dt.total_seconds()

# We have to remove the participant 9 because they never used the Bluetooth functionality, they always typed in the totp manually:
df = df[~(df["id"] == 9)]

# Distribution
plot = sns.displot(df["time_totp"], color=col_blue, linewidth=linewidth)
plot.set(
    title='Verteilung der Authentisierungszeit (Blue TOTP)',
    ylabel="Anzahl",
    xlabel="Authentisierungszeit [s]"
)
plot.figure.savefig("./results/distribution_of_data.png", bbox_inches="tight")
del plot
plt.figure()  # reset plot

# Calculate alternative means without some outliers:
df_describer = df["time_totp"].describe()
q1 = df_describer.loc["25%"]
q3 = df_describer.loc["75%"]
iqr = q3 - q1
std = df_describer.loc["std"]
mean = df_describer.loc["mean"]
iqr_limit = q3 + 1.5 * iqr
std_limit = mean + 2 * std

alternative_means_str += "cleaned by IQR:\n"
df_iqr = df.copy()
values_with_outliers = df_iqr.shape[0]
df_iqr = df_iqr[~(df_iqr["time_totp"] > iqr_limit)]
alternative_means_str += f"- upper limit: {iqr_limit}\n"
alternative_means_str += f"- count of removed values: {values_with_outliers - df_iqr.shape[0]}\n"
alternative_means_str += f"- mean: {df_iqr["time_totp"].describe().loc["mean"]}\n\n"
del df_iqr

alternative_means_str += "cleanded by 2 * STD:\n"
df_std = df.copy()
values_with_outliers = df_std.shape[0]
df_std = df_std[~(df_std["time_totp"] > std_limit)]
alternative_means_str += f"- upper limit: {std_limit}\n"
alternative_means_str += f"- count of removed values: {values_with_outliers - df_std.shape[0]}\n"
alternative_means_str += f"- mean: {df_std["time_totp"].describe().loc["mean"]}\n\n"
del df_std

with open("results/alternative_means.txt", "w") as file:
    file.write(alternative_means_str)
    print("- Saved some inferential statistics in results/alternative_means.txt")

# --------------------------------------------

# add a column that represents the count of days that each participant is participating in the study:
df['days_participating'] = df.groupby('id').cumcount() + 1

# Correlation analysis:
inferential_statistic_str += f"Data\n{str(df)}\n\n"
inferential_statistic_str += "Repeated measures correlation analysis between days_participating and time_totp:\n"
corr = pg.rm_corr(data=df, x='days_participating', y='time_totp', subject='id')
inferential_statistic_str += str(corr) + "\n\n"

# # Pairwise T test:
# print("\nPairwise T test within days_participating and time_totp as dependent variable")
# t = pg.pairwise_tests(data=df, dv="time_totp", padjust="bonf", effsize="cohen", within="days_participating", subject="id")
# print(t)

# Correlation on median values:
mean_df = df.groupby(by="days_participating")["time_totp"].median()
mean_df = mean_df.reset_index()
inferential_statistic_str += "\n------------------------\n\n"
inferential_statistic_str += f"Data with median of time_totp\n{str(mean_df)}\n\n"
inferential_statistic_str += "Correlation on median of times_totp per day_participating:\n"
spearman = mean_df["time_totp"].corr(method="spearman", other=mean_df["days_participating"])
spearman = round(spearman, 4)
inferential_statistic_str += f"-> Spearman:\t{spearman}\n"
pearson = mean_df["time_totp"].corr(method="pearson", other=mean_df["days_participating"])
pearson = round(pearson, 4)
inferential_statistic_str += f"-> Pearson:\t\t{pearson}\n\n"

# store inferential statistics:
with open("results/inferential_statistics.txt", "w") as file:
    file.write(inferential_statistic_str)
    print("- Saved some inferetial statistics in results/inferential_statistics.txt")

# Line plot:
sns.set_style("whitegrid")
plt.figure(figsize=(8,4.8))
plt.subplots_adjust(left=0.1, right=0.87, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)
plot = sns.lineplot(
    data=df,
    y="time_totp",
    x="days_participating",
    hue="id",
    # style="id",
    palette=sns.color_palette("tab10"),
    marker="o",
    linestyle="--",
    alpha=0.8
)
plot.set(
    ylabel="Zeit [s]",
    xlabel="Tage in der Nutzungsphase",
    ylim=(0,40)
)
plot.grid(axis="x")
plot.set_title("Authentisierungszeiten pro Tag (Blue TOTP)", pad=15)
plt.legend(title="Proband", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plot.get_figure().savefig("./results/totp_timings_lineplot.png")
print(f"- Rendered boxplot of TOTP times and stored it at ./results/totp_timings_lineplot.png")

# Boxplot:
sns.set_style()
plt.figure(figsize=(4.8,4))  # reset plot
plt.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9, wspace=0.2, hspace=0.4)
plot = sns.boxplot(data=df["time_totp"], color=col_blue, linewidth=linewidth, linecolor=linecolor, widths = 0.6)
plot.set(
    ylabel="Zeit [s]",
    ylim=(0,35)
)
plot.set_xticklabels(["Blue TOTP"])
plt.title('Authentisierungszeit (Blue TOTP)', pad=15)
plot.get_figure().savefig(plot_filepath)
print(f"- Rendered boxplot of TOTP times and stored it at {plot_filepath}")

table = df["time_totp"].describe()
table.to_csv(plot_values_filepath)
print(f"- Stored related values of boxplot at {plot_values_filepath}")
