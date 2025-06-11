import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os
import joblib

# Grade to GPA conversion function
def convert_grade_to_gpa(grade):
    grade_to_gpa = {
        'A': 4.0,
        'B': 3.0,
        'C': 2.0,
        'D': 1.0,
        'E': 0.7,
        'F': 0.0
    }
    return grade_to_gpa.get(grade, 0.0)

# Load and preprocess the dataset
def load_and_preprocess_data(file_path):
    print("Loading dataset...")
    try:
        df = pd.read_csv(file_path)
        print("Dataset loaded successfully.")

        # Handling categorical variables (Gender)
        label_encoder = LabelEncoder()
        df['Gender'] = label_encoder.fit_transform(df['Gender'])

        # Convert course grades to GPA
        course_columns = [col for col in df.columns if col.startswith('CS')]
        for col in course_columns:
            df[col] = df[col].apply(convert_grade_to_gpa)

        print("Data preprocessing completed.")
        return df
    except Exception as e:
        print(f"Error in loading or preprocessing data: {e}")
        return None

# Function to generate feature and label sets based on the number of courses
def generate_features_labels(df, num_courses):
    print(f"Generating features and labels for {num_courses} courses...")
    try:
        columns = ['Age', 'Gender', 'Attendance', 'Participation'] + [f'CS10{i}A' for i in range(1, num_courses + 1)]
        X = df[columns]
        y = df['CGPA']
        return X, y
    except Exception as e:
        print(f"Error in generating features and labels: {e}")
        return None, None

# Train a model for a specific number of courses
def train_model(X_train, y_train, num_courses):
    print(f"Training model for {num_courses} courses...")
    try:
        model = XGBRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        print(f"Model for {num_courses} courses trained successfully.")
        return model
    except Exception as e:
        print(f"Error in training model for {num_courses} courses: {e}")
        return None

# Test the model and return the error
def test_model(model, X_test, y_test, num_courses):
    print(f"Testing model for {num_courses} courses...")
    try:
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model for {num_courses} courses tested successfully. MSE: {mse}")
        return mse
    except Exception as e:
        print(f"Error in testing model for {num_courses} courses: {e}")
        return None

def convert_gpa_to_grade(gpa):
    if gpa >= 3.85:
        return 'A'
    elif gpa >= 2.85:
        return 'B'
    elif gpa >= 1.85:
        return 'C'
    elif gpa >= 1.0:
        return 'D'
    elif gpa >= 0.7:
        return 'E'
    else:
        return 'F'

def bulk_train_test(df, max_courses=40):
    print("Starting bulk training and testing...")
    results = {}
    
    # Create a directory for saving predictions
    os.makedirs('predictions', exist_ok=True)
    
    for i in range(1, max_courses + 1):
        X, y = generate_features_labels(df, i)
        if X is not None and y is not None:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = train_model(X_train, y_train, i)
            if model:
                mse = test_model(model, X_test, y_test, i)
                results[i] = mse
                
                # Save the model
                model_path = f'models/model_{i}_courses.pkl'
                os.makedirs('models', exist_ok=True)
                joblib.dump(model, model_path)
                print(f"Model for {i} courses saved at {model_path}.")

                # Predict on the test data
                predictions = model.predict(X_test)
                
                # Prepare the DataFrame to save
                feature_names = ['Age', 'Gender', 'Attendance', 'Participation'] + [f'CS10{j}A' for j in range(1, i + 1)]
                result_df = pd.DataFrame(X_test, columns=feature_names)
                result_df['Actual_CGPA'] = y_test
                result_df['Predicted_CGPA'] = predictions
                
                # Convert GPA values back to grades in the course columns
                for j in range(1, i + 1):
                    course_column = f'CS10{j}A'
                    result_df[course_column] = result_df[course_column].apply(convert_gpa_to_grade)
                
                # Save the predictions to a CSV file
                prediction_file_path = f'predictions/predictions_{i}_courses.csv'
                result_df.to_csv(prediction_file_path, index=False)
                print(f"Predictions for {i} courses saved to {prediction_file_path}.")

    print("Bulk training and testing completed.")
    return results

# Main execution
if __name__ == "__main__":
    file_path = 'student_dataset.csv'
    df = load_and_preprocess_data(file_path)
    if df is not None:
        max_courses = 40
        results = bulk_train_test(df, max_courses=max_courses)
        print(f"Results: {results}")