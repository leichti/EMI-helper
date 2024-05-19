import os
import sqlite3
import pandas as pd
import re
import logging

# Configure logging
logging.basicConfig(filename='samples_overview.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def extract_dust_number_and_washed(name):
    # Extract dust number using regex
    dust_number_match = re.search(r'EAFD_(\d+[_\d]*)', name)
    dust_number = dust_number_match.group(1).split('_')[0] if dust_number_match else ''

    # Determine washed status
    washed = 0 if 'W' in name else 1

    return dust_number, washed


def read_measurement_series_meta_info(db_path, samples_list):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if MeasurementSeriesMetaInfo table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='MeasurementSeriesMetaInfo';")
    if cursor.fetchone():
        # Query to get all columns from the MeasurementSeriesMetaInfo table
        cursor.execute("PRAGMA table_info(MeasurementSeriesMetaInfo);")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        # Query to get all data from the MeasurementSeriesMetaInfo table
        cursor.execute("SELECT * FROM MeasurementSeriesMetaInfo;")
        rows = cursor.fetchall()

        for row in rows:
            series = pd.Series(row, index=column_names)
            if 'Samplename' in series:
                name = series['Samplename'].strip()
                dust_number, washed = extract_dust_number_and_washed(name)
                samples_list.append({'Name': name, 'Dust-Nr': dust_number, 'Washed': washed})
            else:
                logging.warning(f"Samplename column missing in database: {db_path}")

    conn.close()


def traverse_directories(root_dir, samples_list):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.dat'):
                db_path = os.path.join(dirpath, filename)
                read_measurement_series_meta_info(db_path, samples_list)


def create_summary_dataframe(df):
    # Create a fictive list of EAFD from 1 to 22
    eafd_list = list(range(1, 23))

    # Initialize a summary list
    summary_list = []

    for eafd in eafd_list:
        # Check availability of unwashed and washed samples
        unwashed_available = not df[(df['Dust-Nr'] == eafd) & (df['Washed'] == 1)].empty
        washed_available = not df[(df['Dust-Nr'] == eafd) & (df['Washed'] == 0)].empty

        summary_list.append({
            'EAFD': eafd,
            'Unwashed available?': int(unwashed_available),
            'Washed available?': int(washed_available)
        })

    # Create a DataFrame from the summary list
    summary_df = pd.DataFrame(summary_list)

    return summary_df


def parse_tables(db_path):
    """Parse the MeasuredValues and ImageList tables from the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    def fetch_table_data(table_name):
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        if rows:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            return pd.DataFrame(rows, columns=columns)
        return pd.DataFrame()

    measured_values_df = fetch_table_data('MeasuredValues')
    image_list_df = fetch_table_data('ImageList')
    conn.close()

    return measured_values_df, image_list_df


def rename_image_files_and_update_db(measured_values_df, folder_path, db_path):
    """Rename image files based on the temperature value in the MeasuredValues DataFrame and update the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for index, row in measured_values_df.iterrows():
        image_nr = row['ImageNr']
        if image_nr != 0:
            temperature = row['Temperature']
            formatted_temp = f"{temperature:.1f}"
            if type(image_nr) is str:
                continue

            old_filename = f"m_{image_nr:05d}.Tif"
            new_filename = f"{formatted_temp}.Tif"
            old_filepath = os.path.join(folder_path, old_filename)
            new_filepath = os.path.join(folder_path, new_filename)
            if os.path.exists(old_filepath):
                os.rename(old_filepath, new_filepath)
                logging.info(f"Renamed {old_filename} to {new_filename}")
                print(f"Renamed {old_filename} to {new_filename}")
                # Update the ImageNr column in the database
                cursor.execute("UPDATE MeasuredValues SET ImageNr = ? WHERE ImageNr = ?", (new_filename, image_nr))
                conn.commit()
                logging.info(f"Updated ImageNr in the database for {new_filename}")

    conn.close()


def main():
    root_directory = 'data'
    samples_list = []

    # Traverse directories and collect sample information
    traverse_directories(root_directory, samples_list)

    # Create a DataFrame from the collected information
    df = pd.DataFrame(samples_list, columns=['Name', 'Dust-Nr', 'Washed'])

    # Convert Dust-Nr to numeric, forcing errors to NaN
    df['Dust-Nr'] = pd.to_numeric(df['Dust-Nr'], errors='coerce')

    # Sort the DataFrame by Dust-Nr and then by Washed
    df = df.sort_values(by=['Dust-Nr', 'Washed'])

    # Save the DataFrame to a CSV file
    df.to_excel('outputs/samples_overview.xlsx', index=False)
    print("Overview table created and saved as 'samples_overview.xlsx'.")

    # Create a summary DataFrame
    summary_df = create_summary_dataframe(df)

    # Save the summary DataFrame to an Excel file
    summary_df.to_excel('samples_summary.xlsx', index=False)
    print("Summary table created and saved as 'samples_summary.xlsx'.")

    # Traverse directories to rename image files and update the database
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.dat'):
                db_path = os.path.join(dirpath, filename)
                measured_values_df, image_list_df = parse_tables(db_path)
                rename_image_files_and_update_db(measured_values_df, dirpath, db_path)


if __name__ == "__main__":
    main()