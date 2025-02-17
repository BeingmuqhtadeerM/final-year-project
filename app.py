from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired
from model_predict import pred_leaf_disease
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'

# Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

disease_dic = ["No Stroke", "Stroke"]

# Patient Form
class PatientForm(FlaskForm):
    name = StringField('Full Name', validators=[InputRequired()])
    age = StringField('Age', validators=[InputRequired()])
    gender = StringField('Gender', validators=[InputRequired()])
    contact = StringField('Contact Number', validators=[InputRequired()])
    address = TextAreaField('Address', validators=[InputRequired()])
    medical_history = TextAreaField('Medical History')
    submit = SubmitField('Continue to Scan Upload')

# PDF Report Generator with Confidence
# def generate_pdf_report(patient_data, image_path, clinical_details, output_filename):
#     try:
#         c = canvas.Canvas(output_filename, pagesize=letter)
        
#         # Patient Information
#         c.setFont("Helvetica-Bold", 16)
#         c.drawString(100, 750, "Patient Stroke Detection Report")
#         c.setFont("Helvetica", 12)
#         y = 720
#         c.drawString(100, y, f"Name: {patient_data.get('name', '')}")
#         c.drawString(100, y-20, f"Age: {patient_data.get('age', '')}")
#         c.drawString(100, y-40, f"Gender: {patient_data.get('gender', '')}")
#         c.drawString(100, y-60, f"Contact: {patient_data.get('contact', '')}")
        
#         # Medical Image
#         c.drawImage(image_path, 100, 400, width=400, height=300)
        
#         # Diagnosis and Treatment
#         y = 380
#         c.setFont("Helvetica-Bold", 14)
#         c.drawString(100, y, "Diagnosis: STROKE DETECTED")
#         y -= 30
#         c.drawString(100, y, "Treatment Plan:")
#         y -= 25
        
#         c.setFont("Helvetica", 12)
#         for key, value in clinical_details.items():
#             if key not in ['Medical History']:
#                 c.drawString(100, y, f"{key}: {value}")
#                 y -= 20
        
#         # Add confidence information
#         c.setFont("Helvetica-Bold", 12)
#         confidence = clinical_details.get("Model Confidence", "N/A")
#         c.drawString(100, 320, f"Model Confidence: {confidence}")
        
#         c.save()
#         return True
#     except Exception as e:
#         print(f"PDF Generation Error: {str(e)}")
#         return False

def generate_pdf_report(patient_data, image_path, clinical_details, output_filename):
    try:
        c = canvas.Canvas(output_filename, pagesize=letter)
        
        # Set initial positions
        left_margin = 100
        right_margin = 500
        top_margin = 750
        line_height = 20
        section_spacing = 30
        
        # Patient Information Section
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_margin, top_margin, "Patient Stroke Detection Report")
        
        # Patient Details
        c.setFont("Helvetica", 12)
        y_position = top_margin - line_height
        details = [
            f"Name: {patient_data.get('name', '')}",
            f"Age: {patient_data.get('age', '')}",
            f"Gender: {patient_data.get('gender', '')}",
            f"Contact: {patient_data.get('contact', '')}"
        ]
        
        for detail in details:
            c.drawString(left_margin, y_position, detail)
            y_position -= line_height
        
        # Add spacing before image
        y_position -= section_spacing
        
        # Medical Image
        img_width = 400
        img_height = 300
        c.drawImage(image_path, left_margin, y_position - img_height, 
                   width=img_width, height=img_height)
        
        # Add spacing after image
        y_position -= (img_height + section_spacing)
        
        # Diagnosis Section
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, y_position, "Diagnosis: STROKE DETECTED")
        y_position -= line_height
        
        # Treatment Plan Section
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, y_position, "Treatment Plan:")
        y_position -= line_height
        
        # Treatment Details
        c.setFont("Helvetica", 12)
        treatment_details = [
            f"Treatment: {clinical_details.get('Treatment', '')}",
            f"Cure: {clinical_details.get('Cure', '')}",
            f"Medication: {clinical_details.get('Medication', '')}",
            f"Ayurvedic Options: {clinical_details.get('Ayurvedic Options', '')}",
            f"Recommended Hospital: {clinical_details.get('Recommended Hospital', '')}",
            f"Suggested Doctor: {clinical_details.get('Suggested Doctor', '')}",
            f"Model Confidence: {clinical_details.get('Model Confidence', '')}"
        ]
        
        for detail in treatment_details:
            if y_position < 100:  # Check for page end
                c.showPage()
                y_position = top_margin
                c.setFont("Helvetica", 12)
            
            c.drawString(left_margin, y_position, detail)
            y_position -= line_height
        
        c.save()
        return True
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        return False

# User Authentication System
class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'admin': {'password': 'password'}}

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if username in users and password == users[username]['password']:
            user = User(username)
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/patient-details', methods=['GET', 'POST'])
@login_required
def patient_details():
    form = PatientForm()
    if form.validate_on_submit():
        session['patient_data'] = {
            'name': form.name.data,
            'age': form.age.data,
            'gender': form.gender.data,
            'contact': form.contact.data,
            'address': form.address.data,
            'medical_history': form.medical_history.data
        }
        return redirect(url_for('disease_prediction'))
    return render_template('patient-form.html', form=form, title='Patient Details')

@app.route('/disease-predict', methods=['GET', 'POST'])
@login_required
def disease_prediction():
    if 'patient_data' not in session:
        return redirect(url_for('patient_details'))
    
    title = 'Brain Stroke Detection'
    prediction = None
    confidence = None
    precaution = ""
    details = {}
    report_filename = None

    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('No file uploaded', 'warning')
            return render_template('rust.html', title=title)
            
        try:
            # Process image
            img = Image.open(file)
            img_path = os.path.join('static', 'output.png')
            img.save(img_path)
            
            # Get prediction and confidence
            pred_class, confidence = pred_leaf_disease(img_path)
            prediction = str(disease_dic[pred_class])

            if prediction == "Stroke":
                precaution = f"Stroke detected with {confidence}% confidence! Immediate action required."
                details = {
                    "Treatment": "Seek emergency medical attention.",
                    "Cure": "Timely intervention and rehabilitation needed.",
                    "Medication": "Anticoagulants, thrombolytics, BP management.",
                    "Ayurvedic Options": "Ashwagandha, Brahmi (with doctor consultation).",
                    "Recommended Hospital": "City General Hospital, Emergency Unit",
                    "Suggested Doctor": "Dr. Jane Doe, Neurologist",
                    "Medical History": session['patient_data']['medical_history'],
                    "Model Confidence": f"{confidence}%"
                }
                
                # Generate report
                report_filename = os.path.join('static', 'patient_report.pdf')
                if generate_pdf_report(session.pop('patient_data'), img_path, details, report_filename):
                    return render_template('rust-result.html',
                                        prediction=prediction,
                                        confidence=confidence,
                                        precaution=precaution,
                                        details=details,
                                        report_filename=report_filename,
                                        title=title)
                else:
                    flash('Error generating PDF report', 'danger')
            else:
                precaution = f"No stroke detected (Confidence: {confidence}%). Maintain healthy lifestyle."
                session.pop('patient_data', None)
                return render_template('rust-result.html',
                                    prediction=prediction,
                                    confidence=confidence,
                                    precaution=precaution,
                                    details={},
                                    title=title)
            
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')
            return render_template('rust.html', title=title)
    
    return render_template('rust.html', title=title)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('index.html', title='Brain Stroke Detection')

@app.route('/download-report/<path:filename>')
@login_required
def download_report(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash('Error downloading report: File not found', 'danger')
        return redirect(url_for('disease_prediction'))

@app.route('/rust')
@login_required
def rust():
    return render_template('rust.html')

if __name__ == '__main__':
    app.run(debug=True)