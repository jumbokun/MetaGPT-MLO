import pydicom
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

def read_dcm_file(file_path):
    """
    Reads a dcm file and extracts relevant information.
    
    Args:
        file_path (str): Path to the dcm file.
    
    Returns:
        dict: A dictionary containing the extracted information.
    """
    try:
        ds = pydicom.read_file(file_path)
        info = {
            'PatientID': ds.PatientID,
            'PatientName': ds.PatientName,
            'StudyDate': ds.StudyDate,
            'SeriesDescription': ds.SeriesDescription
        }
        return info
    except Exception as e:
        print(f"Error reading file: {file_path}, Error: {str(e)}")
        return None

def extract_info_from_dcm_files(file_paths):
    """
    Extracts information from a list of dcm files.
    
    Args:
        file_paths (list): A list of paths to the dcm files.
    
    Returns:
        list: A list of dictionaries containing the extracted information.
    """
    info_list = []
    for file_path in file_paths:
        info = read_dcm_file(file_path)
        if info is not None:
            info_list.append(info)
    return info_list

def preprocess_data(data):
    """
    Preprocesses the data by encoding categorical variables and scaling numerical variables.
    
    Args:
        data (list): A list of dictionaries containing the extracted information.
    
    Returns:
        pd.DataFrame: A pandas DataFrame containing the preprocessed data.
    """
    df = pd.DataFrame(data)
    
    # Encode categorical variables
    le = LabelEncoder()
    df['SeriesDescription'] = le.fit_transform(df['SeriesDescription'])
    
    # Scale numerical variables
    scaler = StandardScaler()
    df[['StudyDate']] = scaler.fit_transform(df[['StudyDate']])
    
    return df

# Example usage:
file_paths = ['path/to/file1.dcm', 'path/to/file2.dcm']
info_list = extract_info_from_dcm_files(file_paths)
df = preprocess_data(info_list)
print(df.head())
