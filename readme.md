# Website Scraper

A smart web scraping tool that automatically extracts and processes hotel listing information from various websites using artificial intelligence.

## What It Does

This tool helps you:

- Automatically collect hotel room information from different booking websites
- Convert messy web data into clean, organized information
- Save the results in an easy-to-read format (CSV file)
- Get accurate location data for each property

## Setup

1. Get the code:

   ```sh
   git clone https://github.com/al-kafi-sohag/website-scraper.git
   cd website-scraper
   ```

2. Set up your workspace:

   ```sh
   python -m venv venv

   # For Mac/Linux:
   source venv/bin/activate

   # For Windows:
   venv\Scripts\activate
   ```

3. Install required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Set up your settings:

   - Copy `.env.example` to `.env`
   - Open `.env` and configure your settings:

   ```env
   # Choose AI provider (groq or gemini)
   AI_PROVIDER="gemini"
   GROQ_API_KEY="your_key_here"
   GEMINI_API_KEY="your_key_here"

   # Choose where to save results (local, google-sheet, or both)
   RESULT="local"

   # Configure logging
   LOG_LEVEL="ERROR"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
   LOG_FILE="scraper.log"

   # Set scraping parameters
   WAITING_TIME="20"
   MAX_WORDS=10000
   MAX_WORKERS=5

   # Choose geocoding service (google or opencage)
   GEOCODING_SERVICE="opencage"
   OPENCAGE_API_KEY="your_key_here"
   GOOGLE_API_KEY="your_key_here"
   ```

   Note: You only need to add the API key for your chosen AI provider and geocoding service.

## How to Use

1. Add your website URLs to `data/websites.csv`

2. Run the scraper interface:

   ```sh
   python scraper_interface.py
   ```

3. Follow the interactive prompts to:

   - Start the main scraping process
   - Process addresses (optional)
   - Add Google Maps links (optional)
   - Retry any failed operations (optional)

4. Find your results in the `results/results.csv` file

## Key Features

- Works with multiple hotel booking websites
- Uses AI to understand and extract information accurately
- Handles different website layouts automatically
- Processes multiple URLs efficiently
- Includes location data for each property
- Manages errors gracefully

## Need Help?

Feel free to:

- Open an issue for problems
- Suggest improvements
- Contribute to the code

## License

MIT License - Feel free to use and modify this tool for your needs.
