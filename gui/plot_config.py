# plot_config.py
class PlotConfig:
    def __init__(self, x_column, y_column, x_label, y_label, x_min, x_max, y_min, y_max, hline_y, vline_x):
        self.x_column = x_column
        self.y_column = y_column
        self.x_label = x_label
        self.y_label = y_label
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.hline_y = hline_y
        self.vline_x = vline_x