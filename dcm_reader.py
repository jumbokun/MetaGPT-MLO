import pydicom
import os

def extract_dcm_data(dcm_file):
    try:
        # Read the dcm file
        ds = pydicom.read_file(dcm_file)
        
        # Extract relevant information
        patient_id = ds.PatientID
        study_date = ds.StudyDate
        series_description = ds.SeriesDescription
        
        return {
            'Patient ID': patient_id,
            'Study Date': study_date,
            'Series Description': series_description
        }
    
    except Exception as e:
        print(f"Error reading {dcm_file}: {str(e)}")
        return None

def main():
    # Specify the directory containing dcm files
    dcm_dir = '/path/to/dcm/files'
    
    # Iterate over all files in the directory
    for filename in os.listdir(dcm_dir):
        if filename.endswith(".dcm"):
            file_path = os.path.join(dcm_dir, filename)
            
            # Extract data from the current dcm file
            data = extract_dcm_data(file_path)
            
            if data:
                print(f"Data extracted from {filename}:")
                for key, value in data.items():
                    print(f"{key}: {value}")
                print()

if __name__ == "__main__":
    main()
