import requests
 # Importing Needed Modules

BASE_URL = "http://localhost:5000" # Base URL for the Orchestrator Service


# defining the query for new trips function
def query_for_new_trips(location): # Location parameter
    response = requests.post(f"{BASE_URL}/query_for_new_trips", json={"location": location})    # Sending a post request with JSON containing the location
    if response.status_code == 200: # Check whether HTTP response is = 200
        data = response.json() # Extract data
        trip_description = data.get('trip_description', {})
        available_trips = [] # Create empty list to store trips

        for tripID, description in trip_description.items():
            trip_information = f"{tripID}: {', '.join(description)}"
            available_trips.append(trip_information) # Append the trips to the available_trips list
        return available_trips # Return list of trips
    else:
        print("Failed to find new trips!") # Error handling if the HTTP response isnt = 200

# defining propose new trip function
def propose_new_trip(user_id, location, start_date, end_date, details): # Parameters of what the user enters
    data = {
        "userID": user_id,
        "location": location,
        "start_date": start_date, # Dictionary of user provided detail
        "end_date": end_date,
        "details": details
    }
    response = requests.post(f"{BASE_URL}/propose_new_trips", json=data) # Send post request containing users provided trip details

    if response.status_code == 200: # Check whether HTTP response is = 200
        tripDetails = response.json().get('trip_details', {}) # Extract trip details from JSON response

        return tripDetails # Returns the trip details
    else:
        return "Failed to propose the new trip please try again..." # Error handling

# defining get all proposed trips function
def get_all_proposed_trips():
    response = requests.get(f"{BASE_URL}/proposed_trips") # Sending GET request

    if response.status_code == 200: # Check whether HTTP response is = 200
        proposed_trips = response.json().get('proposed_trips', []) # If request is successful extract proposed trips from JSON response
        print("\nAll Proposed Trips:")

        for trip in proposed_trips:
            print("Location:", trip.get('location'))
            print("Details:", trip.get('details'))
            print("Start date:", trip.get('start_date'))
            print("End date:", trip.get('end_date'))    # Output of proposed trip including all information
            print("Weather:", trip.get('weather_start'))
            print("Temperature:", trip.get('temperature_start'), "°C")
            print("User ID:", trip.get('userID'))
            print("Trip ID:", trip.get('tripID'))
            print()
    else:
        print("Failed to get proposed trips!") # Error handling

def express_interest_for_trip(user_id, trip_id):
    data = {
        "userID": user_id,
        "tripID": trip_id # Create dictionary
    }
    response = requests.post(f"{BASE_URL}/express_interest", json=data) # Send POST request

    if response.status_code == 200: # Check whether HTTP response is = 200
        data = response.json()
        interest_info = data.get('interest_info', {}) # If response successful extract the interest_info from JSON response

        print("\nExpressed Interest Details:")
        for key, value in interest_info.items():
            print(f"\n{key.capitalize()} - \"{value}\"") # Output all of the information

    else:
        print(f"Failed to express interest. Error: {response.json()}") # Error Handling

# defining check interest on proposed trips function
def check_interest_on_proposed_trips(trip_id): # Parameters for the function
    data = {"tripID": trip_id} # Creating data dictionary
    response = requests.post(f"{BASE_URL}/check_interest_on_proposed_trips", json=data) # Sends POST request

    if response.status_code == 200: # Check whether HTTP response is = 200
        user_ids = response.json().get('user_ids', [])
        print(f"\nUser IDs interested in Trip {trip_id}:")
        for user_id in user_ids: # If the response is succesful output the userID and specific trips
            print(f"- {user_id}")

    else:
        print(f"Failed to check interest. Error: {response.json()}") # Error handling

# defining creating a user function
def create_user(name, password): # Parameters for the function needed
    data = {"name": name, "password": password} # Creating a dictionary of username nad password
    response = requests.post(f"{BASE_URL}/create_user", json=data) # Sending a POST request

    if response.status_code == 200: # Check whether HTTP response is = 200
        user_info = response.json().get('user', {})
        print("\nUser created successfully!")
        print(f"User ID: {user_info.get('userID')}") # If response is successful print out the userID, username, and the password hidden in *
        print(f"Name: {user_info.get('name')}")
        print("Password:", "*" * len(user_info.get('password')))


        choice = input("\nWould you like to login? (yes/no): ").lower() # Prompt the user if they would like to be logged into the application once an account has been created

        if choice == "yes":
            show_trip_buddy_options()   #   Call show trip buddy options function
            # If else statement to allow user to choose yes/no
        elif choice == "no":
            print("Thank you. Goodbye!")

        else:
            print("Invalid choice.") # Error handling
    else:
        print("Failed to create user.") # Error handling

# defining function for loggin in the user
def login_user(name, password): # Parameters for function
    data = {"name": name, "password": password} # Creating dictionary for username and password
    response = requests.post(f"{BASE_URL}/login", json=data) # Sends POST request

    if response.status_code == 200: # Check whether HTTP response is = 200
        user_info = response.json().get('user', {})
        user_id = user_info.get('userID') # If login successful extract JSON response

        print("\nLogin successful!")
        print(f"User ID: {user_info.get('userID')}")
        print(f"Name: {user_info.get('name')}") # Output details of user login and hide password in *
        print("Password:", "*" * len(user_info.get('password')))


        show_trip_buddy_options(user_id) # Display the text interface of the travel buddy application using the show trip buddy options function
    elif response.status_code == 401: # If response = 401 username or password must be incorrect
        print("Incorrect username or password. Please try again.")
    else:
        print("Failed to login.") # Error Handling

# defining function for creating user interaction
def create_user_interaction():
    print("\nCreating a New User")
    name = input("Enter your name: ") # Prompt user with login print statements
    password = input("Enter your password: ")

    created = create_user(name, password) # Call the createUser function provided with the name and password
    if created: # Checks if the created variable is True
        login_user() # Calls the loginUser function


def show_trip_buddy_options(user_id): # Parameters
    print("\n--Welcome to the Trip Buddy Application!--")

    print("  _______                  _   ____            _     _                              ")
    print(" |__   __|                | | |  _ \          | |   | |           /\                ")
    print("    | |_ __ __ ___   _____| | | |_) |_   _  __| | __| |_   _     /  \   _ __  _ __  ")
    print("    | | '__/ _` \ \ / / _ \ | |  _ <| | | |/ _` |/ _` | | | |   / /\ \ | '_ \| '_ \ ")
    print("    | | | | (_| |\ V /  __/ | | |_) | |_| | (_| | (_| | |_| |  / ____ \| |_) | |_) |")
    print("    |_|_|  \__,_| \_/ \___|_| |____/ \__,_|\__,_|\__,_|\__, | /_/    \_\ .__/| .__/ ")
    print("                                                        __/ |          | |   | |    ")
    print("                                                       |___/           |_|   |_|    ")

    while True:
        print("=======================================================================================================================================================================================================================")
        print("\n\---Available Options: ")
        print("\-1. Propose New Trips:")
        print("\--2. Query for New Trips:")
        print("\---3. See all user proposed trips:")    # Output options for user
        print("\----4 Express Interest in Trip:")
        print("\-----5 Check Interest on Trips:")
        print("\ 6. Exit" + "\n")
        print("=======================================================================================================================================================================================================================")
        print("\n")

        user_choice = input("-Enter an option listed above: ") # Prompt user to choose an option


        if user_choice == "1":
            location = input("-Enter location of trip: ")
            start_date = input("-Enter the start date (YYYY-MM-DD): ")
            end_date = input("-Enter the end date (YYYY-MM-DD): ") # If user enters "1" run the propose new trips function
            details = input("-Enter the details of the trip: ")

            tripDetails = propose_new_trip(user_id, location, start_date, end_date, details)
            print("\n Proposed Trip Details:")
            print(f"-Trip ID: {tripDetails.get('tripID')}")
            print(f"--User ID: {tripDetails.get('userID')}")
            print(f"---Location: {tripDetails.get('location')}")
            print(f"----Start Date: {tripDetails.get('start_date')}")   #   Output all of the details associated with the users inputs including the external services weather API details
            print(f"-----End Date: {tripDetails.get('end_date')}")
            print(f"------Weather Start of Trip: {tripDetails.get('weather_start')}")
            print(f"-------Average Temperature: {tripDetails.get('temperature_start')} °C")
            print(f"--------Details of Trip: {tripDetails.get('details')}")
        elif user_choice == "2":
            location = input("\nEnter location to see trips: ")
            trips = query_for_new_trips(location)   #   If user enters "2" run the query for new trips function
            print("\n-Trips for that Location: ")
            for trip in trips:
                print("- " + trip)
        elif user_choice == "3":
            get_all_proposed_trips()    #   If user enters "3" run the get all proposed trips function
        elif user_choice == "4":
            trip_id = input("-Enter the Trip ID to express interest: ")
            express_interest_for_trip(user_id, trip_id) #   If user enters "4" run the express interest for trip function
        elif user_choice == "5":
            trip_id = input("-Enter the Trip ID you would like to check user interest in: ")
            check_interest_on_proposed_trips(trip_id)   #   If user enters "5" run the check interest on proposed trips function
        elif user_choice == "6":
            print("-Goodbye!")  #   If user enters "6" break the program and close it.
            break
        else:
            print("Invalid choice please try again...")    #   Error Handling

# Terminal Output Code Below
if __name__ == "__main__":

    print("--Welcome to the Trip Buddy Application!--")
    user_choice = input("\nEnter '1' to create an account Or '2' to login: ") # Prompt user to create an account or login

    if user_choice == "1":
        name = input("-Enter your name: ")
        password = input("-Enter your password: ")  #   If user selects "1" allow them to enter username and password
        create_user(name, password)  #   Call the createUser Function
    elif user_choice == "2":
        name = input("-Enter your name: ")
        password = input("-Enter your password: ")  #   If user selects "2" allow them to enter login username and password
        login_user(name, password)   #   Call the loginUser function
    else:
        print("-Invalid choice. Please try again.") #   Error Handling
