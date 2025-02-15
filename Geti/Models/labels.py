#Code to sort the images into individual folders based on their phenotype labels
import pandas as pd
import os
import shutil

def read_excel_to_df(file_path):
    """
    Read the first worksheet of an Excel file into a pandas DataFrame
    
    Args:
        file_path (str): Full path to the Excel file
        
    Returns:
        pd.DataFrame: DataFrame containing the first worksheet
    """
    try:
        # Verify file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found at: {file_path}")
            
        # Read only the first worksheet
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Print basic information about the DataFrame
        print(f"Successfully loaded DataFrame with shape: {df.shape}")
        print("\nFirst few rows:")
        print(df.head())
        print("\nColumns:")
        print(df.columns.tolist())
        
        return df
        
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return None

# Full path to the Excel file
file_path = "/Volumes/Dhruv 2TB/Brompton Work/Copy of MASTER DATASET_Bailey v2.xlsx"

# Read the Excel file
df = read_excel_to_df(file_path)



import os
import shutil

def setup_classification_folders(base_path):
    """
    Create folders for each classification (1-15)
    """
    for i in range(1, 16):
        folder_path = os.path.join(base_path, str(i))
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created folder for classification {i}")

def sort_montages_by_classification(df, montage_dir, output_base_dir):
    """
    Sort montage images into classification folders
    
    Args:
        df: Pandas DataFrame containing Patient IDs and classifications
        montage_dir: Directory containing montage images
        output_base_dir: Base directory for classification folders
    """
    # Print DataFrame info for debugging
    print("DataFrame columns:", df.columns.tolist())
    
    # Create mapping of Patient ID to classification
    classification_map = dict(zip(df['Patient ID'], df['SRD Phenotype (1-15)']))
    
    # Create classification folders
    setup_classification_folders(output_base_dir)
    
    # Counter for tracking
    processed = 0
    skipped = 0
    
    # Process each montage file
    for root, _, files in os.walk(montage_dir):
        for filename in files:
            if filename.endswith('.jpg'):
                # Extract patient ID (part before the dot)
                patient_id = filename.split('.')[0]
                
                # If we have a classification for this patient
                if patient_id in classification_map:
                    classification = classification_map[patient_id]
                    
                    # Source and destination paths
                    src_path = os.path.join(root, filename)
                    dst_path = os.path.join(output_base_dir, 
                                          str(int(classification)), # ensure it's an integer
                                          filename)
                    
                    # Copy file to appropriate classification folder
                    try:
                        shutil.move(src_path, dst_path)
                        processed += 1
                        print(f"Copied {filename} to classification {int(classification)}")
                    except Exception as e:
                        print(f"Error copying {filename}: {str(e)}")
                else:
                    print(f"No classification found for {patient_id}")
                    skipped += 1
    
    print(f"\nProcessing complete:")
    print(f"Files processed: {processed}")
    print(f"Files skipped: {skipped}")

# Paths
file_path = "/Volumes/Dhruv 2TB/Brompton Work/Copy of MASTER DATASET_Bailey v2.xlsx"
montage_dir = "/Users/dhruvgupta/Documents/GitHub/BromptonML/Geti/Data"
output_base_dir = "/Users/dhruvgupta/Documents/GitHub/BromptonML/Geti/Data"

# Read Excel file using the existing function
df = read_excel_to_df(file_path)

# Sort montages
if df is not None:
    sort_montages_by_classification(df, montage_dir, output_base_dir)
else:
    print("Failed to load DataFrame")