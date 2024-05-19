import os
from tkinter import Tk, Label, Entry, Frame, Scrollbar, VERTICAL, StringVar, OptionMenu, BooleanVar
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def get_sample_names():
    sample_names = []
    for folder in os.listdir('data'):
        if os.path.isdir(os.path.join('data', folder)):
            sample_names.append(folder)
    return sample_names


def main():
    sample_names = get_sample_names()

    parquet_file = f"parquet_data/{sample_names[0]}_MeasuredValues.parquet"
    df = pd.read_parquet(parquet_file)

    columns = df.columns

    root = Tk()
    root.title("Select Columns")

    # Create frames for layout
    control_frame = Frame(root)
    control_frame.pack(side="left", fill="y")

    plot_frame = Frame(root)
    plot_frame.pack(side="right", fill="both", expand=True)

    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    x_var = StringVar(root)
    y_var = StringVar(root)

    x_var.set("Temperature")
    y_var.set("HeightPercent")

    Label(control_frame, text="Select column for x-axis:").grid(row=0, column=0, sticky='w')
    OptionMenu(control_frame, x_var, *columns).grid(row=0, column=1, sticky='w')

    Label(control_frame, text="Select column for y-axis:").grid(row=1, column=0, sticky='w')
    OptionMenu(control_frame, y_var, *columns).grid(row=1, column=1, sticky='w')

    # Treeview for sample selection
    tree_frame = Frame(control_frame)
    tree_frame.grid(row=2, column=0, columnspan=2, pady=10)
    tree = ttk.Treeview(tree_frame, columns=("Sample", "Select"), show='headings')
    tree.heading("Sample", text="Sample")
    tree.heading("Select", text="Select")
    tree.column("Sample", width=100)
    tree.column("Select", width=50)

    vsb = Scrollbar(tree_frame, orient="vertical", command=tree.yview)
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
            tree.tag_configure(sample, background='white')
        plot()

    tree.bind('<<TreeviewSelect>>', toggle_var)

    Label(control_frame, text="X-axis label:").grid(row=3, column=0, sticky='w')
    x_label_var = StringVar()
    x_label_var.set("Temperature")
    x_label_entry = Entry(control_frame, textvariable=x_label_var)
    x_label_entry.grid(row=3, column=1, sticky='w')

    Label(control_frame, text="Y-axis label:").grid(row=4, column=0, sticky='w')
    y_label_var = StringVar()
    y_label_var.set("HeightPercent")
    y_label_entry = Entry(control_frame, textvariable=y_label_var)
    y_label_entry.grid(row=4, column=1, sticky='w')

    # Combine X and Y limits in two rows
    Label(control_frame, text="X-axis range:").grid(row=5, column=0, sticky='w')
    x_range_frame = Frame(control_frame)
    x_range_frame.grid(row=5, column=1, sticky='w')
    x_min_var = StringVar()
    x_min_entry = Entry(x_range_frame, textvariable=x_min_var, width=9)
    x_min_entry.pack(side='left', padx=(0, 5.5))
    x_min_var.set("800")
    x_max_var = StringVar()
    x_max_entry = Entry(x_range_frame, textvariable=x_max_var, width=9)
    x_max_entry.pack(side='left')
    x_max_var.set("1600")

    Label(control_frame, text="Y-axis range:").grid(row=6, column=0, sticky='w')
    y_range_frame = Frame(control_frame)
    y_range_frame.grid(row=6, column=1, columnspan=2, sticky='w')
    y_min_var = StringVar()
    y_min_entry = Entry(y_range_frame, textvariable=y_min_var, width=9)
    y_min_entry.pack(side='left', padx=(0,5.5))
    y_min_var.set("0")
    y_max_var = StringVar()
    y_max_entry = Entry(y_range_frame, textvariable=y_max_var, width=9)
    y_max_entry.pack(side='left')
    y_max_var.set("110")

    Label(control_frame, text="Horizontal line y-position:").grid(row=7, column=0, sticky='w')
    hline_y_var = StringVar()
    hline_y_entry = Entry(control_frame, textvariable=hline_y_var)
    hline_y_entry.grid(row=7, column=1, sticky='w')
    hline_y_var.set("33")

    Label(control_frame, text="Vertical line x-position:").grid(row=8, column=0, sticky='w')
    vline_x_var = StringVar()
    vline_x_entry = Entry(control_frame, textvariable=vline_x_var)
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
                ax.plot(df[x_column], df[y_column], label=sample)

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