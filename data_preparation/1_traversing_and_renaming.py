import os
import sqlite3
import pandas as pd
from collections import defaultdict
import shutil

# Store folder renaming information
folder_rename_dict = defaultdict(str)


def read_measurement_series_meta_info(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if MeasurementSeriesMetaInfo table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='MeasurementSeriesMetaInfo';")
    if cursor.fetchone():
        # Query to get all column names from the MeasurementSeriesMetaInfo table
        cursor.execute("PRAGMA table_info(MeasurementSeriesMetaInfo);")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        # Query to get all data from the MeasurementSeriesMetaInfo table
        cursor.execute("SELECT * FROM MeasurementSeriesMetaInfo;")
        rows = cursor.fetchall()

        print(f"Data in MeasurementSeriesMetaInfo table from {db_path}:")
        for row in rows:
            series = pd.Series(row, index=column_names)
            print(series)

            # Prompt user for Samplename
            current_name = series['Samplename'].strip()
            new_name = input(
                f"Current Samplename is '{current_name}'. Enter new name or press Enter to keep: ") or current_name

            if new_name == current_name:
                conn.close()
                return

            cursor.execute("UPDATE MeasurementSeriesMetaInfo SET Samplename = ? WHERE Samplename = ?",
                           (new_name, current_name))
            conn.commit()

            # Store folder renaming information
            parent_dir = os.path.dirname(db_path)
            conn.close()
            handle_rename(parent_dir, new_name)
    else:
        print(f"No MeasurementSeriesMetaInfo table found in {db_path}.")

    conn.close()
    print()  # Add a blank line for readability


def traverse_directories(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.dat'):
                db_path = os.path.join(dirpath, filename)
                read_measurement_series_meta_info(db_path)


def handle_rename_conflict(old_name, new_name):
    action = input(
        f"Conflict: '{new_name}' already exists or is in the collection. [s]kip, [d]elete existing, [r]ename different: ").lower()
    if action == 's':
        return 'skip'
    elif action == 'd':
        os.rename(new_name, new_name + "_old")
        return 'delete'
    elif action == 'r':
        return 'rename'
    else:
        return handle_rename_conflict(old_name, new_name)


def handle_rename(old_name, new_name):
    parent_dir = os.path.dirname(old_name)
    new_path = os.path.join(parent_dir, new_name)

    if os.path.exists(new_path) or new_name in folder_rename_dict.values():
        action = handle_rename_conflict(old_name, new_path)
        if action == 'skip':
            return
        elif action == 'rename':
            new_name = input(f"Enter a new name for '{old_name}': ")
            handle_rename(old_name, new_name)
            return

    if not os.path.exists(new_path):
        os.rename(old_name, new_path)
        print(f"Renamed {old_name} to {new_name} ({new_path})")


# Call the functions with the root directory
root_directory = '../data/'
traverse_directories(root_directory)