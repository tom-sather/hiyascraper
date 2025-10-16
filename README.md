# Hiya Phone Number Scraper

This Python script automates the extraction of your ANI (phone number) data and spam labeling information from the Hiya dashboard into a CSV file.

## Features

- Automated login to Hiya dashboard
- Scrapes all phone numbers across multiple pages
- Extracts:
  - Phone numbers
  - Submission dates and email
  - Registration job names
  - Branded Call status
  - Spam labeling (Low risk, etc.)
  - Spam category
  - Registration status
- Exports to CSV with timestamp

## Prerequisites

1. **Python 3.7 or higher**
2. **Google Chrome browser** installed on your system
3. **ChromeDriver** (will be installed automatically via webdriver-manager)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) If you need to install Chrome:
   - **Windows/Mac**: Download from https://www.google.com/chrome/
   - **Linux**: 
     ```bash
     sudo apt-get update
     sudo apt-get install -y google-chrome-stable
     ```

## Usage

### Basic Usage

Simply run the script:
```bash
python hiya_scraper.py
```

You'll be prompted to enter your Hiya username/email and password.

### Advanced Usage

You can modify the script to customize behavior:

```python
# Run in headless mode (no browser window)
scraper = HiyaScraper(headless=True)

# Save to a specific filename
scraper.save_to_csv("my_hiya_data.csv")
```

## Output

The script creates a CSV file named `hiya_phone_numbers_YYYYMMDD_HHMMSS.csv` with the following columns:

- `phone_number`: The ANI/phone number
- `submitted_date`: When it was submitted
- `submitted_by`: Email address that submitted it
- `registration_job_name`: Job name for the registration
- `branded_call`: Branded Call status
- `spam_labeling`: Spam risk level (e.g., "Low risk")
- `spam_category`: Category of spam (if any)
- `registration_status`: Current registration status

## Troubleshooting

### Issue: ChromeDriver not found
**Solution**: The script should auto-download ChromeDriver, but if it fails:
```bash
pip install --upgrade webdriver-manager
```

### Issue: Login fails
**Solution**: 
- Verify your credentials are correct
- Check if Hiya uses 2FA (two-factor authentication) - you may need to disable it temporarily
- Update the login URL in the script if Hiya changed their login page

### Issue: Can't find elements on page
**Solution**: 
- Hiya may have changed their HTML structure
- Open the browser in non-headless mode to see what's happening:
  ```python
  scraper = HiyaScraper(headless=False)
  ```
- You may need to update the CSS selectors in the script

### Issue: Some data is missing
**Solution**: The column structure may have changed. You'll need to:
1. Inspect the page HTML
2. Update the cell index numbers in the `scrape_current_page()` method

## Customization

### Adjusting Wait Times
If your internet is slow, increase wait times:
```python
time.sleep(3)  # Change to 5 or more
```

### Filtering Data
To only scrape certain numbers, add filtering logic in `scrape_current_page()`:
```python
if spam_labeling == "Low risk":
    record = {...}
    self.data.append(record)
```

### Changing Page Navigation
If pagination works differently, modify the `go_to_next_page()` method with the correct selector.

## Important Notes

1. **Rate Limiting**: The script includes delays between pages to avoid overwhelming Hiya's servers
2. **Authentication**: Keep your credentials secure - never commit them to version control
3. **Terms of Service**: Ensure your use of this scraper complies with Hiya's Terms of Service
4. **Data Privacy**: Handle the exported data according to your company's data protection policies

## Security Best Practices

Instead of entering credentials each time, you can use environment variables:

```bash
export HIYA_USERNAME="your_email@company.com"
export HIYA_PASSWORD="your_password"
```

Then modify the script:
```python
import os
username = os.environ.get('HIYA_USERNAME')
password = os.environ.get('HIYA_PASSWORD')
```

## Need Help?

If you encounter issues:
1. Check that Chrome and ChromeDriver versions are compatible
2. Verify the Hiya website structure hasn't changed (inspect with browser DevTools)
3. Run in non-headless mode to see what's happening visually
4. Check the console output for specific error messages

## License

This script is provided as-is for personal/business use. Ensure compliance with Hiya's Terms of Service.
