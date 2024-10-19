# Website Scraper

The Website Scraper is designed to extract data from multiple websites with varying content structures and intelligently process the information using AI. It combines traditional web scraping techniques with AI-driven parsing and processing capabilities, enabling it to adapt to different webpage layouts and extract relevant data more accurately.

## Features

- Multi-Site Scraping: Capable of extracting data from various hotel booking websites.
- Intelligent URL Analysis: Automatically identifies the most relevant page for room listings.
- AI-Powered Data Extraction: Utilizes Groq's advanced AI to parse and extract room details accurately.
- Adaptive Scraping: Handles different webpage layouts and content structures.
- Bulk URL Processing: Efficiently processes multiple URLs from a single website.
- Structured Data Output: Presents extracted data in a clean, JSON format.
- Error Handling: Robust error management for various scraping scenarios.
- Scalable Architecture: Designed to handle large volumes of data and multiple websites.
- Customizable AI Prompts: Easily adjustable AI instructions for different scraping tasks.
- Chunked Processing: Breaks down large text data for more effective AI analysis.

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/al-kafi-sohag/website-scraper.git
   cd website-scraper
   ```

2. Create a virtual environment and activate it:

   On Mac/Linux:

   ```sh
    python -m venv venv
    source venv/bin/activate
   ```

   On Windows:

   ```sh
    python -m venv venv
    venv\Scripts\activate
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure it:

   ```sh
   cp .env.example .env
   ```

   Then, edit the `.env` file and add your API keys:

   ```
   GROQ_API_KEY="your_groq_api_key_here"
   MODEL="llama-3.1-70b-versatile"
   MAX_WORDS=1000
   ```

   Make sure to replace `your_groq_api_key_here` with your actual Groq API key.

## Usage

1. Add url inside `main()` in `main.py` file.

   ```python
   main('https://www.tonsofrentals.com')
   ```

2. Run the `main.py` application:

   ```sh
   python main.py
   ```

3. Wait for the scraping to Complete.

4. View the Results:
   Open the `result/` folder and locate `result.csv` to review the results.

## Project Structure

- `main.py`: Core script that orchestrates the scraping process and calls other modules.
- `link_retriever_agent.py`: Contains logic for identifying the correct room listing URL.
- `data_retriever_agent.py`: Handles the extraction of room details from scraped content.
- `requirements.txt`: Lists all Python dependencies required for the project.
- `.env.example`: Example environment file for storing configuration and API keys.
- `README.md`: Project documentation and usage instructions.

Key files:

- `main.py`: Initiates the scraping process, manages URL collection, and coordinates between modules.
- `link_retriever_agent.py`: Uses AI to analyze URLs and identify the most relevant room listing page.
- `data_retriever_agent.py`: Employs AI to parse scraped content and extract structured room data.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
