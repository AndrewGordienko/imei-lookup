import requests
import json
import time
from bs4 import BeautifulSoup
import os
import csv
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict

class IMEILookup:
    def __init__(self, api_key, target_file="phone_models.txt", cache_file="imei_cache.json", failed_cache_file="failed_imei_cache.json"):
        self.api_url = 'https://api.imeicheck.net/v1/checks'
        self.service_id = 22
        self.api_key = api_key
        self.target_file = target_file
        self.cache_file = cache_file
        self.failed_cache_file = failed_cache_file
        self.google_search_model = None
        
        self.create_target_file_if_not_exists()
        self.imei_cache = self.load_json(self.cache_file)
        self.failed_imei_cache = self.load_json(self.failed_cache_file)

        self.clear_target_file()
    
    def create_target_file_if_not_exists(self):
        try:
            with open(self.target_file, 'x') as file:
                # Optionally write headers or initialize content here
                pass
        except FileExistsError:
            # File already exists, nothing to do
            pass

    def clear_target_file(self):
        with open(self.target_file, 'w') as f:
            f.write('')  # This overwrites the file with an empty string

    # Load JSON data from file
    def load_json(self, file):
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {file} is empty or invalid. Initializing an empty cache.")
                return {}
        return {}

    # Save IMEI cache to JSON file
    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.imei_cache, f, indent=4)

    # Save failed IMEI cache to JSON file
    def save_failed_cache(self):
        with open(self.failed_cache_file, 'w') as f:
            json.dump(self.failed_imei_cache, f, indent=4)

    # Increment the count for a phone model in the target file
    def increment_phone_count(self, phone_model):
        try:
            with open(self.target_file, 'r+') as f:
                try:
                    phone_data = json.load(f)
                except json.JSONDecodeError:
                    phone_data = {}

                if phone_model in phone_data:
                    phone_data[phone_model] += 1
                else:
                    phone_data[phone_model] = 1

                f.seek(0)
                json.dump(phone_data, f, indent=4)
                f.truncate()
        except FileNotFoundError:
            with open(self.target_file, 'w') as f:
                json.dump({phone_model: 1}, f, indent=4)

    # Google search logic
    def search_google_for_imei(self, line):
        first_number = line.split(';')[0]
        tac = first_number[:8]

        if tac in self.failed_imei_cache:
            # print(f"IMEI {tac} found in failed cache. Skipping search.")
            return None

        if tac in self.imei_cache:
            # print(f"IMEI {tac} found in cache: {self.imei_cache[tac]}")
            self.increment_phone_count(self.imei_cache[tac])
            return self.imei_cache[tac]

        search_url = f"https://www.google.com/search?q={tac}+imei+swappa"
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('h3', limit=3)

            for result in search_results:
                result_text = result.text.strip()
                # print(f"Search result title: {result_text}")

                if result_text.startswith(f"IMEI: {tac}"):
                    dash_index = result_text.find(" - ")
                    if dash_index != -1:
                        start_index = result_text.find(" - ") + 3
                        end_index = result_text.rfind(" - ")
                        if start_index != -1 and end_index != -1:
                            phone_model = result_text[start_index:end_index].strip()
                        else:
                            phone_model = result_text[dash_index + 3:].split(" - ")[0].strip()

                        if "," in phone_model:
                            self.increment_phone_count(phone_model)
                            self.imei_cache[tac] = phone_model
                            self.save_cache()
                            # print(f"Saved to cache and file: {phone_model}")
                            return phone_model
                        else:
                            # print(f"No comma found in: {phone_model}. Storing as fallback.")
                            self.google_search_model = phone_model
        # print(f"Google search failed for {tac}.")
        return None

    # API search logic
    def search_api_for_imei(self, imei):
        data = {
            'imei': imei[:15],
            'deviceId': imei[:15],
            'serviceId': self.service_id
        }

        attempt = 0
        retries = 3  # Set the maximum number of retries for rate-limiting errors

        while attempt < retries:
            try:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }

                response = requests.post(self.api_url, headers=headers, json=data, timeout=10)

                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    # print(f"IMEI Check successful for IMEI: {imei[:15]}")
                    if result.get('status') == 'unsuccessful' or not result.get('properties'):
                        # print(f"IMEI {imei[:15]} check was unsuccessful or missing properties.")
                        return None
                    phone_model = result['properties'].get('deviceName', 'Unknown').strip()
                    self.imei_cache[imei[:8]] = phone_model
                    self.increment_phone_count(phone_model)
                    self.save_cache()
                    # print(f"Saved to cache and file: {phone_model}")
                    return phone_model
                elif response.status_code == 429:
                    # Rate limiting error: Too many requests
                    attempt += 1
                    # print(f"Rate limit hit for IMEI {imei[:15]}. Retrying in 10 seconds... (Attempt {attempt}/{retries})")
                    time.sleep(10)  # Wait for 10 seconds before retrying
                else:
                    # print(f"Failed to check IMEI: {imei[:15]}. Status code: {response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                # print(f"Error while making API request: {e}")
                return None

        # If all retries fail, return None
        # print(f"Failed to check IMEI {imei[:15]} after {retries} attempts.")
        return None

    # Combined search function with fallback
    def lookup(self, line):
        first_number = line.split(';')[0]
        tac = first_number[:8]

        if tac in self.failed_imei_cache:
            # print(f"IMEI {tac} found in failed cache. Skipping search.")
            return None

        result = self.search_google_for_imei(line)
        if result:
            # print(f"Google Search succeeded for {tac}: {result}")
            return result

        # print(f"Falling back to API search for {tac}.")
        result = self.search_api_for_imei(first_number)

        if not result and self.google_search_model:
            # print(f"Using fallback Google model without serial: {self.google_search_model}")
            self.increment_phone_count(self.google_search_model)
            self.imei_cache[tac] = self.google_search_model
            self.save_cache()
            return self.google_search_model

        if not result:
            # print(f"Both Google and API failed for {tac}. Adding to failed cache.")
            self.failed_imei_cache[tac] = "failed"
            self.save_failed_cache()

        return result

    # Function to process a whole file
    def process_file(self, file_path):
        with open(file_path, mode='r') as file:
            reader = list(csv.reader(file, delimiter=';'))  # Convert reader to a list to count total lines
            total_rows = len(reader) - 1  # Exclude the header
            reader = reader[1:]
            # Use a set to store unique device combinations (IMEI, IMSI, MSISDN)
            unique_combinations = set()
            
            with tqdm(total=total_rows, desc="Processing file", unit="row") as pbar:
                for n, row in enumerate(reader, start=1):
                    imei = row[0]
                    imsi = row[1]
                    msisdn = row[2]

                    # Create a unique combination of IMEI, IMSI, and MSISDN
                    unique_device = (imei, imsi, msisdn)

                    # Skip if we've seen this device before
                    if unique_device in unique_combinations:
                        pbar.update(1)
                        continue

                    # Process the unique device
                    unique_combinations.add(unique_device)
                    self.lookup(";".join(row))

                    # Update progress bar
                    pbar.update(1)

    # Function to generate bar graph for phone models and pie chart for company market share
    def sort_iphone_models(self, device_count):
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
    def generate_graphs(self):
        # Load the updated device count before generating graphs
        try:
            with open(self.target_file, 'r') as f:
                device_count_summary = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error loading the device count from {self.target_file}.")
            return

        successful_device_count = {device: count for device, count in device_count_summary.items() if count > 0}
        sorted_devices = self.sort_iphone_models(successful_device_count)

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

        # Create the bar chart for device count
        device_colors = [manufacturer_colors.get(device.split(' ')[0], manufacturer_colors['Other']) for device in sorted_devices]
        
        plt.figure(1, figsize=(12, 8))
        counts = [successful_device_count[device] for device in sorted_devices]
        bars = plt.bar(sorted_devices, counts, color=device_colors)

        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count), ha='center', va='bottom', fontsize=8)

        plt.xticks(rotation=90, fontsize=8)
        plt.ylabel('Count', fontsize=10)
        plt.xlabel('Device Model', fontsize=10)
        plt.title('Device Count by Model', fontsize=12)
        plt.tight_layout()

        # Generate pie chart for company market share
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
        
        patches, texts = ax.pie(company_counts_values, labels=None, autopct=None, startangle=90, colors=pie_colors)
 
        for text in texts:
            text.set_fontsize(8)  # Set smaller font size for pie chart text

        ax.set_title('Market Share by Company', fontsize=12)
        ax.axis('equal')

        # Create the legend outside the pie chart
        legend_labels = [f"{company}: {percentage:.1f}%" for company, percentage in zip(companies, company_percentages)]
        plt.legend(patches, legend_labels, title="Companies", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)

        plt.subplots_adjust(left=0.1, right=0.75)
        plt.show()

    def print_results(self):
        # Print successful lookups from the target_file
        print("\nSuccessful Lookups:")
        try:
            with open(self.target_file, 'r') as f:
                phone_data = json.load(f)
                if phone_data:
                    for phone_model, count in phone_data.items():
                        print(f"{phone_model}: {count} device(s)")
                else:
                    print("No successful lookups found.")
        except FileNotFoundError:
            print(f"File {self.target_file} not found.")
        except json.JSONDecodeError:
            print(f"Error reading {self.target_file}.")

        # Print failed lookups from failed_imei_cache
        print("\nFailed Lookups:")
        if self.failed_imei_cache:
            for imei, status in self.failed_imei_cache.items():
                print(f"IMEI: {imei} - Status: {status}")
        else:
            print("No failed lookups found.")


