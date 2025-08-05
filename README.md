# Reimbursement Management System

A web application for managing employee reimbursement claims with Excel report generation.

## Installation

### Prerequisites
- Python 3.9 or higher
- `uv` package manager

### Quick Setup

1. **Install UV** (if not already installed):
   ```bash
   # On macOS and Linux:
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows:
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and start the application**:
   ```bash
   cd reim-form
   
   # Quick start (recommended):
   ./start.sh           # macOS/Linux
   start.bat            # Windows
   
   # OR manual setup:
   uv venv
   uv sync
   uv run python setup.py
   uv run python app.py
   ```

3. **Open your browser**: Go to `http://localhost:5001`

## How to Use

### 1. Create a Claim
- Enter expense details (dates, amount, currency, category)
- Add optional alias name for easy identification
- Upload receipt/invoice (PDF, JPG, PNG)
- Provide business justification

### 2. Add Individual Items
- Break down total expense into line items
- System validates that item totals match claim total
- Each item inherits the claim's expense category

### 3. Generate Reports
- Go to "Reports" section
- Select claims by month or comprehensive export
- Choose report type:
  - **ISD Reimbursement Form**: Professional Excel format
  - **Financial Export**: CSV with detailed breakdown
  - **Comprehensive Report**: ZIP with Excel, CSV, and receipts

## What to Expect (Output Files)

### ISD Reimbursement Form (Excel)
- Multi-month support with separate sections
- Automatic currency totals (HKD, USD, EUR, RMB, GBP, JPY)
- Example: `ISD_Reimbursement_January_2025.xlsx`

### Financial Export (CSV)
- Detailed claim summaries with all metadata
- Ordered and Organised for smooth input experience for FO online expense form
- Example: `financial_expense_2025-01.csv`
