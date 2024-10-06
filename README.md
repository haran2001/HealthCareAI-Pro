# HealthCare Pro

![HealthCareAI Pro Logo](static/images/logo.png)

HealthCare Pro is a comprehensive web application designed to streamline patient data management, data visualization, report generation, and appointment booking in a hospital setting. Leveraging modern technologies like Flask, Bootstrap 5, and Plotly, HealthCare Pro offers an intuitive and efficient platform for healthcare professionals to enhance patient care and administrative tasks.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

1. **Patient Data Upload**
   - Upload and manage patient information, including personal details, medical history, lab results, and wearable data.
2. **Medical Report Generation**
   - Create detailed medical reports for individual patients with options to print or download.
3. **Dashboard**
   - Overview of key statistics such as total patients, average age, and a comprehensive patient list with actionable options.
4. **Appointment Booking Assistant**
   - AI-powered chat interface to assist patients in booking appointments seamlessly.
5. **Responsive Design**
   - Fully responsive and mobile-friendly interface using Bootstrap 5.
6. **Accessibility**
   - Designed with accessibility in mind, ensuring usability for all users.
7. **Data Visualization (WIP)**
   - Generate interactive graphs and charts to visualize patient data using Plotly.

## Technologies Used

- **Backend:**
  - [Flask](https://flask.palletsprojects.com/) - A lightweight WSGI web application framework.
  - [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) - SQL toolkit and Object Relational Mapper.
  - [Flask-WTF](https://flask-wtf.readthedocs.io/) - Simple integration of Flask and WTForms.
  - [Flask-SocketIO](https://flask-socketio.readthedocs.io/) - SocketIO integration for Flask applications.
- **Frontend:**
  - [Bootstrap 5](https://getbootstrap.com/) - CSS framework for responsive design.
  - [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon library for Bootstrap.
  - [Plotly](https://plotly.com/python/) - Interactive graphing library.
- **Database:**
  - [SQLite](https://www.sqlite.org/index.html) - Lightweight disk-based database.
- **Others:**
  - [Jinja2](https://jinja.palletsprojects.com/) - Templating engine for Python.

## Installation

### Prerequisites

- [Python 3.7+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/haran2001/HealthCareAI-Pro.git
   ```

2. **Change directory**

   ```
   cd HealthCareAI-Pro
   ```

3. **Install Packages**
   ```
   pip install -r requirements.txt
   ```
4. **Run app**
   ```
   python app.py
   ```
