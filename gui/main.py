# main.py
from data_handler import get_sample_names, load_parquet_file
from calculations import calculate_intersections
from plotter import plot
from gui import GUIManager

def main():
    sample_names = get_sample_names()
    parquet_file = f"{sample_names[0]}"
    df = load_parquet_file(parquet_file)
    columns = df.columns

    def plot_callback():
        plot(df, gui_manager, calculate_intersections, set_treeview_value)

    def set_treeview_value(sample_value, column, set_value):
        for row in gui_manager.tree.get_children():
            row_values = gui_manager.tree.item(row, "values")
            if row_values[0] == sample_value:
                gui_manager.tree.set(row, column, set_value)
                break

    gui_manager = GUIManager(columns, plot_callback, sample_names)

    plot_callback()
    gui_manager.root.mainloop()

if __name__ == "__main__":
    main()