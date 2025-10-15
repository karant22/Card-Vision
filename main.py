import streamlit as st
import pdfplumber
import re
import json
from datetime import datetime
import pandas as pd

class CreditCardParser:
    """Parse credit card statements from multiple issuers"""
    
    def __init__(self):
        self.supported_issuers = [
            "Axis Bank",
            "HDFC Bank",
            "ICICI Bank", 
            "SBI Card",
            "IDFC FIRST Bank"
        ]
        
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return None
    
    def detect_issuer(self, text):
        """Detect which credit card issuer based on text content"""
        text_lower = text.lower()
        
        if "axis bank" in text_lower or "axis ace" in text_lower:
            return "Axis Bank"
        elif "hdfc bank" in text_lower or "hdfc regalia" in text_lower:
            return "HDFC Bank"
        elif "icici bank" in text_lower or "icici card" in text_lower:
            return "ICICI Bank"
        elif "sbi card" in text_lower or "sbi prime" in text_lower:
            return "SBI Card"
        elif "idfc first" in text_lower or "idfc bank" in text_lower:
            return "IDFC FIRST Bank"
        else:
            return "Unknown Issuer"
    
    def extract_card_last_4(self, text):
        """Extract last 4 digits of card"""
        patterns = [
            r'Card\s+[A-Za-z\s]+\(XXXX-XXXX-XXXX-(\d{4})\)',
            r'XXXX-XXXX-XXXX-(\d{4})',
            r'card\s*ending\s*with\s*\d*(\d{4})',
            r'xx\s*(\d{4})',
            r'card.*?xx.*?(\d{4})',
            r'xxxx\s*xxxx\s*xxxx\s*(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Not found"
    
    def extract_statement_period(self, text):
        """Extract billing cycle/statement period"""
        patterns = [
            r'Statement Period\s+(\d{2}\s+[A-Za-z]{3}\s+\d{4})\s*-\s*(\d{2}\s+[A-Za-z]{3}\s+\d{4})',
            r'Statement Period\s+(\d{2}-[A-Za-z]{3}-\d{4})\s*to\s*(\d{2}-[A-Za-z]{3}-\d{4})',
            r'date\s*range[:\s]*(?:upto\s*)?(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})',
            r'statement\s*(?:period|date|cycle)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:to|-)\s*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'billing\s*(?:period|cycle)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:to|-)\s*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'from\s*(\d{2}[/-]\d{2}[/-]\d{4})\s*to\s*(\d{2}[/-]\d{2}[/-]\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if match.lastindex == 1:
                    return f"Upto {match.group(1)}"
                else:
                    return f"{match.group(1)} to {match.group(2)}"
        return "Not found"
    
    def extract_total_due(self, text):
        """Extract total amount due"""
        patterns = [
            r'Total Amount Due\s+INR\s+([\d,]+\.?\d*)',
            r'Total Amount Due\s+(?:Rs\.?|₹)?\s*([\d,]+\.?\d*)',
            r'total\s*(?:amount\s*)?due[:\s]*(?:rs\.?|₹|inr)?\s*([\d,]+\.?\d*)',
            r'amount\s*due[:\s]*(?:rs\.?|₹|inr)?\s*([\d,]+\.?\d*)',
            r'payment\s*due[:\s]*(?:rs\.?|₹|inr)?\s*([\d,]+\.?\d*)',
            r'outstanding\s*(?:amount|balance)[:\s]*(?:rs\.?|₹|inr)?\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"INR {match.group(1)}"
        return "Not found"
    
    def extract_due_date(self, text):
        """Extract payment due date"""
        patterns = [
            r'Payment Due Date\s+(\d{2}\s+[A-Za-z]{3}\s+\d{4})',
            r'Payment Due Date\s+(\d{2}-[A-Za-z]{3}-\d{4})',
            r'due\s*(?:date|by)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'payment\s*due\s*(?:date|by)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'pay\s*by[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Not found"
    
    def extract_statement_date(self, text):
        """Extract statement generation date"""
        patterns = [
            r'Statement Date\s+(\d{2}\s+[A-Za-z]{3}\s+\d{4})',
            r'Statement Date\s+(\d{2}-[A-Za-z]{3}-\d{4})',
            r'statement\s*date[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Not found"
    
    def extract_minimum_due(self, text):
        """Extract minimum amount due"""
        patterns = [
            r'Minimum Amount Due\s+INR\s+([\d,]+\.?\d*)',
            r'Minimum Amount Due\s+(?:Rs\.?|₹)?\s*([\d,]+\.?\d*)',
            r'minimum\s*(?:amount\s*)?due[:\s]*(?:rs\.?|₹|inr)?\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"INR {match.group(1)}"
        return "Not found"
    
    def extract_customer_info(self, text):
        """Extract customer name and ID"""
        info = {}
        
        name_pattern = r'(?:Name|Customer Name)[:\s]+([A-Z][A-Za-z\s]+?)(?:\n|Customer|Card)'
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            info['customer_name'] = name_match.group(1).strip()
        
        id_pattern = r'(?:Customer ID|Account Number)[:\s]+(\d+)'
        id_match = re.search(id_pattern, text, re.IGNORECASE)
        if id_match:
            info['customer_id'] = id_match.group(1)
        
        return info
    
    def extract_transactions(self, text):
        """Extract all transactions from statement"""
        transactions = []
        
        pattern = r'(\d{2}-[A-Za-z]{3}-\d{4})\s+(DEBIT|CREDIT)\s+([A-Za-z\s]+?)\s+([\d,]+\.?\d*)'
        
        matches = re.findall(pattern, text)
        for match in matches:
            transaction = {
                "date": match[0],
                "type": match[1],
                "description": match[2].strip(),
                "amount": f"INR {match[3]}"
            }
            transactions.append(transaction)
        
        return transactions
    
    def extract_sample_transaction(self, text):
        """Extract first transaction as sample"""
        transactions = self.extract_transactions(text)
        
        if transactions:
            return transactions[0]
        
        fallback_pattern = r'(\d{2}[/-]\d{2}[/-]\d{4})\s+([A-Z\s&\-\.]+?)\s+(?:rs\.?|₹|inr)?\s*([\d,]+\.?\d*)'
        fallback_matches = re.findall(fallback_pattern, text, re.IGNORECASE)
        if fallback_matches:
            transaction = fallback_matches[0]
            return {
                "date": transaction[0],
                "description": transaction[1].strip(),
                "amount": f"INR {transaction[2]}"
            }
        
        return {"date": "Not found", "description": "Not found", "amount": "Not found"}
    
    def parse_statement(self, pdf_file):
        """Main parsing function"""
        text = self.extract_text_from_pdf(pdf_file)
        if not text:
            return None
        
        issuer = self.detect_issuer(text)
        customer_info = self.extract_customer_info(text)
        
        result = {
            "issuer": issuer,
            "card_last_4": self.extract_card_last_4(text),
            "statement_date": self.extract_statement_date(text),
            "statement_period": self.extract_statement_period(text),
            "total_due": self.extract_total_due(text),
            "minimum_due": self.extract_minimum_due(text),
            "due_date": self.extract_due_date(text),
            "sample_transaction": self.extract_sample_transaction(text),
            "transaction_count": len(self.extract_transactions(text))
        }
        
        if customer_info:
            result.update(customer_info)
        
        return result


def main():
    st.set_page_config(
        page_title="Card Vision | Statement Parser",
        page_icon="💳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
        <style>
        .stApp {
            background-color: #f0f2f6;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #1e3a5f;
        }
        
        section[data-testid="stSidebar"] > div {
            background-color: #1e3a5f;
        }
        
        section[data-testid="stSidebar"] .element-container {
            color: white;
        }
        
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] label {
            color: white !important;
        }
        
        h1, h2, h3 {
            color: #1e3a5f;
            font-weight: 600;
        }
        
        .stButton button {
            background-color: #2563eb;
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 5px;
            padding: 10px 24px;
        }
        
        .stButton button:hover {
            background-color: #1e40af;
        }
        
        .stDownloadButton button {
            background-color: #059669;
            color: white;
            font-weight: 600;
        }
        
        .stDownloadButton button:hover {
            background-color: #047857;
        }
        
        [data-testid="stMetricValue"] {
            color: #1e3a5f;
            font-weight: 600;
        }
        
        [data-testid="stFileUploader"] {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
        }
        
        .card-vision-logo {
            background: linear-gradient(90deg, #1e3a5f 0%, #2563eb 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        .card-vision-title {
            font-size: 1.8em;   
            font-weight: 700;
            color: white;
            margin: 8px 0 5px 0;
            letter-spacing: 1px;
        }
        
        .card-vision-tagline {
            font-size: 0.85em;
            color: rgba(255, 255, 255, 0.85);
            font-weight: 400;
            margin: 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1e3a5f 0%, #2563eb 100%); 
                    padding: 30px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>Statement Analysis Portal</h1>
            <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;'>
                Secure Digital Banking Services | Document Intelligence System
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("""
            <div class='card-vision-logo'>
                <div style='font-size: 2.5em; margin-bottom: 5px;'>💳</div>
                <div class='card-vision-title'>CARD VISION</div>
                <div class='card-vision-tagline'>Intelligent Statement Analysis</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### Supported Financial Institutions")
        banks = [
            "Axis Bank",
            "HDFC Bank",
            "ICICI Bank",
            "SBI Card",
            "IDFC FIRST Bank"
        ]
        for bank in banks:
            st.markdown(f"• {bank}")
        
        st.markdown("---")
        
        st.markdown("### Data Extraction Points")
        data_points = [
            "Card/Account Number",
            "Statement Date",
            "Statement Period",
            "Total Amount Due",
            "Minimum Amount Due",
            "Payment Due Date",
            "Transaction History",
            "Customer Profile"
        ]
        for i, point in enumerate(data_points, 1):
            st.markdown(f"{i}. {point}")
        
        st.markdown("---")
        st.info("🔒 SECURE: All documents processed locally")
    
    st.markdown("## Document Upload Center")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "UPLOAD STATEMENT DOCUMENTS (PDF FORMAT)",
            type=['pdf'],
            accept_multiple_files=True,
            help="Drag and drop or click to browse files"
        )
        
        if uploaded_files:
            st.success(f"✓ {len(uploaded_files)} document(s) uploaded and ready for processing")
    
    with col2:
        st.markdown("### Processing Options")
        show_raw_text = st.checkbox("Display extracted text", value=False)
        export_format = st.selectbox("Export format", ["JSON", "CSV"])
    
    st.markdown("---")
    
    if uploaded_files:
        if st.button("🔍 INITIATE DOCUMENT ANALYSIS", type="primary", use_container_width=True):
            parser = CreditCardParser()
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.markdown(f"**PROCESSING:** `{uploaded_file.name}`")
                
                result = parser.parse_statement(uploaded_file)
                
                if result:
                    result['filename'] = uploaded_file.name
                    results.append(result)
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.markdown("**✓ ANALYSIS COMPLETE**")
            
            st.markdown("---")
            st.markdown("## Analysis Results")
            
            for idx, result in enumerate(results):
                with st.expander(f"📄 DOCUMENT {idx+1}: {result['filename']}", expanded=True):
                    
                    if 'customer_name' in result or 'customer_id' in result:
                        st.markdown("### Account Holder Information")
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            if 'customer_name' in result:
                                st.markdown(f"**Account Holder:** `{result['customer_name']}`")
                        with col_info2:
                            if 'customer_id' in result:
                                st.markdown(f"**Customer ID:** `{result['customer_id']}`")
                        st.markdown("---")
                    
                    st.markdown("### Financial Summary")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("FINANCIAL INSTITUTION", result['issuer'])
                        st.metric("ACCOUNT NUMBER", f"XXXX-{result['card_last_4']}")
                    
                    with col_b:
                        st.metric("STATEMENT DATE", result['statement_date'])
                        st.metric("STATEMENT PERIOD", result['statement_period'])
                    
                    with col_c:
                        st.metric("TOTAL TRANSACTIONS", result['transaction_count'])
                    
                    col_d, col_e, col_f = st.columns(3)
                    
                    with col_d:
                        st.metric("TOTAL AMOUNT DUE", result['total_due'])
                    
                    with col_e:
                        st.metric("MINIMUM AMOUNT DUE", result['minimum_due'])
                    
                    with col_f:
                        st.metric("PAYMENT DUE DATE", result['due_date'])
                    
                    st.markdown("---")
                    
                    st.markdown("### Sample Transaction Record")
                    trans = result['sample_transaction']
                    
                    if 'type' in trans:
                        trans_df = pd.DataFrame([{
                            'Date': trans['date'],
                            'Type': trans['type'],
                            'Description': trans['description'],
                            'Amount': trans['amount']
                        }])
                        st.dataframe(trans_df, use_container_width=True, hide_index=True)
                    else:
                        trans_data = pd.DataFrame([trans]).T
                        trans_data.columns = ['Value']
                        st.dataframe(trans_data, use_container_width=True)
                    
                    if show_raw_text:
                        uploaded_files[idx].seek(0)
                        raw_text = parser.extract_text_from_pdf(uploaded_files[idx])
                        with st.expander("📝 VIEW EXTRACTED TEXT DATA"):
                            st.code(raw_text[:2000] + "..." if len(raw_text) > 2000 else raw_text)
            
            st.markdown("---")
            st.markdown("## Data Export Center")
            
            col_export1, col_export2, col_export3 = st.columns([2, 2, 1])
            
            with col_export1:
                if export_format == "JSON":
                    json_str = json.dumps(results, indent=2)
                    st.download_button(
                        label="📥 EXPORT AS JSON",
                        data=json_str,
                        file_name=f"cardvision_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col_export2:
                flat_results = []
                for r in results:
                    trans = r['sample_transaction']
                    flat_r = {
                        'Document': r['filename'],
                        'Institution': r['issuer'],
                        'Account_Last4': r['card_last_4'],
                        'Statement_Date': r['statement_date'],
                        'Statement_Period': r['statement_period'],
                        'Total_Due': r['total_due'],
                        'Minimum_Due': r['minimum_due'],
                        'Due_Date': r['due_date'],
                        'Transaction_Count': r['transaction_count'],
                        'Sample_Transaction_Date': trans.get('date', 'N/A'),
                        'Sample_Transaction_Type': trans.get('type', 'N/A'),
                        'Sample_Transaction_Description': trans.get('description', 'N/A'),
                        'Sample_Transaction_Amount': trans.get('amount', 'N/A')
                    }
                    if 'customer_name' in r:
                        flat_r['Customer_Name'] = r['customer_name']
                    if 'customer_id' in r:
                        flat_r['Customer_ID'] = r['customer_id']
                    flat_results.append(flat_r)
                
                df = pd.DataFrame(flat_results)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 EXPORT AS CSV",
                    data=csv,
                    file_name=f"cardvision_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("## Processing Summary")
            
            col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
            with col_sum1:
                st.metric("DOCUMENTS PROCESSED", len(results))
            with col_sum2:
                issuers = list(set([r['issuer'] for r in results]))
                st.metric("UNIQUE INSTITUTIONS", len(issuers))
            with col_sum3:
                successful = len([r for r in results if r['card_last_4'] != 'Not found'])
                st.metric("SUCCESSFUL EXTRACTIONS", successful)
            with col_sum4:
                success_rate = int((successful/len(results))*100) if len(results) > 0 else 0
                st.metric("SUCCESS RATE", f"{success_rate}%")
    
    else:
        st.info("🔒 SYSTEM READY: Please upload your statement documents to begin the analysis process")
        
        col_welcome1, col_welcome2 = st.columns(2)
        
        with col_welcome1:
            st.markdown("### Process Workflow")
            st.markdown("""
            1. **Upload Documents** - Select one or more PDF statement files
            2. **Initiate Analysis** - Click the analysis button to begin processing
            3. **Review Results** - Examine extracted data in organized format
            4. **Export Data** - Download results in JSON or CSV format
            """)
        
        with col_welcome2:
            st.markdown("### System Capabilities")
            st.markdown("""
            • Multi-institution support
            
            • Batch document processing
            
            • Automated data extraction
            
            • Secure local processing
            
            • Multiple export formats
            
            • Real-time status tracking
            """)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #1C6EA4; padding: 20px 0;'>
            <strong>Card Vision v2.0</strong> | Intelligent Statement Analysis Platform<br>
            © 2024 Digital Banking Solutions | All transactions are encrypted and secure
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()