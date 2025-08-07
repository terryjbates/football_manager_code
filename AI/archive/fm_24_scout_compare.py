# =============================================================================
# 📊 FM24 Squad & Scouting Data Hub — Streamlit App (Robust Refactor)
# =============================================================================

import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
import plotly.express as px
import itertools

# =============================================================================
# 🔧 Utilities & Constants
# =============================================================================

ATTRIBUTES = [
    "Acc", "Agi", "Ant", "Bal", "Bra", "Cmp", "Cnt", "Dec", "Det", "Dri",
    "Fin", "Fir", "Fla", "Hea", "Jum", "Ldr", "Lon", "Mar", "OtB", "Pas",
    "Pos", "Pac", "Sta", "Str", "Tck", "Tec", "Vis", "Wor", "Cro", "Cor",
    "Fre", "L Th", "Pen", "Kic", "Cmd", "Com", "Ecc", "1v1", "Aer"
]

ATTRIBUTE_FILTERS = ["Pac", "Str", "Acc", "Wor", "Agg", "Det", "Cmp"]

META_COLS = ["Name", "Source", "Best Pos", "All Positions"]

# =============================================================================
# 🗓️ Loaders & Parsers
# =============================================================================

def extract_table_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    df = pd.read_html(str(table), header=0)[0]
    return df

def expand_positions(pos_string):
    if pd.isna(pos_string): return []

    expanded = []
    for chunk in re.split(r',\s*', pos_string):
        match = re.match(r'([A-Z/]+)\s*\(([RLMC]+)\)', chunk)
        if match:
            base, mods = match.groups()
            for letter in mods:
                for piece in base.split("/"):
                    expanded.append(piece.strip() + letter)
        else:
            for piece in chunk.split("/"):
                expanded.append(piece.strip())
    return sorted(set(expanded))

# =============================================================================
# 🧋 Cleaning
# =============================================================================

def clean_numeric_columns(df):
    numeric_cols = []
    for col in df.columns:
        try:
            cleaned = pd.to_numeric(df[col].astype(str).str.replace(r"[^\d.\-]+", "", regex=True), errors='coerce')
            if cleaned.notna().sum() > 0:
                df[col] = cleaned
                numeric_cols.append(col)
        except:
            continue
    return df, numeric_cols

# =============================================================================
# 🚀 Streamlit App
# =============================================================================

st.set_page_config(page_title="FM24 Scouting Hub", layout="wide")
st.title(":bar_chart: FM24 Scouting Hub")

uploaded_file = st.file_uploader("Upload your FM24 HTML export", type="html")
scouted_file = st.file_uploader("Optionally Upload Scouted Player HTML", type="html")

if not uploaded_file:
    st.info("Please upload a valid FM24 HTML export.")
    st.stop()

# Process Squad Data
squad_df = extract_table_from_html(uploaded_file.read())
squad_df["All Positions"] = squad_df["Best Pos"].apply(expand_positions)
squad_df, squad_numeric = clean_numeric_columns(squad_df)
squad_df["Source"] = "My Squad"

# Process Scouted Data
if scouted_file:
    scouted_df = extract_table_from_html(scouted_file.read())
    scouted_df["All Positions"] = scouted_df["Best Pos"].apply(expand_positions)
    scouted_df, scouted_numeric = clean_numeric_columns(scouted_df)
    scouted_df["Source"] = "Scouted Players"
    combined_df = pd.concat([squad_df, scouted_df], ignore_index=True)
    numeric_cols = list(set(squad_numeric).intersection(scouted_numeric))
else:
    combined_df = squad_df.copy()
    numeric_cols = squad_numeric

combined_df.reset_index(drop=True, inplace=True)

# Sidebar Position Filter
st.sidebar.title("🌿 Filters")
all_positions = sorted(set(itertools.chain.from_iterable(combined_df["All Positions"].dropna())))
selected_positions = st.sidebar.multiselect("Filter by Position", options=all_positions, default=all_positions)


# New Static Attribute Filters

with st.sidebar.expander("🎛️ Attribute Filters (1-20)", expanded=True):
    slider_style = """
    <style>
    .stSlider > div[data-baseweb="slider"] {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """
    st.markdown(slider_style, unsafe_allow_html=True)

    attrib_filters = {}
    for attrib in ATTRIBUTE_FILTERS:
        attrib_filters[attrib] = st.slider(
            f"{attrib}",
            min_value=1,
            max_value=20,
            value=(1, 20),
            step=1,
            help=f"Filter players based on {attrib} (1–20 scale)"
        )

# # OLD Static Attribute Filters
# st.sidebar.markdown("---")
# st.sidebar.markdown("### Attribute Filters (1-20)")
# attrib_filters = {}
# for attrib in ATTRIBUTE_FILTERS:
#     attrib_filters[attrib] = st.sidebar.slider(f"{attrib}", 1, 20, (1, 20))


# Apply Filters
def satisfies_all_attr_ranges(row):
    for attr, (min_val, max_val) in attrib_filters.items():
        if attr not in row or pd.isna(row[attr]) or not (min_val <= row[attr] <= max_val):
            return False
    return True

pos_mask = combined_df["All Positions"].apply(lambda pos_list: any(pos in pos_list for pos in selected_positions) if isinstance(pos_list, list) else False)
attr_mask = combined_df.apply(satisfies_all_attr_ranges, axis=1)
filtered_df = combined_df[pos_mask & attr_mask].copy()

# Tabs Setup
compare_tab, raw_tab = st.tabs(["🧪 Compare Players", "📋 Raw Data"])

with compare_tab:
    st.subheader("🧪 Compare My Squad vs. Scouted Players")

    x_axis = st.selectbox("Select X Axis", options=numeric_cols)
    y_axis = st.selectbox("Select Y Axis", options=numeric_cols)

    name_col = "Name" if "Name" in filtered_df.columns else None
    hover_data = [name_col, "Source"] if name_col else ["Source"]

    name_filter = st.text_input("Filter by player name (partial match):")
    if name_filter and name_col:
        filtered_df = filtered_df[filtered_df[name_col].astype(str).str.contains(name_filter, case=False, na=False)]

    fig = px.scatter(
        filtered_df,
        x=x_axis,
        y=y_axis,
        color="Source",
        hover_name=name_col,
        hover_data=hover_data,
        title=f"Comparison: {x_axis} vs {y_axis}"
    )
    fig.update_traces(marker=dict(size=10))
    fig.add_vline(x=filtered_df[x_axis].mean(), line_width=1, line_dash="dash", line_color="gray")
    fig.add_hline(y=filtered_df[y_axis].mean(), line_width=1, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    # Goalkeeper Plot
    st.markdown("---")
    st.subheader("🪒 Goalkeeper Assessment")
    gk_df = filtered_df[filtered_df["All Positions"].apply(lambda pos: any(p.startswith("GK") for p in pos))]

    gk_hover = ["xGP", "Ecc", "Aer", "1v1", "Cmd", "Com"]

    if "Reflexes" in gk_df.columns and "xSv %" in gk_df.columns:
        fig1 = px.scatter(
            gk_df,
            x="Reflexes",
            y="xSv %",
            color="Source",
            hover_name=name_col,
            hover_data=gk_hover,
            title="Reflexes vs Expected Save Percentage (xSv %)"
        )
        fig1.update_traces(marker=dict(size=10))
        fig1.add_vline(x=gk_df["Reflexes"].mean(), line_dash="dash", line_color="gray")
        fig1.add_hline(y=gk_df["xSv %"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig1, use_container_width=True)

    if "Kic" in gk_df.columns and "Pas %" in gk_df.columns:
        fig2 = px.scatter(
            gk_df,
            x="Kic",
            y="Pas %",
            color="Source",
            hover_name=name_col,
            hover_data=gk_hover,
            title="Kicking vs Passing %"
        )
        fig2.update_traces(marker=dict(size=10))
        fig2.add_vline(x=gk_df["Kic"].mean(), line_dash="dash", line_color="gray")
        fig2.add_hline(y=gk_df["Pas %"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig2, use_container_width=True)

    # Centerback Plots
    st.markdown("---")
    st.subheader("🛡️ Center Back Assessment")
    cb_df = filtered_df[filtered_df["All Positions"].apply(lambda pos: any(p.startswith("DC") for p in pos))]

    cb_hover = ["Agg", "Mar", "Tck", "Pos", "Str", "Height"]

    if "Aer A/90" in cb_df.columns and "Hdrs W/90" in cb_df.columns:
        fig3 = px.scatter(
            cb_df,
            x="Aer A/90",
            y="Hdrs W/90",
            color="Source",
            hover_name=name_col,
            hover_data=cb_hover,
            title="Aerial Duels Attempted per 90 vs Headers Won per 90"
        )
        fig3.update_traces(marker=dict(size=10))
        fig3.add_vline(x=cb_df["Aer A/90"].mean(), line_dash="dash", line_color="gray")
        fig3.add_hline(y=cb_df["Hdrs W/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig3, use_container_width=True)

    if "Tck/90" in cb_df.columns and "Int/90" in cb_df.columns:
        fig4 = px.scatter(
            cb_df,
            x="Tck/90",
            y="Int/90",
            color="Source",
            hover_name=name_col,
            hover_data=cb_hover,
            title="Tackles per 90 vs Interceptions per 90"
        )
        fig4.update_traces(marker=dict(size=10))
        fig4.add_vline(x=cb_df["Tck/90"].mean(), line_dash="dash", line_color="gray")
        fig4.add_hline(y=cb_df["Int/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig4, use_container_width=True)

    if "Pas %" in cb_df.columns and "K Ps/90" in cb_df.columns:
        fig5 = px.scatter(
            cb_df,
            x="Pas %",
            y="K Ps/90",
            color="Source",
            hover_name=name_col,
            hover_data=cb_hover,
            title="Passing % vs Key Passes per 90"
        )
        fig5.update_traces(marker=dict(size=10))
        fig5.add_vline(x=cb_df["Pas %"].mean(), line_dash="dash", line_color="gray")
        fig5.add_hline(y=cb_df["K Ps/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig5, use_container_width=True)

         
        
    # Full-Back / Wing-Back Plots
    st.markdown("---")
    st.subheader("🏃 Full-Back / Wing-Back Assessment")
    fb_df = filtered_df[filtered_df["All Positions"].apply(lambda pos: any(p.startswith("DL") or p.startswith("DR") 
                                                                           or p.startswith("WB") for p in pos))]

    fb_hover = ["Cro", "Tck", "Pas", "Cmp", "Tec", "Wor", "Acc", "Agg", "Sta", "Dri", "Drb/90"]

    if "Tck" in fb_df.columns and "Int/90" in fb_df.columns:
        fig_fb1 = px.scatter(
            fb_df,
            x="Tck",
            y="Int/90",
            color="Source",
            hover_name=name_col,
            hover_data=fb_hover,
            title="Tackling vs Interceptions per 90 (Defensive Workrate)"
        )
        fig_fb1.update_traces(marker=dict(size=10))
        fig_fb1.add_vline(x=fb_df["Tck"].mean(), line_dash="dash", line_color="gray")
        fig_fb1.add_hline(y=fb_df["Int/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig_fb1, use_container_width=True)

    if "Cro" in fb_df.columns and "Crs C/90" in fb_df.columns:
        fig_fb2 = px.scatter(
            fb_df,
            x="Cro",
            y="Crs C/90",
            color="Source",
            hover_name=name_col,
            hover_data=fb_hover,
            title="Crossing vs Crosses Completed per 90 (Attacking Threat)"
        )
        fig_fb2.update_traces(marker=dict(size=10))
        fig_fb2.add_vline(x=fb_df["Cro"].mean(), line_dash="dash", line_color="gray")
        fig_fb2.add_hline(y=fb_df["Crs C/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig_fb2, use_container_width=True)

    if "Dri" in fb_df.columns and "Drb/90" in fb_df.columns:
        fig_fb3 = px.scatter(
            fb_df,
            x="Dri",
            y="Drb/90",
            color="Source",
            hover_name=name_col,
            hover_data=fb_hover,
            title="Dribbling vs Progressive Runs per 90"
        )
        fig_fb3.update_traces(marker=dict(size=10))
        fig_fb3.add_vline(x=fb_df["Dri"].mean(), line_dash="dash", line_color="gray")
        fig_fb3.add_hline(y=fb_df["Drb/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig_fb3, use_container_width=True)

    if "Cmp" in fb_df.columns and "Poss Lost/90" in fb_df.columns:
        fig_fb4 = px.scatter(
            fb_df,
            x="Cmp",
            y="Poss Lost/90",
            color="Source",
            hover_name=name_col,
            hover_data=fb_hover,
            title="Composure vs Poss Lost/90 % (Possession Retention)"
        )
        fig_fb4.update_traces(marker=dict(size=10))
        fig_fb4.add_vline(x=fb_df["Cmp"].mean(), line_dash="dash", line_color="gray")
        fig_fb4.add_hline(y=fb_df["Poss Lost/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig_fb4, use_container_width=True)

        
    # Midfielder Plots (CM/DM)
    st.markdown("---")
    st.subheader("🧠 Midfield Assessment")
    mid_df = filtered_df[filtered_df["All Positions"].apply(lambda pos: any(p.startswith("DM") or p.startswith("MC") for p in pos))]

    # ========== Calculated Fields ==========
    mid_df["Defensive Actions"] = mid_df[["Tck W", "Blk", "Clear", "Hdrs"]].sum(axis=1, skipna=True)
    mid_df["Excitement"] = mid_df[["Gls", "Ast", "Drb", "K Pas"]].sum(axis=1, skipna=True)
    mid_df["Scout Factor"] = (mid_df["Drb/90"] / mid_df["Poss Lost/90"]).round(3)

    # ========== Progression ==========
    st.markdown("#### 🔄 Progression")
    prog_hover = ["Drb/90", "Dist/90", "Scout Factor", "Source"]

    if "Pas" in mid_df.columns and "Pr passes/90" in mid_df.columns:
        fig6 = px.scatter(
            mid_df, x="Pas", y="Pr passes/90", color="Source",
            hover_name=name_col, hover_data=prog_hover,
            title="Passing vs Progressive Passes per 90"
        )
        fig6.update_traces(marker=dict(size=10))
        fig6.add_vline(x=mid_df["Pas"].mean(), line_dash="dash", line_color="gray")
        fig6.add_hline(y=mid_df["Pr passes/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig6, use_container_width=True)

    if "Drb/90" in mid_df.columns and "Dist/90" in mid_df.columns:
        fig7 = px.scatter(
            mid_df, x="Drb/90", y="Dist/90", color="Source",
            hover_name=name_col, hover_data=prog_hover,
            title="Dribbles per 90 vs Distance Covered per 90"
        )
        fig7.update_traces(marker=dict(size=10))
        fig7.add_vline(x=mid_df["Drb/90"].mean(), line_dash="dash", line_color="gray")
        fig7.add_hline(y=mid_df["Dist/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig7, use_container_width=True)

    # ========== Creation ==========
    st.markdown("#### ✨ Creation")
    creation_hover = ["K Ps/90", "xA/90", "OP-KP/90", "Excitement", "Source"]

    if "Vis" in mid_df.columns and "K Ps/90" in mid_df.columns:
        fig8 = px.scatter(
            mid_df, x="Vis", y="K Ps/90", color="Source",
            hover_name=name_col, hover_data=creation_hover,
            title="Vision vs Key Passes per 90"
        )
        fig8.update_traces(marker=dict(size=10))
        fig8.add_vline(x=mid_df["Vis"].mean(), line_dash="dash", line_color="gray")
        fig8.add_hline(y=mid_df["K Ps/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig8, use_container_width=True)

    if "Dec" in mid_df.columns and "xA/90" in mid_df.columns:
        fig9 = px.scatter(
            mid_df, x="Dec", y="xA/90", color="Source",
            hover_name=name_col, hover_data=creation_hover,
            title="Decisions vs Expected Assists per 90"
        )
        fig9.update_traces(marker=dict(size=10))
        fig9.add_vline(x=mid_df["Dec"].mean(), line_dash="dash", line_color="gray")
        fig9.add_hline(y=mid_df["xA/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig9, use_container_width=True)

    # ========== Destruction ==========
    st.markdown("#### 🧨 Destruction")
    destruct_hover = ["Tck", "Agg", "Int/90", "Poss Won/90", "Defensive Actions", "Source"]

    if "Tck" in mid_df.columns and "Tck/90" in mid_df.columns:
        fig10 = px.scatter(
            mid_df, x="Tck", y="Tck/90", color="Source",
            hover_name=name_col, hover_data=destruct_hover,
            title="Tackling vs Tackles per 90"
        )
        fig10.update_traces(marker=dict(size=10))
        fig10.add_vline(x=mid_df["Tck"].mean(), line_dash="dash", line_color="gray")
        fig10.add_hline(y=mid_df["Tck/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig10, use_container_width=True)

    if "Agg" in mid_df.columns and "Poss Won/90" in mid_df.columns:
        fig11 = px.scatter(
            mid_df, x="Agg", y="Poss Won/90", color="Source",
            hover_name=name_col, hover_data=destruct_hover,
            title="Aggression vs Possession Won per 90"
        )
        fig11.update_traces(marker=dict(size=10))
        fig11.add_vline(x=mid_df["Agg"].mean(), line_dash="dash", line_color="gray")
        fig11.add_hline(y=mid_df["Poss Won/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig11, use_container_width=True)

        
    # Attacking Mid & Winger Section
    st.markdown("---")
    st.subheader("🎨 Attacking Mids & Wingers")
    amw_df = filtered_df[filtered_df["All Positions"].apply(lambda pos: any(p.startswith(("AM", "ML", "MR")) for p in pos))]

    # Add Excitement and Scout Factor
    amw_df = amw_df.copy()
    amw_df["Excitement"] = amw_df[["Gls", "Ast", "Drb", "K Pas"]].sum(axis=1, min_count=1)
    amw_df["Scout Factor"] = (amw_df["Drb/90"] / amw_df["Poss Lost/90"]).round(3)

    amw_hover = ["Excitement", "Scout Factor", "Ast", "Gls", "Drb", "K Pas", "Cr C/A", "Pas %"]

    # Plot 1: Creativity — Key Passes vs Expected Assists
    if "K Ps/90" in amw_df.columns and "xA/90" in amw_df.columns:
        fig1 = px.scatter(
            amw_df,
            x="K Ps/90",
            y="xA/90",
            color="Source",
            hover_name=name_col,
            hover_data=amw_hover,
            title="Key Passes/90 vs xA/90"
        )
        fig1.update_traces(marker=dict(size=10))
        fig1.add_vline(x=amw_df["K Ps/90"].mean(), line_dash="dash", line_color="gray")
        fig1.add_hline(y=amw_df["xA/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig1, use_container_width=True)

    # Plot 2: Crossing Ability — Crosses Completed vs Cross Accuracy
    if "OP-Crs C/90" in amw_df.columns and "Cr C/A" in amw_df.columns:
        fig2 = px.scatter(
            amw_df,
            x="OP-Crs C/90",
            y="Cr C/A",
            color="Source",
            hover_name=name_col,
            hover_data=amw_hover,
            title="Open Play Crosses Completed/90 vs Cross Completion %"
        )
        fig2.update_traces(marker=dict(size=10))
        fig2.add_vline(x=amw_df["OP-Crs C/90"].mean(), line_dash="dash", line_color="gray")
        fig2.add_hline(y=amw_df["Cr C/A"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig2, use_container_width=True)

    # Plot 3: Dribbling & Risk — Dribbles/90 vs Poss Lost/90
    if "Drb/90" in amw_df.columns and "Poss Lost/90" in amw_df.columns:
        fig3 = px.scatter(
            amw_df,
            x="Drb/90",
            y="Poss Lost/90",
            color="Source",
            hover_name=name_col,
            hover_data=amw_hover,
            title="Dribbles/90 vs Possession Lost/90"
        )
        fig3.update_traces(marker=dict(size=10))
        fig3.add_vline(x=amw_df["Drb/90"].mean(), line_dash="dash", line_color="gray")
        fig3.add_hline(y=amw_df["Poss Lost/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig3, use_container_width=True)

    # Plot 4: Shot Creation — Shot % vs Shots Outside Box
    if "Shot %" in amw_df.columns and "Shots Outside Box/90" in amw_df.columns:
        fig4 = px.scatter(
            amw_df,
            x="Shot %",
            y="Shots Outside Box/90",
            color="Source",
            hover_name=name_col,
            hover_data=amw_hover,
            title="Shooting Accuracy vs Shots Outside Box"
        )
        fig4.update_traces(marker=dict(size=10))
        fig4.add_vline(x=amw_df["Shot %"].mean(), line_dash="dash", line_color="gray")
        fig4.add_hline(y=amw_df["Shots Outside Box/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig4, use_container_width=True)

    # Plot 5: Passing Impact — Pass % vs Open Play Key Passes
    if "Pas %" in amw_df.columns and "OP-KP/90" in amw_df.columns:
        fig5 = px.scatter(
            amw_df,
            x="Pas %",
            y="OP-KP/90",
            color="Source",
            hover_name=name_col,
            hover_data=amw_hover,
            title="Passing % vs Open Play Key Passes per 90"
        )
        fig5.update_traces(marker=dict(size=10))
        fig5.add_vline(x=amw_df["Pas %"].mean(), line_dash="dash", line_color="gray")
        fig5.add_hline(y=amw_df["OP-KP/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig5, use_container_width=True)


    # Striker Section
    st.markdown("---")
    st.subheader("🥅 Striker Assessment")
    st_df = filtered_df[filtered_df["All Positions"].apply(lambda pos: any(p.startswith("ST") for p in pos))]

    # Calculate Excitement and Scout Factor
    st_df = st_df.copy()
    st_df["Excitement"] = st_df[["Gls", "Ast", "Drb", "K Pas"]].sum(axis=1, min_count=1)
    st_df["Scout Factor"] = (st_df["Drb/90"] / st_df["Poss Lost/90"]).round(3)

    st_hover = ["Excitement", "Scout Factor", "Gls", "Ast", "Drb", "K Ps/90", "Shot %", "Hdrs W/90", "xG/90"]

    # Plot 1: Finishing — Shot % vs Goals
    if "Shot %" in st_df.columns and "Gls" in st_df.columns:
        fig1 = px.scatter(
            st_df,
            x="Shot %",
            y="Gls",
            color="Source",
            hover_name=name_col,
            hover_data=st_hover,
            title="Shot Accuracy vs Total Goals"
        )
        fig1.update_traces(marker=dict(size=10))
        fig1.add_vline(x=st_df["Shot %"].mean(), line_dash="dash", line_color="gray")
        fig1.add_hline(y=st_df["Gls"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig1, use_container_width=True)

    # Plot 2: Conversion — xG/90 vs Goals
    if "xG/90" in st_df.columns and "Gls" in st_df.columns:
        fig2 = px.scatter(
            st_df,
            x="xG/90",
            y="Gls",
            color="Source",
            hover_name=name_col,
            hover_data=st_hover,
            title="Expected Goals/90 vs Goals"
        )
        fig2.update_traces(marker=dict(size=10))
        fig2.add_vline(x=st_df["xG/90"].mean(), line_dash="dash", line_color="gray")
        fig2.add_hline(y=st_df["Gls"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig2, use_container_width=True)

    # Plot 3: Aerial Ability — Jumping vs Headers Won/90
    if "Jum" in st_df.columns and "Hdrs W/90" in st_df.columns:
        fig3 = px.scatter(
            st_df,
            x="Jum",
            y="Hdrs W/90",
            color="Source",
            hover_name=name_col,
            hover_data=st_hover,
            title="Jumping vs Headers Won per 90"
        )
        fig3.update_traces(marker=dict(size=10))
        fig3.add_vline(x=st_df["Jum"].mean(), line_dash="dash", line_color="gray")
        fig3.add_hline(y=st_df["Hdrs W/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig3, use_container_width=True)

    # Plot 4: Movement — Off the Ball vs Conversion Rate
    if "OtB" in st_df.columns and "Conv %" in st_df.columns:
        fig4 = px.scatter(
            st_df,
            x="OtB",
            y="Conv %",
            color="Source",
            hover_name=name_col,
            hover_data=st_hover,
            title="Off the Ball vs Conversion Rate"
        )
        fig4.update_traces(marker=dict(size=10))
        fig4.add_vline(x=st_df["OtB"].mean(), line_dash="dash", line_color="gray")
        fig4.add_hline(y=st_df["Conv %"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig4, use_container_width=True)

    # Plot 5: Risk vs Reward — Dribbles/90 vs Possession Lost/90
    if "Drb/90" in st_df.columns and "Poss Lost/90" in st_df.columns:
        fig5 = px.scatter(
            st_df,
            x="Drb/90",
            y="Poss Lost/90",
            color="Source",
            hover_name=name_col,
            hover_data=st_hover,
            title="Dribbles vs Possession Lost"
        )
        fig5.update_traces(marker=dict(size=10))
        fig5.add_vline(x=st_df["Drb/90"].mean(), line_dash="dash", line_color="gray")
        fig5.add_hline(y=st_df["Poss Lost/90"].mean(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig5, use_container_width=True)

with raw_tab:
    st.subheader(":clipboard: Raw Data")
    st.dataframe(combined_df)
