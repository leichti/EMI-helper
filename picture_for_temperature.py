import os
import sqlite3
import pandas as pd
import shutil
from PIL import Image, ImageDraw, ImageFont

def parse_measured_values_table(db_path):
    """Parse the MeasuredValues table from the SQLite database and return the DataFrame."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM MeasuredValues;")
    rows = cursor.fetchall()
    if rows:
        cursor.execute("PRAGMA table_info(MeasuredValues);")
        columns = [col[1] for col in cursor.fetchall()]
        measured_values_df = pd.DataFrame(rows, columns=columns)
        conn.close()
        return measured_values_df
    conn.close()
    return pd.DataFrame()

def find_closest_temperature(measured_values_df, target_temperature):
    """Find the closest temperature with an available image in the MeasuredValues DataFrame."""
    measured_values_df = measured_values_df[measured_values_df['ImageNr'] != 0].copy()  # Filter out rows with no image
    measured_values_df.loc[:, 'TemperatureDiff'] = abs(measured_values_df['Temperature'] - target_temperature)
    closest_row = measured_values_df.loc[measured_values_df['TemperatureDiff'].idxmin()]
    closest_temperature = closest_row['Temperature']
    image_filename = closest_row['ImageNr']
    return closest_temperature, image_filename


def copy_image_to_folder(image_filename, source_folder, target_folder, new_filename, target_format='JPEG'):
    """Copy and convert image to the target folder with a new filename and format."""
    os.makedirs(target_folder, exist_ok=True)
    source_path = os.path.join(source_folder, image_filename)
    target_path = os.path.join(target_folder, f"{os.path.splitext(new_filename)[0]}.{target_format.lower()}")

    img = Image.open(source_path)
    img.save(target_path, format=target_format)
    return target_path

def write_text_to_image(image_path, text):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)

        # Get image dimensions
        image_width, image_height = img.size

        # Set font size to 10% of the image height
        font_size = int(image_height * 7.5 / 100)
        font = ImageFont.truetype("TitilliumWeb-Regular.ttf", font_size)  # Use a truetype font

        # Split the text into lines
        lines = text.splitlines()

        # Calculate the total height of all lines combined
        total_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines)
        total_height += (len(lines) - 1) * font_size * 0.2  # Include spacing between lines

        # Starting y position for the first line (vertically centered)
        y = image_height - total_height*1.3

        for line in lines:
            # Get width and height of the current line
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
            line_width = right - left
            line_height = bottom - top

            # Calculate the x position (horizontally centered)
            x = (image_width - line_width) / 2

            # Draw the text line by line
            draw.text((x, y), line, font=font, fill="white")

            # Update y position for the next line
            y += line_height + font_size * 0.2  # Adjust for spacing between lines

        img.save(image_path)
        #print(f"Added text '{text}' to {image_path}")

def get_closest_image_filepath(root_directory, target_temperature, samplename=None):
    """Get the file path of the closest image based on the target temperature."""
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.dat'):
                db_path = os.path.join(dirpath, filename)
                measured_values_df = parse_measured_values_table(db_path)
                temp, image_filename = find_closest_temperature(measured_values_df, target_temperature)
                current_samplename = os.path.basename(dirpath)

                if samplename and current_samplename != samplename:
                    continue

                if image_filename:
                    #print(f"Closest temperature: {temp} in folder {current_samplename}")
                    #print(f"Corresponding image filename: {image_filename}")
                    return os.path.join(dirpath, image_filename), temp, current_samplename
                else:
                    print(f"No available image found for the given temperature in folder {current_samplename}.")

    return None, None, None

import os


def process_folder(root_directory, target_temperature, samplename=None, force=True, target_format='JPEG'):
    """Process a folder to find and copy the closest image based on the target temperature."""

    def construct_target_image_path(target_folder, samplename, target_format):
        return os.path.join(target_folder, f"{samplename}.{target_format.lower()}")

    def process_single_folder(folder_path, target_temperature, samplename, force, target_format):
        for filename in os.listdir(folder_path):
            if filename.endswith('.dat'):
                db_path = os.path.join(folder_path, filename)
                measured_values_df = parse_measured_values_table(db_path)
                temp, image_filename = find_closest_temperature(measured_values_df, target_temperature)
                current_samplename = os.path.basename(folder_path)

                if samplename and current_samplename != samplename:
                    continue

                if image_filename:
                    target_folder = os.path.join('selected_images', f"{target_temperature:.0f}")
                    new_filename = f"{current_samplename}.{target_format.lower()}"
                    target_image_path = construct_target_image_path(target_folder, current_samplename, target_format)

                    if not force and os.path.exists(target_image_path):
                        print(
                            f"Image for {current_samplename} at {target_temperature} °C already exists. Skipping processing.")
                        continue

                    target_image_path = copy_image_to_folder(image_filename, folder_path, target_folder, new_filename,
                                                             target_format)
                    write_text_to_image(target_image_path, f"{temp:.0f} °C\n{current_samplename}")
                else:
                    print(f"No available image found for the given temperature in folder {current_samplename}")

    if samplename:
        # Process only the specified folder
        folder_path = os.path.join(root_directory, samplename)
        target_folder = os.path.join('selected_images', f"{target_temperature:.0f}")
        target_image_path = construct_target_image_path(target_folder, samplename, target_format)

        if not force and os.path.exists(target_image_path):
            print(f"Image for {samplename} at {target_temperature} °C already exists. Skipping processing.")
            return

        if os.path.isdir(folder_path):
            process_single_folder(folder_path, target_temperature, samplename, force, target_format)
        else:
            print(f"Sample folder '{samplename}' not found in the root directory.")
    else:
        # Iterate over all folders in the root directory
        for dirpath, dirnames, filenames in os.walk(root_directory):
            current_samplename = os.path.basename(dirpath)
            target_folder = os.path.join('selected_images', f"{target_temperature:.0f}")
            target_image_path = construct_target_image_path(target_folder, current_samplename, target_format)

            if not force and os.path.exists(target_image_path):
                print(f"Image for {current_samplename} at {target_temperature} °C already exists. Skipping processing.")
                continue

            process_single_folder(dirpath, target_temperature, samplename, force, target_format)

# Example usage:
# process_folder('data', 1200, 'sample_name', force=False)
# Example usage:
# process_folder('data', 1200, 'sample_name', force=False)
def main(target_temperature, samplenames=None):
    root_directory = 'data'
    if samplenames:
        for samplename in samplenames:
            process_folder(root_directory, target_temperature, samplename)
    else:
        process_folder(root_directory, target_temperature)

if __name__ == "__main__":
    target_temperature = float(input("Enter the target temperature: "))
    main(target_temperature)