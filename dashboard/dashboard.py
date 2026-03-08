import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from babel.numbers import format_currency
import os

# ========= CONFIG =========
st.set_page_config(
    page_title="Dashboard Analisis E-Commerce Brasil",
    page_icon="🛒",
    layout="wide"
)

# ========= HELPER FUNCTIONS =========
def load_data():
    """Load main_data.csv dari folder dashboard."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'main_data.csv')
    df = pd.read_csv(data_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'], errors='coerce')
    return df


def create_rfm_df(df):
    """Membuat dataframe RFM dari data yang sudah difilter."""
    max_date = df['order_purchase_timestamp'].max()
    
    rfm_df = df.groupby('customer_unique_id').agg(
        last_order_date=('order_purchase_timestamp', 'max'),
        frequency=('order_id', 'nunique'),
        monetary=('price', 'sum')
    ).reset_index()
    
    rfm_df['recency'] = (max_date - rfm_df['last_order_date']).dt.days
    rfm_df.drop('last_order_date', axis=1, inplace=True)
    
    return rfm_df


def format_big_number(num):
    """Format angka besar ke string yang mudah dibaca.""" 
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}"


# ========= LOAD DATA =========
all_df = load_data()

# ========= SIDEBAR FILTERS =========
st.sidebar.image(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'myphoto.jpeg'),
    width=150
)
st.sidebar.title("🛒 E-Commerce Brasil")
st.sidebar.markdown("---")

# 1. Filter Rentang Tanggal
st.sidebar.subheader("📅 Filter Rentang Tanggal")
min_date = all_df['order_purchase_timestamp'].min().date()
max_date = all_df['order_purchase_timestamp'].max().date()

start_date = st.sidebar.date_input(
    "Tanggal Mulai",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "Tanggal Akhir",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# 2. Filter Status Order
st.sidebar.subheader("📦 Filter Status Order")
all_statuses = sorted(all_df['order_status'].unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Pilih Status Order",
    options=all_statuses,
    default=all_statuses
)

# 3. Top-N Selector
st.sidebar.subheader("🔢 Top-N Selector")
top_n = st.sidebar.slider(
    "Jumlah item yang ditampilkan di chart",
    min_value=3,
    max_value=20,
    value=10
)

# ========= APPLY FILTERS =========
filtered_df = all_df[
    (all_df['order_purchase_timestamp'].dt.date >= start_date) &
    (all_df['order_purchase_timestamp'].dt.date <= end_date) &
    (all_df['order_status'].isin(selected_statuses))
]

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Data terfilter: **{len(filtered_df):,}** baris dari **{len(all_df):,}** total")

# ========= MAIN CONTENT =========
st.title("📊 Dashboard Analisis E-Commerce Brasil")

# ========= METRICS ROW =========
total_orders = filtered_df['order_id'].nunique()
total_revenue = filtered_df['price'].sum()
total_customers = filtered_df['customer_unique_id'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Pesanan", format_big_number(total_orders))
with col2:
    st.metric("Total Pendapatan", f"R$ {format_big_number(total_revenue)}")
with col3:
    st.metric("Total Pelanggan", format_big_number(total_customers))
with col4:
    st.metric("Rata-rata Nilai Pesanan", f"R$ {avg_order_value:,.2f}")

st.markdown("---")

# ========= NAVIGATION TABS =========
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏷️ Kategori Produk",
    "🌍 Penjualan per Wilayah",
    "👥 Pelanggan Aktif/Tidak Aktif",
    "📈 Tren Penjualan",
    "💎 RFM Analysis"
])

# ========= TAB 1: KATEGORI PRODUK =========
with tab1:
    st.subheader("1. Kategori Produk dengan Pesanan dan Pendapatan Tertinggi (Jan 2017 - Ags 2018)")
    
    # Hitung data berdasarkan filter
    category_orders = (
        filtered_df.groupby('product_category_name_english')
        .agg(total_orders=('order_id', 'nunique'), total_revenue=('price', 'sum'))
        .reset_index()
    )
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write(f"#### Top {top_n} Categories by Total Orders")
        top_cat_orders = category_orders.sort_values('total_orders', ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#1f77b4' if i == 0 else '#aec7e8' for i in range(len(top_cat_orders))]
        sns.barplot(
            data=top_cat_orders,
            x='total_orders',
            y='product_category_name_english',
            hue='product_category_name_english',
            palette=colors,
            legend=False,
            ax=ax
        )
        ax.set_title(f'Top {top_n} Categories by Total Orders', fontsize=14)
        ax.set_xlabel('Total Orders')
        ax.set_ylabel('Product Category')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_b:
        st.write(f"#### Top {top_n} Categories by Total Revenue")
        top_cat_revenue = category_orders.sort_values('total_revenue', ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#2ca02c' if i == 0 else '#98df8a' for i in range(len(top_cat_revenue))]
        sns.barplot(
            data=top_cat_revenue,
            x='total_revenue',
            y='product_category_name_english',
            hue='product_category_name_english',
            palette=colors,
            legend=False,
            ax=ax
        )
        ax.set_title(f'Top {top_n} Categories by Total Revenue', fontsize=14)
        ax.set_xlabel('Total Revenue (R$)')
        ax.set_ylabel('Product Category')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    st.write("**Insight:** Kategori produk di atas dihitung secara dinamis berdasarkan rentang tanggal dan status order yang dipilih. "
             "Ubah filter di sidebar untuk melihat bagaimana ranking berubah pada periode berbeda.")

# ========= TAB 2: PENJUALAN PER WILAYAH =========
with tab2:
    st.subheader("2. Penjualan dan Profit Tertinggi per Wilayah Kota (Jan 2017 - Ags 2018)")
    
    city_sales = (
        filtered_df.groupby('customer_city')
        .agg(total_orders=('order_id', 'nunique'), total_revenue=('price', 'sum'))
        .reset_index()
    )
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write(f"#### Top {top_n} Cities by Total Orders")
        top_city_orders = city_sales.sort_values('total_orders', ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#ff7f0e' if i == 0 else '#ffbb78' for i in range(len(top_city_orders))]
        sns.barplot(
            data=top_city_orders,
            x='customer_city',
            y='total_orders',
            hue='customer_city',
            palette=colors,
            legend=False,
            ax=ax
        )
        ax.set_title(f'Top {top_n} Cities by Total Orders', fontsize=14)
        ax.set_xlabel('City')
        ax.set_ylabel('Total Orders')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_b:
        st.write(f"#### Top {top_n} Cities by Total Revenue")
        top_city_revenue = city_sales.sort_values('total_revenue', ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#9467bd' if i == 0 else '#c5b0d5' for i in range(len(top_city_revenue))]
        sns.barplot(
            data=top_city_revenue,
            x='customer_city',
            y='total_revenue',
            hue='customer_city',
            palette=colors,
            legend=False,
            ax=ax
        )
        ax.set_title(f'Top {top_n} Cities by Total Revenue', fontsize=14)
        ax.set_xlabel('City')
        ax.set_ylabel('Total Revenue (R$)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    # Scatter plot
    st.write("#### Scatter Plot: Total Orders vs Total Revenue per City")
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        city_sales['total_orders'],
        city_sales['total_revenue'],
        alpha=0.5,
        c='#1f77b4',
        edgecolors='white',
        s=50
    )
    ax.set_title('Total Orders vs Total Revenue by City', fontsize=14)
    ax.set_xlabel('Total Orders')
    ax.set_ylabel('Total Revenue (R$)')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.write("**Insight:** Terdapat korelasi positif antara total pesanan dan total pendapatan. "
             "Kota-kota besar cenderung mendominasi kedua metrik tersebut.")

# ========= TAB 3: PELANGGAN AKTIF =========
with tab3:
    st.subheader("3. Jumlah Pelanggan Aktif (>1 Transaksi) dan Tidak Aktif per Kota (Jan 2017 - Ags 2018)")
    
    # Pelanggan yang punya lebih dari 1 order = aktif, 1 order = tidak aktif
    customer_activity = (
        filtered_df.groupby(['customer_unique_id', 'customer_city'])
        .agg(order_count=('order_id', 'nunique'))
        .reset_index()
    )
    customer_activity['status'] = customer_activity['order_count'].apply(
        lambda x: 'Aktif' if x > 1 else 'Tidak Aktif'
    )
    
    active_by_city = (
        customer_activity[customer_activity['status'] == 'Aktif']
        .groupby('customer_city').size().reset_index(name='Total Pelanggan Aktif')
        .sort_values('Total Pelanggan Aktif', ascending=False)
        .head(top_n)
    )
    
    non_active_by_city = (
        customer_activity[customer_activity['status'] == 'Tidak Aktif']
        .groupby('customer_city').size().reset_index(name='Total Pelanggan Tidak Aktif')
        .sort_values('Total Pelanggan Tidak Aktif', ascending=False)
        .head(top_n)
    )
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write(f"#### Top {top_n} Cities by Active Customers")
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#2ca02c' if i == 0 else '#98df8a' for i in range(len(active_by_city))]
        sns.barplot(
            data=active_by_city,
            x='Total Pelanggan Aktif',
            y='customer_city',
            hue='customer_city',
            palette=colors,
            legend=False,
            ax=ax
        )
        ax.set_title(f'Top {top_n} Cities by Active Customers', fontsize=14)
        ax.set_xlabel('Total Active Customers')
        ax.set_ylabel('City')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_b:
        st.write(f"#### Top {top_n} Cities by Non-Active Customers")
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#d62728' if i == 0 else '#ff9896' for i in range(len(non_active_by_city))]
        sns.barplot(
            data=non_active_by_city,
            x='Total Pelanggan Tidak Aktif',
            y='customer_city',
            hue='customer_city',
            palette=colors,
            legend=False,
            ax=ax
        )
        ax.set_title(f'Top {top_n} Cities by Non-Active Customers', fontsize=14)
        ax.set_xlabel('Total Non-Active Customers')
        ax.set_ylabel('City')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.write("**Insight:** São Paulo mendominasi baik dalam jumlah pelanggan aktif maupun tidak aktif. "
             "Hal ini menunjukkan potensi besar untuk re-engagement di kota tersebut.")

# ========= TAB 4: TREN PENJUALAN =========
with tab4:
    st.subheader("4. Tren Penjualan Bulanan dan Musiman (Jan 2017 - Ags 2018)")
    
    # Monthly trend
    monthly_data = (
        filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period('M'))
        .agg(total_orders=('order_id', 'nunique'), total_revenue=('price', 'sum'))
        .reset_index()
    )
    monthly_data['order_purchase_timestamp'] = monthly_data['order_purchase_timestamp'].astype(str)
    
    st.write("#### Monthly Sales Trend")
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    color1 = '#1f77b4'
    ax1.set_xlabel('Month-Year', fontsize=12)
    ax1.set_ylabel('Total Revenue (R$)', color=color1, fontsize=12)
    ax1.plot(monthly_data['order_purchase_timestamp'], monthly_data['total_revenue'],
             marker='o', color=color1, linewidth=2, label='Revenue')
    ax1.tick_params(axis='y', labelcolor=color1)
    plt.xticks(rotation=45, ha='right')
    
    ax2 = ax1.twinx()
    color2 = '#ff7f0e'
    ax2.set_ylabel('Total Orders', color=color2, fontsize=12)
    ax2.plot(monthly_data['order_purchase_timestamp'], monthly_data['total_orders'],
             marker='s', color=color2, linewidth=2, linestyle='--', label='Orders')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.95))
    ax1.set_title('Monthly Revenue & Orders Trend', fontsize=14)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # Quarterly trend
    st.write("#### Quarterly Sales Trend")
    quarterly_data = (
        filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period('Q'))
        .agg(total_orders=('order_id', 'nunique'), total_revenue=('price', 'sum'))
        .reset_index()
    )
    quarterly_data['order_purchase_timestamp'] = quarterly_data['order_purchase_timestamp'].astype(str)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(quarterly_data))
    bars = ax.bar(x, quarterly_data['total_revenue'], color='#1f77b4', alpha=0.8)
    
    # Highlight bar tertinggi
    max_idx = quarterly_data['total_revenue'].idxmax()
    bars[max_idx].set_color('#ff7f0e')
    
    ax.set_xticks(x)
    ax.set_xticklabels(quarterly_data['order_purchase_timestamp'], rotation=45, ha='right')
    ax.set_title('Quarterly Revenue', fontsize=14)
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Total Revenue (R$)')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.write("**Insight:** Tren penjualan menunjukkan pola peningkatan yang signifikan. "
             "Filter rentang tanggal untuk melihat tren pada periode spesifik.")

# ========= TAB 5: RFM ANALYSIS =========
with tab5:
    st.subheader("RFM Analysis (Recency, Frequency, Monetary)")
    
    st.write("""
    **RFM Analysis** bertujuan mengelompokkan pelanggan berdasarkan perilaku pembelian:
    - **Recency (R):** Jumlah hari sejak terakhir kali pelanggan melakukan pembelian
    - **Frequency (F):** Jumlah total transaksi yang dilakukan pelanggan
    - **Monetary (M):** Total pengeluaran pelanggan
    """)
    
    rfm_df = create_rfm_df(filtered_df)
    
    # RFM Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_recency = round(rfm_df['recency'].mean(), 1)
        st.metric("Rata-rata Recency (hari)", f"{avg_recency}")
    with col2:
        avg_freq = round(rfm_df['frequency'].mean(), 2)
        st.metric("Rata-rata Frequency", f"{avg_freq}")
    with col3:
        avg_monetary = round(rfm_df['monetary'].mean(), 2)
        st.metric("Rata-rata Monetary", f"R$ {avg_monetary:,.2f}")
    
    st.markdown("---")
    
    # Top customers per RFM dimension
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.write(f"#### Top {top_n} by Recency (Terbaru)")
        top_recency = rfm_df.sort_values('recency', ascending=True).head(top_n)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#2ca02c' if i == 0 else '#98df8a' for i in range(len(top_recency))]
        ax.barh(
            range(len(top_recency)),
            top_recency['recency'].values,
            color=colors
        )
        ax.set_yticks(range(len(top_recency)))
        ax.set_yticklabels([f"Cust {i+1}" for i in range(len(top_recency))], fontsize=9)
        ax.set_xlabel('Recency (hari)')
        ax.set_title(f'Top {top_n} Pelanggan Terbaru', fontsize=12)
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_b:
        st.write(f"#### Top {top_n} by Frequency")
        top_freq = rfm_df.sort_values('frequency', ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#1f77b4' if i == 0 else '#aec7e8' for i in range(len(top_freq))]
        ax.barh(
            range(len(top_freq)),
            top_freq['frequency'].values,
            color=colors
        )
        ax.set_yticks(range(len(top_freq)))
        ax.set_yticklabels([f"Cust {i+1}" for i in range(len(top_freq))], fontsize=9)
        ax.set_xlabel('Frequency (jumlah transaksi)')
        ax.set_title(f'Top {top_n} Pelanggan Paling Sering', fontsize=12)
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_c:
        st.write(f"#### Top {top_n} by Monetary")
        top_monetary = rfm_df.sort_values('monetary', ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#ff7f0e' if i == 0 else '#ffbb78' for i in range(len(top_monetary))]
        ax.barh(
            range(len(top_monetary)),
            top_monetary['monetary'].values,
            color=colors
        )
        ax.set_yticks(range(len(top_monetary)))
        ax.set_yticklabels([f"Cust {i+1}" for i in range(len(top_monetary))], fontsize=9)
        ax.set_xlabel('Monetary (R$)')
        ax.set_title(f'Top {top_n} Pelanggan Paling Bernilai', fontsize=12)
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    st.markdown("---")
    
    # RFM Segmentation
    st.write("#### Segmentasi RFM")
    st.write("Pelanggan dikelompokkan berdasarkan skor RFM (1-4) menggunakan metode quartile:")
    
    # Buat skor RFM berdasarkan quartile
    rfm_scored = rfm_df.copy()
    
    # Recency: semakin kecil semakin baik (skor tinggi)
    rfm_scored['R_score'] = pd.qcut(rfm_scored['recency'], q=4, labels=[4, 3, 2, 1], duplicates='drop')
    
    # Frequency: semakin besar semakin baik
    try:
        rfm_scored['F_score'] = pd.qcut(rfm_scored['frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4], duplicates='drop')
    except ValueError:
        rfm_scored['F_score'] = 1
    
    # Monetary: semakin besar semakin baik
    rfm_scored['M_score'] = pd.qcut(rfm_scored['monetary'], q=4, labels=[1, 2, 3, 4], duplicates='drop')
    
    # Buat segment berdasarkan kombinasi RFM score
    rfm_scored['R_score'] = rfm_scored['R_score'].astype(int)
    rfm_scored['F_score'] = rfm_scored['F_score'].astype(int)
    rfm_scored['M_score'] = rfm_scored['M_score'].astype(int)
    rfm_scored['RFM_score'] = rfm_scored['R_score'] + rfm_scored['F_score'] + rfm_scored['M_score']
    
    def rfm_segment(score):
        if score >= 9:
            return 'Best Customers'
        elif score >= 6:
            return 'Loyal Customers'
        elif score >= 4:
            return 'At Risk'
        else:
            return 'Lost Customers'
    
    rfm_scored['segment'] = rfm_scored['RFM_score'].apply(rfm_segment)
    
    segment_counts = rfm_scored['segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Jumlah Pelanggan']
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        fig, ax = plt.subplots(figsize=(8, 6))
        segment_colors = {
            'Best Customers': '#2ca02c',
            'Loyal Customers': '#1f77b4',
            'At Risk': '#ff7f0e',
            'Lost Customers': '#d62728'
        }
        colors = [segment_colors.get(s, '#888888') for s in segment_counts['Segment']]
        ax.pie(
            segment_counts['Jumlah Pelanggan'],
            labels=segment_counts['Segment'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        ax.set_title('Distribusi Segmen RFM', fontsize=14)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_right:
        st.dataframe(
            segment_counts.style.format({'Jumlah Pelanggan': '{:,}'}),
            use_container_width=True,
            hide_index=True
        )
        
        st.write("""
        **Penjelasan Segmen:**
        - 🟢 **Best Customers:** Skor RFM tertinggi (9-12), beli baru-baru ini, sering, dan bernilai tinggi
        - 🔵 **Loyal Customers:** Skor menengah-atas (6-8), pelanggan setia
        - 🟠 **At Risk:** Skor menengah-bawah (4-5), berisiko tidak kembali
        - 🔴 **Lost Customers:** Skor rendah (3), sudah lama tidak membeli
        """)

# ========= FOOTER =========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Dashboard dibuat oleh <b>Wardiansyah Fauzi Abdillah</b> | 
    Universitas Gunadarma | 
    Data: Brazilian E-Commerce Public Dataset by Olist</p>
</div>
""", unsafe_allow_html=True)
