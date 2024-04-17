# Importing necessary libraries
import requests
import json
import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Get the values
NR_ACCOUNT_ID = config.get('DEFAULT', 'NR_ACCOUNT_ID')
NR_ENTITY_GUID = config.get('DEFAULT', 'NR_ENTITY_GUID')
NR_API_KEY = config.get('DEFAULT', 'NR_API_KEY')
SPLIT_API_KEY = config.get('DEFAULT', 'SPLIT_API_KEY')

# URL for New Relic's GraphQL API
url = "https://api.newrelic.com/graphql"

# Payload for the GraphQL query, fetching BrowserInteraction events
payload = json.dumps({
  "query": "{\n  actor {\n    account(id: "+NR_ACCOUNT_ID+") {\n      nrql(query: \"SELECT * FROM BrowserInteraction WHERE entityGuid = '"+NR_ENTITY_GUID+"' AND sessionTraceId IS NOT NULL SINCE 2 hour ago\") {\n        results\n      }\n    }\n  }\n}",
  "variables": ""
})

# Define the headers for the API request
headers = {
  'Content-Type': 'application/json',  # The body of the request is JSON
  'API-Key': NR_API_KEY  # The API key for New Relic
}

# Send a POST request to the New Relic API
response = requests.request("POST", url, headers=headers, data=payload, verify=False)
print('recieved events response from newrelic')  # Log that the response has been received

print(response.text)  # Print the text of the response

# Parse the response text into a JSON object
json_response = json.loads(response.text)


# Function to create split events for different event types
def create_split_event(event_type_id, value):
    split_event = {
        "eventTypeId": event_type_id,
        "trafficTypeName": "user",
        "key": result['userId'],
        "timestamp": result['timestamp'],
        "value": value,
        "properties": {
            "sessionTraceId": result['sessionTraceId'],
            "browserInteractionId": result['browserInteractionId'],
            "previousUrl": result['previousUrl'],
            "countryCode": result['countryCode'],
            "entityGuid": result['entityGuid'],
            "asnOrganization": result['asnOrganization'],
            "previousGroupedUrl": result['previousGroupedUrl'],
            "city": result['city'],
            "userAgentName": result['userAgentName'],
            "deviceType": result['deviceType'],
            "session": result['session'],
            "regionCode": result['regionCode'],
            "userAgentVersion": result['userAgentVersion'],
            "asn": result['asn'],
            "targetGroupedUrl": result['targetGroupedUrl'],
            "ajaxCount": result['ajaxCount'],
            "appName": result['appName'],
            "domain": result['domain'],
            "userAgentOS": result['userAgentOS'],
            "asnLatitude": result['asnLatitude'],
            "targetUrl": result['targetUrl'],
            "asnLongitude": result['asnLongitude'],
            "appId ": result['appId'],
            "browserInteractionName": result['browserInteractionName']
        }
    }
    return split_event


# Convert json_response to Split.io format
split_events = []  # Initialize an empty list to store the split events
# Define the event types to be processed
event_types = ["timeToLoadEventEnd", "timeToDomComplete", "timeToResponseStart", "duration", "timeToLoadEventStart", "timeToDomainLookupStart", "timeToDomContentLoadedEventStart", "timeToDomInteractive", "timeToDomainLookupEnd", "timeToConnectEnd", "timeToRequestStart", "timeToResponseEnd", "timeToUnloadEventStart", "timeToFetchStart", "timeToDomContentLoadedEventEnd", "timeToUnloadEventEnd", "timeToConnectStart"]

# Loop through each result in the json_response
for result in json_response['data']['actor']['account']['nrql']['results']:
    # For each event type, create a split event and append it to the split_events list
    for event_type in event_types:
        split_event = create_split_event(event_type, result[event_type])
        split_events.append(split_event)

# Split events into chunks to ensure each request is less than 100mb
chunk_size = 100000000  # 100mb
chunks = [split_events[i:i+chunk_size] for i in range(0, len(split_events), chunk_size)]
url = "https://events.split.io/api/events/bulk"  # URL for the Split.io bulk events API
headers = {
  'Content-Type': 'application/json',  # The body of the request is JSON
  'Authorization': 'Bearer '+SPLIT_API_KEY,  # The API key for Split.io
}

# Send each chunk to Split
for chunk in chunks:
    payload = json.dumps(chunk)  # Convert the chunk to a JSON string

        
    # Send a POST request to the Split.io API
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print(response.text)  # Print the text of the response
    # If the response status code is not 200, print the response text and break the loop
    if(response.status_code != 200):
        print(response.text)
        break
    else:
        print('successfully sent chunk')  # If the response status code is 200, print a success message





