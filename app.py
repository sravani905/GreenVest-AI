import io
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
import streamlit as st

st.set_page_config(page_title="GreenVest AI", page_icon="🌱", layout="wide")


@dataclass
class AssetProfile:
    esg_score: float
    carbon_risk: float
    sector: str


ASSET_DB: Dict[str, AssetProfile] = {
    "RELIANCE": AssetProfile(52, 74, "Energy"),
    "TCS": AssetProfile(81, 24, "IT"),
    "INFY": AssetProfile(84, 21, "IT"),
    "HDFCBANK": AssetProfile(78, 19, "Financials"),
    "ICICIBANK": AssetProfile(75, 23, "Financials"),
    "LT": AssetProfile(66, 48, "Industrials"),
    "ADANIENT": AssetProfile(41, 82, "Conglomerate"),
    "NTPC": AssetProfile(49, 88, "Power"),
    "TATAMOTORS": AssetProfile(62, 54, "Auto"),
    "SUNPHARMA": AssetProfile(77, 17, "Healthcare"),
}

DEFAULT_ESG = 60
DEFAULT_CARBON = 45


REQUIRED_COLUMNS = {"ticker", "quantity", "price"}


st.title("🌱 GreenVest AI")
st.caption("Every Rupee Leaves a Footprint.")

st.markdown(
    """
Upload your portfolio as CSV to analyze:
- total value in INR (₹)
- weighted ESG score
- carbon risk exposure
- high-risk assets
- AI-style greener alternatives

**Expected columns:** `ticker`, `quantity`, `price`
"""
)


def normalize_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df = df.copy()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    df = df.dropna(subset=["ticker", "quantity", "price"])
    df = df[df["quantity"] > 0]
    df = df[df["price"] > 0]

    if df.empty:
        raise ValueError("Portfolio has no valid rows after cleaning.")

    return df


def enrich_assets(df: pd.DataFrame) -> pd.DataFrame:
    def get_profile(ticker: str) -> AssetProfile:
        return ASSET_DB.get(ticker, AssetProfile(DEFAULT_ESG, DEFAULT_CARBON, "Unknown"))

    profiles = df["ticker"].map(get_profile)
    enriched = df.copy()
    enriched["esg_score"] = profiles.map(lambda p: p.esg_score)
    enriched["carbon_risk"] = profiles.map(lambda p: p.carbon_risk)
    enriched["sector"] = profiles.map(lambda p: p.sector)
    enriched["value"] = enriched["quantity"] * enriched["price"]
    enriched["risk_flag"] = enriched["carbon_risk"].apply(
        lambda x: "High" if x >= 70 else "Medium" if x >= 40 else "Low"
    )
    return enriched


def summarize(df: pd.DataFrame) -> Dict[str, float]:
    total_value = df["value"].sum()
    weighted_esg = (df["esg_score"] * df["value"]).sum() / total_value
    weighted_carbon = (df["carbon_risk"] * df["value"]).sum() / total_value
    high_risk_share = (df.loc[df["risk_flag"] == "High", "value"].sum() / total_value) * 100
    return {
        "total_value": total_value,
        "weighted_esg": weighted_esg,
        "weighted_carbon": weighted_carbon,
        "high_risk_share": high_risk_share,
    }


def ai_insights(df: pd.DataFrame, stats: Dict[str, float]) -> List[str]:
    messages: List[str] = []
    if stats["weighted_esg"] < 60:
        messages.append(
            "Your weighted ESG score is below 60. Consider increasing allocation to higher-ESG sectors like IT and Healthcare."
        )
    else:
        messages.append("Your weighted ESG score is healthy. Keep monitoring sector concentration.")

    if stats["weighted_carbon"] > 55:
        messages.append(
            "Carbon exposure is elevated. Reduce holdings in high-carbon assets and rebalance toward lower-carbon companies."
        )

    high_risk_assets = df[df["risk_flag"] == "High"].sort_values("value", ascending=False)
    if not high_risk_assets.empty:
        top = ", ".join(high_risk_assets["ticker"].head(3).tolist())
        messages.append(f"Top high-risk contributors: {top}.")

    greener_universe = [
        (t, p)
        for t, p in ASSET_DB.items()
        if p.esg_score >= 75 and p.carbon_risk <= 25
    ]
    if greener_universe:
        picks = ", ".join([t for t, _ in greener_universe[:4]])
        messages.append(f"Greener alternatives to explore: {picks}.")

    return messages


example_csv = """ticker,quantity,price
RELIANCE,10,2950
TCS,5,4100
NTPC,30,340
SUNPHARMA,8,1650
"""

uploaded = st.file_uploader("Upload portfolio CSV", type=["csv"])
use_sample = st.checkbox("Use sample portfolio", value=not bool(uploaded))

raw_df = None
if uploaded:
    raw_df = pd.read_csv(uploaded)
elif use_sample:
    raw_df = pd.read_csv(io.StringIO(example_csv))

if raw_df is not None:
    try:
        cleaned = normalize_portfolio(raw_df)
        portfolio = enrich_assets(cleaned)
        stats = summarize(portfolio)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Portfolio Value", f"₹{stats['total_value']:,.0f}")
        c2.metric("Avg ESG Score", f"{stats['weighted_esg']:.1f}")
        c3.metric("Carbon Risk", f"{stats['weighted_carbon']:.1f}")
        c4.metric("High-Risk Share", f"{stats['high_risk_share']:.1f}%")

        left, right = st.columns([2, 1])

        with left:
            st.subheader("Portfolio Breakdown")
            st.dataframe(
                portfolio[
                    [
                        "ticker",
                        "sector",
                        "quantity",
                        "price",
                        "value",
                        "esg_score",
                        "carbon_risk",
                        "risk_flag",
                    ]
                ].sort_values("value", ascending=False),
                use_container_width=True,
            )

            sector_view = (
                portfolio.groupby("sector", as_index=False)["value"].sum().sort_values("value", ascending=False)
            )
            st.subheader("Sector Allocation")
            st.bar_chart(sector_view.set_index("sector"))

        with right:
            st.subheader("🤖 AI Insights")
            for msg in ai_insights(portfolio, stats):
                st.info(msg)

            st.subheader("Risk Distribution")
            risk_view = portfolio.groupby("risk_flag", as_index=False)["value"].sum()
            st.dataframe(risk_view, use_container_width=True, hide_index=True)

    except ValueError as exc:
        st.error(str(exc))
else:
    st.warning("Upload a CSV or enable sample portfolio to begin.")
