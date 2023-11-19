from flask import Flask, render_template, request, redirect, url_for,session
import pyrebase
import requests
import json
from io import BytesIO

app = Flask(__name__)

app.secret_key = 'qwerqwer'

# Firebase configuration
config = {
    'apiKey': "AIzaSyDKactLflnQCUHCeNfErPv2Uv3FeILhplw",
    'authDomain': "bus-time-prediction-20aba.firebaseapp.com",
    'databaseURL': "https://bus-time-prediction-20aba-default-rtdb.firebaseio.com",
    'projectId': "bus-time-prediction-20aba",
    'storageBucket': "bus-time-prediction-20aba.appspot.com",
    'messagingSenderId': "407313964038",
    'appId': "1:407313964038:web:343d1edbaac57ad0897787",
    'measurementId': "G-64R2GB440S",
}

# Initialize Firebase app
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
auth = firebase.auth()

def download_json_from_firebase():
    # Get download URL
    download_url = storage.child("data.json").get_url(None)

    # Download JSON file from Firebase Storage using requests
    response = requests.get(download_url)
    json_data = response.text

    # Parse the JSON string into a dictionary
    json_data_dict = json.loads(json_data)

    return json_data_dict

def download_json_from_firebase_time():
    # Get download URL
    download_url = storage.child("data_time.json").get_url(None)

    # Download JSON file from Firebase Storage using requests
    response = requests.get(download_url)
    json_data = response.text

    # Parse the JSON string into a dictionary
    json_data_dict = json.loads(json_data)

    return json_data_dict

@app.route('/')
def index():
    return render_template('login.html')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin_panel')
def show_json():
    json_data = download_json_from_firebase()
    return render_template('show.html', json_data=json_data)

@app.route('/feed_back')
def feed_back():
    return render_template('feed_back.html')


@app.route('/show_register')  # Changed the endpoint name
def show_register():
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            
            session['uid'] = user['localId']
            print("loging success")

            json_data = download_json_from_firebase_time()

    # Extract relevant fields for display
            bus_time_details = []
            for bus_number, bus_info in json_data['buses'].items():
                bus_time_details.append({
                    'bus_number': bus_number,
                    'driver_name': bus_info['driverName'],
                    'departures': bus_info['departures']
                })

            return render_template('home.html', bus_time_details=bus_time_details)
            
            
       
        except Exception as e:
            print("Error logging in:", e)
            return render_template('login_error.html')


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            print("User created successfully:", user)
            return redirect(url_for('index'))
        except Exception as e:
            print("Error creating user:", e)
            # Handle the error, you may want to render a registration error page
            return render_template('registration_error.html')


@app.route('/edit', methods=['POST'])
def edit_bus():
    bus_number = request.form.get('bus_number')
    json_data = download_json_from_firebase()
    bus_info = json_data['buses'][bus_number]
    return render_template('edit.html', bus_number=bus_number, bus_info=bus_info)

@app.route('/add_new')
def add_new_bus():
    return render_template('add_bus.html')


@app.route('/back_index')
def back_index():
    json_data = download_json_from_firebase_time()

    # Extract relevant fields for display
    bus_time_details = []
    for bus_number, bus_info in json_data['buses'].items():
        bus_time_details.append({
            'bus_number': bus_number,
            'driver_name': bus_info['driverName'],
            'departures': bus_info['departures']
        })
    return render_template('show.html', bus_time_details=bus_time_details)

@app.route('/update', methods=['POST'])
def update_bus():
    bus_number = request.form.get('bus_number')
    json_data = download_json_from_firebase()

    # Update only specific fields
    json_data['buses'][bus_number]['driverName'] = request.form.get('driverName')
    json_data['buses'][bus_number]['driverID'] = request.form.get('driverID')
    json_data['buses'][bus_number]['conductorName'] = request.form.get('conductorName')
    json_data['buses'][bus_number]['conductorID'] = request.form.get('conductorID')

    # Save the updated JSON data back to Firebase Storage
    bytes_io = BytesIO(json.dumps(json_data).encode())
    storage.child("data.json").put(bytes_io)

    return redirect(url_for('show_json'))

@app.route('/delete', methods=['POST'])
def delete_bus():
    bus_number = request.form.get('bus_number')
    json_data = download_json_from_firebase()

    # Check if the bus number exists before attempting to delete
    if bus_number in json_data['buses']:
        del json_data['buses'][bus_number]

        # Save the updated JSON data back to Firebase Storage
        bytes_io = BytesIO(json.dumps(json_data).encode())
        storage.child("data.json").put(bytes_io)

    return redirect(url_for('show_json'))


@app.route('/add', methods=['POST'])
def add_bus():
    new_bus_number = request.form.get('new_bus_number')
    new_chassi_number = request.form.get('new_chassi_number')
    new_driver_name = request.form.get('new_driver_name')
    new_driver_id = request.form.get('new_driver_id')
    new_conductor_name = request.form.get('new_conductor_name')
    new_conductor_id = request.form.get('new_conductor_id')
    new_starting_point = request.form.get('new_starting_point')
    new_end_point = request.form.get('new_end_point')

    # Download existing JSON data from Firebase
    json_data = download_json_from_firebase()

    # Add the new bus details to the dictionary
    json_data['buses'][new_bus_number] = {
        'busNumber': new_bus_number,
        'chassiNumber': new_chassi_number,
        'driverName': new_driver_name,
        'driverID': new_driver_id,
        'conductorName': new_conductor_name,
        'conductorID': new_conductor_id,
        'startingPoint': new_starting_point,
        'endPoint': new_end_point
    }

    # Save the updated JSON data back to Firebase Storage
    bytes_io = BytesIO(json.dumps(json_data).encode())
    storage.child("data.json").put(bytes_io)

    # Redirect to the show page to see the updated bus list
    return redirect(url_for('show_json'))

@app.route('/bus_details')
def bus_details():
    # Retrieve json_data
    json_data = download_json_from_firebase_time()

    # Extract relevant fields for display
    bus_details_list = []
    for bus_number, bus_info in json_data['buses'].items():
        bus_details_list.append({
            'bus_number': bus_number,
            'chassi_number': bus_info['chassiNumber'],
            'departures': bus_info['departures']
        })

    return render_template('bus_details.html', bus_details_list=bus_details_list)

if __name__ == '__main__':
    app.run(debug=True)
