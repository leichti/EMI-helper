import os
import time
from tkinter import Tk, Label, StringVar, Entry, Checkbutton, BooleanVar, Frame, Canvas, Scrollbar, VERTICAL, \
    HORIZONTAL, Scale, OptionMenu, IntVar
from PIL import Image, ImageTk
from picture_for_temperature import process_folder

previous_num_images_per_row = None
def get_sample_names():
    sample_names = []
    for folder in os.listdir('data'):
        if os.path.isdir(os.path.join('data', folder)):
            sample_names.append(folder)
    return sample_names


def main():
    sample_names = get_sample_names()
    image_cache = {}  # Cache to store loaded images

    root = Tk()#
    root.title("Image Loader")
    root.state('zoomed')  # Start maximized

    # Create frames for layout
    control_frame = Frame(root)
    control_frame.pack(side="left", fill="y")

    image_canvas = Canvas(root)
    image_canvas.pack(side="right", fill="both", expand=True)

    scroll_y = Scrollbar(root, orient=VERTICAL, command=image_canvas.yview)
    scroll_y.pack(side="right", fill="y")

    scroll_x = Scrollbar(root, orient=HORIZONTAL, command=image_canvas.xview)
    scroll_x.pack(side="bottom", fill="x")

    image_canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    image_frame = Frame(image_canvas)
    image_canvas.create_window((0, 0), window=image_frame, anchor='nw')

    # Add title to image_frame
    Label(image_frame, text="Images at Specified Temperature").grid(row=0, column=0, columnspan=6)

    temp_var = StringVar(root)
    temp_var.set("1200")

    Label(control_frame, text="Set Temperature:").pack()
    temp_entry = Entry(control_frame, textvariable=temp_var)
    temp_entry.pack()

    temp_slider = Scale(control_frame, from_=0, to=1600, orient=HORIZONTAL, command=lambda v: update_temperature(v))
    temp_slider.set(1200)
    temp_slider.pack()

    def update_temperature(value):
        temp_var.set(value)
        temp_slider.set(value)
        load_images()

    temp_entry.bind("<Return>", lambda event: load_images())
    root.bind("<Left>", lambda event: adjust_temperature(-20))
    root.bind("<Right>", lambda event: adjust_temperature(20))

    def adjust_temperature(delta):
        try:
            new_temp = int(temp_var.get()) + delta
            if 0 <= new_temp <= 1600:
                temp_var.set(str(new_temp))
                temp_slider.set(new_temp)
                load_images()
        except ValueError:
            print("Invalid temperature value. Please enter a valid number.")

    # Create a dropdown for the number of images per row
    num_images_var = IntVar(root)
    num_images_var.set(3)
    Label(control_frame, text="Images per Row:").pack()
    OptionMenu(control_frame, num_images_var, *range(1, 7), command=lambda _: load_images()).pack()

    # Create a canvas for the checkboxes
    checkbox_canvas = Canvas(control_frame, height=300)
    checkbox_canvas.pack(side="left", fill="y", expand=True)

    scrollbar = Scrollbar(control_frame, orient=VERTICAL, command=checkbox_canvas.yview)
    scrollbar.pack(side="right", fill="y")

    checkbox_frame = Frame(checkbox_canvas)
    checkbox_canvas.create_window((0, 0), window=checkbox_frame, anchor='nw')

    experiment_vars = {}
    for sample in sample_names:
        var = BooleanVar()
        experiment_vars[sample] = var
        Checkbutton(checkbox_frame, text=sample, variable=var, command=lambda: load_images()).pack(anchor='w')

    checkbox_canvas.configure(yscrollcommand=scrollbar.set)
    checkbox_frame.bind("<Configure>", lambda e: checkbox_canvas.configure(scrollregion=checkbox_canvas.bbox("all")))


    def load_images():
        start_time = time.time()

        # Clear existing widgets
        for widget in image_frame.winfo_children():
            if isinstance(widget, Label) and widget.cget("text") != "Images at Specified Temperature":
                widget.destroy()
        print(f"Clearing widgets took {time.time() - start_time:.2f} seconds")

        Label(image_frame, text="Images at Specified Temperature").grid(row=0, column=0, columnspan=6)
        print(f"Adding title took {time.time() - start_time:.2f} seconds")

        try:
            temp = int(temp_var.get())
        except ValueError:
            print("Invalid temperature value. Please enter a valid number.")
            return

        num_images_per_row = num_images_var.get()

        # Clear image cache when layout changes
        global previous_num_images_per_row
        if num_images_per_row != previous_num_images_per_row:
            image_cache.clear()
            previous_num_images_per_row = num_images_per_row
            print("Cleared image cache due to layout change")

        canvas_width = image_canvas.winfo_width()
        if canvas_width == 1:  # If canvas width is not calculated yet
            root.update_idletasks()
            canvas_width = image_canvas.winfo_width()
        img_width = canvas_width // num_images_per_row
        print(f"Calculating image dimensions took {time.time() - start_time:.2f} seconds")

        row = 1
        col = 0
        for sample, var in experiment_vars.items():
            if var.get():
                image_key = f"{sample}_{temp}"
                if image_key not in image_cache:
                    try:
                        process_start_time = time.time()
                        process_folder('data', temp, sample, force=False, target_format='JPEG')
                        print(f"Processing folder for {sample} took {time.time() - process_start_time:.2f} seconds")

                        image_path = f'selected_images/{temp}/{sample}.jpeg'
                        if os.path.exists(image_path):
                            img = Image.open(image_path)
                            img_ratio = img.width / img.height
                            img_height = int(img_width / img_ratio)
                            img = img.resize((img_width, img_height))  # Resize for display
                            img_tk = ImageTk.PhotoImage(img)
                            image_cache[image_key] = img_tk
                            print(
                                f"Loading and caching image for {sample} took {time.time() - process_start_time:.2f} seconds")
                        else:
                            print(f"Image file not found for {sample}: {image_path}")
                    except Exception as e:
                        print(f"Error loading image for {sample}: {e}")

                if image_key in image_cache:
                    img_label = Label(image_frame, image=image_cache[image_key])
                    img_label.image = image_cache[image_key]  # Keep a reference to avoid garbage collection
                    img_label.grid(row=row, column=col)
                    col += 1
                    if col == num_images_per_row:
                        col = 0
                        row += 1

        image_frame.update_idletasks()
        image_canvas.config(scrollregion=image_canvas.bbox("all"))
        print(f"Total load_images execution time: {time.time() - start_time:.2f} seconds")
        previous_num_images_per_row = num_images_var.get()

    root.mainloop()


if __name__ == "__main__":
    main()