import csv
import requests
import json
import time
import os
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from bs4 import BeautifulSoup

# Load the configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Get the token and CSV file path from the configuration
token = config['token']
csv_file_path = config['csv_file_path']

# Base URL for the IMEI check endpoint
api_url = 'https://api.imeicheck.net/v1/checks'

# Use one of the sandbox service IDs
serviceId = 22  # Mock service with successful results

# Headers for authentication
headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}

# Define the folder to store all JSON files
json_folder = 'json_results'
if not os.path.exists(json_folder):
    os.makedirs(json_folder)

# Define file paths for storing results in the folder
local_tac_db_path = os.path.join(json_folder, 'local_tac_db.json')
output_file_path = os.path.join(json_folder, 'successful_lookups.json')
failed_lookup_path = os.path.join(json_folder, 'failed_lookups.json')
device_count_path = os.path.join(json_folder, 'device_count_summary.json')  # New path for device count summary

# Dictionary to keep track of unique IMEIs and their occurrences
unique_imeis = {}
device_count = {}  # To store the count of each device model

# Track already processed IMEIs to prevent double counting
processed_imeis = set()

# Load local TAC and failed lookups from files (or initialize new ones)
if os.path.exists(local_tac_db_path):
    with open(local_tac_db_path, 'r') as f:
        local_tac_db = json.load(f)
else:
    local_tac_db = {}

if os.path.exists(failed_lookup_path):
    with open(failed_lookup_path, 'r') as f:
        failed_lookups = json.load(f)
else:
    failed_lookups = {}

# Function to send the POST request to check the IMEI via API (only use the first 15 digits of the IMEI)
def check_imei_api(imei, retries=3, backoff_factor=2):
    data = {
        'imei': imei[:15],  # Use only the first 15 digits of the IMEI
        'deviceId': imei[:15],
        'serviceId': serviceId
    }

    attempt = 0
    while attempt < retries:
        try:
            # Wait 10 seconds before the API call
            print(f"Waiting for 10 seconds before checking IMEI: {imei[:15]}")
            time.sleep(10)

            response = requests.post(api_url, headers=headers, json=data, timeout=10)  # Set a timeout
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                print(f"IMEI Check successful for IMEI: {imei[:15]}")
                print(json.dumps(result, indent=4))  # Pretty print the JSON response

                # Check if the status is 'unsuccessful' and skip it
                if result.get('status') == 'unsuccessful' or not result.get('properties'):
                    print(f"IMEI {imei[:15]} check was unsuccessful or missing properties. Skipping this entry.")
                    return None

                save_successful_lookup(result)
                update_device_count(result, imei)  # Update device count by model/manufacturer
                return result  # Return result for success
            elif response.status_code == 429:
                print(f"Rate limit hit for IMEI {imei[:15]}. Sleeping for 10 seconds before retrying...")
                time.sleep(10)  # Wait before retrying
            else:
                print(f"Failed to check IMEI: {imei[:15]}. Status code: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error for IMEI {imei[:15]}: {e}")
            attempt += 1
            sleep_time = backoff_factor ** attempt  # Exponential backoff
            print(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        except requests.exceptions.Timeout:
            print(f"Request timed out for IMEI {imei[:15]}. Retrying...")
            attempt += 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    print(f"Failed to check IMEI: {imei[:15]} after {retries} retries.")
    return None


# Function to update the count of each device model
def update_device_count(result, imei):
    # Only update if the result is marked as successful
    if result.get('status') == 'successful':
        if imei in processed_imeis:
            print(f"Device count for IMEI {imei} has already been updated.")
            return  # Avoid double counting

        properties = result.get('properties', None)
        if properties and isinstance(properties, dict):
            device_name = properties.get('deviceName', None)
            if device_name:
                if device_name in device_count:
                    device_count[device_name] += 1
                else:
                    device_count[device_name] = 1
                print(f"Device count updated for {device_name}: {device_count[device_name]}")
                processed_imeis.add(imei)  # Mark the IMEI as processed


# Function to handle failed IMEI lookups
def save_failed_lookup(imei):
    failed_lookups[imei] = "failed"
    with open(failed_lookup_path, 'w') as f:
        json.dump(failed_lookups, f, indent=4)

# Function to save a successful lookup result to a JSON file
def save_successful_lookup(result):
    try:
        with open(output_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(result)
    with open(output_file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Function to save the TAC to the local database
def save_tac_to_local_db(tac, phone_details):
    local_tac_db[tac] = phone_details
    with open(local_tac_db_path, 'w') as f:
        json.dump(local_tac_db, f, indent=4)

# Function to save the device count summary to a JSON file
def save_device_count_summary():
    with open(device_count_path, 'w') as f:
        json.dump(device_count, f, indent=4)

# Function to deduplicate and filter successful IMEIs
def deduplicate_and_filter_success():
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)

        for row in reader:
            full_imei = row[0]
            truncated_imei = full_imei[:15]
            tac = truncated_imei[:8]

            if truncated_imei in failed_lookups:
                print(f"Skipping failed IMEI: {truncated_imei}")
                continue

            if truncated_imei not in unique_imeis:
                unique_imeis[truncated_imei] = {"tac": tac, "count": 1}
            else:
                unique_imeis[truncated_imei]["count"] += 1

# Web scraping function to search for device name using TAC
def google_search(tac):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    search_url = f"https://www.google.com/search?q={tac}+imei+swappa"
    response = requests.get(search_url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    first_result = soup.find('h3')

    if first_result:
        result_text = first_result.text.strip()
        print(f"First search result title: {result_text}")

        if result_text[:5] == "IMEI:":
            phone_details = result_text.split(" - ")[-1]
            return phone_details
    return None

# Main function to handle the lookup with fallback logic
def process_device_lookup(imei, tac):
    # Check if this IMEI has already been processed to prevent double counting
    if imei in processed_imeis:
        print(f"IMEI {imei} has already been processed. Skipping.")
        return None

    device_name_from_google = google_search(tac)

    if device_name_from_google:
        print(f"Device name found via Google search for TAC {tac}: {device_name_from_google}")
        processed_imeis.add(imei)  # Mark the IMEI as processed
        return {
            'deviceId': imei[:15],
            'status': 'successful',
            'properties': {
                'deviceName': device_name_from_google
            }
        }
    else:
        print(f"Google search did not yield results for TAC {tac}. Trying API for IMEI: {imei[:15]}")
        time.sleep(10)

        phone_details_from_api = check_imei_api(imei[:15])

        if phone_details_from_api:
            processed_imeis.add(imei)  # Mark the IMEI as processed
            return phone_details_from_api
        else:
            print(f"Both Google and API failed for IMEI: {imei[:15]}. Marking as failed.")
            save_failed_lookup(imei[:15])
            return None

# Main function to process device lookups and update counts
def process_device_lookups():
    deduplicate_and_filter_success()

    n = 0
    for imei in unique_imeis:
        n += 1
        tac = unique_imeis[imei]['tac']

        # Check if the IMEI has already been processed
        if imei in processed_imeis:
            print(f"IMEI {imei} previously processed. Skipping.")
            continue

        if imei in failed_lookups:
            print(f"IMEI {imei} previously failed. Skipping.")
            continue

        if tac in local_tac_db:
            phone_details = local_tac_db[tac]
            if phone_details.get('status') == 'successful':
                update_device_count(phone_details, imei)
        else:
            phone_details = process_device_lookup(imei, tac)
            if phone_details and phone_details.get('status') == 'successful':
                save_tac_to_local_db(tac, phone_details)
                update_device_count(phone_details, imei)
        
        print()

    save_device_count_summary()

# Function to sort iPhone models by number and variant
def sort_iphone_models(device_count):
    iphones = []
    ipads = []
    other_devices = []

    for device in device_count.keys():
        if "iPhone" in device:
            iphones.append(device)
        elif "iPad" in device:
            ipads.append(device)
        else:
            other_devices.append(device)

    iphones_sorted = sorted(iphones, key=lambda d: (int(''.join(filter(str.isdigit, d.split()[1]))) if any(char.isdigit() for char in d.split()[1]) else 1000, d.lower()))
    ipads_sorted = sorted(ipads, key=lambda d: (int(''.join(filter(str.isdigit, d.split()[1]))) if any(char.isdigit() for char in d.split()[1]) else 1000, d.lower()))

    return iphones_sorted + ipads_sorted + sorted(other_devices)

# Generate both graphs and show them simultaneously
def generate_graphs():
    # Load the updated device count before generating graphs
    device_count_summary = load_json(device_count_path)
    successful_device_count = {device: count for device, count in device_count_summary.items() if count > 0}
    sorted_devices = sort_iphone_models(successful_device_count)

    manufacturer_colors = {
        'Apple': '#FF9999',   # Red for Apple
        'Samsung': '#99FF99',  # Green for Samsung
        'Huawei': '#FFCC99',   # Orange for Huawei
        'Pixel': '#99CCFF',    # Light Blue for Pixel
        'Google': '#99CCFF',   # Pink for Google
        'Other': '#9999FF',    # Blue for other manufacturers
        'Galaxy': '#99FF99',   # Green for Samsung Galaxy (same as Samsung)
        'Google Pixel': '#99CCFF'
    }

    device_colors = [manufacturer_colors.get(device.split(' ')[0], manufacturer_colors['Other']) for device in sorted_devices]

    plt.figure(1, figsize=(12, 8))
    counts = [successful_device_count[device] for device in sorted_devices]
    bars = plt.bar(sorted_devices, counts, color=device_colors)

    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count), ha='center', va='bottom', fontsize=8)

    plt.xticks(rotation=90, fontsize=8)
    plt.ylabel('Count')
    plt.xlabel('Device Model')
    plt.title('Device Count by Model')
    plt.tight_layout()

    company_counts = defaultdict(int)
    for device, count in successful_device_count.items():
        manufacturer = device.split(' ')[0]
        company_counts[manufacturer] += count

    companies = list(company_counts.keys())
    company_counts_values = list(company_counts.values())

    pie_colors = [manufacturer_colors.get(company, manufacturer_colors['Other']) for company in companies]
    total = sum(company_counts_values)
    company_percentages = [(count / total) * 100 for count in company_counts_values]

    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Remove percentage labels by setting autopct to None
    patches, texts = ax.pie(company_counts_values, labels=None, autopct=None, startangle=90, colors=pie_colors)
    
    ax.set_title('Market Share by Company')
    ax.axis('equal')

    legend_labels = [f"{company}: {percentage:.1f}%" for company, percentage in zip(companies, company_percentages)]
    plt.legend(patches, legend_labels, title="Companies", loc="center left", bbox_to_anchor=(1, 0.5), fontsize='small')

    plt.subplots_adjust(left=0.1, right=0.75)
    plt.show()

# Function to update IMEI names if they are not fully known (start with "IMEI:")
def update_imei_device_names(token, service_id):
    device_summary = load_json(device_count_path)
    failed_lookups = load_json(failed_lookup_path)

    for device_name in list(device_summary.keys()):
        # Check if the device name starts with "IMEI:"
        if device_name.startswith("IMEI:"):
            imei_number = device_name.split(": ")[1]  # Extract IMEI number from "IMEI: [number]"
            imei_first_15_digits = imei_number[:15]

            print(f"Updating device name for IMEI: {imei_first_15_digits}")

            # Perform an API lookup for the IMEI
            phone_details_from_api = check_imei_api(imei_first_15_digits)

            if phone_details_from_api:
                device_name_from_api = phone_details_from_api.get('properties', {}).get('deviceName', None)
                if device_name_from_api:
                    print(f"API returned device name: {device_name_from_api} for IMEI: {imei_first_15_digits}")
                    # Update the device name in the summary and remove the "IMEI:" entry
                    device_summary[device_name_from_api] = device_summary.pop(device_name)

                    # Save the successful lookup to the JSON files
                    save_successful_lookup(phone_details_from_api)
                else:
                    print(f"No valid device name returned by the API for IMEI: {imei_first_15_digits}")
                    # If the API didn't return a valid device name, mark as failed
                    failed_lookups[imei_first_15_digits] = "failed"
                    device_summary.pop(device_name, None)  # Remove the entry from device summary
            else:
                print(f"No valid details returned by the API for IMEI: {imei_first_15_digits}")
                # If API fails to return any valid details, mark as failed
                failed_lookups[imei_first_15_digits] = "failed"
                device_summary.pop(device_name, None)  # Remove the entry from device summary
    
    save_json(device_count_path, device_summary)
    save_json(failed_lookup_path, failed_lookups)

# Function to load JSON data from a file
def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"File {file_path} not found or empty. Returning empty dictionary.")
        return {}

# Function to save JSON data to a file
def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Call the update_imei_device_names function after processing device lookups
process_device_lookups()

# Update IMEI names that start with "IMEI"
update_imei_device_names(token, 22)

# Generate the graphs based on the device count data
generate_graphs()
