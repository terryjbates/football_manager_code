# =============================================================================
# 📊 FM24 Squad & Scouting Data Hub Replica — Streamlit App
# Created by BangocheFM
# =============================================================================

import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
import plotly.express as px






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
# 🧹 COLUMN CLEANING & TYPE DETECTION
# =============================================================================

def clean_numeric_column(series):
    return (
        series.astype(str)
        .str.replace(r"[^\d.\-]+", "", regex=True)
        .replace("", pd.NA)
        .astype(float)
    )


# =============================================================================
# 🚀 STREAMLIT PAGE SETUP
# =============================================================================

st.set_page_config(page_title="FM24 Data Hub", layout="wide")
st.title("📊 FM24 Squad/Scouting Data Hub Replica")

uploaded_file = st.file_uploader("Upload your FM24 HTML export", type="html")

if uploaded_file:
    html_string = uploaded_file.read()
    df = extract_table_from_html(html_string)
    # Use full dataframe for comparison features
    filtered_df = df.copy()

    # === 🖥️ Raw Preview ===
    st.subheader("🧾 Raw Data Preview")
    st.dataframe(df.head())


    # =============================================================================
    # 🧠 COLUMN TYPE SETUP: NUMERIC & CATEGORICAL
    # =============================================================================

    potential_numeric_cols = []
    for col in df.columns:
        try:
            cleaned = pd.to_numeric(df[col].astype(str).str.replace(r"[^\d.\-]+", "", regex=True), errors='coerce')
            if cleaned.notna().sum() > 0:
                potential_numeric_cols.append(col)
                df[col] = cleaned
        except:
            continue

    numeric_cols = st.multiselect(
        "Select numeric columns to use",
        options=df.columns.tolist(),
        default=potential_numeric_cols
    )

    cat_cols = [col for col in df.columns if col not in numeric_cols]


    # =============================================================================
    # 🧭 SIDEBAR FILTERING: POSITION SELECTOR
    # =============================================================================

    # =============================================================================
    # 🧭 SIDEBAR FILTERING (SQUAD DEPTH ONLY)
    # =============================================================================

    st.sidebar.title("🎯 Squad Depth Filter")
    position_col = st.sidebar.selectbox("Position Column", options=cat_cols)
    unique_positions = df[position_col].dropna().unique().tolist()

    selected_positions = st.sidebar.multiselect(
        "Select Positions (affects squad depth only)",
        unique_positions,
        default=unique_positions
    )

    # This is only used for squad depth now
    squad_df = df[df[position_col].isin(selected_positions)] if selected_positions else df.copy()

    # =============================================================================
    # 📈 PLAYER COMPARISON (GROUPED BY PLAYER)
    # =============================================================================

    st.subheader("📈 Compare Players by Stats (Grouped by Player)")

    player_id_col = st.selectbox("Select Player Identifier", options=cat_cols, index=0)
    players = filtered_df[player_id_col].dropna().unique().tolist()

    selected_players = st.multiselect(
        "Select Players to Compare",
        options=players,
        default=players[:3],
        help="Search for players by name or ID",
    )

    selected_stats = st.multiselect(
        "Select Stats/Attributes to Compare",
        options=numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
        help="Search for attributes like Possession Won, Dribbles, etc.",
    )

    if selected_players and selected_stats:
        comp_df = filtered_df[filtered_df[player_id_col].isin(selected_players)]
        display_df = comp_df[[player_id_col] + selected_stats].copy()

        # Reshape to long format
        melted_df = display_df.melt(
            id_vars=player_id_col,
            value_vars=selected_stats,
            var_name="Attribute",
            value_name="Value"
        )

        # Plot: Cluster by Player, color by Stat
        fig = px.bar(
            melted_df,
            x=player_id_col,
            y="Value",
            color="Attribute",
            barmode="group",
            title="Player Comparison (Grouped by Player)",
            labels={player_id_col: "Player", "Value": "Stat Value"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # Raw table view
        with st.expander("📋 See Raw Comparison Table"):
            st.dataframe(display_df.set_index(player_id_col)[selected_stats])
    else:
        st.warning("Please select at least two players and one or more stats/attributes.")

		
    # =============================================================================
    # 🍕 INDIVIDUAL RADAR CHARTS (FIXED SCALE FOR ATTRIBUTES)
    # =============================================================================

    st.subheader("🍕 Player Radar Charts (Fixed Attribute Scale)")

    if selected_players and selected_stats and len(selected_stats) >= 3:
        radar_df = df[df[player_id_col].isin(selected_players)][[player_id_col] + selected_stats].copy()
        radar_df = radar_df.set_index(player_id_col)
        radar_df = radar_df.apply(pd.to_numeric, errors="coerce")

        for player in selected_players:
            player_data = radar_df.loc[player]

            scaled_data = []
            for stat in selected_stats:
                val = player_data.get(stat, 0)
                if stat in fm_attributes_0_20:
                    scaled_val = val / 20.0  # Normalize FM attributes
                else:
                    # Normalize against this stat's max value across all players selected
                    max_val = radar_df[stat].max()
                    scaled_val = val / max_val if max_val and max_val != 0 else 0
                scaled_data.append((stat, scaled_val))

            attr_labels = [x[0] for x in scaled_data]
            attr_values = [x[1] for x in scaled_data]

            fig = px.line_polar(
                r=attr_values,
                theta=attr_labels,
                line_close=True,
                title=f"Radar Chart for {player} (Normalized)"
            )
            fig.update_traces(fill='toself')
            st.plotly_chart(fig, use_container_width=True)
    elif selected_players and len(selected_stats) < 3:
        st.info("Please select at least 3 attributes to enable radar comparison.")
# =============================================================================
# 🍕 INDIVIDUAL RADAR CHARTS (WITH HOVER VALUES)
# =============================================================================

st.subheader("🍕 Player Radar Charts (Hover for Real Values)")

if selected_players and selected_stats and len(selected_stats) >= 3:
    radar_df = df[df[player_id_col].isin(selected_players)][[player_id_col] + selected_stats].copy()
    radar_df = radar_df.set_index(player_id_col)
    radar_df = radar_df.apply(pd.to_numeric, errors="coerce")

    for player in selected_players:
        player_data = radar_df.loc[player]

        theta_labels = []
        normalized_values = []
        raw_values = []

        for stat in selected_stats:
            raw_val = player_data.get(stat, 0)
            if stat in fm_attributes_0_20:
                norm_val = raw_val / 20.0
            else:
                max_val = radar_df[stat].max()
                norm_val = raw_val / max_val if max_val and max_val != 0 else 0

            theta_labels.append(stat)
            normalized_values.append(norm_val)
            raw_values.append(raw_val)

        # Build DataFrame with hover text
        chart_data = pd.DataFrame({
            "Attribute": theta_labels,
            "Normalized": normalized_values,
            "RawValue": raw_values
        })

        fig = px.line_polar(
            chart_data,
            r="Normalized",
            theta="Attribute",
            line_close=True,
            title=f"Radar Chart for {player}",
            custom_data=["RawValue"]
        )
        fig.update_traces(
            fill='toself',
            hovertemplate="%{theta}: %{customdata[0]}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)
elif selected_players and len(selected_stats) < 3:
    st.info("Please select at least 3 attributes to enable radar comparison.")


    # =============================================================================
    # 🧱 SQUAD DEPTH VISUALIZATION
    # =============================================================================
    st.subheader("📌 Squad Depth by Position (Filtered)")

    if not squad_df.empty:
        depth_counts = squad_df[position_col].value_counts().reset_index()
        depth_counts.columns = [position_col, "Player Count"]
        st.bar_chart(depth_counts.set_index(position_col))
    else:
        st.warning("No positions selected. Showing empty squad depth chart.")

    # =============================================================================
    # 🧾 FOOTER
    # =============================================================================

    st.markdown("---")
    st.caption("Prototype by BangocheFM — replicating FM24's Data Hub in Streamlit")

else:
    st.info("Please upload a valid FM24 HTML export (Squad or Scouting View).")
