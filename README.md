
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

To build and install locally:

```bash
python3 -m build
python3 -m pip install dist/*.whl
```

## Usage

### Basic Lookup

You can use the library to look up phone models from a list of IMEI numbers. The `lookup()` function checks for cached results, uses Google search, and falls back to API calls if necessary.

```python
from imei_lookup import IMEILookup

# Initialize the IMEI Lookup object
lookup = IMEILookup(api_key='your_api_key')

# Lookup a single IMEI
result = lookup.lookup('123456789012345;imsi;msisdn')

# Process a file of IMEI, IMSI, MSISDN combinations
lookup.process_file('imei_file.csv')
```

### Generate Graphs

After processing IMEI numbers, you can generate a bar chart of phone model counts and a pie chart for company market share.

```python
lookup.generate_graphs()
```

### Print Results

To print a summary of successful and failed lookups:

```python
lookup.print_results()
```

### Cache Management

Results from lookups are cached in JSON files for faster subsequent lookups. You can clear the target file by calling:

```python
lookup.clear_target_file()
```

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
