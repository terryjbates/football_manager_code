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
# 🩹 COLUMN CLEANING & TYPE DETECTION
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
st.title("📊 FM24 Squad/Scouting Data Hub Replica")

uploaded_file = st.file_uploader("Upload your FM24 HTML export", type="html")

if uploaded_file:
    html_string = uploaded_file.read()
    df = extract_table_from_html(html_string)

    # Expand position abbreviations
    df["All Positions"] = df["Best Pos"].apply(expand_positions)

    # Clone for radar + player compare sections
    filtered_df = df.copy()

    # Detect column types
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

    # Tabs
    analytics_tab, radar_tab, depth_tab, raw_tab = st.tabs([
        "📊 Player Analytics",
        "🍕 Radar Comparison",
        "📌 Squad Depth",
        "📋 Raw Data"
    ])

    # 📊 PLAYER ANALYTICS TAB
    with analytics_tab:
        st.subheader("📊 Player Analytics Overview")

        def bin_player(pos_list):
            if not isinstance(pos_list, list):
                return "Unknown"
            if any(pos.startswith("GK") for pos in pos_list):
                return "Goalkeepers"
            if any(pos.startswith("D") for pos in pos_list):
                return "Defenders"
            if any(pos.startswith("M") for pos in pos_list):
                return "Midfielders"
            if any(pos.startswith("AM") or pos.startswith("ST") for pos in pos_list):
                return "Forwards"
            return "Unknown"

        df["Player Type"] = df["All Positions"].apply(bin_player)

        # Static scatter plots
        default_charts = [
            ("Assisting - Forwards", "xA/90", "K Ps/90"),
            ("Shooting - Forwards", "ShT/90", "xG/shot"),
            ("Goal Output - Forwards",  "xA/90", "NP-xG/90"),
            ("Assisting - Defenders", "xA/90", "K Ps/90"),
            ("Passing - Goalkeepers", "Pas %", "Pas A")
        ]

        shown_any = False

        with st.expander("🧾 Show Available Columns in Dataset"):
            st.write("**All Columns:**")
            st.write(list(df.columns))

            st.write("**Detected Numeric Columns:**")
            st.write(numeric_cols)

            st.write("**Detected Categorical Columns:**")
            st.write(cat_cols)

        st.markdown("### 🔍 Search Column Names")
        search_term = st.text_input("Enter keyword to search column names (case-insensitive)")

        if search_term:
            matching_cols = [col for col in df.columns if search_term.lower() in col.lower()]
            if matching_cols:
                st.success(f"Found {len(matching_cols)} matching columns:")
                st.write(matching_cols)
            else:
                st.warning("No matching columns found.")
        
        
        
        
        
        
        for title, x_stat, y_stat in default_charts:
            if x_stat in df.columns and y_stat in df.columns:
                fig = px.scatter(
                    df,
                    x=x_stat,
                    y=y_stat,
                    color="Player Type",
                    title=title,
                    hover_name=df[cat_cols[0]] if cat_cols else None,
                )
                # Larger scatter points
                fig.update_traces(marker=dict(size=10))  # Adjust size here as needed

                # Add vertical and horizontal mean lines
                x_mean = df[x_stat].mean()
                y_mean = df[y_stat].mean()

                fig.add_vline(x=x_mean, line_width=1, line_dash="dash", line_color="gray")
                fig.add_hline(y=y_mean, line_width=1, line_dash="dash", line_color="gray")

                fig.add_annotation(
                    x=x_mean, y=df[y_stat].max(),
                    text=f"Avg {x_stat}: {round(x_mean, 2)}",
                    showarrow=False,
                    yanchor="bottom",
                    font=dict(size=10),
                    #bgcolor="white",
                    opacity=0.8
                )

                fig.add_annotation(
                    x=df[x_stat].max(), y=y_mean + 0.05,
                    text=f"Avg {y_stat}: {round(y_mean, 2)}",
                    showarrow=False,
                    xanchor="right",
                    font=dict(size=10),
                    #bgcolor="white",
                    opacity=0.8
                )

                
                # Optional: Add labels near the lines
                # fig.add_annotation(
                #     x=x_mean, y=df[y_stat].max(), text="Avg X", showarrow=False,
                #     yanchor="bottom", font=dict(size=10), bgcolor="white", opacity=0.7
                # )
                # fig.add_annotation(
                #     x=df[x_stat].max(), y=y_mean, text="Avg Y", showarrow=False,
                #     xanchor="right", font=dict(size=10), bgcolor="white", opacity=0.7
                # )

                
                
                
                
                st.plotly_chart(fig, use_container_width=True)
                shown_any = True
            else:
                st.info(f"⚠️ Skipped chart '{title}' — missing column(s): {x_stat} or {y_stat}")

        if not shown_any:
            st.warning("No analytics charts could be displayed due to missing columns in your dataset.")


    # 🍕 RADAR CHART TAB
    with radar_tab:
        st.subheader("🍕 Player Radar Charts (Hover for Real Values)")

        player_id_col = st.selectbox("Select Player Identifier", options=cat_cols, key="radar_id")
        players = df[player_id_col].dropna().unique().tolist()

        selected_players = st.multiselect(
            "Select Players to Compare",
            options=players,
            default=players[:3],
            help="Search for players by name or ID",
            key="radar_players"
        )

        selected_stats = st.multiselect(
            "Select Stats/Attributes to Compare",
            options=numeric_cols,
            default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols,
            help="Pick stats or FM attributes to visualize",
            key="radar_stats"
        )

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

    # 📌 SQUAD DEPTH TAB
    with depth_tab:
        st.sidebar.title("🎯 Squad Depth Filter")
        position_col = st.sidebar.selectbox("Position Column", options=cat_cols)

        sort_mode = st.sidebar.radio(
            "Sort Squad Depth Chart By:",
            options=["Player Count Asc", "Player Count Desc", "Field Position Order"],
            index=2
        )

        if position_col == "All Positions":
            all_pos_flat = list(itertools.chain.from_iterable(df["All Positions"].dropna()))
            unique_positions = sorted(set(all_pos_flat))
        else:
            unique_positions = df[position_col].dropna().unique().tolist()

        selected_positions = st.sidebar.multiselect(
            "Select Positions (affects squad depth only)",
            unique_positions,
            default=unique_positions
        )

        if position_col == "All Positions":
            def contains_selected(position_list):
                try:
                    return any(pos in position_list for pos in selected_positions)
                except TypeError:
                    return False
            squad_df = df[df["All Positions"].apply(contains_selected)]
        else:
            squad_df = df[df[position_col].isin(selected_positions)]

        st.caption(f"✅ Found {len(squad_df)} players matching position filter.")

        st.subheader("📌 Squad Depth by Position (Unraveled from 'Best Pos')")

        if not squad_df.empty:
            pos_exploded = squad_df.explode("All Positions")
            pos_counts = pos_exploded["All Positions"].value_counts().reset_index()
            pos_counts.columns = ["Position", "Player Count"]

            if sort_mode == "Player Count Asc":
                pos_counts = pos_counts.sort_values("Player Count", ascending=True)
            elif sort_mode == "Player Count Desc":
                pos_counts = pos_counts.sort_values("Player Count", ascending=False)
            elif sort_mode == "Field Position Order":
                field_order = [
                    "GK", "DC", "DCL", "DCR", "DL", "DR",
                    "WBL", "WBR", "DM", "DMC", "MC", "MCL", "MCR",
                    "ML", "MR", "AM", "AMC", "AML", "AMR",
                    "ST", "STC", "STL", "STR"
                ]
                pos_counts["Position"] = pd.Categorical(pos_counts["Position"], categories=field_order, ordered=True)
                pos_counts = pos_counts.sort_values("Position")

            fig = px.bar(
                pos_counts,
                x="Position",
                y="Player Count",
                title="Squad Depth by Position",
                labels={"Player Count": "Count"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No players matched the selected positions.")

    # 📋 RAW TAB
    with raw_tab:
        st.subheader("💾 Raw Data Preview")
        st.dataframe(df.head())

    st.markdown("---")
    st.caption("Prototype by BangocheFM — replicating FM24's Data Hub in Streamlit")

else:
    st.info("Please upload a valid FM24 HTML export (Squad or Scouting View).")
