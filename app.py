import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =============================================================================
# 1. KONFIGURASI HALAMAN & STYLING CUSTOM CSS (Sesuai Gambar UI)
# =============================================================================
st.set_page_config(
    page_title="Executive Sales & Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Background Utama Modern Light Purple Gray */
    .stApp {
        background-color: #F3F1FA;
    }
    
    /* Font Header */
    h1, h2, h3, h4 {
        color: #5D54A4;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-weight: 700;
    }

    /* KPI Cards Styling */
    .kpi-card {
        padding: 16px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        min-height: 90px;
    }
    .kpi-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.9;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 800;
    }

    /* Warna Khas KPI Sesuai Gambar */
    .kpi-purple { background: linear-gradient(135deg, #A89FE2 0%, #8E82E0 100%); }
    .kpi-red    { background: linear-gradient(135deg, #FF8A8A 0%, #FF5A5A 100%); }
    .kpi-pink   { background: linear-gradient(135deg, #FF7BB0 0%, #FF408C 100%); }
    .kpi-green  { background: linear-gradient(135deg, #2CD196 0%, #10B981 100%); }
    .kpi-blue   { background: linear-gradient(135deg, #4DA8FF 0%, #1A8CFF 100%); }

    /* Custom Container/Card untuk Chart */
    .chart-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(100, 90, 160, 0.05);
        margin-bottom: 20px;
        border: 1px solid #EBE7F6;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #5D4FA8 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #7262C0 !important;
        border-color: #8D7DD8 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. LOAD DATA CLEANED (Menggunakan File Hasil Download)
# =============================================================================
@st.cache_data
def load_clean_data():
    sf_file = 'Sleekflow_Cleaned.csv'
    sl_file = 'Sales_Cleaned.csv'
    csat_file = 'CSAT_Cleaned.csv'
    rt_file = 'Response_Time_Cleaned.csv'

    sf = pd.read_csv(sf_file, low_memory=False) if os.path.exists(sf_file) else pd.DataFrame()
    sl = pd.read_csv(sl_file, low_memory=False) if os.path.exists(sl_file) else pd.DataFrame()
    csat = pd.read_csv(csat_file, low_memory=False) if os.path.exists(csat_file) else pd.DataFrame()
    rt = pd.read_csv(rt_file, low_memory=False) if os.path.exists(rt_file) else pd.DataFrame()

    # Fast Date Parsing
    if not sf.empty:
        sf['Last_Contact_Date'] = pd.to_datetime(sf['Last_Contact_Date'], errors='coerce').dt.date
    if not sl.empty:
        sl['Tanggal_Date'] = pd.to_datetime(sl['Tanggal_Date'], errors='coerce').dt.date
    if not csat.empty:
        csat['Tanggal_Date'] = pd.to_datetime(csat['Tanggal_Date'], errors='coerce').dt.date
    if not rt.empty:
        rt['Tanggal_Date'] = pd.to_datetime(rt['Tanggal_Date'], errors='coerce').dt.date

    return sf, sl, csat, rt

sf_df, sl_df, csat_df, rt_df = load_clean_data()


# =============================================================================
# 3. SIDEBAR & FILTER PANEL
# =============================================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1828/1828859.png", width=50)
st.sidebar.markdown("## Navigation & Filters")

# Filter Agent / Sales CS
all_agents = sorted(list(set(
    [a for a in sf_df['ContactOwner'].dropna().unique() if a and str(a) != 'nan'] +
    [a for a in sl_df['sales'].dropna().unique() if a and str(a) != 'nan'] +
    [a for a in csat_df['Nama Agent'].dropna().unique() if a and str(a) != 'nan']
)))

selected_agent = st.sidebar.selectbox("👤 Select Sales / Agent", ["All Agents"] + all_agents)

# Date Filter
min_d = pd.to_datetime('2026-09-01').date()
max_d = pd.to_datetime('2026-09-24').date()
selected_dates = st.sidebar.date_input("📅 Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

start_d, end_d = selected_dates if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2 else (min_d, max_d)

# Applying Filter
sf_f = sf_df[(sf_df['Last_Contact_Date'] >= start_d) & (sf_df['Last_Contact_Date'] <= end_d)] if not sf_df.empty else sf_df
sl_f = sl_df[(sl_df['Tanggal_Date'] >= start_d) & (sl_df['Tanggal_Date'] <= end_d)] if not sl_df.empty else sl_df
csat_f = csat_df[(csat_df['Tanggal_Date'] >= start_d) & (csat_df['Tanggal_Date'] <= end_d)] if not csat_df.empty else csat_df
rt_f = rt_df[(rt_df['Tanggal_Date'] >= start_d) & (rt_df['Tanggal_Date'] <= end_d)] if not rt_df.empty else rt_df

if selected_agent != "All Agents":
    sf_f = sf_f[sf_f['ContactOwner'] == selected_agent]
    sl_f = sl_f[sl_f['sales'] == selected_agent]
    csat_f = csat_f[csat_f['Nama Agent'] == selected_agent]
    rt_f = rt_f[rt_f['Agent_Clean'] == selected_agent]


# =============================================================================
# 4. DASHBOARD HEADER & TOP KPI CARDS
# =============================================================================
st.title("Performance & Sales Executive Dashboard")
st.markdown("<p style='color: #7A72A9; margin-top: -10px;'>Cleaned Dataset Analytics Overview</p>", unsafe_allow_html=True)

# Calculation for Top KPI Box
total_revenue = sl_f['amount_clean'].sum() if not sl_f.empty else 0
avg_deal = sl_f['amount_clean'].mean() if not sl_f.empty else 0
total_invoices = sl_f['invoice_no'].nunique() if not sl_f.empty else 0
total_traffic = sf_f['PhoneNumber_Clean'].nunique() if not sf_f.empty else 0
total_meals = sl_f['qty_meal'].sum() if not sl_f.empty else 0

k1, k2, k3, k4, k5 = st.columns(5)

k1.markdown(f'''
<div class="kpi-card kpi-purple">
    <div class="kpi-title"> Total Revenue</div>
    <div class="kpi-value">{total_revenue/1e6:,.1f}M</div>
</div>
''', unsafe_allow_html=True)

k2.markdown(f'''
<div class="kpi-card kpi-red">
    <div class="kpi-title"> Avg Deal Value</div>
    <div class="kpi-value">{avg_deal/1e3:,.0f}K</div>
</div>
''', unsafe_allow_html=True)

k3.markdown(f'''
<div class="kpi-card kpi-pink">
    <div class="kpi-title"> Total Invoices</div>
    <div class="kpi-value">{total_invoices:,}</div>
</div>
''', unsafe_allow_html=True)

k4.markdown(f'''
<div class="kpi-card kpi-green">
    <div class="kpi-title"> Total Traffic</div>
    <div class="kpi-value">{total_traffic:,}</div>
</div>
''', unsafe_allow_html=True)

k5.markdown(f'''
<div class="kpi-card kpi-blue">
    <div class="kpi-title"> Total Meals Sold</div>
    <div class="kpi-value">{total_meals:,.0f}</div>
</div>
''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# 5. MIDDLE ROW CHARTS
# =============================================================================
col_m1, col_m2 = st.columns([1.6, 1])

# --- Chart Left: Line Trend (Sales vs Traffic) ---
with col_m1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("<h4>📈 Revenue & Traffic Trend Harian</h4>", unsafe_allow_html=True)
    
    # Keterangan Warna Sesuai Permintaan (Badge Penjelas)
    st.markdown("""
        <div style="display: flex; gap: 15px; margin-bottom: 10px; font-size: 13px; font-weight: bold;">
            <span style="color: #8E82E0; background-color: #F0EBFB; padding: 4px 10px; border-radius: 6px; border: 1px solid #8E82E0;">
                🟣 Revenue (IDR)
            </span>
            <span style="color: #FF5A5A; background-color: #FFEAEA; padding: 4px 10px; border-radius: 6px; border: 1px solid #FF5A5A;">
                🔴 Traffic / Leads
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    tr_harian = sf_f.groupby('Last_Contact_Date')['PhoneNumber_Clean'].nunique().reset_index().rename(columns={'Last_Contact_Date':'Tanggal', 'PhoneNumber_Clean':'Traffic'}) if not sf_f.empty else pd.DataFrame(columns=['Tanggal', 'Traffic'])
    sl_harian = sl_f.groupby('Tanggal_Date')['amount_clean'].sum().reset_index().rename(columns={'Tanggal_Date':'Tanggal', 'amount_clean':'Revenue'}) if not sl_f.empty else pd.DataFrame(columns=['Tanggal', 'Revenue'])
    
    trend_df = pd.merge(tr_harian, sl_harian, on='Tanggal', how='outer').fillna(0).sort_values('Tanggal')

    fig_trend = go.Figure()
    
    # Garis Ungu untuk Revenue
    fig_trend.add_trace(go.Scatter(
        x=trend_df['Tanggal'], 
        y=trend_df['Revenue'], 
        name='Revenue (IDR)', 
        mode='lines+markers', 
        line=dict(color='#8E82E0', width=3)
    ))
    
    # Garis Merah Putus-putus untuk Traffic
    fig_trend.add_trace(go.Scatter(
        x=trend_df['Tanggal'], 
        y=trend_df['Traffic'], 
        name='Traffic (Leads)', 
        yaxis='y2', 
        mode='lines+markers', 
        line=dict(color='#FF5A5A', width=2, dash='dot')
    ))
    
    fig_trend.update_layout(
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        
        # Axis Y Kiri (Revenue - Ungu)
        yaxis=dict(
            title=dict(text='Revenue (IDR)', font=dict(color='#8E82E0', size=12)),
            tickfont=dict(color='#8E82E0'),
            showgrid=True, 
            gridcolor='#F0EBFB'
        ),
        
        # Axis Y Kanan (Traffic - Merah)
        yaxis2=dict(
            title=dict(text='Traffic / Leads Qty', font=dict(color='#FF5A5A', size=12)),
            tickfont=dict(color='#FF5A5A'),
            overlaying='y', 
            side='right', 
            showgrid=False
        ),
        
        # Format Legenda Lebih Kontras & Jelas Ditonton
        legend=dict(
            orientation='h', 
            y=1.12, 
            x=0.1,
            font=dict(color='#2D4A3E', size=12, family="Arial"),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#D1C7EF',
            borderwidth=1
        ),
        
        # Format Sumbu X
        xaxis=dict(
            tickfont=dict(color='#5D54A4')
        ),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Chart Right: Donut Charts (Total Revenue by Division / Working Type style) ---
with col_m2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("<h4> Revenue by Division</h4>", unsafe_allow_html=True)
    
    if not sl_f.empty:
        div_summary = sl_f.groupby('Division_Mapped')['amount_clean'].sum().reset_index()
        fig_donut = px.pie(
            div_summary, 
            names='Division_Mapped', 
            values='amount_clean', 
            hole=0.6,
            color_discrete_sequence=['#8E82E0', '#2CD196', '#FF8A8A']
        )
        fig_donut.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig_donut.update_layout(
            height=320,
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# 6. BOTTOM ROW CHARTS (3 Columns - Bar, Horizontal Bar, Lollipop/Bar)
# =============================================================================
b1, b2, b3 = st.columns([1.1, 1.3, 0.8])

# --- Bottom Left: Horizontal Bar Chart (Revenue by Sales Agent) ---
with b1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("<h4>🏆 Top Sales Agents</h4>", unsafe_allow_html=True)
    if not sl_f.empty:
        agent_rev = sl_f.groupby('sales')['amount_clean'].sum().reset_index().sort_values('amount_clean', ascending=True).tail(7)
        fig_agent = px.bar(
            agent_rev, 
            y='sales', 
            x='amount_clean', 
            orientation='h',
            text_auto='.2s',
            color_discrete_sequence=['#7262C0']
        )
        fig_agent.update_traces(
            textfont=dict(color='white', size=11, family="Arial Black"),
            textposition='inside'
        )
        fig_agent.update_layout(
            height=360,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=dict(text="Revenue (IDR)", font=dict(color='#2D4A3E', size=12, family="Arial")),
                tickfont=dict(color='#2D4A3E', size=11),
                showgrid=True,
                gridcolor='#EBE7F6'
            ),
            yaxis=dict(
                title=None,
                tickfont=dict(color='#2D4A3E', size=11, family="Arial"), # Teks nama agent jadi gelap & jelas
            ),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_agent, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Bottom Center: Grouped Bar Chart (Branch & Program Performance) ---
with b2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("<h4>🏬 Revenue by Branch & Program</h4>", unsafe_allow_html=True)
    if not sl_f.empty:
        branch_prog = sl_f.groupby(['branch', 'program'])['amount_clean'].sum().reset_index()
        fig_branch = px.bar(
            branch_prog, 
            x='branch', 
            y='amount_clean', 
            color='program', 
            barmode='group',
            color_discrete_sequence=['#8E82E0', '#FF7BB0', '#2CD196', '#4DA8FF', '#FF9F43', '#54a0ff']
        )
        fig_branch.update_layout(
            height=360,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=dict(text="Branch", font=dict(color='#2D4A3E', size=12)),
                tickfont=dict(color='#2D4A3E', size=10),
                tickangle=-45 # Miringkan teks branch agar tidak bertumpukan
            ),
            yaxis=dict(
                title=dict(text="Revenue (IDR)", font=dict(color='#2D4A3E', size=12)),
                tickfont=dict(color='#2D4A3E', size=11),
                showgrid=True,
                gridcolor='#EBE7F6'
            ),
            legend=dict(
                orientation='h', 
                y=1.2, 
                x=0,
                font=dict(color='#2D4A3E', size=10),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#D1C7EF',
                borderwidth=1
            ),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_branch, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Bottom Right: CSAT Point Performance ---
with b3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("<h4>⭐ CSAT Distribution</h4>", unsafe_allow_html=True)
    if not csat_f.empty:
        csat_counts = csat_f['CSAT_Point_Clean'].value_counts().reset_index()
        csat_counts.columns = ['CSAT', 'Count']
        fig_csat = px.bar(
            csat_counts, 
            x='CSAT', 
            y='Count',
            color='CSAT',
            text_auto=True,
            color_discrete_sequence=['#2CD196', '#FF8A8A', '#4DA8FF', '#FF7BB0']
        )
        fig_csat.update_traces(
            textfont=dict(color='white', size=12, family="Arial Black"),
            textposition='inside'
        )
        fig_csat.update_layout(
            height=360,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=None,
                tickfont=dict(color='#2D4A3E', size=11),
                tickangle=-30 # Miringkan teks CSAT agar terbaca jelas
            ),
            yaxis=dict(
                title=dict(text="Jumlah Respon", font=dict(color='#2D4A3E', size=12)),
                tickfont=dict(color='#2D4A3E', size=11),
                showgrid=True,
                gridcolor='#EBE7F6'
            ),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_csat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)