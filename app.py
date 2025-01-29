# Importing essential libraries and modules

from flask import Flask, render_template, request, Markup
import numpy as np
import pandas as pd

import requests
import config
import pickle
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ==============================================================================================

# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------

# Loading plant disease classification model

disease_dic= ["No Stroke","Stroke"]



from model_predict  import pred_leaf_disease

# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)

# render home page


@ app.route('/')
def home():
    title = 'Brain Stroke Detection'
    return render_template('index.html', title=title)

# render crop recommendation form page

@app.route('/disease-predict', methods=['GET', 'POST'])
def disease_prediction():
    title = 'Brain Stroke Detection'

    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            return render_template('rust.html', title=title)

        # Process the uploaded file
        img = Image.open(file)
        img.save('output.png')

        # Make the prediction
        prediction = pred_leaf_disease("output.png")
        prediction = str(disease_dic[prediction])

        print("Prediction result:", prediction)

        # Define response based on prediction
        if prediction == "Stroke":
            precaution = "Stroke detected! Immediate action is required."
            details = {
                "treatment": "Seek emergency medical attention.",
                "cure": "Timely medical intervention and rehabilitation can improve outcomes.",
                "medication": "Common treatments include anticoagulants, thrombolytics, and blood pressure management.",
                "ayurvedic": "Consider herbs like Ashwagandha and Brahmi under a doctor's guidance.",
                "hospital": "Nearby hospital: City General Hospital, Emergency Unit.",
                "doctor": "Recommended Specialist: Dr. Jane Doe, Neurologist."
            }
        else:
            precaution = "Congratulations! No signs of stroke detected."
            details = {}

        # Render the result page with prediction and details
        return render_template('rust-result.html', prediction=prediction, precaution=precaution, details=details, title=title)

    # Default page rendering
    return render_template('rust.html', title=title)



# render disease prediction result page


# ===============================================================================================
if __name__ == '__main__':
    app.run(debug=True)
