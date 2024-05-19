import os
import sqlite3
import pandas as pd


def list_sample_names(root_directory):
    """List available sample names by reading the folder structure in the root directory."""
    sample_names = []
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for dirname in dirnames:
            sample_names.append(dirname)
        break  # Only read the top-level directories
    return sample_names


def get_all_tables(db_path):
    """Retrieve all tables from the SQLite database and return them as a dictionary of DataFrames."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    dataframes = {}

    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        if rows:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            df = pd.DataFrame(rows, columns=columns)
            # Drop the Contour column if it exists
            if 'Contour' in df.columns:
                df = df.drop(columns=['Contour'])
            # Ensure correct data types for parquet conversion
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, bytes) else x)
                    df[col] = df[col].astype(str)
            dataframes[table_name] = df

    conn.close()
    return dataframes


def save_dataframes_as_parquet(dataframes, target_folder, samplename):
    """Save the DataFrames as Parquet files into the target folder."""
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for table_name, df in dataframes.items():
        parquet_path = os.path.join(target_folder, f"{samplename}_{table_name}.parquet")
        df.to_parquet(parquet_path)
        print(f"Saved {table_name} as {parquet_path}")


def process_samples(root_directory, target_directory):
    """Process all samples to extract tables and save them as Parquet files."""
    sample_names = list_sample_names(root_directory)

    for sample_name in sample_names:
        sample_dir = os.path.join(root_directory, sample_name)
        for filename in os.listdir(sample_dir):
            if filename.endswith('.dat'):
                db_path = os.path.join(sample_dir, filename)
                dataframes = get_all_tables(db_path)
                save_dataframes_as_parquet(dataframes, target_directory, sample_name)
                break  # Assuming one .dat file per sample directory


def main():
    root_directory = '../data'
    target_directory = '../parquet_data'
    process_samples(root_directory, target_directory)


if __name__ == "__main__":
    main()