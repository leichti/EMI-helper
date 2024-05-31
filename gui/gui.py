# gui.py
import json
import os

from customtkinter import CTk, CTkLabel, CTkOptionMenu, CTkEntry, CTkFrame, CTkScrollbar, CTkButton
from tkinter import BooleanVar, StringVar
from tkinter import ttk
import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from plot_style_popup import PlotStylePopup

customtkinter.set_default_color_theme("h2-lab.json")


# gui.py
class GUIManager:
    def __init__(self, columns, plot_callback, sample_names):
        self.plot_callback = plot_callback
        sample_names = sorted(sample_names)
        self.sample_names = sample_names
        self.config_file = "plot_styles.json"
        self.root = CTk()
        self.root.title("Select Columns")

        self.control_frame = CTkFrame(self.root)
        self.control_frame.pack(side="left", fill="y", padx=(10, 10))

        self.plot_frame = CTkFrame(self.root)
        self.plot_frame.pack(side="right", fill="both", expand=True)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.x_var = StringVar(self.root)
        self.y_var = StringVar(self.root)
        self.x_var.set("Temperature")
        self.y_var.set("HeightPercent")

        CTkLabel(self.control_frame, text="X-axis:").grid(row=0, column=0, sticky='w', pady=5)
        CTkOptionMenu(self.control_frame, variable=self.x_var, command=lambda _: self.plot_callback(),
                      values=columns).grid(row=0, column=1, sticky='w')

        CTkLabel(self.control_frame, text="Y-axis:").grid(row=1, column=0, sticky='w')
        CTkOptionMenu(self.control_frame, variable=self.y_var, command=lambda _: self.plot_callback(),
                      values=columns).grid(row=1, column=1, sticky='w')

        self.tree_frame = CTkFrame(self.control_frame)
        self.tree_frame.grid(row=2, column=0, columnspan=2, pady=5)
        self.tree = ttk.Treeview(self.tree_frame, columns=("Sample", "Select", "X", "Y"), show='headings')
        self.tree.heading("Sample", text="Sample")
        self.tree.heading("Select", text="Select")
        self.tree.heading("X", text="X")
        self.tree.heading("Y", text="Y")
        self.tree.column("Sample", width=100)
        self.tree.column("Select", width=50)
        self.tree.column("X", width=50)
        self.tree.column("Y", width=50)

        vsb = CTkScrollbar(self.tree_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='y')

        self.experiment_vars = {}
        for sample in sample_names:
            var = BooleanVar()
            self.experiment_vars[sample] = var
            self.tree.insert("", "end", values=(sample, ""), tags=(sample,))

        self.tree.bind('<<TreeviewSelect>>', self.toggle_var)

        self.x_label_var = StringVar()
        self.x_label_entry = self.create_label_entry_pair(self.control_frame, 3, "X-axis label:", self.x_label_var,
                                                          "Temperature")

        self.y_label_var = StringVar()
        self.y_label_entry = self.create_label_entry_pair(self.control_frame, 4, "Y-axis label:", self.y_label_var,
                                                          "HeightPercent")

        CTkLabel(self.control_frame, text="X-axis range:").grid(row=5, column=0, sticky='w')
        self.x_range_frame = CTkFrame(self.control_frame)
        self.x_range_frame.grid(row=5, column=1, sticky='w')
        self.x_min_var = StringVar()
        self.x_min_entry = CTkEntry(self.x_range_frame, textvariable=self.x_min_var, width=67)
        self.x_min_entry.pack(side='left', padx=(0, 5.5))
        self.x_min_var.set("800")
        self.x_max_var = StringVar()
        self.x_max_entry = CTkEntry(self.x_range_frame, textvariable=self.x_max_var, width=67)
        self.x_max_entry.pack(side='left', pady=5)
        self.x_max_var.set("1600")

        CTkLabel(self.control_frame, text="Y-axis range:").grid(row=6, column=0, sticky='w')
        self.y_range_frame = CTkFrame(self.control_frame)
        self.y_range_frame.grid(row=6, column=1, columnspan=2, sticky='w')
        self.y_min_var = StringVar()
        self.y_min_entry = CTkEntry(self.y_range_frame, textvariable=self.y_min_var, width=67)
        self.y_min_entry.pack(side='left', padx=(0, 5.5))
        self.y_min_var.set("0")
        self.y_max_var = StringVar()
        self.y_max_entry = CTkEntry(self.y_range_frame, textvariable=self.y_max_var, width=67)
        self.y_max_entry.pack(side='left')
        self.y_max_var.set("110")

        self.hline_y_var = StringVar()
        self.hline_y_entry = self.create_label_entry_pair(self.control_frame, 7, "Horizontal line:", self.hline_y_var,
                                                          "33")

        self.vline_x_var = StringVar()
        self.vline_x_entry = self.create_label_entry_pair(self.control_frame, 8, "Vertical line:", self.vline_x_var,
                                                          "1200")

        self.styles = self.load_styles(sample_names)
        self.style_button = CTkButton(self.control_frame, text="Plot Style Configuration", command=self.open_style_popup)
        self.style_button.grid(row=9, columnspan=2, pady=10)

        self.plot_style_popup = None
        self.bind_entries()

    def init_styles(self, sample_names):
        styles = {}
        for sample in sample_names:
            styles[sample] = {
                "Color": StringVar(value="C0"),
                "Linestyle": StringVar(value="solid"),
                "Alpha": StringVar(value="1.0"),
                "Linewidth": StringVar(value="1.0"),
                "Legend-Label": StringVar(value=sample)
            }
        return styles
    def save_styles(self):
        styles_dict = {sample: {key: var.get() for key, var in style.items()} for sample, style in self.styles.items()}
        with open(self.config_file, 'w') as f:
            json.dump(styles_dict, f)

    def load_styles(self, sample_names):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                styles_dict = json.load(f)
            styles = {sample: {key: StringVar(value=value) for key, value in style.items()} for sample, style in styles_dict.items()}
        else:
            styles = self.init_styles(sample_names)
        return styles

    def open_style_popup(self):
        if self.plot_style_popup is not None:
            self.plot_style_popup.popup.destroy()

        self.plot_style_popup = PlotStylePopup(self, self.plot_callback, self.sample_names, self.styles)

    def create_label_entry_pair(self, frame, row, text, var, default_value):
        CTkLabel(frame, text=text).grid(row=row, column=0, sticky='w')
        entry = CTkEntry(frame, textvariable=var)
        entry.grid(row=row, column=1, sticky='w', pady=5)
        var.set(default_value)
        return entry

    def bind_entries(self):
        self.x_min_entry.bind("<Return>", lambda event: self.plot_callback())
        self.x_max_entry.bind("<Return>", lambda event: self.plot_callback())
        self.y_min_entry.bind("<Return>", lambda event: self.plot_callback())
        self.y_max_entry.bind("<Return>", lambda event: self.plot_callback())
        self.hline_y_entry.bind("<Return>", lambda event: self.plot_callback())
        self.vline_x_entry.bind("<Return>", lambda event: self.plot_callback())
        self.x_label_entry.bind("<Return>", lambda event: self.plot_callback())
        self.y_label_entry.bind("<Return>", lambda event: self.plot_callback())

    def toggle_var(self, event):
        item = self.tree.selection()[0]
        sample = self.tree.item(item, "values")[0]
        var = self.experiment_vars[sample]
        var.set(not var.get())
        if var.get():
            self.tree.set(item, column="Select", value='x')
            self.tree.tag_configure(sample, background='yellow')
        else:
            self.tree.set(item, column="Select", value='')
            self.tree.set(item, column="X", value='')
            self.tree.set(item, column="Y", value='')
            self.tree.tag_configure(sample, background='white')

        self.plot_callback()