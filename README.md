# 🚗 Sales Data Analyzer

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful sales analytics tool with AI-powered insights and projections.

## Features

- **Data Analysis**
  - Sales summaries and trends
  - Regional performance breakdowns
  - Year-over-year growth metrics

- **AI Insights**
  - 3-year sales projections
  - Natural language query support
  - Market trend analysis

- **Technical Highlights**
  - Verified Groq/Llama3 integration
  - Cryptographic call verification
  - Full audit logging

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/krish777/Sales-Data-Analyzer.git
cd Sales-Data-Analyzer

2. Set up environment:

python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

3. Install dependencies

pip install -r requirements.txt

4. Add your Groq API key:

echo "GROQ_API_KEY=your_key_here" > .env

5. Run the analyzer:

python main.py

6. python main.py

7. Data Format

Prepare your CSV file (data/car_sales.csv):

Year,Make,Model,Quantity,Region,Price
2023,Toyota,Camry,15000,North,25000
2023,Ford,F-150,18000,West,32000
...
Usage:

python main.py [--debug] [--test-llm]

Troubleshooting
Common Issues:

GROQ_API_KEY not found: Verify your .env file

Missing columns: Check CSV format requirements

LLM connection issues: Test with python -m llm_verifier

