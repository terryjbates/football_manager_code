# =============================================================================
# 📊 FM24 Squad & Scouting Data Hub Replica — Streamlit App
# Created by BangocheFM
# =============================================================================

import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
import plotly.express as px
import itertools

# =============================================================================
# 🎮 FM Attribute Abbreviations (0–20 Scale)
# =============================================================================

fm_attributes_0_20 = [
    "Acc", "Agi", "Ant", "Bal", "Bra", "Cmp", "Cnt", "Dec", "Det", "Dri",
    "Fin", "Fir", "Fla", "Hea", "Jum", "Ldr", "Lon", "Mar", "OtB", "Pas",
    "Pos", "Pac", "Sta", "Str", "Tck", "Tec", "Vis", "Wor", "Cro", "Cor",
    "Fre", "L Th", "Pen"
]

# =============================================================================
# 📁 FILE HANDLING & HTML EXTRACTION
# =============================================================================

def extract_table_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    df = pd.read_html(str(table), header=0)[0]
    return df

# =============================================================================
# 🪩 COLUMN CLEANING & TYPE DETECTION
# =============================================================================

def clean_numeric_column(series):
    return (
        series.astype(str)
        .str.replace(r"[^\d.\-]+", "", regex=True)
        .replace("", pd.NA)
        .astype(float)
    )

# =============================================================================
# 🔍 Position Parser: Unravel "Best Pos" into All Specific Positions
# =============================================================================

def expand_positions(pos_string):
    if pd.isna(pos_string):
        return []

    position_blocks = re.findall(r'([A-Z/]+)\s*\(([RLMC]+)\)', pos_string)
    base_positions = re.sub(r'\s*\(([RLMC]+)\)', '', pos_string)
    base_parts = re.split(r',\s*', base_positions)

    expanded = []

    for part in base_parts:
        if "/" in part:
            role_types = part.strip().split("/")
        else:
            role_types = [part.strip()]

        paren_match = re.search(r'([A-Z/]+)\s*\(([RLMC]+)\)', pos_string)
        if paren_match:
            modifiers = list(paren_match.group(2))
        else:
            modifiers = []

        for role in role_types:
            for mod in modifiers:
                expanded.append(role + mod)
            if not modifiers:
                expanded.append(role)

    pos_chunks = re.split(r',\s*', pos_string)
    for chunk in pos_chunks:
        match = re.match(r'([A-Z/]+)\s*\(([RLMC]+)\)', chunk)
        if match:
            base, mods = match.groups()
            for letter in mods:
                for piece in base.split("/"):
                    expanded.append(piece.strip() + letter)
        elif chunk.strip():
            expanded.append(chunk.strip())

    return sorted(set(expanded))

# =============================================================================
# 🚀 STREAMLIT PAGE SETUP
# =============================================================================

st.set_page_config(page_title="FM24 Data Hub", layout="wide")
st.title(":bar_chart: FM24 Squad Insights")

uploaded_file = st.file_uploader("Upload your FM24 HTML export", type="html")

if uploaded_file:
    html_string = uploaded_file.read()
    df = extract_table_from_html(html_string)
    df["All Positions"] = df["Best Pos"].apply(expand_positions)

    potential_numeric_cols = []
    for col in df.columns:
        try:
            cleaned = pd.to_numeric(df[col].astype(str).str.replace(r"[^\d.\-]+", "", regex=True), errors='coerce')
            if cleaned.notna().sum() > 0:
                potential_numeric_cols.append(col)
                df[col] = cleaned
        except:
            continue

    numeric_cols = potential_numeric_cols
    cat_cols = [col for col in df.columns if col not in numeric_cols]

    analytics_tab, scatter_tab, radar_tab, depth_tab, raw_tab = st.tabs([
        "📊 Player Analytics",
        "⭕ Custom Scatter",
        "🍕 Radar Charts",
        "📌 Squad Depth",
        "📋 Raw Data"
    ])

    with analytics_tab:
        st.subheader(":bar_chart: Player Analytics Overview")
        st.dataframe(df.head())

    with scatter_tab:
        st.subheader("⭕ Custom Scatter Plot")
        st.write("Coming soon...")

    with radar_tab:
        st.subheader(":pizza: Radar (WIP)")
        st.write("Coming soon...")

    with depth_tab:
        st.subheader(":round_pushpin: Depth (WIP)")
        st.write("Coming soon...")

    with raw_tab:
        st.subheader(":clipboard: Raw Data")
        st.dataframe(df)

else:
    st.info("Please upload a valid FM24 HTML export (Squad View).")
