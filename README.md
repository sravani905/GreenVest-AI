# GreenVest AI

🌱 **Every Rupee Leaves a Footprint.**

GreenVest AI is an India-focused sustainable investment analytics platform that helps users evaluate not only financial returns, but also environmental and ESG impact.

## Features

- 💰 Portfolio value analysis in INR (₹)
- 🌍 Carbon risk exposure calculation
- 🧭 Weighted ESG score tracking
- ⚠️ High-risk asset flagging
- 🤖 AI-style insights and greener suggestions
- 📂 CSV portfolio upload support

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL (usually `http://localhost:8501`).

## CSV format

Your input file should include:

- `ticker` (e.g., `TCS`)
- `quantity` (number of shares)
- `price` (current price in INR)

Example:

```csv
ticker,quantity,price
RELIANCE,10,2950
TCS,5,4100
NTPC,30,340
```

You can also use the included `sample_portfolio.csv`.

## Core idea

**Financial returns + Environmental responsibility = Smarter long-term investing**
