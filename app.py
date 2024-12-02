from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import plotly
import plotly.express as px
import json
import pickle
import sqlite3
import numpy as np

app = Flask(__name__)
app.secret_key = 'd4f1c3e42b9a6c8420fe6d44b8c67e18'  # Make sure this key is kept secret


# Load your trained model
try:
    with open(r"C:\Users\user\Downloads\NEW1\NEW1\groundwater_model.pkl", 'rb') as file:
        model = pickle.load(file)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load the scaler used for standardization during training
try:
    with open(r"C:\Users\user\Downloads\NEW1\NEW1\scaler.pkl", 'rb') as file:
        scaler = pickle.load(file)
    print("Scaler loaded successfully!")
except Exception as e:
    print(f"Error loading scaler: {e}")
    scaler = None
    
# Predict groundwater levels
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if not model or not scaler:
        flash("Error: AI model or scaler could not be loaded.", 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            # Parse input parameters from the form
            input_params = [
                'temperature', 'relative_humidity', 'heat_index', 'wind_speed',
                'wind_direction', 'precipitation', 'sea_level_pressure', 'latitude',
                'longitude', 'relative_humidity_percentage', 'population_density',
                'recharge_coefficient', 'recharge_rate', 'abstraction_urban',
                'abstraction_green', 'average_abstraction', 'surface_runoff',
                'soil_relative_erodibility', 'soil_moisture', 'evaporation_transpiration',
                'permeability', 'hydraulic_conductivity', 'discharge_rate'
            ]
            
            # Retrieve and process all parameters
            inputs = []
            for param in input_params:
                value = float(request.form.get(param))
                inputs.append(value)
            
            # Standardize the input data using the loaded scaler
            standardized_data = scaler.transform([inputs])
            
            # Print the standardized values for debugging
            print("Standardized Input Values:", standardized_data)

            # Convert to numpy array and make prediction
            prediction = model.predict(standardized_data)[0]

            # Print the prediction for debugging
            print("Model Prediction (Standardized Value):", prediction)

            # Denormalize the output if needed
            target_mean = 12.233599290780141  # Replace with your actual target mean
            target_std = 3.631995326328184  # Replace with your actual target std
            original_value = (prediction * target_std) + target_mean
            print("Original Value (Denormalized):", original_value)

            # Insert the input data and prediction into the database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO predictions (
                                temperature, relative_humidity, heat_index, wind_speed,
                                wind_direction, precipitation, sea_level_pressure, latitude,
                                longitude, relative_humidity_percentage, population_density,
                                recharge_coefficient, recharge_rate, abstraction_urban,
                                abstraction_green, average_abstraction, surface_runoff,
                                soil_relative_erodibility, soil_moisture, evaporation_transpiration,
                                permeability, hydraulic_conductivity, discharge_rate, predicted_value)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           tuple(inputs) + (original_value,))
            conn.commit()
            conn.close()

            # Render the result
            return render_template('predict_result.html', prediction=original_value)
        except Exception as e:
            flash(f"Error in prediction: {e}", 'danger')
            return redirect(url_for('predict'))
    
    # Render the input form
    return render_template('predict_form.html')


try:
    data = pd.read_csv(r"C:\Users\user\Downloads\NEW1\NEW1\cleaned_file.csv")
    print("Dataset loaded successfully!")
except Exception as e:
    print(f"Error loading dataset: {e}")
    data = None

# Function to create a filtered map
def create_map(filtered_data):
    try:
        fig = px.scatter_mapbox(
            filtered_data,
            lat="Latitude",
            lon="Longitude",
            hover_name="Village",
            hover_data={
                "State_Name_With_LGD_Code": True,
                "Pre-monsoon_2022 (meters below ground level)": True,
                "Post-monsoon_2022 (meters below ground level)": True
            },
            color="Pre-monsoon_2022 (meters below ground level)",  # Color by groundwater level
            size_max=15,
            zoom=6,
            title="Groundwater Levels"
        )
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creating map: {e}")
        return None

# Primary Route
@app.route('/')
def primary():
    return render_template('primary.html')

@app.route('/about')
def about():
    # Define team members with their photo, role, and skills
    team_members = [
        {
            "name": "Moinak Chatterjee",
            "role": "Lead Developer",
            "photo": "static/images/moinak.jpg",
            "skills": ["Leadership", "FullStack Developer", "UI/UX Design"]
        },
        {
            "name": "Subhankar Ghosh",
            "role": "Android Developer",
            "photo": "static/images/subhankar.jpg",
            "skills": ["Android", "Data Analysis", "Canva"]
        },
        {
            "name": "Ankita Pal",
            "role": "Ml Engineer",
            "photo": "static/images/ankita.jpg",
            "skills": ["Data Analysis", "Machine Learning", "Python"]
        },
        {
            "name": "Bittu Bera",
            "role": "Ml Engineer",
            "photo": "static/images/bittu.jpg",
            "skills": ["Python", "Machine Learning", "Excel"]
        },
        {
            "name": "Champak Ray",
            "role": "Ml Engineer",
            "photo": "static/images/champak.jpg",
            "skills": ["Powerpoint", "SQL", "Python"]
        },
        {
            "name": "Aritra Das",
            "role": "Ml Engineer",
            "photo": "static/images/aritra.jpg",
            "skills": ["Data Analysis", "Machine Learning", "Python"]
        }
    ]

    return render_template('about.html', team_members=team_members)

# Route for the Contact Us page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Here, you can handle form submission (e.g., save to database or send email)
        # For now, we'll just flash a success message
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# Tracker Route
@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    global data

    if data is None:
        return "Error: Dataset could not be loaded."

    # Default is full dataset
    filtered_data = data

    # Handle user input
    if request.method == 'POST':
        state_filter = request.form.get('state')
        village_filter = request.form.get('village')

        # Apply filters
        if state_filter:
            filtered_data = filtered_data[filtered_data['State_Name_With_LGD_Code'].str.contains(state_filter, case=False, na=False)]
        if village_filter:
            filtered_data = filtered_data[filtered_data['Village'].str.contains(village_filter, case=False, na=False)]

    map_json = create_map(filtered_data)
    if map_json is None:
        return "Error: Map could not be generated."

    return render_template('tracker.html', map_json=map_json)


# Ensure init_db() is called before running the app
import sqlite3

# Function to initialize the database with both user and prediction tables
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL)''')

    # Create predictions table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        temperature REAL,
                        relative_humidity REAL,
                        heat_index REAL,
                        wind_speed REAL,
                        wind_direction REAL,
                        precipitation REAL,
                        sea_level_pressure REAL,
                        latitude REAL,
                        longitude REAL,
                        relative_humidity_percentage REAL,
                        population_density REAL,
                        recharge_coefficient REAL,
                        recharge_rate REAL,
                        abstraction_urban REAL,
                        abstraction_green REAL,
                        average_abstraction REAL,
                        surface_runoff REAL,
                        soil_relative_erodibility REAL,
                        soil_moisture REAL,
                        evaporation_transpiration REAL,
                        permeability REAL,
                        hydraulic_conductivity REAL,
                        discharge_rate REAL,
                        predicted_value REAL)''')

    conn.commit()
    conn.close()

# Call init_db() when starting the app to ensure both tables are created
init_db()


# Sign Up Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert user into the database
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                           (username, hashed_password, email))
            conn.commit()
            conn.close()
            flash("Signup successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting user: {e}")  # Debug output for errors
            flash("Username or Email already exists. Please try again.", "danger")

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check credentials
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            stored_password = user[2]  # Assuming the password is the 3rd column
            if check_password_hash(stored_password, password):  # Compare hashed passwords
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))  # Change to the appropriate route after login
            else:
                flash("Invalid email or password. Please try again.", "danger")
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

# Dashboard Route (For example purposes)
@app.route('/dashboard')
def dashboard():
    #return "Welcome to the dashboard!"
    return render_template('index.html')

@app.route('/')
def home():
    return render_template('visualization.html')

@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    plotType = request.form.get('plotType')

    # Dummy data for charts
    prediction_values = [20, 30, 40, 50, 60]
    precipitation_data = [10, 20, 15, 25, 18, 22, 30]
    data = [[30, 65], [32, 60], [28, 70], [29, 68], [33, 62]]
    seasonal_data = [25, 40, 55, 35]

    return render_template(
        'visualization.html',
        plotType=plotType,
        prediction_values=prediction_values,
        precipitation_data=precipitation_data,
        data=data,
        seasonal_data=seasonal_data
    )


if __name__ == '__main__':
    app.run(debug=True)
