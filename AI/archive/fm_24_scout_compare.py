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
# 🧩 COLUMN CLEANING & TYPE DETECTION
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

st.set_page_config(page_title="FM24 Scouting Hub", layout="wide")
st.title(":bar_chart: FM24 Scouting Hub")

uploaded_file = st.file_uploader("Upload your FM24 HTML export", type="html")
scouted_file = st.file_uploader("Optionally Upload Scouted Player HTML", type="html")

if uploaded_file:
    html_string = uploaded_file.read()
    df = extract_table_from_html(html_string)
    df["All Positions"] = df["Best Pos"].apply(expand_positions)

    filtered_df = df.copy()

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

    compare_tab, analytics_tab, radar_tab, depth_tab, raw_tab = st.tabs([
        "🪪 Compare Players",
        "📊 Player Analytics",
        "🍕 Radar Comparison",
        "📌 Squad Depth",
        "📋 Raw Data"
    ])

    with compare_tab:
        st.subheader("🪪 Compare My Squad vs. Scouted Players")

        if scouted_file:
            scouted_html = scouted_file.read()
            scouted_df = extract_table_from_html(scouted_html)
            scouted_df["All Positions"] = scouted_df["Best Pos"].apply(expand_positions) if "Best Pos" in scouted_df.columns else [[]] * len(scouted_df)

            scouted_numeric_cols = []
            for col in scouted_df.columns:
                try:
                    cleaned = pd.to_numeric(scouted_df[col].astype(str).str.replace(r"[^\d.\-]+", "", regex=True), errors='coerce')
                    if cleaned.notna().sum() > 0:
                        scouted_numeric_cols.append(col)
                        scouted_df[col] = cleaned
                except:
                    continue

            scouted_cat_cols = [col for col in scouted_df.columns if col not in scouted_numeric_cols]

            shared_numeric = list(set(numeric_cols).intersection(scouted_numeric_cols))
            shared_cat = list(set(cat_cols).intersection(scouted_cat_cols))

            df_shared = df[shared_cat + shared_numeric].copy()
            df_shared["Source"] = "My Squad"

            scouted_shared = scouted_df[shared_cat + shared_numeric].copy()
            scouted_shared["Source"] = "Scouted Players"

            combined_df = pd.concat([df_shared, scouted_shared], ignore_index=True)

            x_axis = st.selectbox("Select X Axis", options=shared_numeric)
            y_axis = st.selectbox("Select Y Axis", options=shared_numeric)

            name_col = "Name" if "Name" in combined_df.columns else None
            hover_data = [name_col, "Source"] if name_col else ["Source"]

            name_filter = st.text_input("Filter by player name (partial match):")
            if name_filter and name_col:
                combined_df = combined_df[
                    combined_df[name_col].astype(str).str.contains(name_filter, case=False, na=False)
                ]

            fig = px.scatter(
                combined_df,
                x=x_axis,
                y=y_axis,
                color="Source",
                hover_name=name_col,
                hover_data=hover_data,
                title=f"Comparison: {x_axis} vs {y_axis}"
            )
            fig.update_traces(marker=dict(size=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Upload a scouted player file to enable comparison.")

    with analytics_tab:
        st.subheader(":bar_chart: Player Analytics Overview")
        st.dataframe(df.head())

    with radar_tab:
        st.subheader(":pizza: Radar (WIP)")

    with depth_tab:
        st.subheader(":round_pushpin: Depth (WIP)")

    with raw_tab:
        st.subheader(":clipboard: Raw Data")
        st.dataframe(df)

else:
    st.info("Please upload a valid FM24 HTML export (Squad or Scouting View).")