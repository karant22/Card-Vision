CardVision
CardVision is a Python-based tool that reads and analyzes credit card statements in PDF format.
It extracts key details such as billing period, total due, due date, and sample transactions from multiple banks and presents them through a simple Streamlit interface.
________________________________________________________________________________________________________________________________________________________________________
#Features:
- Works with statements from Axis, HDFC, ICICI, SBI, and IDFC First Bank.
- Upload one or more PDFs for analysis.
- Automatically detects the bank and extracts main details.
- Shows a summary dashboard with all parsed information.
- Export results as JSON or CSV.
- Runs locally  no data is uploaded online.
________________________________________________________________________________________________________________________________________________________________________
#TechStack:
- Frontend / UI -- Streamlit (custom styled dashboard)
- Backend Parsing -- pdfplumber, regex
- Data Handling -- pandas
- Export Formats -- JSON, CSV
- Language -- Python
________________________________________________________________________________________________________________________________________________________________________
# How to Run

 1. Clone the repository:

```bash
git clone https://github.com/CardVision.git
cd CardVision
```

 2. Create and activate a virtual environment:

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

 3. Install dependencies:

```bash
pip install -r requirements.txt
```

 4. Run the Streamlit app:

```bash
cd src
streamlit run main.py
```

 5. Upload your PDF statements and view the extracted data in the browser.
________________________________________________________________________________________________________________________________________________________________________
#Example Output:
- Bank: HDFC Bank
- Card Last 4: 4589
- Statement Period: 01 Aug 2025 – 30 Aug 2025
- Total Due: ₹12,450.00
- Due Date: 15 Sep 2025
________________________________________________________________________________________________________________________________________________________________________
#Added screnshot for look over 
- Home page
- Result





