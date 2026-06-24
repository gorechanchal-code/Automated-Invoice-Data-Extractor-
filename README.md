Automated Invoice Data Extractor (Gemini)

An automated Python pipeline that extracts structured data points from invoice PDFs into standardized JSON objects using the google-genai SDK and native schemas.

📂 Repository Structure

invoice-extractor-genai/
├── invoice_extractor.py   # Main Python extraction script
├── generate_invoices.py   # Helper script to dynamically generate 3 test PDFs
├── README.md              # Project documentation (This file)
├── requirements.txt       # Project dependencies
├── .gitignore             # Excludes .env and local caches
├── invoices/              # Source invoice PDFs
└── outputs/               # Structured JSON outputs


⚙️ Setup & Installation

Clone & Navigate:

git clone <your-repository-url>
cd invoice-extractor-genai

Virtual Environment (Recommended):

python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
source .venv/bin/activate


Install Dependencies:

pip install -r requirements.txt

Add Your API Key:
Create a .env file in the root folder and add your key:

GEMINI_API_KEY=your_actual_gemini_api_key_here

🚀 How to Run

Generate Sample PDFs:

python generate_invoices.py


Extract Data:

python invoice_extractor.py

The pipeline will read the PDFs, extract the values, and save matching JSON results inside the outputs/ folder.

📊 Tested Invoice Varieties

Invoice 1 (Velora Services): Service layout capturing project hours and domestic currency values (INR).

Invoice 2 (Tech-Mart Electronics): Retail receipt featuring multiple items; has no due date (validates null fallback logic).

Invoice 3 (Apex Utility): Complex utility layout representing electricity charges; has no discount (validates null fallback logic).