import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import imageio.v3 as iio
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from gui.data_handler import get_sample_names, load_parquet_file
from picture_for_temperature import process_folder


def create_gif(sample_name, min_temp, max_temp, temp_step):
    images = []
    temp = min_temp
    df = load_parquet_file(sample_name, "")

    while temp <= max_temp:
        process_folder('data', temp, sample_name)
        img_path = f'selected_images/{temp:.0f}/{sample_name}.jpeg'

        # Load image
        img = Image.open(img_path)

        # Create Matplotlib plot
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        filtered_df = df[df['Temperature'] <= temp]
        ax.plot(filtered_df['Temperature'], filtered_df['HeightPercent'], label=sample_name)
        ax.set_xlim(min_temp, max_temp)
        ax.set_ylim(0, 120)
        ax.set_xlabel('Temperature')
        ax.set_ylabel('Height Percent')
        ax.legend()

        # Save the plot to a PNG image
        plot_path = f'selected_images/{temp:.0f}/{sample_name}_plot.png'
        fig.savefig(plot_path)
        plt.close(fig)

        # Open the plot image and measure its height
        plot_img = Image.open(plot_path)
        plot_height = plot_img.height

        # Shrink the GIF image to the same height as the plot while maintaining aspect ratio
        img = ImageOps.fit(img, (int(img.width * plot_height / img.height), plot_height), method=Image.Resampling.LANCZOS)

        # Cut 20% off the left and right sides of the GIF image
        crop_width = int(img.width * 0.2)
        img = img.crop((crop_width, 0, img.width - crop_width, img.height))

        # Combine the plot and the modified GIF image side by side
        combined_width = plot_img.width + img.width
        combined_height = plot_height
        combined_img = Image.new('RGB', (combined_width, combined_height))

        # Place the plot on the left and the modified GIF image on the right
        combined_img.paste(plot_img, (0, 0))
        combined_img.paste(img, (plot_img.width, 0))

        # Save the combined image
        combined_img_path = f'selected_images/{temp:.0f}/{sample_name}_combined.jpeg'
        combined_img.save(combined_img_path)

        # Append the combined image to the GIF
        images.append(iio.imread(combined_img_path))
        temp += temp_step

    gif_path = f'{sample_name}_temperature_change.gif'
    iio.imwrite(gif_path, images, format='GIF', duration=0.5)
    return gif_path


class GIFCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Creator")

        self.frames = []
        self.current_frame = 0
        self.frame_count = 0
        self.playing = False

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.create_gif_tab = ttk.Frame(self.notebook)
        self.view_gif_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.create_gif_tab, text="Create GIF")
        self.notebook.add(self.view_gif_tab, text="View GIFs")

        self.setup_create_gif_tab()
        self.setup_view_gif_tab()

    def setup_create_gif_tab(self):
        self.sample_var = tk.StringVar()
        samples = get_sample_names("data")

        tk.Label(self.create_gif_tab, text="Sample:").grid(row=0, column=0)
        self.sample_menu = ttk.Combobox(self.create_gif_tab, textvariable=self.sample_var, values=samples)
        self.sample_menu.grid(row=0, column=1)

        tk.Label(self.create_gif_tab, text="Min Temp:").grid(row=1, column=0)
        self.min_temp_entry = tk.Entry(self.create_gif_tab)
        self.min_temp_entry.grid(row=1, column=1)

        tk.Label(self.create_gif_tab, text="Max Temp:").grid(row=2, column=0)
        self.max_temp_entry = tk.Entry(self.create_gif_tab)
        self.max_temp_entry.grid(row=2, column=1)

        tk.Label(self.create_gif_tab, text="Temp Step:").grid(row=3, column=0)
        self.temp_step_entry = tk.Entry(self.create_gif_tab)
        self.temp_step_entry.grid(row=3, column=1)

        self.create_button = tk.Button(self.create_gif_tab, text="Create GIF", command=self.on_create_gif)
        self.create_button.grid(row=4, column=0, columnspan=2)

        self.result_label = tk.Label(self.create_gif_tab, text="")
        self.result_label.grid(row=5, column=0, columnspan=2)


    def setup_view_gif_tab(self):
        tk.Label(self.view_gif_tab, text="Select GIF:").grid(row=0, column=0)
        self.gif_var = tk.StringVar()
        self.gif_menu = ttk.Combobox(self.view_gif_tab, textvariable=self.gif_var)
        self.gif_menu.grid(row=0, column=1)
        self.gif_menu.bind("<<ComboboxSelected>>", self.on_gif_select)

        self.gif_label = tk.Label(self.view_gif_tab)
        self.gif_label.grid(row=1, column=0, columnspan=2)

        self.play_button = tk.Button(self.view_gif_tab, text="Play", command=self.play_gif)
        self.play_button.grid(row=2, column=0)

        self.pause_button = tk.Button(self.view_gif_tab, text="Pause", command=self.pause_gif)
        self.pause_button.grid(row=2, column=1)

        self.frame_slider = tk.Scale(self.view_gif_tab, from_=0, to=0, orient=tk.HORIZONTAL, command=self.on_slider_move)
        self.frame_slider.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.load_gif_files()


    def load_gif_files(self):
        if not os.path.exists('gifs'):
            os.makedirs('gifs')
        gif_files = [f for f in os.listdir('gifs') if f.endswith('.gif')]
        self.gif_menu['values'] = gif_files


    def on_gif_select(self, event):
        selected_gif = self.gif_var.get()
        gif_path = os.path.join('gifs', selected_gif)
        self.display_gif(gif_path)


    def display_gif(self, gif_path):
        gif_image = Image.open(gif_path)
        self.frames = []

        try:
            while True:
                frame = ImageTk.PhotoImage(gif_image.copy().convert("RGBA"))
                self.frames.append(frame)
                gif_image.seek(gif_image.tell() + 1)
        except EOFError:
            pass

        self.current_frame = 0
        self.frame_count = len(self.frames)

        if self.frame_count > 0:
            self.frame_slider.config(to=self.frame_count - 1)
            self.playing = False
            self.update_gif_frame()


    def update_gif_frame(self):
        if self.playing:
            self.gif_label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.frame_slider.set(self.current_frame)
            self.root.after(100, self.update_gif_frame)  # Adjust delay as needed


    def play_gif(self):
        if self.frames:
            self.playing = True
            self.update_gif_frame()


    def pause_gif(self):
        self.playing = False


    def on_slider_move(self, value):
        if self.frames:
            self.current_frame = int(value)
            self.gif_label.config(image=self.frames[self.current_frame])


    def on_create_gif(self):
        sample_name = self.sample_var.get()
        min_temp = float(self.min_temp_entry.get())
        max_temp = float(self.max_temp_entry.get())
        temp_step = float(self.temp_step_entry.get())

        gif_path = create_gif(sample_name, min_temp, max_temp, temp_step)
        gif_filename = os.path.basename(gif_path)

        if not os.path.exists('gifs'):
            os.makedirs('gifs')

        new_gif_path = os.path.join('gifs', gif_filename)
        os.rename(gif_path, new_gif_path)

        self.result_label.config(text=f"GIF saved as {gif_filename}")
        self.load_gif_files()


if __name__ == "__main__":
    root = tk.Tk()
    app = GIFCreatorApp(root)
    root.mainloop()