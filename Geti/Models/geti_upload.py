import os
from pathlib import Path
from geti_sdk import Geti
from geti_sdk.rest_clients import ProjectClient, ImageClient
from geti_sdk.rest_clients.annotation_clients.annotation_client import AnnotationClient
from geti_sdk.utils import get_server_details_from_env
from tqdm import tqdm
from geti_sdk.data_models.annotation_scene import AnnotationScene
from geti_sdk.data_models.annotations import Annotation
from geti_sdk.data_models.shapes import Rectangle

from PIL import Image

def get_full_image_rectangle(image_file: str) -> Rectangle:
    """
    Creates a Rectangle object that covers the entire image using PIL.
    
    Args:
        image_file (str): Path to the image file
        
    Returns:
        Rectangle: A Rectangle object with dimensions matching the full image
    """
    # Read image dimensions using PIL
    with Image.open(str(image_file)) as img:
        width, height = img.size
    
    # Create rectangle starting at (0,0) with full image dimensions
    rectangle = Rectangle(
        x=0,
        y=0,
        width=width,
        height=height
    )
    
    return rectangle

# Configurable parameters
PROJECT_NAME = "Sarcoid Phen - Montage, NoSeg, 10 samples"
PROJECT_TYPE = "classification"  # can be changed to "detection", "segmentation" etc.
DATA_PATH = "/Users/dhruvgupta/Documents/GitHub/BromptonML/Geti/Data"
IMAGE_EXTENSIONS = ['.jpg']  # can add more like ['.jpg', '.jpeg', '.png']
HOST = "https://192.168.109.232"
TOKEN = "geti_pat_GlXjjyvY6R6ZPM0qDGtmEGZ0r3IXVyVnleXaD3WFT7e_2jrsMz"
VERIFY_CERT = False

def create_project_and_upload_data(project_name, project_type, data_path, image_extensions, host_ip, token_val, verify_cert):
    """
    Creates a new Geti project and uploads images with annotations based on folder structure.
    """
    
    print(f"Initializing connection to Geti server...")
    
   
    
    # Connect to Geti server
    geti = Geti(
        host=host_ip,
        token=token_val,
        verify_certificate = verify_cert
    )
    
    project_client = ProjectClient(
        session=geti.session, 
        workspace_id=geti.workspace_id
    )
    
    # Get label names from folder structure
    data_dir = Path(data_path)
    label_folders = [f for f in data_dir.iterdir() if f.is_dir()]
    labels = [folder.name for folder in label_folders]
    
    print(f"Found {len(labels)} labels: {labels}")
    
    # Create new project
    print(f"Creating new project: {project_name}")
    project = project_client.create_project(
        project_name=project_name,
        project_type=project_type,
        labels=[labels]
    )

    # Get all labels from project to create label dictionary
    all_labels = project.get_all_labels()
    label_dict = {label.name: label for label in all_labels}
    
    # Set up image and annotation clients
    image_client = ImageClient(
        session=geti.session,
        workspace_id=geti.workspace_id,
        project=project,
    )
    
    annotation_client = AnnotationClient(
        session=geti.session, 
        workspace_id=geti.workspace_id, 
        project=project
    )
    
    # Count total images
    total_images = sum(
        len([f for f in folder.glob('*') if f.suffix.lower() in image_extensions])
        for folder in label_folders
    )
    
    print(f"Beginning upload of {total_images} images...")
    
    # Upload images and create annotations
    with tqdm(total=total_images, desc="Uploading images and annotations") as pbar:
        for label_folder in label_folders:
            label_name = label_folder.name
            image_files = [
                f for f in label_folder.glob('*') 
                if f.suffix.lower() in image_extensions
            ]
            
            for image_file in image_files:
                # Upload image
                image = image_client.upload_image(image=str(image_file))

                 # Get rectangle covering whole image
                full_rect = get_full_image_rectangle(str(image_file))
                
                # Create classification annotation
                if project_type == "classification":
                    # For classification, we just need the label
                    annotation = Annotation(
                        labels=[label_dict[label_name],],
                        shape = full_rect,
                    )
                    annotation_scene = AnnotationScene([annotation,])
                    
                # Create annotation
                annotation_client.upload_annotation(
                    image,
                    annotation_scene
                )
                
                pbar.update(1)
    
    print(f"\nProject creation and data upload complete!")
    print(f"Created project '{project_name}' with {total_images} images across {len(labels)} classes")
    
    return project

if __name__ == "__main__":
    project = create_project_and_upload_data(
        project_name=PROJECT_NAME,
        project_type=PROJECT_TYPE,
        data_path=DATA_PATH,
        image_extensions=IMAGE_EXTENSIONS,
        host_ip=HOST,
        token_val=TOKEN,
        verify_cert=VERIFY_CERT
    )