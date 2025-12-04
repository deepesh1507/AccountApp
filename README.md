# AccountApp - Professional ERP & Accounting System

A comprehensive ERP and Accounting application built with Python and CustomTkinter, featuring multi-company management, financial modules, and modern UI.

## Features

- 🏢 **Multi-Company Management** - Create and manage multiple companies
- 📊 **Financial Modules** - Chart of Accounts, Journal Entries, Ledger
- 📈 **ERP Modules** - FI (Financial Accounting), CO (Controlling), and Integration modules
- 💼 **Business Management** - Clients, Vendors, Invoices, Expenses
- 📦 **Inventory Management** - Track products and stock
- 📋 **Reports & Analytics** - Comprehensive financial reporting
- 🎨 **Modern UI** - Clean, responsive interface with CustomTkinter

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/AccountApp.git
cd AccountApp
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
AccountApp/
├── main.py                 # Application entry point
├── modules/               # Application modules
│   ├── home_screen.py
│   ├── create_company.py
│   ├── select_company.py
│   ├── edit_company.py
│   ├── dashboard.py
│   ├── chart_of_accounts.py
│   ├── journal_entries.py
│   ├── ledger.py
│   ├── clients.py
│   ├── vendors.py
│   ├── invoice.py
│   ├── expenses.py
│   ├── inventory.py
│   ├── reports.py
│   └── erp/              # ERP modules
├── data/                  # Application data
└── requirements.txt       # Python dependencies
```

## Requirements

- Python 3.8+
- CustomTkinter
- Pillow
- Other dependencies listed in requirements.txt

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Deepesh Patel

## Acknowledgments

- Built with CustomTkinter
- Inspired by enterprise ERP systems like SAP and Tally
