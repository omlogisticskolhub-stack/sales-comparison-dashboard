import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Sales & Weight Cycle Comparison - Om Logistics",
    page_icon="📊",
    layout="wide",
)

# ==========================================
# 🔒 PASSWORD PROTECTION SYSTEM (123456)
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == "123456":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("### 🔒 Om Logistics — Sales Comparison Portal")
        st.text_input(
            "Enter Password:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Incorrect Password!")
    return False

if not check_password():
    st.stop()

# ==========================================
# 🎨 PROFESSIONAL DASHBOARD STYLING
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #0f172a; }
    .stApp { background-color: #f8fafc; }
    
    .hub-header {
        background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
        padding: 20px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
    }
    .hub-title { font-size: 22px; font-weight: 900; margin: 0; letter-spacing: -0.5px; }
    .hub-sub { font-size: 13px; opacity: 0.95; margin-top: 4px; font-weight: 500; }
    
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }
    
    .section-head {
        font-size: 16px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 15px;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 3px solid #dc2626;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hub-header">
        <div class="hub-title">📊 SALES & TONNAGE CYCLE COMPARISON HUB</div>
        <div class="hub-sub">Om Logistics Control Tower — Branch-Wise & Mode-Wise Performance Variance (WT & AMT)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 🛠️ DATA PROCESSING
# ==========================================
MODE_COLS = [
    "SURFACE", "EXPRESS", "TRAIN", "AIR", "WH", "OM_EXP",
    "SPEED_TRUCKING", "HAND_CARRY", "IN_CONTAINER", "AIR_EXPRESS", "TOTAL"
]

def process_sales_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.upper()

    available_modes = [c for c in MODE_COLS if c in df.columns]
    for col in available_modes:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["CONTROL_BRANCH"] = pd.to_numeric(df["CONTROL_BRANCH"], errors="coerce").fillna(0).astype(int)
    df["BRANCH_CODE"] = pd.to_numeric(df["BRANCH_CODE"], errors="coerce").fillna(0).astype(int)
    df["CTR_BRANCH_NAME"] = df["CTR_BRANCH_NAME"].astype(str).str.strip()
    df["BRANCH_NAME"] = df["BRANCH_NAME"].astype(str).str.strip()
    df["STATUS"] = df["STATUS"].astype(str).str.strip().str.upper()

    df_wt = df[df["STATUS"] == "WT"].copy()
    df_amt = df[df["STATUS"] == "AMT"].copy()

    group_keys = ["CONTROL_BRANCH", "CTR_BRANCH_NAME", "BRANCH_CODE", "BRANCH_NAME"]
    wt_grouped = df_wt.groupby(group_keys, as_index=False)[available_modes].sum()
    amt_grouped = df_amt.groupby(group_keys, as_index=False)[available_modes].sum()

    merged = pd.merge(
        wt_grouped,
        amt_grouped,
        on=group_keys,
        how="outer",
        suffixes=("_WT", "_AMT"),
    ).fillna(0.0)

    return merged, available_modes

def format_wt_clean(kg):
    if abs(kg) >= 1000000:
        return f"{kg / 1000000:,.2f} MT"
    elif abs(kg) >= 1000:
        return f"{kg / 1000:,.2f} Ton"
    return f"{kg:,.1f} KG"

def format_amt_clean(val):
    if abs(val) >= 10000000:
        return f"₹ {val / 10000000:,.2f} Cr"
    elif abs(val) >= 100000:
        return f"₹ {val / 100000:,.2f} L"
    return f"₹ {val:,.0f}"

# ==========================================
# 📥 FILE UPLOADERS FOR DUAL CYCLES
# ==========================================
if "df_p1" not in st.session_state:
    st.session_state["df_p1"] = None
if "df_p2" not in st.session_state:
    st.session_state["df_p2"] = None
if "modes_list" not in st.session_state:
    st.session_state["modes_list"] = []

u_col1, u_col2 = st.columns(2)

with u_col1:
    p1_label = st.text_input("🗓️ Period 1 Label:", value="Cycle 1 (Base)")
    file_p1 = st.file_uploader("📥 Upload Period 1 Sales Report", type=["xlsx", "xls"], key="up1")
    if file_p1 is not None:
        df1, modes1 = process_sales_file(file_p1)
        st.session_state["df_p1"] = df1
        st.session_state["modes_list"] = modes1

with u_col2:
    p2_label = st.text_input("🗓️ Period 2 Label:", value="Cycle 2 (Current)")
    file_p2 = st.file_uploader("📥 Upload Period 2 Sales Report (Optional)", type=["xlsx", "xls"], key="up2")
    if file_p2 is not None:
        df2, modes2 = process_sales_file(file_p2)
        st.session_state["df_p2"] = df2
        if not st.session_state["modes_list"]:
            st.session_state["modes_list"] = modes2

st.markdown("---")

# ==========================================
# 📊 DASHBOARD ANALYTICS & FILTERS
# ==========================================
if st.session_state["df_p1"] is not None:
    df1 = st.session_state["df_p1"].copy()
    modes = st.session_state["modes_list"]
    has_p2 = st.session_state["df_p2"] is not None

    df2 = st.session_state["df_p2"].copy() if has_p2 else df1.copy()
    if not has_p2:
        for col in df2.columns:
            if col.endswith("_WT") or col.endswith("_AMT"):
                df2[col] = 0.0

    keys = ["CONTROL_BRANCH", "CTR_BRANCH_NAME", "BRANCH_CODE", "BRANCH_NAME"]
    comp_df = pd.merge(df1, df2, on=keys, how="outer", suffixes=("_P1", "_P2")).fillna(0.0)

    comp_df["CONTROL_LABEL"] = comp_df["CONTROL_BRANCH"].astype(str) + " - " + comp_df["CTR_BRANCH_NAME"]
    comp_df["BRANCH_LABEL"] = comp_df["BRANCH_CODE"].astype(str) + " - " + comp_df["BRANCH_NAME"]

    # Filters
    f1, f2, f3 = st.columns([1.2, 1.2, 1])

    all_controls = sorted(comp_df["CONTROL_LABEL"].unique().tolist())
    default_ctrl = [c for c in all_controls if c.startswith("801 ")]

    with f1:
        selected_controls = st.multiselect(
            "🏢 Controlling Branch (e.g. 801):",
            options=all_controls,
            default=default_ctrl if default_ctrl else [],
        )

    temp_df = comp_df[comp_df["CONTROL_LABEL"].isin(selected_controls)] if selected_controls else comp_df

    with f2:
        all_branches = sorted(temp_df["BRANCH_LABEL"].unique().tolist())
        selected_branches = st.multiselect("📍 Sub-Branch Filter:", options=all_branches, default=[])

    with f3:
        selectable_modes = [m for m in modes if m != "TOTAL"]
        selected_mode = st.selectbox("🚛 Service Mode:", options=["ALL MODES (TOTAL)"] + selectable_modes, index=0)

    filtered = temp_df.copy()
    if selected_branches:
        filtered = filtered[filtered["BRANCH_LABEL"].isin(selected_branches)]

    mode_key = "TOTAL" if selected_mode == "ALL MODES (TOTAL)" else selected_mode

    wt_p1_col, wt_p2_col = f"{mode_key}_WT_P1", f"{mode_key}_WT_P2"
    amt_p1_col, amt_p2_col = f"{mode_key}_AMT_P1", f"{mode_key}_AMT_P2"

    tot_wt_p1 = filtered[wt_p1_col].sum()
    tot_wt_p2 = filtered[wt_p2_col].sum() if has_p2 else 0.0
    diff_wt = tot_wt_p2 - tot_wt_p1
    pct_wt = ((diff_wt / tot_wt_p1) * 100) if tot_wt_p1 > 0 else 0.0

    tot_amt_p1 = filtered[amt_p1_col].sum()
    tot_amt_p2 = filtered[amt_p2_col].sum() if has_p2 else 0.0
    diff_amt = tot_amt_p2 - tot_amt_p1
    pct_amt = ((diff_amt / tot_amt_p1) * 100) if tot_amt_p1 > 0 else 0.0

    # KPI Summary with Correct Delta Color Logic
    st.markdown(f"<div class='section-head'>📌 Overall Performance Summary ({selected_mode})</div>", unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric(f"⚖️ {p1_label} Weight", format_wt_clean(tot_wt_p1))
    
    # Correct delta color: normal means positive=green, negative=red (inverse=False)
    wt_delta_color = "normal" if diff_wt >= 0 else "inverse"
    k2.metric(
        f"⚖️ {p2_label} Weight", 
        format_wt_clean(tot_wt_p2) if has_p2 else "Waiting...", 
        delta=f"{diff_wt/1000:+,.2f} Ton ({pct_wt:+.1f}%)" if has_p2 else None,
        delta_color=wt_delta_color
    )
    k3.metric("📉 Weight Variance", f"{diff_wt:+,.1f} KG" if has_p2 else "-")

    k4.metric(f"💰 {p1_label} Sales", format_amt_clean(tot_amt_p1))
    
    amt_delta_color = "normal" if diff_amt >= 0 else "inverse"
    k5.metric(
        f"💰 {p2_label} Sales", 
        format_amt_clean(tot_amt_p2) if has_p2 else "Waiting...", 
        delta=f"₹ {diff_amt:+,.0f} ({pct_amt:+.1f}%)" if has_p2 else None,
        delta_color=amt_delta_color
    )
    k6.metric("📉 Sales Variance", f"₹ {diff_amt:+,.0f}" if has_p2 else "-")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    c_chart1, c_chart2 = st.columns(2)
    chart_df = filtered.groupby(["BRANCH_CODE", "BRANCH_NAME"], as_index=False)[[wt_p1_col, wt_p2_col, amt_p1_col, amt_p2_col]].sum().sort_values(by=wt_p1_col, ascending=False).head(12)
    chart_df["Branch"] = chart_df["BRANCH_CODE"].astype(str) + "-" + chart_df["BRANCH_NAME"].str[:12]

    with c_chart1:
        st.markdown("<div class='section-head'>⚖️ Branch Weight Comparison</div>", unsafe_allow_html=True)
        fig_wt = go.Figure()
        fig_wt.add_trace(go.Bar(name=p1_label, x=chart_df["Branch"], y=chart_df[wt_p1_col], marker_color="#475569"))
        if has_p2:
            fig_wt.add_trace(go.Bar(name=p2_label, x=chart_df["Branch"], y=chart_df[wt_p2_col], marker_color="#dc2626"))
        fig_wt.update_layout(
            barmode="group", height=360, margin=dict(l=10, r=10, t=20, b=40),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_wt, use_container_width=True)

    with c_chart2:
        st.markdown("<div class='section-head'>💰 Branch Sales Amount Comparison</div>", unsafe_allow_html=True)
        fig_amt = go.Figure()
        fig_amt.add_trace(go.Bar(name=p1_label, x=chart_df["Branch"], y=chart_df[amt_p1_col], marker_color="#0284c7"))
        if has_p2:
            fig_amt.add_trace(go.Bar(name=p2_label, x=chart_df["Branch"], y=chart_df[amt_p2_col], marker_color="#16a34a"))
        fig_amt.update_layout(
            barmode="group", height=360, margin=dict(l=10, r=10, t=20, b=40),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_amt, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Table
    st.markdown(f"<div class='section-head'>📋 Branch-Wise Detailed Comparison Report ({selected_mode})</div>", unsafe_allow_html=True)
    table_df = filtered[["CONTROL_BRANCH", "CTR_BRANCH_NAME", "BRANCH_CODE", "BRANCH_NAME", wt_p1_col, wt_p2_col, amt_p1_col, amt_p2_col]].copy()
    table_df["WT_Diff (KG)"] = table_df[wt_p2_col] - table_df[wt_p1_col]
    table_df["WT_Growth %"] = table_df.apply(lambda r: round(((r[wt_p2_col] - r[wt_p1_col]) / r[wt_p1_col] * 100), 1) if r[wt_p1_col] > 0 else 0.0, axis=1)
    table_df["AMT_Diff (₹)"] = table_df[amt_p2_col] - table_df[amt_p1_col]
    table_df["AMT_Growth %"] = table_df.apply(lambda r: round(((r[amt_p2_col] - r[amt_p1_col]) / r[amt_p1_col] * 100), 1) if r[amt_p1_col] > 0 else 0.0, axis=1)

    table_df = table_df.sort_values(by=wt_p1_col, ascending=False).reset_index(drop=True)
    table_df.columns = [
        "Ctrl Code", "Controlling Hub", "Branch Code", "Branch Name",
        f"{p1_label} WT (KG)", f"{p2_label} WT (KG)",
        f"{p1_label} AMT (₹)", f"{p2_label} AMT (₹)",
        "WT Variance (KG)", "WT Growth %",
        "AMT Variance (₹)", "AMT Growth %"
    ]

    if not has_p2:
        table_df = table_df[["Ctrl Code", "Controlling Hub", "Branch Code", "Branch Name", f"{p1_label} WT (KG)", f"{p1_label} AMT (₹)"]]

    st.dataframe(table_df, use_container_width=True, height=400, hide_index=True)

    csv_out = table_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Comparison Report (CSV)", data=csv_out, file_name="OmLogistics_Sales_Comparison.csv", mime="text/csv")

else:
    st.info("💡 ऊपर **Period 1** में अपनी सेल्स रिपोर्ट अपलोड करें। जब दूसरी साइकिल की फाइल आए, तो **Period 2** में डालें — कंपैरिजन अपने आप तैयार हो जाएगा!")
