# Student Success Prediction System

## Overview
The Student Success Prediction System is a machine learning-powered application designed to help academic institutions like Zimbabwe Open University (ZOU) identify at-risk students early and provide targeted interventions. This system analyzes student performance data to predict academic success and recommend personalized learning paths.

## Key Features
- **Academic Performance Prediction**: Uses XGBoost models to predict student CGPA based on various factors
- **Risk Stratification**: Classifies students into risk categories from "Extremely Low Risk" to "Extremely High Risk"
- **Multiple Model Support**: Contains specialized models for different numbers of courses (1-40 courses)
- **Web Interface**: Provides dashboards for different user roles (Academic Staff, Data Analysts, Administrators, Students)
- **Intervention Planning**: Allows staff to create personalized intervention plans for at-risk students
- **Data Management**: Stores student records and predictions in MySQL database

## Technical Specifications
### Machine Learning
- **Algorithm**: XGBoost Regressor
- **Features Used**:
  - Demographic data (age, gender)
  - Academic metrics (attendance, participation)
  - Course grades (converted to GPA)
- **Model Training**: Separate models trained for different numbers of courses (1-40)
- **Evaluation Metric**: Mean Squared Error (MSE)

### Backend
- **Framework**: Flask
- **Database**: MySQL
- **Data Processing**:
  - Grade to GPA conversion
  - Label encoding for categorical variables
  - Feature engineering for different course counts

### Frontend
- **Templates**: HTML with Bootstrap
- **Forms**: Flask-WTF with comprehensive validation
- **User Roles**:
  - Academic Staff: Submit student data, view predictions, create interventions
  - Data Analysts: Access analytical dashboards
  - Administrators: System management
  - Students: View their own performance predictions

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up MySQL database:
   - Configure connection in `app.py`
   - Create 'student_prediction' database
   - Set up tables for users and results
4. Train models (optional):
   ```bash
   python train_bulk_test.py
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Usage
1. Access the web interface at `http://localhost:5000`
2. Login with appropriate credentials (different dashboards for different roles)
3. For academic staff:
   - Select student from dashboard
   - Enter academic data (attendance, participation, course grades)
   - Submit to view prediction and risk level
   - Create intervention plan if needed
4. For students:
   - View personal performance predictions
   - See recommended interventions

## Project Significance
This system addresses critical challenges at Zimbabwe Open University by:
- Enabling early identification of at-risk students
- Providing data-driven insights for academic support
- Offering personalized intervention recommendations
- Supporting diverse learning needs in open university settings
- Leveraging existing student data that was previously underutilized

## Future Enhancements
- Integration with university LMS systems
- Additional predictive models (dropout risk, course completion)
- Enhanced visualization dashboards
- Mobile application for student access
- Automated intervention recommendations
- Continuous model retraining with new student data

## License
[Specify license information here]

## Acknowledgments
Zimbabwe Open University for providing the academic context and data requirements that shaped this project's development. Special thanks to supervisor Mr. E. Thomu for guidance.