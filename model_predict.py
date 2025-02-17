#import cv2
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from PIL import Image

# Load model
loaded_model_imageNet = load_model("Brain_stroke_detection.h5")

def pred_leaf_disease(image_path):
    # Image preprocessing
    img = image.load_img(image_path, target_size=(100, 100))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    
    # Make prediction
    prediction = loaded_model_imageNet.predict(x)
    
    # Get class index and confidence
    probabilities = prediction[0]
    class_index = np.argmax(probabilities)
    confidence = np.max(probabilities) * 100  # Convert to percentage
    
    # Maintain original print functionality
    int_percentages = (probabilities * 100).astype('int')
    print("Class probabilities (int percentages):", int_percentages)
    print("Max confidence:", int_percentages.max())
    
    return class_index, round(confidence, 2)  # Return both index and float confidence

# Example usage:
# class_idx, confidence = pred_leaf_disease('brain_scan.jpg')
# print(f"Predicted class index: {class_idx}, Confidence: {confidence}%")