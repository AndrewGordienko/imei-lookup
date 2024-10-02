
# IMEI Lookup

This project processes a list of IMEI numbers from a CSV file, performs device lookups using an API, and generates statistics about the devices. Results are visualized in two graphs: one showing the number of devices per model, and another displaying market share by company. The project supports device name lookups via an API, with a Google search fallback, and tracks both successful and failed IMEI lookups.

---

## Features
- **IMEI Lookup:** Perform IMEI lookups using the IMEI Check API with fallback to Google search.
- **Device Count Tracking:** Track occurrences of each device model.
- **Failed Lookup Handling:** Store and review failed IMEI lookups.
- **Data Deduplication:** Avoid redundant API calls by preventing multiple lookups for the same IMEI.
- **Graph Generation:** Generates bar and pie charts from the collected device data.
- **Dynamic Updates:** Automatically updates device names using additional API lookups when incomplete names (e.g., "IMEI: [number]") are found.

---

## How It Works

1. **IMEI Processing:** Reads a list of IMEI numbers from a CSV file. IMEIs are truncated to 15 digits and deduplicated.
2. **Device Lookup:** For each unique IMEI, the program attempts a Google search using the TAC (first 8 digits). If Google fails, the IMEI Check API is used.
3. **Data Storage:**
   - **Successful Lookups:** Saved in `successful_lookups.json`.
   - **Failed Lookups:** Saved in `failed_lookups.json`.
   - **Local Database:** Stores processed IMEIs in `local_tac_db.json` to prevent redundant lookups.
   - **Device Summary:** Counts occurrences of each model in `device_count_summary.json`.
   - **Graph Generation:** Generates:
     - **Bar Chart:** Number of devices per model.
     - **Pie Chart:** Market share of companies based on the number of devices.

---

## Installation

### Prerequisites

- Python 3.x
- Required Python packages: `requests`, `matplotlib`, `beautifulsoup4`, `numpy`.

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

3. Create your configuration file (`config.json`):

   ```json
   {
       "token": "top_secret_:)",
       "csv_file_path": "sample_data.csv"
   }
   ```

---

## Configuration

The IMEI lookup is configured via a `config.json` file:

- **token**: Your API token for the IMEI Check API. You can sign up [here](https://imeicheck.net/sign-in).
- **csv_file_path**: Path to the CSV file with input data.

---

## Graphs

Below are examples of the generated graphs:

1. **Device Count by Model:**

   ![Device Count](https://github.com/user-attachments/assets/3a70e1cd-2551-41d1-b248-26f6179789c3)

   This graph shows the number of devices associated with each model.

2. **Market Share by Company:**

   ![Market Share](https://github.com/user-attachments/assets/97403790-5ef6-4e16-872f-fe64c2127f8a)

   This pie chart shows the market share of different client devices.

---

## Code Overview

The following is a simplified overview of the main parts of the code:

- **IMEI Check:** Sends requests to the IMEI Check API, processes the results, and handles retries and failures.
- **Device Count:** Tracks device model counts and stores the results in JSON files.
- **Graphs:** Generates both bar and pie charts using `matplotlib`.

The complete code is included in the repository under `imei_lookup.py`.

---

## Contribution Guidelines

Contributions are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License.
