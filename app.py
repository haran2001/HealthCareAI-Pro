import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from models import db, Patient, Appointment
import openai
import pandas as pd
import json
from sklearn.linear_model import LogisticRegression
import joblib
import plotly
import plotly.express as px
from dotenv import load_dotenv
from datetime import datetime, date, time
import os
from flask_mail import Mail, Message
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "data", "patients.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key_here"  # Replace with a secure key

# Flask-Mail configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"  # Example: Gmail SMTP server
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")  # Your email
app.config["MAIL_PASSWORD"] = os.getenv(
    "MAIL_PASSWORD"
)  # Your email password or app-specific password
app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_DEFAULT_SENDER"
)  # Default sender email
app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_DEFAULT_SENDER"
)  # Default sender email


mail = Mail(app)
db.init_app(app)

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()


# Function to send emails asynchronously
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f"Email sent to {msg.recipients}")
        except Exception as e:
            logger.error(f"Failed to send email to {msg.recipients}: {e}")


def send_email(subject, recipients, html_body, sender=None):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    if sender:
        msg.sender = sender  # Specify sender explicitly
    Thread(target=send_async_email, args=(app, msg)).start()


def send_appointment_email(patient, appointment):
    if not patient.email:
        logger.error(
            f"Cannot send appointment email, patient {patient.id} has no email."
        )
        return
    subject = "Appointment Confirmation - HealthCare Pro"
    recipients = [patient.email]
    html_body = render_template(
        "appointment_confirmation.html", patient=patient, appointment=appointment
    )
    sender = app.config.get("MAIL_DEFAULT_SENDER")  # Use default sender from config
    send_email(subject, recipients, html_body, sender=sender)


def schedule_email_reminder(patient, appointment, reminder_time):
    job_id = f"reminder_{appointment.id}"
    if not scheduler.get_job(job_id):
        scheduler.add_job(
            func=send_email_reminder,
            trigger="date",
            run_date=reminder_time,
            args=[patient, appointment],
            id=job_id,
        )
        logger.info(
            f"Scheduled reminder email for appointment ID {appointment.id} at {reminder_time}"
        )


def send_email_reminder(patient, appointment):
    if not patient.email:
        logger.error(f"Cannot send reminder email, patient {patient.id} has no email.")
        return
    subject = "Upcoming Appointment Reminder - HealthCare Pro"
    recipients = [patient.email]
    html_body = render_template(
        "appointment_reminder.html", patient=patient, appointment=appointment
    )
    sender = app.config.get("MAIL_DEFAULT_SENDER")  # Use default sender from config
    send_email(subject, recipients, html_body, sender=sender)


def create_tables():
    with app.app_context():
        db.create_all()


# Initialize the database tables
create_tables()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")  # Email Field
        age = request.form.get("age")
        gender = request.form.get("gender")
        medical_history = request.form.get("medical_history")
        lab_results = request.form.get("lab_results")
        wearable_data = request.form.get("wearable_data")

        print(
            f"Received data - Name: {name}, Email: {email}, Age: {age}, Gender: {gender}"
        )

        # Validate email
        if not email:
            return render_template("upload.html", error="Email is required.")
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            return render_template("upload.html", error=str(e))

        # Check if email already exists
        existing_patient = Patient.query.filter_by(email=email).first()
        if existing_patient:
            return render_template(
                "upload.html", error="A patient with this email already exists."
            )

        # Create new patient
        new_patient = Patient(
            name=name,
            email=email,
            age=age,
            gender=gender,
            medical_history=medical_history,
            lab_results=lab_results,
            wearable_data=wearable_data,
        )
        try:
            db.session.add(new_patient)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template(
                "upload.html", error="An error occurred while saving the patient data."
            )

        return render_template(
            "upload.html", success="Patient data uploaded successfully!"
        )

    return render_template("upload.html")


@app.route("/dashboard")
def dashboard():
    patients = Patient.query.all()
    # Example: Basic statistics
    total_patients = Patient.query.count()
    average_age = db.session.query(db.func.avg(Patient.age)).scalar()

    return render_template(
        "dashboard.html",
        patients=patients,
        total_patients=total_patients,
        average_age=average_age,
    )


@app.route("/analyze")
def analyze():
    patients = Patient.query.all()
    data = [
        {
            "id": p.id,
            "age": p.age,
            "gender": p.gender,
            "medical_history": p.medical_history,
            "lab_results": json.loads(p.lab_results) if p.lab_results else {},
            "wearable_data": json.loads(p.wearable_data) if p.wearable_data else {},
        }
        for p in patients
    ]

    df = pd.DataFrame(data)

    # Example analysis: Age distribution
    fig = px.histogram(df, x="age", nbins=20, title="Age Distribution of Patients")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("visualize.html", graphJSON=graphJSON)


@app.route("/report/<int:patient_id>")
def report(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Use OpenAI to generate a report
    prompt = f"Generate a comprehensive medical report for the following patient data with suggestions and diagnosis:\n\nName: {patient.name}\nAge: {patient.age}\nGender: {patient.gender}\nMedical History: {patient.medical_history}\nLab Results: {patient.lab_results}\nWearable Data: {patient.wearable_data}\n"
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a medical professional."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,  # Adjust based on desired response length
        temperature=0.2,
    )
    report_text = response["choices"][0]["message"]["content"].strip()

    return render_template("reports.html", patient=patient, report=report_text)


@app.route("/predict", methods=["GET"])
def predict():
    # Load ML model
    model = joblib.load("ml_model/model.pkl")
    patients = Patient.query.all()
    data = [
        {
            "age": p.age,
            "gender": 1 if p.gender.lower() == "male" else 0,  # Example encoding
            # Add more features as needed
        }
        for p in patients
    ]

    df = pd.DataFrame(data)
    predictions = model.predict(df)
    df["risk"] = predictions

    # Visualization
    fig = px.bar(df, x=df.index, y="risk", title="Predicted Health Risk per Patient")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("visualize.html", graphJSON=graphJSON)


@app.route("/chat_interface")
def chat_interface():
    return render_template("chat.html")


# Chat Route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        appointment_booked = False
        user_message = request.json.get("message")
        patient_id = session.get("patient_id")  # Ensure patient_id is stored in session
        print(f"{user_message}")
        if not patient_id:
            # Optionally, handle cases where no patient is in session
            return jsonify(
                {"reply": "No patient session found. Please upload patient data first."}
            )

        patient = Patient.query.get(patient_id)

        if not patient:
            return jsonify(
                {"reply": "Patient not found. Please upload patient data first."}
            )

        if not patient.email:
            return jsonify(
                {
                    "reply": "Patient email not found. Please update patient data with a valid email."
                }
            )

        # Initialize conversation state if not present
        if "conversation_state" not in session:
            session["conversation_state"] = {
                "step": "init",
                "provider": None,
                "date": None,
                "time": None,
                "reason": None,
            }

        state = session["conversation_state"]
        step = state["step"]

        if step == "init":
            reply = "Sure, I can help you book an appointment. Which healthcare provider would you like to see?"
            state["step"] = "awaiting_provider"

        elif step == "awaiting_provider":
            state["provider"] = user_message
            reply = f"Great. What date would you like to schedule the appointment for? Please provide a date in YYYY-MM-DD format."
            state["step"] = "awaiting_date"

        elif step == "awaiting_date":
            try:
                appointment_date = datetime.strptime(user_message, "%Y-%m-%d").date()
                state["date"] = user_message
                reply = "What time works best for you on that day? Please provide time in HH:MM format (24-hour)."
                state["step"] = "awaiting_time"
            except ValueError:
                reply = "I'm sorry, I didn't understand the date format. Please provide the date in YYYY-MM-DD format."

        elif step == "awaiting_time":
            try:
                appointment_time = datetime.strptime(user_message, "%H:%M").time()
                state["time"] = user_message
                reply = "What's the reason for your visit?"
                state["step"] = "awaiting_reason"
            except ValueError:
                reply = "I'm sorry, I didn't understand the time format. Please provide the time in HH:MM format (24-hour)."

        elif step == "awaiting_reason":
            state["reason"] = user_message
            provider = state["provider"]
            date_str = state["date"]
            time_str = state["time"]
            reason = state["reason"]

            # Validate and book the appointment
            try:
                appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                appointment_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                reply = "There was an error with the date or time format. Please try booking the appointment again."
                session.pop("conversation_state", None)
                return jsonify({"reply": reply})

            # Check availability
            existing_appointment = Appointment.query.filter_by(
                provider=provider, date=appointment_date, time=appointment_time
            ).first()
            if existing_appointment:
                reply = "I'm sorry, that time slot is already booked. Would you like to choose a different time?"
                state["step"] = "awaiting_time"
            else:
                # Book the appointment
                new_appointment = Appointment(
                    patient_id=patient.id,
                    provider=provider,
                    date=appointment_date,
                    time=appointment_time,
                    reason=reason,
                )
                db.session.add(new_appointment)
                db.session.commit()
                reply = f"Your appointment with {provider} on {date_str} at {time_str} for {reason} has been booked successfully."
                session.pop("conversation_state", None)  # Reset conversation
                appointment_booked = True

                # Send Immediate Confirmation Email
                send_appointment_email(patient, new_appointment)

                # Schedule Reminder Email (e.g., 1 day before the appointment)
                reminder_datetime = datetime.combine(
                    appointment_date, appointment_time
                ) - timedelta(days=1)
                if reminder_datetime > datetime.now():
                    schedule_email_reminder(patient, new_appointment, reminder_datetime)

        else:
            reply = "I'm here to help you book an appointment. Let's get started."

        session["conversation_state"] = state  # Update the session

        return jsonify({"reply": reply, "appointment_booked": appointment_booked})

    except Exception as e:
        logger.error(f"Error in /chat route: {e}")
        return (
            jsonify({"reply": "An unexpected error occurred. Please try again later."}),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
