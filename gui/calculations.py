# calculations.py
import numpy as np

def calculate_intersections(df, x_column, y_column, hline_y, vline_x):
    y_intersect = None
    x_intersect = None

    y_data = df[y_column].values
    x_data = df[x_column].values

    if np.any(y_data == hline_y):
        x_intersect = df.loc[y_data == hline_y, x_column].values[0]
    else:
        indices = np.where(np.diff(np.sign(y_data - hline_y)))[0]
        if indices.size > 0:
            idx = indices[0]
            x_intersect = np.interp(hline_y, [y_data[idx], y_data[idx + 1]], [x_data[idx], x_data[idx + 1]])

    if np.any(x_data == vline_x):
        y_intersect = df.loc[x_data == vline_x, y_column].values[0]
    else:
        indices = np.where(np.diff(np.sign(x_data - vline_x)))[0]
        if indices.size > 0:
            idx = indices[0]
            y_intersect = np.interp(vline_x, [x_data[idx], x_data[idx + 1]], [y_data[idx], y_data[idx + 1]])

    return x_intersect, y_intersect