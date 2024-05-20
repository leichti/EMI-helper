# plotter.py (modifications)
from tkinter import StringVar

import pandas as pd


def plot(df, gui_manager, calculate_intersections, set_treeview_value):
    ax = gui_manager.ax
    canvas = gui_manager.canvas

    ax.clear()

    styles = gui_manager.plot_style_popup.get_styles() if gui_manager.plot_style_popup else {}

    for sample, var in gui_manager.experiment_vars.items():
        if var.get():
            parquet_file = f"../parquet_data/{sample}_MeasuredValues.parquet"
            df = pd.read_parquet(parquet_file)
            v_intersect, h_intersect = calculate_intersections(
                df, gui_manager.x_var.get(), gui_manager.y_var.get(),
                float(gui_manager.hline_y_var.get()), float(gui_manager.vline_x_var.get())
            )

            style = styles.get(sample, {
                "Color": StringVar(value="C0"), "Linestyle": StringVar(value="solid"), "Alpha": StringVar(value="1.0"), "Linewidth": StringVar(value="1.0"), "Legend-Label": StringVar(value=sample)})
            ax.plot(df[gui_manager.x_var.get()], df[gui_manager.y_var.get()], label=style["Legend-Label"].get(),
                    color=style["Color"].get(), linestyle=style["Linestyle"].get(), linewidth=float(style["Linewidth"].get()), alpha=float(style["Alpha"].get()))

            if h_intersect is not None:
                ax.scatter([float(gui_manager.vline_x_var.get())], [h_intersect])
                set_treeview_value(sample, "Y", f"{h_intersect:.1f}")

            if v_intersect is not None:
                ax.scatter([v_intersect], [float(gui_manager.hline_y_var.get())])
                set_treeview_value(sample, "X", f"{v_intersect:.1f}")

    if gui_manager.y_var.get() == "HeightPercent":
        ax.axhline(y=float(gui_manager.hline_y_var.get()), color='r', linestyle='--')

    if gui_manager.x_var.get() == "Temperature":
        ax.axvline(x=float(gui_manager.vline_x_var.get()), color='b', linestyle='--')

    ax.set_xlabel(gui_manager.x_label_var.get())
    ax.set_ylabel(gui_manager.y_label_var.get())
    ax.set_xlim(float(gui_manager.x_min_var.get()), float(gui_manager.x_max_var.get()))
    ax.set_ylim(float(gui_manager.y_min_var.get()), float(gui_manager.y_max_var.get()))
    ax.legend()
    canvas.draw()