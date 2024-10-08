![image](https://github.com/user-attachments/assets/3af0be9c-1f18-440a-8e75-8230ff43bae2)

# IMEI Lookup Library

The IMEI Lookup Library is a Python package that allows you to look up phone models using IMEI numbers. It combines Google search and API calls to check IMEI numbers and retrieve relevant phone model information. Additionally, it generates visualizations for phone model counts and market share distributions.

## Features

- Lookup phone models via IMEI using Google and API calls.
- Cache results to avoid redundant lookups.
- Track failed IMEI lookups.
- Generate bar graphs and pie charts for phone model distribution and market share.
- Process CSV files containing multiple IMEI entries.
- Support for visual progress bar during file processing using `tqdm`.

## Installation

Install the library and dependencies via `pip`:

```bash
pip install imei-lookup
```

Ensure the following dependencies are installed:

- `requests`
- `tqdm`
- `matplotlib`
- `beautifulsoup4`

## Usage

The documentation is in docs.ipynb.

## File Format

The input file for processing IMEIs should be a CSV with semicolon (`;`) separated values:

```
IMEI;IMSI;MSISDN
123456789012345;123456789012345;0123456789
234567890123456;234567890123456;9876543210
```

## Project Structure

- `main.py`: Main logic of the IMEI lookup.
- `utils.py`: Contains helper functions for file operations and data handling.
- `phone_models.txt`: File to store the results of phone model lookups.
- `imei_cache.json`: JSON cache for successful IMEI lookups.
- `failed_imei_cache.json`: JSON cache for failed IMEI lookups.

## License

This project is licensed under the MIT License.
