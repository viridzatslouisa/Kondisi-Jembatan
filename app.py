from click import style
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================

st.set_page_config(
    page_title="Dashboard Kondisi Jembatan Berdasarkan Ruas Jalan Provinsi Jawa Timur",
    page_icon="🌉",
    layout="wide"
)

# =====================================================
# CSS CUSTOM
# =====================================================

st.markdown("""
<style>

/* SIDEBAR */
[data-testid="stSidebar"]{
    background-color:#EEF3F8;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{
    color:#0B3C91;
}

/* MULTISELECT */
.stMultiSelect > div > div{
    border-radius:12px !important;
    border:2px solid #D6E4F0 !important;
}

/* PILLS FILTER */
span[data-baseweb="tag"]{
    background-color:#3B5B8A !important;
    color:white !important;
    border-radius:20px !important;
}

/* LABEL FILTER */
label{
    font-weight:600 !important;
}

/* KPI */
[data-testid="stMetric"]{
    background:white;
    border-left:5px solid #3B5B8A;
    padding:18px;
    border-radius:15px;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

            
.chart-card{
background:white;
padding:20px;
border-radius:20px;
box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

.main {
    background-color: #F5F7FA;
}

.kpi-card {
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}

.main{
background: linear-gradient(
180deg,
#F4F8FC 0%,
#EEF4FA 100%
);
}
}

[data-testid="stMetric"]{
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 3px 10px rgba(0,0,0,0.1);
}

</style>
""",
unsafe_allow_html=True)

st.markdown("""
<style>

.main::before{
content:"";
position:fixed;
top:50%;
left:55%;
width:600px;
height:600px;
background-image:url('https://upload.wikimedia.org/wikipedia/commons/7/74/Coat_of_arms_of_East_Java.svg');
background-repeat:no-repeat;
background-size:contain;
opacity:0.03;
transform:translate(-50%,-50%);
pointer-events:none;
z-index:-1;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv(
    "kondisi_jembatan.csv",
    sep=";"
)

# =====================================================

# HEADER

# =====================================================

col1, col2, col3 = st.columns([1,5,1])

with col1:
    st.image("logo_provinsi_jatim.png", width=60)

with col2:
    st.markdown("""<div style="text-align:center;">
        <h1 style="color:#0B3C91; margin-bottom:5px; font-size:34px;">
            Dashboard Analisis Kondisi Jembatan Jawa Timur
        </h1>
        <p style="color:#666666; font-size:18px; margin-top:0px;">
            Monitoring dan Evaluasi Kondisi Infrastruktur Jembatan
        </p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.image("logo_kominfo.png", width=90)

st.markdown("""

<div style="
background-color:#F8FAFC;
padding:12px;
border-radius:10px;
border-left:6px solid #0B3C91;
margin-top:10px;
margin-bottom:15px;
">

Dashboard ini digunakan untuk memantau kondisi jembatan berdasarkan
wilayah, periode update, dan kategori kondisi jembatan.

</div>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# SIDEBAR FILTER
# =====================================================

st.sidebar.header("Filter Dashboard")

st.sidebar.info(
    f"""
    Total Data : {len(df):,}

    Kabupaten/Kota : {df['kab_kota'].nunique()}

    Jembatan : {df['nama_jembatan'].nunique()}
    """
)

periode_filter = st.sidebar.multiselect(
    "📅 Pilih Periode",
    options=sorted(df["periode_update"].unique()),
    default=sorted(df["periode_update"].unique())
)

kab_filter = st.sidebar.multiselect(
    "📍 Pilih Kabupaten/Kota",
    options=sorted(df["kab_kota"].unique()),
    default=sorted(df["kab_kota"].unique())
)

kategori_filter = st.sidebar.multiselect(
    "🏗️ Pilih Kondisi",
    options=sorted(df["kategori"].unique()),
    default=sorted(df["kategori"].unique())
)

filtered = df[
    (df["periode_update"].isin(periode_filter)) &
    (df["kab_kota"].isin(kab_filter)) &
    (df["kategori"].isin(kategori_filter))
]

if st.sidebar.button("🔄 Reset Filter"):
    st.rerun()
if len(periode_filter) == 0:
    periode_label = "Semua Periode"
elif len(periode_filter) == 1:
    periode_label = f"Periode {periode_filter[0]}"
else:
    periode_label = f"Periode {min(periode_filter)}–{max(periode_filter)}"

st.markdown("### 📊 Ringkasan Utama")

# =====================================================
# KPI
# =====================================================

total_jembatan = filtered["nama_jembatan"].nunique()

rusak_ringan = filtered[
    filtered["kategori"].str.contains("RINGAN", case=False, na=False)
].shape[0]

rusak_berat = filtered[
    filtered["kategori"].str.contains("BERAT", case=False, na=False)
].shape[0]

kritis = filtered[
    filtered["kategori"].str.contains("KRITIS", case=False, na=False)
].shape[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🌉 Total Jembatan",
        total_jembatan
    )

with col2:
    st.metric(
        "🟡 Rusak Ringan",
        rusak_ringan
    )

with col3:
    st.metric(
        "🟠 Rusak Berat",
        rusak_berat
    )

with col4:
    st.metric(
        "🔴 Kritis",
        kritis
    )

st.divider()

# =====================================================
# GRAFIK BARIS PERTAMA
# =====================================================

col1, col2 = st.columns([1,1])

with col1:

    kondisi = (
        filtered.groupby("kategori")
        .size()
        .reset_index(name="Jumlah")
    )

    fig1 = px.pie(
        kondisi,
        names="kategori",
        values="Jumlah",
        title="Distribusi Kondisi Jembatan",
        color="kategori",
        color_discrete_map={
            "KONDISI RUSAK RINGAN": "#8DA9C4",
            "KONDISI RUSAK SEDANG": "#5E81AC",
            "KONDISI RUSAK BERAT": "#3B5B8A",
            "KONDISI KRITIS": "#1B365D",
            "KONDISI BAIK": "#D9E6F2",
            "KONDISI RUNTUH": "#0F172A"
        }
    )

    fig1.update_traces(
        textposition="outside",
        textinfo="percent",
        textfont_size=14,
        automargin=True,
        marker=dict(
            line=dict(
                color="white",
                width=2
            )
        )
    )

    fig1.update_layout(
        height=500,
        title={
            "text":f"Distribusi Kondisi Jembatan ({periode_label})",
            "x":0.5,
            "xanchor":"center",
            "y":0.95
        },
        legend=dict(
            orientation="h",
            y=-0.15,
            x=0.5,
            xanchor="center",
            font=dict(size=12)
        ),
        margin=dict(
            l=20,
            r=20,
            t=80,
            b=80
        ),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with col2:

    top_kab = (
        filtered.groupby("kab_kota")
        .size()
        .reset_index(name="Jumlah")
        .sort_values("Jumlah", ascending=False)
        .head(10)
    )

    fig2 = px.bar(
        top_kab,
        x="Jumlah",
        y="kab_kota",
        orientation="h",
        title="Top 10 Kabupaten/Kota",
        template="plotly_white",
        color_discrete_sequence=["#3B5B8A"]
    )

    fig2.update_layout(
        title={
            'text': 'Top 10 Kabupaten/Kota',
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =====================================================
# TREND PERIODE
# =====================================================

# =====================================================
# KOMPOSISI KONDISI PER PERIODE
# =====================================================

trend = (
    filtered.groupby(["periode_update", "kategori"])
    .size()
    .reset_index(name="Jumlah")
)

fig3 = px.bar(
    trend,
    x="periode_update",
    y="Jumlah",
    color="kategori",
    barmode="stack",
    text_auto=True,
    title="Komposisi Kondisi Jembatan per Periode",
    color_discrete_map={
        "KONDISI BAIK": "#D9E6F2",
        "KONDISI RUSAK RINGAN": "#8DA9C4",
        "KONDISI RUSAK SEDANG": "#5E81AC",
        "KONDISI RUSAK BERAT": "#3B5B8A",
        "KONDISI KRITIS": "#1B365D",
        "KONDISI RUNTUH": "#0F172A"
    }
)

fig3.update_layout(
    height=550,
    title={
        "text": "Komposisi Kondisi Jembatan per Periode",
        "x": 0.5,
        "xanchor": "center"
    },
    xaxis_title="Periode Update",
    yaxis_title="Jumlah Jembatan",
    legend_title="Kategori",
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=20, r=20, t=70, b=20),
    legend=dict(
        orientation="h",
        y=-0.25,
        x=0.5,
        xanchor="center"
    )
)

fig3.update_traces(
    marker_line_color="white",
    marker_line_width=1
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =====================================================
# INSIGHT
# =====================================================

st.subheader("")

if len(filtered) > 0:

    top_area = (
        filtered.groupby("kab_kota")
        .size()
        .sort_values(ascending=False)
        .index[0]
    )

    st.markdown(f"""
<div style="
background:#E8F0FE;
padding:20px;
border-left:8px solid #0B3C91;
border-radius:10px;
">

<h4>📌 Insight Utama</h4>

Kabupaten/Kota dengan jumlah data kondisi jembatan terbanyak adalah
<b>{top_area}</b>.

</div>
""",
unsafe_allow_html=True)

# =====================================================
# DETAIL DATA
# =====================================================

st.subheader("📋 Detail Data Jembatan")

st.dataframe(
    filtered[
        [
            "kab_kota",
            "nama_jembatan",
            "kategori",
            "periode_update",
            "tahun"
        ]
    ],
    use_container_width=True
)
