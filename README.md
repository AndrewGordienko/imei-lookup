# imei-lookup

This project is designed to process a list of IMEI numbers from a CSV file, perform device lookups using an API, and generate statistics about the devices based on their IMEI numbers. The results are visualized in two graphs: one showing the number of devices per model, and another displaying the market share by company. The project supports device name lookups using a combination of API and Google search fallbacks, and it tracks both successful and failed IMEI lookups.

___

## Features
- **IMEI Lookup:** Perform IMEI lookups using the IMEI Check API with fallback to Google search.
- **Device Count Tracking:** Track the number of occurrences of each device model.
- **Failed Lookup Handling:** Manage and store failed IMEI lookups for further review.
- **Data Deduplication:** Prevents multiple lookups for the same IMEI, reducing redundant calls to the API.
- **Graph Generation:** Generates bar and pie charts based on the collected device data.
- **Dynamic Updates:** Automatically updates device names if incomplete names (e.g., "IMEI: [number]") are encountered, using additional API lookups.

___

## How It Works

1. **IMEI Processing:** The program reads a list of IMEI numbers from a CSV file. Each IMEI is truncated to 15 digits and deduplicated to avoid unnecessary API calls.
2. **Device Lookup:** For each unique IMEI, the program first attempts a Google search using the TAC (first 8 digits of the IMEI). If Google does not return useful results, the program falls back to the IMEI Check API for additional details.
3. **Data Storage:**
- Successful Lookups: Devices that are successfully looked up are saved in the successful_lookups.json file.
- Failed Lookups: Devices that are not successfully looked up are saved in the failed_lookups.json file.
- Local Database: A local TAC database (local_tac_db.json) is used to avoid redundant lookups for IMEIs that have already been processed.
- Device Summary: The number of occurrences for each device model is stored in the device_count_summary.json file.
- Graph Generation: The program generates two types of graphs based on the device data:
- - Bar Chart: A bar chart showing the number of devices per model.
- - Pie Chart: A pie chart showing the market share of different companies based on the number of devices.
 
___

## Installation

Prerequisites: Python 3.x. Required Python packages (can be installed via pip): requests, matplotlib, beautifulsoup4, numpy.

### From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/AndrewGordienko/imei-lookup.git
   cd imei-lookup
   ```

2. Install the required Python dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Create your configuration file:

```json

{
    "token": "top_secret_:)",
    "csv_file_path": "sample_data.csv"
}

```

___

## Configuration

The IMEI-lookup is highly configurable through a JSON file (`config.json`).

### YAML Configuration

The JSON file defines the token for the IMEI API to look up IMEI's. Found here[https://imeicheck.net/sign-in](url). The path to the csv file is also specified. 

- **token**: API token.
- **csv_file_path**: The path to the csv with input data.

  ___

  ## Graphs

Here’s an graph of the IMEI lookup on example data:

![image](https://github.com/user-attachments/assets/3a70e1cd-2551-41d1-b248-26f6179789c3)

This graph tells us all the devices and serial numbers associated with them.

![image](https://github.com/user-attachments/assets/97403790-5ef6-4e16-872f-fe64c2127f8a)

This graph tells us the market share of client devices.
