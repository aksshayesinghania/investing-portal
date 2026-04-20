"""
╔══════════════════════════════════════════════════════════════╗
║     SAFAL NIVESHAK MASTERMIND — VALUE INVESTING PORTAL      ║
║     Type a company name. Get a full value investing report. ║
╚══════════════════════════════════════════════════════════════╝

SETUP (one time):
    pip3 install streamlit yfinance pandas

RUN:
    python3 -m streamlit run investing_portal.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import math
from curl_cffi import requests as curl_requests

# Impersonate a real Chrome browser to bypass Yahoo Finance bot detection
_session = curl_requests.Session(impersonate="chrome110")

st.set_page_config(
    page_title="Value Investing Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    .stApp { background-color: #f0f2f6 !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Top banner */
    .portal-header {
        background: linear-gradient(135deg, #0f2444 0%, #1a3a6e 100%);
        border-radius: 14px;
        padding: 26px 32px;
        margin-bottom: 22px;
        color: white;
    }
    .portal-header h1 { color: white; font-size: 24px; font-weight: 800; margin: 0 0 4px 0; }
    .portal-header p  { color: #a8c4e0; font-size: 13px; margin: 0; }

    /* White cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 16px;
        border: 1px solid #e4e8ef;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    /* Company name block */
    .company-name { font-size: 22px; font-weight: 800; color: #0f2444; margin: 0 0 3px 0; }
    .company-meta { font-size: 12px; color: #6b7a99; margin: 0 0 10px 0; }
    .company-desc { font-size: 12px; color: #4a5568; line-height: 1.6; border-top: 1px solid #f0f2f6; padding-top: 10px; margin-top: 6px; }
    .price-big    { font-size: 30px; font-weight: 800; color: #0f2444; }
    .price-label  { font-size: 11px; color: #9aa5b4; margin-top: 2px; }
    .price-sub    { font-size: 12px; color: #6b7a99; margin-top: 10px; line-height: 1.8; }

    /* Section headers */
    .sec-head {
        font-size: 13px;
        font-weight: 700;
        color: #0f2444;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        padding: 8px 0 6px 0;
        border-bottom: 2px solid #e4e8ef;
        margin: 18px 0 8px 0;
    }

    /* Metric rows */
    .mrow {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        border-radius: 7px;
        margin: 3px 0;
        background: #f8f9fc;
    }
    .mrow:hover { background: #eef1f8; }
    .mlabel { font-size: 12px; color: #4a5568; font-weight: 500; }
    .mval   { font-size: 13px; font-weight: 700; color: #1a202c; }
    .mval.g { color: #16a34a; }
    .mval.r { color: #dc2626; }
    .mval.a { color: #d97706; }
    .mnote  { font-size: 10px; color: #9aa5b4; margin-left: 5px; font-weight: 400; }

    /* DCF cards */
    .dcf-card  { background: #f8f9fc; border-radius: 10px; padding: 18px; border: 1px solid #e4e8ef; }
    .dcf-title { font-size: 13px; font-weight: 700; color: #0f2444; margin-bottom: 2px; }
    .dcf-sub   { font-size: 10px; color: #9aa5b4; margin-bottom: 14px; }
    .dcf-iv    { font-size: 26px; font-weight: 800; color: #0f2444; margin: 6px 0; }
    .dcf-line  { font-size: 12px; color: #4a5568; margin: 3px 0; }
    .dcf-line span { font-weight: 700; color: #16a34a; }

    /* Verdict */
    .v-buy  { background: #f0fdf4; border: 2px solid #16a34a; border-radius: 10px; padding: 14px 20px; color: #15803d; font-weight: 700; font-size: 15px; text-align: center; }
    .v-sbuy { background: #dcfce7; border: 2px solid #15803d; border-radius: 10px; padding: 14px 20px; color: #14532d; font-weight: 700; font-size: 15px; text-align: center; }
    .v-wtch { background: #fffbeb; border: 2px solid #f59e0b; border-radius: 10px; padding: 14px 20px; color: #92400e; font-weight: 700; font-size: 15px; text-align: center; }
    .v-avd  { background: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 14px 20px; color: #991b1b; font-weight: 700; font-size: 15px; text-align: center; }

    /* Checklist */
    .chk { display: flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 7px; margin: 2px 0; font-size: 12px; font-weight: 500; }
    .chk.ok { background: #f0fdf4; color: #15803d; }
    .chk.no { background: #f8f9fc; color: #9aa5b4; }

    /* Streamlit metric override */
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid #e4e8ef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    div[data-testid="metric-container"] label {
        color: #6b7a99 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.4px !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0f2444 !important;
        font-size: 19px !important;
        font-weight: 800 !important;
    }

    /* Search */
    .stTextInput input {
        font-size: 15px !important;
        padding: 11px 16px !important;
        border-radius: 9px !important;
        border: 2px solid #e4e8ef !important;
        background: white !important;
        color: #1a202c !important;
    }
    .stTextInput input:focus {
        border-color: #1a3a6e !important;
        box-shadow: 0 0 0 3px rgba(26,58,110,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
#  TICKER RESOLVER
# ─────────────────────────────────────────────────
INDIAN_MAP = {
    "reliance": "RELIANCE.NS", "tcs": "TCS.NS", "infosys": "INFY.NS",
    "hdfc bank": "HDFCBANK.NS", "hdfcbank": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS", "icicibank": "ICICIBANK.NS",
    "wipro": "WIPRO.NS", "hcl": "HCLTECH.NS", "hcltech": "HCLTECH.NS",
    "bajaj finance": "BAJFINANCE.NS", "bajajfinance": "BAJFINANCE.NS",
    "asian paints": "ASIANPAINT.NS", "asianpaint": "ASIANPAINT.NS",
    "itc": "ITC.NS", "kotak": "KOTAKBANK.NS", "kotakbank": "KOTAKBANK.NS",
    "sbi": "SBIN.NS", "state bank": "SBIN.NS",
    "larsen": "LT.NS", "l&t": "LT.NS", "lt": "LT.NS",
    "maruti": "MARUTI.NS", "hero motocorp": "HEROMOTOCO.NS",
    "hero": "HEROMOTOCO.NS", "bajaj auto": "BAJAJ-AUTO.NS",
    "titan": "TITAN.NS", "nestle india": "NESTLEIND.NS", "nestle": "NESTLEIND.NS",
    "britannia": "BRITANNIA.NS", "hindustan unilever": "HINDUNILVR.NS",
    "hul": "HINDUNILVR.NS", "hindunilvr": "HINDUNILVR.NS",
    "dmart": "DMART.NS", "avenue supermarts": "DMART.NS",
    "pidilite": "PIDILITIND.NS", "berger paints": "BERGEPAINT.NS",
    "tata motors": "TATAMOTORS.NS", "tatamotors": "TATAMOTORS.NS",
    "tata steel": "TATASTEEL.NS", "sun pharma": "SUNPHARMA.NS",
    "dr reddy": "DRREDDY.NS", "cipla": "CIPLA.NS",
    "divis": "DIVISLAB.NS", "ultratech": "ULTRACEMCO.NS",
    "eicher": "EICHERMOT.NS", "royal enfield": "EICHERMOT.NS",
    "zomato": "ZOMATO.NS", "paytm": "PAYTM.NS", "nykaa": "NYKAA.NS",
    "mrf": "MRF.NS", "page industries": "PAGEIND.NS",
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL",
    "alphabet": "GOOGL", "amazon": "AMZN", "tesla": "TSLA",
    "meta": "META", "nvidia": "NVDA", "netflix": "NFLX",
    "berkshire": "BRK-B", "jpmorgan": "JPM", "visa": "V",
}

def resolve_ticker(query: str):
    q = query.strip()
    q_lower = q.lower()
    if q_lower in INDIAN_MAP:
        return INDIAN_MAP[q_lower]
    if "." not in q:
        for suffix in [".NS", ".BO", ""]:
            ticker = q.upper() + suffix
            try:
                info = yf.Ticker(ticker, session=_session).info
                if info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose"):
                    return ticker
            except Exception:
                continue
    return q.upper()


# ─────────────────────────────────────────────────
#  DATA FETCHER
# ─────────────────────────────────────────────────
def get_stmt(stmt, row_name, col=0, default=0):
    try:
        if stmt is None or stmt.empty:
            return default
        if row_name in stmt.index:
            val = stmt.loc[row_name].iloc[col]
            return float(val) if pd.notna(val) else default
        matches = [i for i in stmt.index if row_name.lower() in i.lower()]
        if matches:
            val = stmt.loc[matches[0]].iloc[col]
            return float(val) if pd.notna(val) else default
        return default
    except Exception:
        return default

def fetch(ticker_symbol: str) -> dict:
    t = yf.Ticker(ticker_symbol, session=_session)
    info = t.info or {}
    try:
        inc = t.financials
        bs  = t.balance_sheet
        cf  = t.cashflow
    except Exception:
        inc = bs = cf = pd.DataFrame()

    revenue  = get_stmt(inc, "Total Revenue")
    cogs     = get_stmt(inc, "Cost Of Revenue")
    gp       = get_stmt(inc, "Gross Profit")
    op       = get_stmt(inc, "Operating Income")
    ebit     = get_stmt(inc, "EBIT") or op
    np_      = get_stmt(inc, "Net Income")
    int_exp  = abs(get_stmt(inc, "Interest Expense") or 0)
    tax_exp  = get_stmt(inc, "Tax Provision") or get_stmt(inc, "Income Tax Expense")
    pretax   = get_stmt(inc, "Pretax Income")
    depr     = abs(get_stmt(inc, "Reconciled Depreciation") or get_stmt(inc, "Depreciation") or 0)
    tax_rate = max(0, min(0.5, tax_exp / pretax)) if pretax and pretax != 0 and tax_exp else 0.25

    ta_c  = get_stmt(bs, "Total Assets")
    ta_p  = get_stmt(bs, "Total Assets", col=1) or ta_c
    ca    = get_stmt(bs, "Current Assets")
    cl    = get_stmt(bs, "Current Liabilities")
    cash  = get_stmt(bs, "Cash And Cash Equivalents") or get_stmt(bs, "Cash") or 0
    sti   = get_stmt(bs, "Short Term Investments") or 0
    rec   = get_stmt(bs, "Receivables") or get_stmt(bs, "Net Receivables") or 0
    inv   = get_stmt(bs, "Inventory") or 0
    inv_p = get_stmt(bs, "Inventory", col=1) or inv
    ppe   = get_stmt(bs, "Net PPE") or get_stmt(bs, "Property Plant Equipment") or 0
    ppe_p = get_stmt(bs, "Net PPE", col=1) or ppe
    debt  = get_stmt(bs, "Total Debt") or (get_stmt(bs, "Long Term Debt") + get_stmt(bs, "Current Debt"))
    eq    = get_stmt(bs, "Stockholders Equity") or get_stmt(bs, "Total Equity Gross Minority Interest") or 0
    eq_p  = get_stmt(bs, "Stockholders Equity", col=1) or eq
    pay   = get_stmt(bs, "Accounts Payable") or 0
    pay_p = get_stmt(bs, "Accounts Payable", col=1) or pay

    ocf   = get_stmt(cf, "Operating Cash Flow") or get_stmt(cf, "Cash From Operations") or 0
    capex = abs(get_stmt(cf, "Capital Expenditure") or get_stmt(cf, "Purchase Of PP And E") or 0)

    price   = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0
    shares  = info.get("sharesOutstanding") or 0
    mktcap  = info.get("marketCap") or (price * shares)
    eps     = info.get("trailingEps") or 0
    bvps    = info.get("bookValue") or (eq / shares if eq and shares else 0)
    pe      = info.get("trailingPE") or 0
    fpe     = info.get("forwardPE") or 0
    eg5     = (info.get("earningsGrowth") or 0) * 100
    curr    = info.get("currency", "USD")
    cs      = "₹" if curr == "INR" else "$"

    net_debt = debt - cash
    avg_ta   = (ta_c + ta_p) / 2
    avg_eq   = (eq + eq_p) / 2
    avg_inv  = (inv + inv_p) / 2
    avg_ppe  = (ppe + ppe_p) / 2
    avg_pay  = (pay + pay_p) / 2
    wc       = ca - cl

    return dict(
        name=info.get("longName") or info.get("shortName") or ticker_symbol,
        ticker=ticker_symbol, sector=info.get("sector","N/A"),
        industry=info.get("industry","N/A"), country=info.get("country","N/A"),
        desc=(info.get("longBusinessSummary","")[:360]+"...") if info.get("longBusinessSummary","") else "",
        currency=curr, cs=cs,
        revenue=revenue, cogs=cogs, gp=gp, op=op, ebit=ebit, np_=np_,
        int_exp=int_exp, tax_rate=tax_rate, depr=depr,
        ta=ta_c, ca=ca, cl=cl, cash=cash, sti=sti, rec=rec,
        inv=inv, ppe=ppe, debt=debt, eq=eq, pay=pay,
        avg_ta=avg_ta, avg_eq=avg_eq, avg_inv=avg_inv,
        avg_ppe=avg_ppe, avg_pay=avg_pay, wc=wc,
        ocf=ocf, capex=capex, fcf=ocf-capex, depr_cf=depr,
        price=price, shares=shares, mktcap=mktcap, eps=eps,
        bvps=bvps, pe=pe, fpe=fpe, eg5=eg5,
        net_debt=net_debt,
        w52h=info.get("fiftyTwoWeekHigh"),
        w52l=info.get("fiftyTwoWeekLow"),
        beta=info.get("beta"),
    )


# ─────────────────────────────────────────────────
#  CALCULATIONS
# ─────────────────────────────────────────────────
def sd(a, b, default=None):
    try:
        return a / b if b and b != 0 else default
    except Exception:
        return default

def calc(d):
    r = {}
    days = 365

    r["inv_t"]  = sd(d["cogs"], d["avg_inv"])
    r["inv_d"]  = sd(days, r["inv_t"])
    r["rec_t"]  = sd(d["revenue"], d["rec"])
    r["rec_d"]  = sd(days, r["rec_t"])
    r["pay_t"]  = sd(d["cogs"], d["avg_pay"])
    r["pay_d"]  = sd(days, r["pay_t"])
    r["fa_t"]   = sd(d["revenue"], d["avg_ppe"])
    r["ta_t"]   = sd(d["revenue"], d["avg_ta"])
    r["wc_t"]   = sd(d["revenue"], d["wc"]) if d["wc"] != 0 else None
    r["ccc"]    = (r["inv_d"] + r["rec_d"] - r["pay_d"]) if all([r["inv_d"], r["rec_d"], r["pay_d"]]) else None

    r["cr"]  = sd(d["ca"], d["cl"])
    r["qr"]  = sd(d["cash"] + d["sti"] + d["rec"], d["cl"])

    r["dte"]  = sd(d["debt"], d["eq"])
    r["dta"]  = sd(d["debt"], d["ta"])
    r["dtc"]  = sd(d["debt"], d["debt"] + d["eq"])
    r["fl"]   = sd(d["avg_ta"], d["avg_eq"])
    r["ic"]   = sd(d["ebit"], d["int_exp"]) if d["int_exp"] else None

    r["gm"]   = sd(d["gp"], d["revenue"], 0) * 100 if d["revenue"] else None
    r["om"]   = sd(d["op"], d["revenue"], 0) * 100 if d["revenue"] else None
    r["nm"]   = sd(d["np_"], d["revenue"], 0) * 100 if d["revenue"] else None
    adj       = d["np_"] + d["int_exp"] * (1 - d["tax_rate"])
    r["roa"]  = sd(adj, d["avg_ta"], 0) * 100 if d["avg_ta"] else None
    r["roce"] = sd(d["ebit"], d["debt"] + d["eq"], 0) * 100
    r["roe"]  = sd(d["np_"], d["avg_eq"], 0) * 100 if d["avg_eq"] else None
    r["dupont"] = None
    if r["nm"] and r["ta_t"] and r["fl"]:
        r["dupont"] = (r["nm"] / 100) * r["ta_t"] * r["fl"] * 100

    r["fcf"]   = d["fcf"]
    r["fcf_y"] = sd(d["fcf"], d["mktcap"], 0) * 100 if d["mktcap"] else None
    r["oe"]    = d["np_"] + d["depr_cf"] - d["capex"] * 0.6

    r["pe"]   = d["pe"] or sd(d["price"], d["eps"])
    r["fpe"]  = d["fpe"]
    r["peg"]  = sd(r["pe"], d["eg5"]) if d["eg5"] and r["pe"] else None
    r["pbv"]  = sd(d["price"], d["bvps"]) if d["bvps"] else None
    r["pcf"]  = sd(d["mktcap"], d["ocf"]) if d["ocf"] else None
    r["ps"]   = sd(d["mktcap"], d["revenue"]) if d["revenue"] else None
    r["ey"]   = sd(d["eps"], d["price"], 0) * 100 if d["price"] else None
    r["ev"]   = d["mktcap"] + d["net_debt"]
    r["eveb"] = sd(r["ev"], d["op"]) if d["op"] else None
    r["gn"]   = math.sqrt(22.5 * d["eps"] * d["bvps"]) if d["eps"] and d["bvps"] and d["eps"] > 0 and d["bvps"] > 0 else None

    if d["fcf"] > 0 and d["shares"] > 0:
        r["dcf_base"] = run_dcf(d["fcf"], 0.12, 0.08, 0.02, 0.12, d["net_debt"], d["shares"])
        r["dcf_cons"] = run_dcf(d["fcf"], 0.08, 0.05, 0.01, 0.12, d["net_debt"], d["shares"])
        if d["mktcap"] > 0:
            r["rdcf"] = reverse_dcf(d["mktcap"], d["fcf"], d["net_debt"])
        else:
            r["rdcf"] = None
    else:
        r["dcf_base"] = r["dcf_cons"] = r["rdcf"] = None

    if r["dcf_base"] and d["price"] > 0:
        iv = r["dcf_base"]["ps"]
        r["mos"] = (iv - d["price"]) / iv * 100 if iv > 0 else None
    else:
        r["mos"] = None

    return r

def run_dcf(fcf, g1, g2, gt, dr, net_debt, shares):
    pv = 0
    f = fcf
    for yr in range(1, 6):
        f *= (1 + g1); pv += f / (1 + dr) ** yr
    for yr in range(6, 11):
        f *= (1 + g2); pv += f / (1 + dr) ** yr
    tv = f * (1 + gt) / (dr - gt) if dr > gt else 0
    total = pv + tv / (1 + dr) ** 10
    ps = (total - net_debt) / shares if shares else 0
    return {"ps": ps, "b30": ps * 0.7, "b50": ps * 0.5, "total": total}

def reverse_dcf(mktcap, fcf, net_debt, dr=0.12, gt=0.02):
    target = mktcap + net_debt
    lo, hi = -0.3, 2.0
    mid = 0.1
    for _ in range(80):
        mid = (lo + hi) / 2
        res = run_dcf(fcf, mid, mid * 0.75, gt, dr, 0, 1)
        if abs(res["total"] - target) / max(abs(target), 1) < 0.005:
            break
        if res["total"] < target:
            lo = mid
        else:
            hi = mid
    if mid > 0.30:
        label = "🔴 Priced for perfection — market expects >30% FCF growth"
    elif mid >= 0.10:
        label = "🟡 Fairly priced — market expects 10–30% FCF growth"
    else:
        label = "🟢 Potentially undervalued — market expects <10% FCF growth"
    return {"g1": mid * 100, "g2": mid * 75, "label": label}


# ─────────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────────
def fmt(val, d=1, pfx=""):
    if val is None:
        return "—"
    try:
        v = abs(val)
        sign = "-" if val < 0 else ""
        if v >= 1e12: return f"{sign}{pfx}{v/1e12:.{d}f}T"
        if v >= 1e9:  return f"{sign}{pfx}{v/1e9:.{d}f}B"
        if v >= 1e6:  return f"{sign}{pfx}{v/1e6:.{d}f}M"
        if v >= 1e3:  return f"{sign}{pfx}{v/1e3:.{d}f}K"
        return f"{sign}{pfx}{v:.{d}f}"
    except Exception:
        return "—"

def row(label, value, suffix="", prefix="", good_above=None, good_below=None, note=""):
    """Render a metric row. Skips silently if value is None."""
    if value is None:
        return
    if isinstance(value, str):
        # Already formatted (e.g. from fmt())
        val_str = f"{prefix}{value}{suffix}"
        color_cls = ""
    else:
        val_str = f"{prefix}{value:.1f}{suffix}"
        color_cls = ""
        if good_above is not None:
            color_cls = "g" if value >= good_above else ("a" if value >= good_above * 0.7 else "r")
        elif good_below is not None:
            color_cls = "g" if value <= good_below else ("a" if value <= good_below * 1.4 else "r")
    note_html = f'<span class="mnote">{note}</span>' if note else ""
    st.markdown(f"""
    <div class="mrow">
        <span class="mlabel">{label}</span>
        <span class="mval {color_cls}">{val_str}{note_html}</span>
    </div>""", unsafe_allow_html=True)

def sec(title, icon=""):
    st.markdown(f'<div class="sec-head">{icon}&nbsp; {title}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="portal-header">
        <h1>📊 Value Investing Portal</h1>
        <p>Safal Niveshak Mastermind &nbsp;·&nbsp; Ratios · DCF Valuation · Margin of Safety · Moat Checklist</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1:
        query = st.text_input("", placeholder="Type a company or ticker — e.g. Infosys, AAPL, Asian Paints, Tesla...", label_visibility="collapsed")
    with c2:
        go = st.button("Analyze →", type="primary", use_container_width=True)

    st.caption("🇮🇳 Indian: Reliance · HDFC Bank · Asian Paints · Bajaj Finance · Infosys · ITC · TCS     🇺🇸 US: Apple · Microsoft · Google · Tesla")

    if not (go and query):
        st.markdown("""
        <div style='text-align:center; padding:80px 20px; color:#9aa5b4'>
            <div style='font-size:52px'>📈</div>
            <div style='font-size:17px; font-weight:700; color:#6b7a99; margin-top:12px'>Enter a company above to get started</div>
            <div style='font-size:12px; margin-top:6px'>Full value investing analysis — ratios, DCF, margin of safety, moat checklist</div>
        </div>""", unsafe_allow_html=True)
        return

    ticker = resolve_ticker(query)
    st.caption(f"Looking up: **{ticker}**")

    with st.spinner("Fetching data from Yahoo Finance..."):
        try:
            d = fetch(ticker)
        except Exception as e:
            st.error(f"Could not fetch data for '{ticker}'. Try the exact ticker symbol (e.g. RELIANCE.NS)")
            return

    if not d["price"]:
        st.warning(f"No data found for '{ticker}'. Try: RELIANCE.NS · HDFCBANK.NS · AAPL · MSFT")
        return

    with st.spinner("Running calculations..."):
        r = calc(d)

    cs = d["cs"]

    # ── COMPANY HEADER ────────────────────────────────────────
    col_info, col_price = st.columns([3, 1])
    with col_info:
        st.markdown(f"""
        <div class="card">
            <div class="company-name">{d['name']}</div>
            <div class="company-meta">{d['ticker']} &nbsp;·&nbsp; {d['sector']} &nbsp;·&nbsp; {d['industry']} &nbsp;·&nbsp; {d['country']}</div>
            {f'<div class="company-desc">{d["desc"]}</div>' if d['desc'] else ''}
        </div>""", unsafe_allow_html=True)

    with col_price:
        w52_html = ""
        if d['w52l'] and d['w52h']:
            w52_html = f"""
            <div class="price-sub">
                52W Low &nbsp; <strong>{cs}{d['w52l']:,.0f}</strong><br>
                52W High &nbsp; <strong>{cs}{d['w52h']:,.0f}</strong>
                {f"<br>Beta &nbsp; <strong>{d['beta']:.2f}</strong>" if d.get('beta') else ""}
            </div>"""
        st.markdown(f"""
        <div class="card" style="text-align:right">
            <div class="price-big">{cs}{d['price']:,.2f}</div>
            <div class="price-label">Current Market Price</div>
            {w52_html}
        </div>""", unsafe_allow_html=True)

    # ── KPI STRIP ─────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1: st.metric("Market Cap",       fmt(d["mktcap"], pfx=cs))
    with k2: st.metric("P/E Ratio",        f"{r['pe']:.1f}x"   if r['pe']  else "—")
    with k3: st.metric("ROE",              f"{r['roe']:.1f}%"  if r['roe'] else "—")
    with k4: st.metric("Net Margin",       f"{r['nm']:.1f}%"   if r['nm']  else "—")
    with k5: st.metric("Free Cash Flow",   fmt(d["fcf"], pfx=cs))
    with k6: st.metric("Margin of Safety", f"{r['mos']:.1f}%"  if r['mos'] is not None else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LEFT / RIGHT PANELS ───────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        sec("Activity Ratios", "⚙️")
        if r["inv_t"] is not None:
            row("Inventory Turnover", r["inv_t"], suffix="x")
        if r["inv_d"] is not None:
            row("Inventory Days", r["inv_d"], suffix=" days", good_below=60)
        if r["rec_d"] is not None:
            row("Receivable Days", r["rec_d"], suffix=" days", good_below=45)
        if r["pay_d"] is not None:
            row("Payable Days", r["pay_d"], suffix=" days")
        if r["ccc"] is not None:
            row("Cash Conversion Cycle", r["ccc"], suffix=" days", good_below=0, note="negative = great")
        if r["ta_t"] is not None:
            row("Total Asset Turnover", r["ta_t"], suffix="x")
        if r["fa_t"] is not None:
            row("Fixed Asset Turnover", r["fa_t"], suffix="x")

        sec("Liquidity", "💧")
        if r["cr"] is not None:
            row("Current Ratio", r["cr"], good_above=1.5, note=">1.5 = healthy")
        if r["qr"] is not None:
            row("Quick Ratio", r["qr"], good_above=1.0, note=">1.0 = healthy")

        sec("Solvency", "🏦")
        if r["dte"] is not None:
            row("Debt / Equity", r["dte"], good_below=1.0, note="<1 = safe")
        if r["dta"] is not None:
            row("Debt / Assets", r["dta"], good_below=0.5, note="<0.5 = safe")
        if r["dtc"] is not None:
            row("Debt / Capital", r["dtc"])
        if r["fl"] is not None:
            row("Financial Leverage", r["fl"], suffix="x")
        if r["ic"] is not None:
            row("Interest Coverage", r["ic"], suffix="x", good_above=3, note=">3x = safe")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        sec("Profitability", "📈")
        if r["gm"] is not None:
            row("Gross Margin", r["gm"], suffix="%", good_above=35, note=">35% = moat signal")
        if r["om"] is not None:
            row("Operating Margin", r["om"], suffix="%", good_above=15)
        if r["nm"] is not None:
            row("Net Profit Margin", r["nm"], suffix="%", good_above=10, note=">10% = moat signal")
        if r["roa"] is not None:
            row("ROA", r["roa"], suffix="%", good_above=10)
        if r["roce"] is not None:
            row("ROCE", r["roce"], suffix="%", good_above=15)
        if r["roe"] is not None:
            row("ROE", r["roe"], suffix="%", good_above=20, note=">20% = moat signal")
        if r.get("dupont") is not None:
            st.caption(f"DuPont breakdown: {r['nm']:.1f}% margin × {r['ta_t']:.2f}x turnover × {r['fl']:.1f}x leverage = {r['dupont']:.1f}% ROE")

        sec("Moat Metrics", "🏰")
        row("Free Cash Flow", fmt(d["fcf"], pfx=cs))
        if r["fcf_y"] is not None:
            row("FCF Yield", r["fcf_y"], suffix="%", good_above=5, note=">5% = attractive")
        row("Owner Earnings (est.)", fmt(r["oe"], pfx=cs))
        row("Net Debt", fmt(d["net_debt"], pfx=cs), note="negative = net cash")

        sec("Relative Valuation", "💰")
        if r["pe"]:
            row("P/E (Trailing)", r["pe"], suffix="x")
        if r["fpe"]:
            row("P/E (Forward)", r["fpe"], suffix="x")
        if r["peg"] is not None:
            row("PEG Ratio", r["peg"], good_below=1.0, note="<1 = attractive")
        if r["pbv"] is not None:
            row("Price / Book", r["pbv"], suffix="x")
        if r["pcf"] is not None:
            row("Price / Cash Flow", r["pcf"], suffix="x")
        if r["ps"] is not None:
            row("Price / Sales", r["ps"], suffix="x")
        if r["eveb"] is not None:
            row("EV / EBITDA", r["eveb"], suffix="x")
        if r["ey"] is not None:
            row("Earnings Yield", r["ey"], suffix="%", good_above=6)
        if r["gn"] is not None:
            below = d["price"] < r["gn"]
            gap = abs((r["gn"] - d["price"]) / r["gn"] * 100)
            row("Graham Number", r["gn"], prefix=cs,
                note=f"price {'BELOW ✅' if below else 'ABOVE ⚠️'} ({gap:.0f}% gap)")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DCF VALUATION ─────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    sec("Intrinsic Value & DCF Analysis", "🎯")

    v1, v2, v3 = st.columns(3)

    with v1:
        st.markdown('<div class="dcf-card">', unsafe_allow_html=True)
        st.markdown('<div class="dcf-title">📐 DCF — Base Case</div>', unsafe_allow_html=True)
        st.markdown('<div class="dcf-sub">12% growth yr 1–5 · 8% yr 6–10 · 2% terminal · 12% discount</div>', unsafe_allow_html=True)
        if r["dcf_base"]:
            dcf = r["dcf_base"]
            st.markdown(f'<div class="dcf-iv">{cs}{dcf["ps"]:,.1f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dcf-line">30% MoS buy price: <span>{cs}{dcf["b30"]:,.1f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dcf-line">50% MoS buy price: <span>{cs}{dcf["b50"]:,.1f}</span></div>', unsafe_allow_html=True)
            if r["mos"] is not None:
                col = "#16a34a" if r["mos"] >= 30 else "#d97706" if r["mos"] >= 10 else "#dc2626"
                st.markdown(f'<div style="margin-top:12px;font-size:15px;font-weight:800;color:{col}">Current MoS: {r["mos"]:.1f}%</div>', unsafe_allow_html=True)
        else:
            st.info("No positive FCF — DCF not applicable")
        st.markdown('</div>', unsafe_allow_html=True)

    with v2:
        st.markdown('<div class="dcf-card">', unsafe_allow_html=True)
        st.markdown('<div class="dcf-title">🛡️ DCF — Conservative</div>', unsafe_allow_html=True)
        st.markdown('<div class="dcf-sub">8% growth yr 1–5 · 5% yr 6–10 · 1% terminal · 12% discount</div>', unsafe_allow_html=True)
        if r["dcf_cons"]:
            dcf_c = r["dcf_cons"]
            st.markdown(f'<div class="dcf-iv">{cs}{dcf_c["ps"]:,.1f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dcf-line">30% MoS buy price: <span>{cs}{dcf_c["b30"]:,.1f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dcf-line">50% MoS buy price: <span>{cs}{dcf_c["b50"]:,.1f}</span></div>', unsafe_allow_html=True)
            if d["price"] > 0 and dcf_c["ps"] > 0:
                mos_c = (dcf_c["ps"] - d["price"]) / dcf_c["ps"] * 100
                col = "#16a34a" if mos_c >= 30 else "#d97706" if mos_c >= 10 else "#dc2626"
                st.markdown(f'<div style="margin-top:12px;font-size:15px;font-weight:800;color:{col}">Current MoS: {mos_c:.1f}%</div>', unsafe_allow_html=True)
        else:
            st.info("No positive FCF — DCF not applicable")
        st.markdown('</div>', unsafe_allow_html=True)

    with v3:
        st.markdown('<div class="dcf-card">', unsafe_allow_html=True)
        st.markdown('<div class="dcf-title">🔄 Reverse DCF</div>', unsafe_allow_html=True)
        st.markdown('<div class="dcf-sub">What growth rate is the market pricing in right now?</div>', unsafe_allow_html=True)
        if r["rdcf"]:
            rdcf = r["rdcf"]
            st.markdown(f'<div class="dcf-iv" style="font-size:22px">{rdcf["g1"]:.1f}% p.a.</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dcf-line">Yr 1–5 implied FCF growth</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dcf-line">Yr 6–10: {rdcf["g2"]:.1f}% p.a.</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:14px;font-size:12px;font-weight:600;line-height:1.5">{rdcf["label"]}</div>', unsafe_allow_html=True)
        else:
            st.info("Insufficient data")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── VERDICT + CHECKLIST ───────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    sec("Verdict & Quality Checklist", "⚖️")

    mos = r["mos"]
    if mos is not None:
        if mos >= 50:
            st.markdown('<div class="v-sbuy">🟢 STRONG BUY — More than 50% margin of safety</div>', unsafe_allow_html=True)
        elif mos >= 30:
            st.markdown('<div class="v-buy">🟢 BUY — 30–50% margin of safety. Good downside protection.</div>', unsafe_allow_html=True)
        elif mos >= 10:
            st.markdown('<div class="v-wtch">🟡 WATCH — 10–30% margin of safety. Wait for a better price.</div>', unsafe_allow_html=True)
        elif mos >= 0:
            st.markdown('<div class="v-avd">🔴 AVOID — Trading near intrinsic value. No margin of safety.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="v-avd">🔴 OVERVALUED — Trading {abs(mos):.1f}% above intrinsic value.</div>', unsafe_allow_html=True)
    else:
        st.info("Verdict unavailable — insufficient FCF data for DCF calculation")

    st.markdown("<br>", unsafe_allow_html=True)

    checks = [
        ("ROE consistently >20%",           r["roe"] is not None and r["roe"] > 20),
        ("Gross Margin >35%",               r["gm"]  is not None and r["gm"]  > 35),
        ("Net Profit Margin >10%",          r["nm"]  is not None and r["nm"]  > 10),
        ("Positive Free Cash Flow",         d["fcf"] > 0),
        ("Debt-to-Equity < 1",             r["dte"] is not None and 0 <= r["dte"] < 1),
        ("Interest Coverage > 3x",         r["ic"]  is not None and r["ic"]  > 3),
        ("FCF Yield > 5%",                 r["fcf_y"] is not None and r["fcf_y"] > 5),
        ("PEG Ratio < 1",                  r["peg"] is not None and r["peg"] < 1),
        ("Price below Graham Number",      r["gn"]  is not None and d["price"] < r["gn"]),
        ("Negative Cash Conversion Cycle", r["ccc"] is not None and r["ccc"] < 0),
    ]
    passed = sum(1 for _, v in checks if v)

    ch1, ch2 = st.columns(2)
    for i, (label, ok) in enumerate(checks):
        with (ch1 if i % 2 == 0 else ch2):
            icon = "✅" if ok else "☐"
            cls  = "ok" if ok else "no"
            st.markdown(f'<div class="chk {cls}">{icon}&nbsp; {label}</div>', unsafe_allow_html=True)

    st.markdown(f"<br><div style='font-size:14px;font-weight:700;color:#0f2444'>Score: {passed} / {len(checks)} quality checks passed</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("⚠️ Data from Yahoo Finance · Based on Safal Niveshak Mastermind frameworks · Not financial advice · Always apply your own judgment")


if __name__ == "__main__":
    main()
