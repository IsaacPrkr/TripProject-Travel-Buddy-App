import requests
from flask import Flask, request, jsonify# importing needed modules
import json

BASE_URL = "https://localhost:5000" # Flask server base URL
WORLD_WEATHER_API_URL = "https://api.worldweatheronline.com/premium/v1/weather.ashx"
WORLD_WEATHER_API_KEY = "8e3584cbdc8346079c5230106230911" # importing API key for external service

app = Flask(__name__)

#   Creating the Create User REST method to allow users to create accounts with password protection - each account is stored in the users.json file...
@app.route('/create_user', methods=['POST']) # Will be triggered when a HTTP post request is sent to this endpoint
def create_user():
    data = request.json # Retrieve JSON data
    name = data.get('name')
    password = data.get('password')

    user_id = generate_unique_user_id_internal() # Generate the account an unique User ID with the function built into the orchestrator service using the random API


    new_user = {
        "userID": user_id,
        "name": name,   #   Creates a dictionary with user id, name, password
        "password": password
    }

    with open('users.json', 'r+') as file:  #   Open file in read and write mode
        try:
            user_data = json.load(file) #   Load JSON user data
        except json.JSONDecodeError:
            user_data = [] # create user data list

        user_data.append(new_user) # adds user to user data list
        file.seek(0)
        json.dump(user_data, file, indent=4) # writes the user data in JSON format to the users.json file

    return jsonify(user=new_user) # responds the details of the account created

#   Creating REST Method for logging in the user
@app.route('/login', methods=['POST'])  #   Define route for handling POST requests for the login endpoint
def login_user():
    data = request.get_json()   #   Retrieve the JSON data from the POST request

    if 'name' in data and 'password' in data:
        name = data['name']     #   Check if name and password exits in the data, extract the name and password
        password = data['password']

        with open('users.json', 'r') as file:   #   Open users.json file in read
            users = json.load(file) #   Read file

        for user in users:
            if user['name'] == name and user['password'] == password: #   Check for matching name and password
                return jsonify({'message': 'Login successful!', 'user': user}), 200

        return jsonify({'message': 'Incorrect username or password. Please try again.'}), 401
                                                                                                    #   Handling errors or misinputs
    return jsonify({'message': 'Invalid request. Please provide both name and password.'}), 400


#Creating querying for new trips REST method
@app.route('/query_for_new_trips', methods=['POST'])    #   Defining route as POST to handle requests to the endpoint
def query_for_new_trips():

    with open('query_trips.json', 'r') as file: #   Open file in read mode
        query_trips = json.load(file)

    data = request.json #   Retrieve JSON data
    location = data.get('location') #   Find the location from the JSON data
    matching_trip = [trip for trip in query_trips if trip['location'] == location]
    trip_description = {                                                                        #   Filter through query_trips.json to match the location and then output the Trips associated with that location
        trip['id']: [trip['Trip1'], trip['Trip2'], trip['Trip3']] for trip in matching_trip
    }
    return jsonify(trip_description=trip_description)   #   Return JSON response of description of trips in location

#   Creating proposing new trips REST method
@app.route('/propose_new_trips', methods=['POST'])  #   Route defined as POST
def propose_new_trips():
    data = request.json
    userID = data.get('userID')
    location = data.get('location')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    details = data.get('details', '')



    parametersStart = {
        "key": WORLD_WEATHER_API_KEY,
        "q": location,
        "format": "json",
        "date": start_date
    }
    parametersEnd = {                      #   Constructing the parameters for making API requests
        "key": WORLD_WEATHER_API_KEY,
        "q": location,
        "format": "json",
        "date": end_date
    }

    response_start = requests.get(WORLD_WEATHER_API_URL, params=parametersStart)   #   Sending API requests for the weather conditions
    response_end = requests.get(WORLD_WEATHER_API_URL, params=parametersEnd)

    if response_start.status_code == 200 and response_end.status_code == 200:   #   If the requests are successful process the data
        weather_data_start = response_start.json()
        weather_data_end = response_end.json()

        temperature_start = weather_data_start['data']['weather'][0]['maxtempC'] if 'maxtempC' in weather_data_start['data']['weather'][0] else "Temperature data unavailable"
        temperature_end = weather_data_end['data']['weather'][0]['maxtempC'] if 'maxtempC' in weather_data_end['data']['weather'][0] else "Temperature data unavailable"

        weather_description_start = weather_data_start['data']['weather'][0]['hourly'][0]['weatherDesc'][0]['value']

    else:
        temperature_start = "Error fetching temperature"
        temperature_end = "Error fetching temperature"  #   Error handling
        weather_description_start = "Error fetching weather"

    tripID = generate_unique_trip_id_internal()
    details = data.get('details', '')

    new_trip = {
        "tripID": tripID,
        "userID": userID,
        "location": location,
        "start_date": start_date,    #   Creating trip object
        "end_date": end_date,
        "temperature_start": temperature_start,
        "weather_start": weather_description_start,
        "details": details
    }
    with open('proposed_trips.json', 'r') as file:
        try:
            existing_trips = json.load(file)    #   Open the proposed trips .json file as read and write
        except json.JSONDecodeError:
            existing_trips = []

    existing_trips.append(new_trip) #   Add trip to existing trips list

    with open('proposed_trips.json', 'w') as file:
            json.dump(existing_trips, file, indent=4)   #   Save the trip to the proposed trips json file

    return jsonify(trip_details=new_trip, temperature_start=temperature_start, temperature_end=temperature_end) #   Return the details of the trip and weather condition


#   Creating get all user proposed trips REST method
@app.route('/proposed_trips', methods=['GET'])  #   Defining route for handling GET requests
def get_proposed_trips():
    with open('proposed_trips.json', 'r') as file:  #   Open the file proposed_trips.json
        try:
            proposed_trips = json.load(file)    #   Load the data from the json file
        except json.JSONDecodeError:
            proposed_trips = []
    return jsonify(proposed_trips=proposed_trips)   #   Returns JSON response of the proposed trips

#   Creating REST method for expressing interest in user proposed trips
@app.route('/express_interest', methods=['POST'])   #   Defining route for post requests
def express_interest():
    data = request.json
    trip_id = data.get('tripID')
    user_id = data.get('userID')

    selected_trip = None

    with open('proposed_trips.json', 'r') as file:  #   Open the proposed trips json file so it can retieve the data
        try:
            proposed_trips = json.load(file)
        except json.JSONDecodeError:
            proposed_trips = []

    for trip in proposed_trips:
        if trip.get('tripID') == trip_id:   #   Look for the trip by using the trip ID
            selected_trip = trip
            break

    if selected_trip:
        interest_data = {
            "userID": user_id,  #   When found create dictionary of userID and tripID
            "tripID": trip_id
        }

        try:
            with open('expressed_interest_in_trip.json', 'r') as file:  #   Open new json file named expressed_interest_in_trip.json
                interests = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            interests = []

        interests.append(interest_data)

        with open('expressed_interest_in_trip.json', 'w') as file:
            json.dump(interests, file, indent=4)   # Write the interest data to the expressed_interest_in_trip.json

        return jsonify(interest_info=interest_data)
    else:
        return jsonify(message="Trip not found")    #   Error handling

#   Creating REST method for checking interest on user proposed trips
@app.route('/check_interest_on_proposed_trips', methods=['POST'])   #   Defining route to handle HTTP post requests
def check_interest_on_proposed_trips():
    data = request.json
    trip_id = data.get('tripID')    #   Extracting JSON data to find tripID

    with open('expressed_interest_in_trip.json', 'r') as file:  #   Open expressed interest in trip json file and retrieve the data
        expressed_interest_data = json.load(file)

    user_ids = [entry['userID'] for entry in expressed_interest_data if entry['tripID'] == trip_id] #   Extract the userID for the trip ID in interest Data

    return jsonify(user_ids=user_ids)   #   Return JSON response with the user IDs that are interested in that specific trip


#   Creating function for generating unique user ID
def generate_unique_user_id_internal():
    response = requests.get('https://www.random.org/integers/?num=1&min=100000&max=999999&col=1&base=10&format=plain&rnd=new')  #   Api link for random.org
    if response.status_code == 200:     #   Check if response is successful
        userID = response.text.strip()
        return 'User' + userID  # return user with generated unique ID
    else:
        return 'Error could not generate.'  # Errror handling

#   Creating function for generating unique trip ID
def generate_unique_trip_id_internal():
    response = requests.get('https://www.random.org/integers/?num=1&min=100000&max=999999&col=1&base=10&format=plain&rnd=new')  #   Api link for random.org
    if response.status_code == 200: #   Check if response is successful
        tripID = response.text.strip()
        return 'Trip' + tripID  #   return trip with generated unique ID
    else:
        return 'Error could not generate.'  #   Error handling


# :)
# heheeeheh ahhaaah a


if __name__ == '__main__':
    app.run(debug=True) # Flask server starting
