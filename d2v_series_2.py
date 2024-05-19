import os

import pandas as pd
import matplotlib.pyplot as plt


class EMIFolder():

    def __init__(self, path):
        self.path = path
        self.filenames = [
            f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f)) and f.endswith('.csv')
        ]
        self.filenames = [x.split(".")[-2] for x in self.filenames]

        if len(self.filenames) == 0:
            raise ValueError("No Files Found")

folder = EMIFolder("data/d2v_washing_series_2")


def plot_dust(ax, dust_nr):
    unwashed = f"D2V_EAFD_{dust_nr}"
    washed = f"W2_D2V_EAFD_{dust_nr}"
    df_unwashed = pd.read_csv(folder.path+"/"+unwashed+".csv", delimiter=";")
    df_washed = pd.read_csv(folder.path+"/"+washed+".csv", delimiter=";")

    ax.plot(df_washed["Sample: T in °C"], df_washed["h in px"]/df_washed["h in px"].iloc[0], label=washed)
    ax.plot(df_unwashed["Sample: T in °C"], df_unwashed["h in px"]/df_unwashed["h in px"].iloc[0], label=unwashed)
    ax.set_ylim(0,1.2)
    ax.set_xlim(500,1650)
    ax.legend()


fig, axes = plt.subplots(3,3)
axes = axes.flatten()

for i, dust in enumerate([6,7]):
    plot_dust(axes[i], dust)

#plt.plot([1200, 1200], [0,1], color="grey", linestyle="dashed")
#plt.plot([1100, 1100], [0,1], color="grey", linestyle="dashed")
#plt.plot([1000, 1000], [0,1], color="grey", linestyle="dashed")

plt.xlabel("Temperature [°C]")
plt.ylabel("Relative Sample Height [-]")
plt.savefig("emi-d2v_washing_series2.webp", dpi=600)
plt.show()
print(df.columns)

