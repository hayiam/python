# Python Projects Collection
This repository contains three comprehensive Python applications for various application domains: medical system, internet cafe, and scientific tool for empirical function fitting.

## 📋 Project 1: Medical Information System
### Description
Medical organization management system with Tkinter GUI and PostgreSQL database.

### Functionality
Patient Management: CRUD operations for patient data

Doctor Management: Registration and maintenance of doctor information

Appointments: Creation and tracking of medical appointments

Medical Records: Electronic health record management

Reports: PDF report generation with Russian language support

Validation: Input data validation

### Technologies
Python 3.8+

Tkinter for GUI

PostgreSQL 12+

ReportLab for PDF generation

NumPy for calculations

Configure environment variables or modify connection parameters in database.py

Run the application: python app.py

## 📋 Project 2: Internet Cafe Management System
### Description
Accounting and management system for internet cafes with session tracking, tariff management, and financial reporting.

### Functionality
Session Management: Tracking computer usage time

Tariff System: Flexible pricing based on time of day

Receipts: Financial document generation

Analytics: Usage statistics and efficiency analysis

IP Address Validation: Network data validation

### Technologies
Python 3.8+

Tkinter for GUI

PostgreSQL 12+

Matplotlib for data visualization

## 📋 Project 3: Empirical Functions Fitting
### Description
Scientific application for fitting optimal mathematical models to experimental data using the least squares method.

### Functionality
Fitting 5 function types: Linear, quadratic, power, exponential, logarithmic

Model Comparison: Automatic quality comparison of fits

Visualization: Graphical representation of results

Interactive Input: Tabular data editor

Quality Metrics: R², RMSE, MAE and other indicators

Supported Models
Linear: y = ax + b

Quadratic: y = ax² + bx + c

Power: y = axᵇ

Exponential: y = aeᵇˣ

Logarithmic: y = a + b·ln(x)

Technologies
Python 3.8+

Tkinter for GUI

NumPy for calculations

SciPy for optimization

Matplotlib for graphs


## 🔧 Requirements
Python 3.8 or higher

PostgreSQL 12+ (for first two projects)

pip for dependency installation

Internet access for package installation

## 📝 Dependencies
Main dependencies:

psycopg2-binary - PostgreSQL interaction

numpy - mathematical calculations

matplotlib - graph plotting

scipy - scientific computing

reportlab - PDF generation

tkinter - graphical interface (usually included with Python)
