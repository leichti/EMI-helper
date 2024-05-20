from tkinter import Toplevel, StringVar
from tkinter.ttk import Treeview, OptionMenu, Entry, Button
from tkinter import ttk

from customtkinter import CTkOptionMenu, CTkEntry


class PlotStylePopup:
    def __init__(self, gui, plot_callback, sample_names, styles):
        self.gui = gui
        self.master = gui.root
        self.plot_callback = plot_callback
        self.sample_names = sample_names
        self.styles = styles

        self.popup = Toplevel(self.master)
        self.popup.title("Plot Style Configuration")

        self.tree = Treeview(self.popup, columns=("Sample-Nr", "Samplename", "Color", "Linestyle", "Alpha", "Linewidth", "Legend-Label"), show='headings')
        self.tree.heading("Sample-Nr", text="Sample Nr")
        self.tree.heading("Samplename", text="Samplename")
        self.tree.heading("Color", text="Color")
        self.tree.heading("Linestyle", text="Linestyle")
        self.tree.heading("Alpha", text="Alpha")
        self.tree.heading("Linewidth", text="Linewidth")
        self.tree.heading("Legend-Label", text="Legend Label")

        for i, sample in enumerate(sample_names):
            self.tree.insert("", "end", values=(
                i + 1, sample,
                self.styles[sample]["Color"].get(),
                self.styles[sample]["Linestyle"].get(),
                self.styles[sample]["Alpha"].get(),
                self.styles[sample]["Linewidth"].get(),
                self.styles[sample]["Legend-Label"].get()
            ))

        self.tree.pack()

        self.tree.bind("<Double-1>", self.on_item_double_click)

        self.save_button = Button(self.popup, text="Save", command=self.save_styles)
        self.save_button.pack()

    def on_item_double_click(self, event):
        item = self.tree.selection()[0]
        sample = self.tree.item(item, "values")[1]

        top = Toplevel(self.popup)
        top.title(f"Edit Style for {sample}")

        color_label = ttk.Label(top, text="Color:")
        color_label.grid(row=0, column=0)
        color_option = CTkOptionMenu(top, variable=self.styles[sample]["Color"], values=["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"])
        color_option.grid(row=0, column=1)

        linestyle_label = ttk.Label(top, text="Linestyle:")
        linestyle_label.grid(row=1, column=0)
        linestyle_option = CTkOptionMenu(top, variable=self.styles[sample]["Linestyle"], values=["solid", "dashed", "dotted"])
        linestyle_option.grid(row=1, column=1)

        alpha_label = ttk.Label(top, text="Alpha:")
        alpha_label.grid(row=2, column=1)
        alpha_option = CTkOptionMenu(top, variable=self.styles[sample]["Alpha"], values=["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"])
        alpha_option.grid(row=2, column=1)

        linewidth_label = ttk.Label(top, text="Linewidth:")
        linewidth_label.grid(row=3, column=0)
        linewidth_entry = CTkEntry(top, textvariable=self.styles[sample]["Linewidth"])
        linewidth_entry.grid(row=3, column=1)

        legend_label = ttk.Label(top, text="Legend Label:")
        legend_label.grid(row=4, column=0)
        legend_entry = CTkEntry(top, textvariable=self.styles[sample]["Legend-Label"])
        legend_entry.grid(row=4, column=1)

        button = Button(top, text="Save", command=lambda: self.update_treeview(item, sample, top))
        button.grid(row=5, columnspan=2)

    def update_treeview(self, item, sample, top):
        self.tree.item(item, values=(
            self.tree.item(item, 'values')[0],
            sample,
            self.styles[sample]["Color"].get(),
            self.styles[sample]["Linestyle"].get(),
            self.styles[sample]["Alpha"].get(),
            self.styles[sample]["Linewidth"].get(),
            self.styles[sample]["Legend-Label"].get()
        ))
        top.destroy()

    def save_styles(self):
        self.plot_callback()
        self.gui.save_styles()
        self.popup.destroy()

    def get_styles(self):
        return self.styles