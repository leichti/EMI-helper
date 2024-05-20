import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import BooleanVar, StringVar
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from customtkinter import CTk, CTkLabel, CTkOptionMenu, CTkEntry, CTkFrame, CTkScrollbar
import customtkinter

customtkinter.set_default_color_theme("gui/h2-lab.json")

def get_sample_names():
    sample_names = []
    for folder in os.listdir('data'):
        if os.path.isdir(os.path.join('data', folder)):
            sample_names.append(folder)
    return sample_names


def calculate_intersections(df, x_column, y_column, hline_y, vline_x):
    y_intersect = None
    x_intersect = None

    # Find intersection with horizontal line
    y_data = df[y_column].values
    x_data = df[x_column].values

    if np.any(y_data == hline_y):
        x_intersect = df.loc[y_data == hline_y, x_column].values[0]
    else:
        indices = np.where(np.diff(np.sign(y_data - hline_y)))[0]
        if indices.size > 0:
            idx = indices[0]
            x_intersect = np.interp(hline_y, [y_data[idx], y_data[idx + 1]], [x_data[idx], x_data[idx + 1]])

    # Find intersection with vertical line
    if np.any(x_data == vline_x):
        y_intersect = df.loc[x_data == vline_x, y_column].values[0]
    else:
        indices = np.where(np.diff(np.sign(x_data - vline_x)))[0]
        if indices.size > 0:
            idx = indices[0]
            y_intersect = np.interp(vline_x, [x_data[idx], x_data[idx + 1]], [y_data[idx], y_data[idx + 1]])

    return x_intersect, y_intersect


def main():
    sample_names = get_sample_names()

    parquet_file = f"parquet_data/{sample_names[0]}_MeasuredValues.parquet"
    df = pd.read_parquet(parquet_file)

    columns = df.columns

    root = CTk()
    root.title("Select Columns")

    # Create frames for layout
    control_frame = CTkFrame(root)
    control_frame.pack(side="left", fill="y", padx=(10,10))

    plot_frame = CTkFrame(root)
    plot_frame.pack(side="right", fill="both", expand=True)

    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    x_var = StringVar(root)
    y_var = StringVar(root)

    x_var.set("Temperature")
    y_var.set("HeightPercent")

    CTkLabel(control_frame, text="X-axis:").grid(row=0, column=0, sticky='w', pady=5)
    CTkOptionMenu(control_frame, variable=x_var, command=lambda _: plot(), values=columns).grid(row=0, column=1, sticky='w')

    CTkLabel(control_frame, text="Y-axis:").grid(row=1, column=0, sticky='w')
    CTkOptionMenu(control_frame, variable=y_var, command=lambda _: plot(), values=columns).grid(row=1, column=1, sticky='w')

    # Treeview for sample selection
    tree_frame = CTkFrame(control_frame)
    tree_frame.grid(row=2, column=0, columnspan=2, pady=5)
    tree = ttk.Treeview(tree_frame, columns=("Sample", "Select", "X", "Y"), show='headings')
    tree.heading("Sample", text="Sample")
    tree.heading("Select", text="Select")
    tree.heading("X", text="X")
    tree.heading("Y", text="Y")
    tree.column("Sample", width=100)
    tree.column("Select", width=50)
    tree.column("X", width=50)
    tree.column("Y", width=50)

    vsb = CTkScrollbar(tree_frame,  command=tree.yview)

    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    tree.pack(side='left', fill='y')

    experiment_vars = {}
    for sample in sample_names:
        var = BooleanVar()
        experiment_vars[sample] = var
        tree.insert("", "end", values=(sample, ""), tags=(sample,))

    def toggle_var(event):
        item = tree.selection()[0]
        sample = tree.item(item, "values")[0]
        var = experiment_vars[sample]
        var.set(not var.get())
        if var.get():
            tree.set(item, column="Select", value='x')
            tree.tag_configure(sample, background='yellow')
        else:
            tree.set(item, column="Select", value='')
            tree.set(item, column="X", value='')
            tree.set(item, column="Y", value='')
            tree.tag_configure(sample, background='white')
        plot()

    tree.bind('<<TreeviewSelect>>', toggle_var)

    CTkLabel(control_frame, text="X-axis label:").grid(row=3, column=0, sticky='w')
    x_label_var = StringVar()
    x_label_var.set("Temperature")
    x_label_entry = CTkEntry(control_frame, textvariable=x_label_var)
    x_label_entry.grid(row=3, column=1, sticky='w', pady=5)

    CTkLabel(control_frame, text="Y-axis label:").grid(row=4, column=0, sticky='w')
    y_label_var = StringVar()
    y_label_var.set("HeightPercent")
    y_label_entry = CTkEntry(control_frame, textvariable=y_label_var)
    y_label_entry.grid(row=4, column=1, sticky='w')

    # Combine X and Y limits in two rows
    CTkLabel(control_frame, text="X-axis range:").grid(row=5, column=0, sticky='w')
    x_range_frame = CTkFrame(control_frame)
    x_range_frame.grid(row=5, column=1, sticky='w')
    x_min_var = StringVar()
    x_min_entry = CTkEntry(x_range_frame, textvariable=x_min_var, width=67)
    x_min_entry.pack(side='left', padx=(0, 5.5))
    x_min_var.set("800")
    x_max_var = StringVar()
    x_max_entry = CTkEntry(x_range_frame, textvariable=x_max_var, width=67)
    x_max_entry.pack(side='left', pady=5)
    x_max_var.set("1600")

    CTkLabel(control_frame, text="Y-axis range:").grid(row=6, column=0, sticky='w')
    y_range_frame = CTkFrame(control_frame)
    y_range_frame.grid(row=6, column=1, columnspan=2, sticky='w')
    y_min_var = StringVar()
    y_min_entry = CTkEntry(y_range_frame, textvariable=y_min_var, width=67)
    y_min_entry.pack(side='left', padx=(0, 5.5))
    y_min_var.set("0")
    y_max_var = StringVar()
    y_max_entry = CTkEntry(y_range_frame, textvariable=y_max_var, width=67)
    y_max_entry.pack(side='left')
    y_max_var.set("110")

    CTkLabel(control_frame, text="Horizontal line:").grid(row=7, column=0, sticky='w')
    hline_y_var = StringVar()
    hline_y_entry = CTkEntry(control_frame, textvariable=hline_y_var)
    hline_y_entry.grid(row=7, column=1, sticky='w', pady=5)
    hline_y_var.set("33")

    CTkLabel(control_frame, text="Vertical line:").grid(row=8, column=0, sticky='w')
    vline_x_var = StringVar()
    vline_x_entry = CTkEntry(control_frame, textvariable=vline_x_var)
    vline_x_entry.grid(row=8, column=1, sticky='w')
    vline_x_var.set("1200")

    def plot():
        ax.clear()
        x_column = x_var.get()
        y_column = y_var.get()
        x_label = x_label_var.get()
        y_label = y_label_var.get()
        try:
            x_min = float(x_min_var.get())
            x_max = float(x_max_var.get())
            y_min = float(y_min_var.get())
            y_max = float(y_max_var.get())
            hline_y = float(hline_y_var.get())
            vline_x = float(vline_x_var.get())
        except ValueError:
            # Set default limits if inputs are invalid
            x_min, x_max = 800, 1600
            y_min, y_max = 0, 110
            hline_y = 33
            vline_x = 1200

        for sample, var in experiment_vars.items():
            if var.get():
                parquet_file = f"parquet_data/{sample}_MeasuredValues.parquet"
                df = pd.read_parquet(parquet_file)
                v_intersect, h_intersect = calculate_intersections(df, x_column, y_column, hline_y, vline_x)
                ax.plot(df[x_column], df[y_column], label=sample)

                point_vertical = [[vline_x], [h_intersect]]
                point_horizontal = [[v_intersect], [hline_y]]

                if h_intersect is not None:
                    ax.scatter([vline_x], [h_intersect])
                    set_treeview_value(sample, "Y", set_value=f"{h_intersect:.1f}")

                if v_intersect is not None:
                    ax.scatter([v_intersect], [hline_y])
                    set_treeview_value(sample, "X", set_value=f"{v_intersect:.1f}")


        if y_column == "HeightPercent":
            ax.axhline(y=hline_y, color='r', linestyle='--')

        if x_column == "Temperature":
            ax.axvline(x=vline_x, color='b', linestyle='--')

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.legend()
        canvas.draw()

    def on_enter(event):
        plot()

    def set_treeview_value(sample_value, column, set_value):
        for row in tree.get_children():
            row_values = tree.item(row, "values")
            if row_values[0] == sample_value:
                tree.set(row, column, set_value)
                break

    # Bind Enter key to all input fields to update the plot
    x_min_entry.bind("<Return>", on_enter)
    x_max_entry.bind("<Return>", on_enter)
    y_min_entry.bind("<Return>", on_enter)
    y_max_entry.bind("<Return>", on_enter)
    hline_y_entry.bind("<Return>", on_enter)
    vline_x_entry.bind("<Return>", on_enter)
    x_label_entry.bind("<Return>", on_enter)
    y_label_entry.bind("<Return>", on_enter)

    # Initial plot
    plt.ion()  # Turn on interactive mode
    plot()
    root.mainloop()

if __name__ == "__main__":
    main()