<div align="center">
  <img src="https://github.com/user-attachments/assets/9b0b57cd-f25c-4ef1-8f81-057fb5ba12e5" alt="image" width="300" height="300" style="border-radius: 300%;">
</div>

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

   <img width="1187" alt="image" src="https://github.com/user-attachments/assets/8cfa9901-5120-4f5c-aff0-3d1bcacd84ab">

   This graph shows the number of devices associated with each model.

2. **Market Share by Company:**

   <img width="946" alt="image" src="https://github.com/user-attachments/assets/308a982f-936b-4b2f-9781-d57a75233bf3">

   This pie chart shows the market share of different client devices.

---

## License

This project is licensed under the MIT License.
