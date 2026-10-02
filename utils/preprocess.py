"""
Image Preprocessing Utilities
Shared preprocessing logic for GSDCNet model
"""

import numpy as np
from PIL import Image

IMG_SIZE = 224


def preprocess_image_from_pil(img: Image.Image):
    """
    Preprocess a PIL Image for GSDCNet model prediction
    
    Args:
        img: PIL Image object
        
    Returns:
        numpy array ready for model.predict(), shape (1, 224, 224, 3)
    """
    # Convert to RGB if needed (handles RGBA, grayscale, etc.)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to model's expected input size
    img = img.resize((IMG_SIZE, IMG_SIZE))
    
    # Convert to numpy array and normalize
    img_array = np.array(img, dtype=np.float32) / 255.0
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def preprocess_image_from_path(image_path: str):
    """
    Preprocess an image file for GSDCNet model prediction
    
    Args:
        image_path: Path to image file
        
    Returns:
        numpy array ready for model.predict(), shape (1, 224, 224, 3)
    """
    img = Image.open(image_path)
    return preprocess_image_from_pil(img)


def parse_class_name(full_class_name: str):
    """
    Parse a class name like 'Tomato___Early_blight' into crop and disease
    
    Args:
        full_class_name: Class name in format 'Crop___Disease'
        
    Returns:
        tuple: (crop, disease)
    """
    parts = full_class_name.split('___')
    crop = parts[0] if len(parts) > 0 else 'Unknown'
    disease = parts[1] if len(parts) > 1 else 'Unknown'
    return crop, disease


def is_healthy(disease_name: str):
    """Check if a disease name indicates a healthy plant"""
    return 'healthy' in disease_name.lower()