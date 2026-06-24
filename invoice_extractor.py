import os
import json
import typing
import pdfplumber
from dotenv import load_dotenv
from google import genai

# Load environment variables from local .env file
load_dotenv()

# Initialize the Gemini API client
# It automatically picks up GEMINI_API_KEY from the environment
client = genai.Client()

# STEP 4 (PART A): TypedDict Schema Definitions

class LineItem(typing.TypedDict):
    item: typing.Optional[str]
    amount: typing.Optional[str]

class InvoiceSchema(typing.TypedDict):
    # Field definitions mapping exactly to the 13 required rubric fields
    invoice_number: typing.Optional[str]
    invoice_date: typing.Annotated[typing.Optional[str], "Must format strictly to DD-MM-YYYY"]
    due_date: typing.Optional[str]
    billed_by: typing.Optional[str]
    billed_to: typing.Optional[str]
    line_items: typing.List[LineItem]
    subtotal: typing.Optional[str]
    discount: typing.Optional[str]
    tax_or_gst: typing.Optional[str]
    total_amount: typing.Optional[str]
    currency: typing.Optional[str]
    payment_method: typing.Optional[str]
    notes: typing.Optional[str]


# STEP 1, 2, 3: PDF Extract and Clean Text Pipeline
def extract_text_from_pdf(pdf_path: str) -> str:
    """Opens a PDF file, extracts raw text, and sanitizes whitespace (Steps 1, 2, 3)."""
    raw_text = ""
    
    # Step 1 & 2: Load PDF and Extract Raw Text
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                raw_text += text + "\n"
                
    if not raw_text.strip():
        raise ValueError(f"No readable text found in {pdf_path}. Ensure it is not a scanned image PDF.")

    # Step 3: Clean raw text by stripping whitespace and removing empty lines
    cleaned_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    return "\n".join(cleaned_lines)


# STEP 4 (PART B), 5, & 6: LLM Configuration & JSON Parsing Pipeline
def extract_invoice_data(cleaned_text: str) -> typing.Optional[dict]:
    """Sends cleaned text to Gemini with System Prompt & Schema constraint (Steps 4, 5, 6)."""
    
    # Step 4: Engineer precise system instructions
    system_prompt = """
    You are an expert financial document parser. Extract data from the raw invoice text.
    
    Strict Extraction Rules:
    1. If a field is not present in the invoice text, return null. 
    2. Never guess, make up, or use placeholder text like "N/A" or "None". Always return JSON literal null.
    3. Format 'invoice_date' strictly to "DD-MM-YYYY". If format conversion is impossible, return the raw date string.
    4. Ensure line items are extracted into an array of objects containing 'item' and 'amount'.
    """
    
    try:
        # Step 5: Send content to Gemini using Structured Output Schema
        # Passing InvoiceSchema in response_schema guarantees structured JSON mapping
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Invoice text to extract:\n\n{cleaned_text}",
            config={
                "system_instruction": system_prompt,
                "temperature": 0.0,  # Ensure completely consistent, reproducible output
                "response_mime_type": "application/json",
                "response_schema": InvoiceSchema,
            }
        )
        
        # Step 6: Parse the clean, structured JSON response
        return json.loads(response.text)
        
    except Exception as e:
        print(f"[!] Error during Gemini extraction: {e}")
        return None


# STEP 7: Batch Local Execution and Output Saving
if __name__ == "__main__":
    # Ensure local directory folders are active
    invoices_dir = "invoices"
    outputs_dir = "outputs"
    os.makedirs(invoices_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    print("       INVOICE DATA EXTRACTOR PIPELINE ACTIVATED    ")

    processed_count = 0
    
    # Sequentially process invoice_1.pdf, invoice_2.pdf, and invoice_3.pdf
    start_invoice_index = 1
    end_invoice_index = 4  # Remember: range(1, 4) generates exactly [1, 2, 3]
    
    for i in range(start_invoice_index, end_invoice_index):
        pdf_path = os.path.join(invoices_dir, f"invoice_{i}.pdf")
        output_json_path = os.path.join(outputs_dir, f"output_invoice_{i}.json")
        
        if os.path.exists(pdf_path):
            print(f"\n[*] Processing: {pdf_path}")
            
            try:
                # Steps 1 - 3: Extract and Clean
                cleaned_text = extract_text_from_pdf(pdf_path)
                
                # Steps 4 - 6: Prompt, LLM processing, and Parse JSON
                invoice_data = extract_invoice_data(cleaned_text)
                
                if invoice_data:
                    # Save structured JSON directly into your outputs/ directory
                    with open(output_json_path, "w", encoding="utf-8") as out_file:
                        json.dump(invoice_data, out_file, indent=4)
                    
                    # Step 7: Print clean structured output in the console
                    print(f"[✓] Saved extracted data to: {output_json_path}")
                    print(json.dumps(invoice_data, indent=4))
                    processed_count += 1
                else:
                    print(f"[×] Failed to extract data from {pdf_path}")
                    
            except Exception as err:
                print(f"[×] Critical error parsing {pdf_path}: {err}")
        else:
            print(f"[i] Invoice file not found: {pdf_path}. Please place your PDF in the invoices/ folder.")
            
    print(f"Execution complete. Successfully parsed {processed_count} invoice(s).")