#

import pydicom
import SimpleITK as sitk
import os
import numpy as np
from PIL import Image
import random

folder = '/Volumes/Dhruv 2TB/Brompton Work/RBH_Scans'

sub_folders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
print(sub_folders)

base_path = '/Volumes/Dhruv 2TB/Brompton Work/RBH_Scans'
paths = [os.path.join(base_path, sub_folder) for sub_folder in sub_folders]
paths_dict = {sub_folder: os.path.join(base_path, sub_folder) for sub_folder in sub_folders}

def loadImageSeries(base_path):
    # Find the last sub-folder containing files
    for root, dirs, files in os.walk(base_path, topdown=False):
    
        if files:  # Check if files exist in the current folder
            dicom_reader = sitk.ImageSeriesReader()
            dicom_files = dicom_reader.GetGDCMSeriesFileNames(root)
            dicom_reader.SetFileNames(dicom_files)
            try:
                image_out = dicom_reader.Execute()
                return image_out
            except RuntimeError as e:
                raise RuntimeError(f"Error reading DICOM series in folder {root}: {e}")
    raise RuntimeError(f"No valid DICOM series found in {base_path}")

# Initialize the nested dictionary
nested_dict = {}

# Iterate over the sub_folders
for sub_folder in sub_folders:
    folder_path = os.path.join(base_path, sub_folder)
    try:
        # Load the image series for the folder
        image_series = loadImageSeries(folder_path)
    except RuntimeError as e:
        print(f"Error loading image series for {sub_folder}: {e}")
        image_series = None  # Handle failed image loads gracefully
    
    # Populate the nested dictionary
    nested_dict[sub_folder] = {
        "path": folder_path,
        "image": image_series
    }

# Now nested_dict contains the desired structure

print(nested_dict)



def normalize_hu(array):
    """
    Normalize Hounsfield units to 0-255 range for JPEG output
    """
    clipped = np.clip(array, -1000, 400)
    normalized = ((clipped + 1000) * (255.0 / 1400.0)).astype(np.uint8)
    return normalized

def create_montages(nested_dict, output_dir,number):
    """
    Create 5 random 4-slice montages from each CT series
    Calculates slice boundaries individually for each study
    """
    for study_name, data in nested_dict.items():
        try:
            if data["image"] is None:
                print(f"Skipping study {study_name} - no image data")
                continue
                
            print(f"Processing study: {study_name}")
            
            # Convert SimpleITK image to numpy array
            image_array = sitk.GetArrayFromImage(data["image"])
            n_slices = image_array.shape[0]
            
            # Calculate boundaries for this specific study
            start_idx = int(n_slices * 0.1)  # Remove first 10%
            end_idx = int(n_slices * 0.9)    # Remove last 10%
            valid_slices = image_array[start_idx:end_idx]
            n_valid_slices = len(valid_slices)
            
            # Check if we have enough slices
            if n_valid_slices < 8:  # Minimum 2 slices per section
                print(f"Skipping study {study_name} - insufficient valid slices ({n_valid_slices})")
                continue
            
            # Create 5 montages for this study
            for montage_idx in range(number):
                try:
                    # For each montage, calculate fresh section boundaries
                    section_size = n_valid_slices // 4
                    selected_slices = []
                    slice_indices = []
                    
                    # Select slices from each quarter of the valid range
                    for i in range(4):
                        section_start = i * section_size
                        section_end = (i + 1) * section_size if i < 3 else n_valid_slices
                        
                        # Select random slice from this section
                        section_slice_idx = random.randint(section_start, section_end - 1)
                        selected_slice = valid_slices[section_slice_idx]
                        selected_slices.append(selected_slice)
                        
                        # Store original slice index for reporting
                        original_idx = start_idx + section_slice_idx
                        slice_indices.append(original_idx)
                    
                    # Normalize slices using HU window
                    selected_slices_normalized = [normalize_hu(slice_array) 
                                                for slice_array in selected_slices]
                    
                    # Create 2x2 montage
                    montage = np.vstack([
                        np.hstack([selected_slices_normalized[0], selected_slices_normalized[1]]),
                        np.hstack([selected_slices_normalized[2], selected_slices_normalized[3]])
                    ])
                    
                    # Create PIL Image and resize
                    montage_image = Image.fromarray(montage, mode='L')
                    montage_image = montage_image.resize((350, 350), Image.LANCZOS)
                    
                    # Save montage
                    output_filename = f"{study_name}.{montage_idx + 1}.jpg"
                    output_path = os.path.join(output_dir, output_filename)
                    montage_image.save(output_path, quality=95)
                    
                    # Print slice information
                    print(f"  Montage {montage_idx + 1} for study {study_name}:")
                    print(f"    Total slices in study: {n_slices}")
                    print(f"    Valid slice range: {start_idx} to {end_idx}")
                    print(f"    Selected slice indices: {slice_indices}")
                    
                except Exception as e:
                    print(f"Error creating montage {montage_idx + 1} for study {study_name}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error processing study {study_name}: {str(e)}")
            continue


output_dir = "/Users/dhruvgupta/Documents/GitHub/BromptonML/Geti/Data"
create_montages(nested_dict, output_dir,5)

