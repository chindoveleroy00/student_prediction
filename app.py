from flask import Flask, render_template, request, redirect, url_for, flash, session, flash
import mysql.connector
from mysql.connector import Error
import joblib
import os
import pandas as pd
from xgboost import XGBRegressor

app = Flask(__name__)
app.secret_key = 'IUHDKNWLQJPOJDOWE982U30932'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'student_prediction',
    'port': '3306'

}

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Convert grade to GPA
def convert_grade_to_gpa(grade):
    grade_to_gpa = {
        'A': 4.0,
        'B': 3.0,
        'C': 2.0,
        'D': 1.0,
        'E': 0.7,
        'F': 0.0
    }
    return grade_to_gpa.get(grade.strip(), 0.0)

# Assign risk level based on CGPA
def assign_risk(cgpa):
    if cgpa >= 3.9:
        return 'Extremely Low Risk'
    elif cgpa >= 3.7:
        return 'Very Low Risk'
    elif cgpa >= 3.5:
        return 'Low Risk'
    elif cgpa >= 3.2:
        return 'Moderately Low Risk'
    elif cgpa >= 3.0:
        return 'Moderate Risk'
    elif cgpa >= 2.7:
        return 'Moderately High Risk'
    elif cgpa >= 2.5:
        return 'High Risk'
    elif cgpa >= 2.0:
        return 'Very High Risk'
    else:
        return 'Extremely High Risk'

# Prediction function
def single_prediction(age, gender, attendance, participation, course_grades):
    num_courses = len(course_grades)
    try:
        model_path = f'models/model_{num_courses}_courses.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)

            # Convert grades to GPA
            course_grades_gpa = [convert_grade_to_gpa(grade) for grade in course_grades]

            # Define the feature names used in training
            feature_names = ['Age', 'Gender', 'Attendance', 'Participation'] + [f'CS10{i+1}A' for i in range(num_courses)]

            # Create a DataFrame for the input features
            X_single_df = pd.DataFrame([[age, gender, attendance, participation] + course_grades_gpa], columns=feature_names)

            # Make a prediction using the model
            prediction = model.predict(X_single_df)
            return prediction[0]
        else:
            print(f"No model found for {num_courses} courses.")
            return None
    except Exception as e:
        print(f"Error in single prediction: {e}")
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/academic_staff_dashboard', methods=['GET', 'POST'])
def academic_staff_dashboard():
    print("academic_staff_dashboard route accessed")
    connection = create_connection()
    print("Connection created")
    cursor = connection.cursor(dictionary=True)
    print("Cursor created")

    cursor.execute("SELECT id, name FROM users WHERE user_type='Student'")
    print("Query executed")
    students = cursor.fetchall()
    print(f"Students fetched: {students}")

    cursor.close()
    print("Cursor closed")
    connection.close()
    print("Connection closed")

    if request.method == 'POST':
        print("POST request received")
        try:
            print("Trying to fetch data from form...")
            student_name = request.form['student_name']
            print(f"Student name: {student_name}")
            user_id = request.form['user_id']
            print(f"User ID: {user_id}")
            attendance = float(request.form['attendance'])
            print(f"Attendance: {attendance}")
            participation = float(request.form['participation'])
            print(f"Participation: {participation}")
            course_grades = request.form['course_grades'].split(',')
            print(f"Course grades: {course_grades}")
            age = int(request.form['age'])  # Convert to int
            print(f"Age: {age}")
            sex = request.form['gender']
            print(f"Sex: {sex}")

            # flash(str(age) + " " + sex + " " + str(attendance) + " " + str(participation) + " " + str(course_grades))
            print("Flash message created")

            gender = 1 if sex == 'Male' else 0
            print(f"Gender (Male=1, Female=0): {gender}")

            # Call prediction function
            predicted_gpa = float(single_prediction(age, gender, attendance, participation, course_grades))
            print(f"Predicted GPA: {predicted_gpa}")

            # flash(predicted_gpa)
            print("Flash message created")

            if predicted_gpa is not None:
                print("Predicted GPA is not None")
                risk_level = assign_risk(predicted_gpa)
                print(f"Risk level: {risk_level}")

                # Store/update the result in the database
                connection = create_connection()
                print("Connection created")
                cursor = connection.cursor()
                print("Cursor created")

                # Check if the record exists for the user_id and student_name
                cursor.execute("""
                    SELECT * FROM results WHERE user_id = %s AND student_name = %s
                """, (user_id, student_name))
                existing_record = cursor.fetchone()

                if existing_record:
                    # Update the existing record
                    cursor.execute("""
                        UPDATE results
                        SET grades = %s, predicted_cgpa = %s, risk_level = %s
                        WHERE user_id = %s AND student_name = %s
                    """, (','.join(course_grades), predicted_gpa, risk_level, user_id, student_name))
                    print("Record updated")
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO results (student_name, user_id, grades, predicted_cgpa, risk_level)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (student_name, user_id, ','.join(course_grades), predicted_gpa, risk_level))
                    print("New record inserted")

                connection.commit()
                print("Changes committed")
                cursor.close()
                print("Cursor closed")
                connection.close()
                print("Connection closed")

                return render_template('results.html', student_name=student_name, user_id=user_id, gpa=predicted_gpa, risk_level=risk_level)
            else:
                print("Predicted GPA is None")
                #  flash('Prediction failed. Please try again.', 'danger')
        except Exception as e:
            print(f"An error occurred: {e}")
            # flash(f'An error occurred: {e}', 'danger')

    print("Rendering academic_staff_dashboard.html")
    return render_template('academic_staff_dashboard.html', students=students)


@app.route('/intervention/<int:user_id>/<string:student_name>', methods=['GET', 'POST'])
def intervention(user_id, student_name):
    if request.method == 'POST':
        intervention_plan = request.form['intervention_plan']
        learning_objectives = request.form['learning_objectives']
        resources = request.form['resources']
        timeline = request.form['timeline']

        connection = create_connection()
        cursor = connection.cursor()

        # Update the results table with intervention plan and learning path
        cursor.execute("""
            UPDATE results
            SET intervention_plan = %s, learning_objectives = %s, recommended_resources = %s, timeline_milestones = %s
            WHERE user_id = %s AND student_name = %s
        """, (intervention_plan, learning_objectives, resources, timeline, user_id, student_name))

        connection.commit()
        cursor.close()
        connection.close()

        # flash('Intervention Plan and Learning Path submitted successfully!', 'success')
        return redirect(url_for('academic_staff_dashboard'))

    return render_template('intervention.html', student_name=student_name, user_id=user_id)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            name = request.form['name']
            surname = request.form['surname']
            email = request.form['email']
            gender = request.form['gender']
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm-password']
            user_type = request.form['user_type']
            student_id = request.form.get('student_id', None)

            if password != confirm_password:
                flash("Passwords do not match", "danger")
                return redirect(url_for('signup'))

            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO users (name, surname, email, gender, username, password, user_type, student_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, surname, email, gender, username, password, user_type, student_id))
                connection.commit()
                cursor.close()
                connection.close()
                flash("Signup successful! Please log in.", "success")
                return redirect(url_for('login'))
            else:
                flash("Database connection failed", "danger")
        except Error as e:
            if "1062" in str(e):
                flash("Username already exists. Please choose a different username.", "danger")
            else:
                flash("An error occurred during signup. Please try again.", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            connection = create_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT * FROM users WHERE username=%s AND password=%s
                """, (username, password))
                user = cursor.fetchone()
                cursor.close()
                connection.close()

                if user:
                    session['user_type'] = user['user_type']
                    session['user_id'] = user['id']  # Store user_id in session
                    session['student_name'] = user['name']  # Store name in session
                    flash("Login successful!", "success")
                    
                    if user['user_type'] == 'Academic Staff':
                        return redirect(url_for('academic_staff_dashboard'))
                    elif user['user_type'] == 'Data Analyst':
                        return redirect(url_for('data_analyst_dashboard'))
                    elif user['user_type'] == 'Administrator':
                        return redirect(url_for('administrator_dashboard'))
                    elif user['user_type'] == 'Student':
                        return redirect(url_for('student_dashboard'))  # Redirect to student dashboard
                else:
                    flash("Invalid credentials. Please try again.", "danger")
            else:
                flash("Database connection failed", "danger")
        except Exception as e:
            flash(f"An error occurred during login: {e}", "danger")

    return render_template('login.html')




@app.route('/data_analyst_dashboard')
def data_analyst_dashboard():
    return render_template('data_analyst_dashboard.html')

@app.route('/administrator_dashboard')
def administrator_dashboard():
    return render_template('administrator_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    user_id = session.get('user_id')  # Get user_id from session
    student_name = session.get('student_name')  # Get student_name from session

    if user_id is None:
        flash("You must be logged in to view this page.", "danger")
        return redirect(url_for('login'))

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch student results from the 'results' table based on user_id
    cursor.execute("""
        SELECT * FROM results WHERE user_id = %s AND student_name = %s
    """, (user_id, student_name))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    # Pass the result to the template
    return render_template('student_dashboard.html', student=result)


if __name__ == '__main__':
    app.run(debug=True)
