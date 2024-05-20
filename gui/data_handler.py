# data_handler.py
import os
import pandas as pd

def get_sample_names(data_dir='../data'):
    sample_names = []
    for folder in os.listdir(data_dir):
        if os.path.isdir(os.path.join(data_dir, folder)):
            sample_names.append(folder)
    return sample_names

def load_parquet_file(file_path):
    return pd.read_parquet("../"+file_path)