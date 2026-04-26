import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

KURS = 1 
 
def format_currency(val, decimals=0):
    if decimals == 0:
        return f"R$ {val:,.0f}".replace(",", ".")
    return f"R$ {val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    layout="wide"
)

sns.set_theme(style="whitegrid", palette="muted")

DATA_PATH = os.path.join(os.path.dirname(__file__), "main_data.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"])
    df["month"] = df["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    
    df["price"] = df["price"] * KURS
    
    return df

df = load_data()

revenue_by_cat = (
    df.groupby("product_category_name_english")["price"]
    .sum().sort_values(ascending=False).reset_index()
)
revenue_by_cat.columns = ["category", "total_revenue"]

customer_loyalty = (
    df.groupby("customer_unique_id")
    .agg(order_count=("order_id", "nunique"), total_spent=("price", "sum"))
    .reset_index()
)

st.sidebar.title("Filter")

min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

try:
    start_date, end_date = st.sidebar.date_input(
        "Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
except ValueError:
    st.error("Pilih rentang waktu (Mulai & Selesai)")
    st.stop()

main_df = df[(df["order_purchase_timestamp"].dt.date >= start_date) & 
             (df["order_purchase_timestamp"].dt.date <= end_date)]

top_n = st.sidebar.slider("Tampilkan Top N Kategori", min_value=5, max_value=20, value=10)

revenue_by_cat = (
    main_df.groupby("product_category_name_english")["price"]
    .sum().sort_values(ascending=False).reset_index()
)
revenue_by_cat.columns = ["category", "total_revenue"]

all_cats = revenue_by_cat["category"].tolist()
selected_cats = st.sidebar.multiselect(
    "Pilih kategori untuk analisis tren",
    options=all_cats[:20],
    default=all_cats[:3]
)

st.title("E-Commerce Public Dataset — Analisis Dashboard")
st.markdown(
    "**Nama:** Nisa Jamalia Hanif &nbsp;|&nbsp; "
    "**Email:** nisajamalia99@gmail.com &nbsp;|&nbsp; "
    "**ID Dicoding:** nisajamalia-9899"
)
st.markdown("---")

total_rev    = main_df["price"].sum()
total_orders = main_df["order_id"].nunique()
total_cust   = main_df["customer_unique_id"].nunique()
avg_order    = total_rev / total_orders if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", format_currency(total_rev))
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Unique Customers", f"{total_cust:,}")
col4.metric("Avg Order Value", format_currency(avg_order, 2))

st.markdown("---")

st.header("Pertanyaan 1: Kategori Produk dengan Revenue Tertinggi")

col_left, col_right = st.columns([3, 2])

with col_left:
    top_data = revenue_by_cat.head(top_n).sort_values("total_revenue")
    fig1, ax1 = plt.subplots(figsize=(14, max(4, top_n * 0.45)))
    palette = sns.color_palette("Blues_d", top_n)
    bars = ax1.barh(top_data["category"], top_data["total_revenue"], color=palette)
    for bar in bars:
        w = bar.get_width()
        ax1.text(w + total_rev * 0.003, bar.get_y() + bar.get_height() / 2,
                 format_currency(w), va="center", fontsize=8)
    ax1.set_title(f"Top {top_n} Kategori Produk — Revenue", fontweight="bold", fontsize=12)
    ax1.set_xlabel("Total Revenue (R$)")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_currency(x)))
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close()

with col_right:
    st.subheader("Tabel Revenue")
    show_df = revenue_by_cat.head(top_n).copy()
    show_df["total_revenue"] = show_df["total_revenue"].map(lambda x: format_currency(x, 2))
    show_df.columns = ["Kategori", "Total Revenue"]
    st.dataframe(show_df, use_container_width=True, hide_index=True)

st.subheader("Tren Revenue Bulanan")
if selected_cats:
    df_trend = main_df[main_df["product_category_name_english"].isin(selected_cats)]
    monthly = df_trend.groupby(["month", "product_category_name_english"])["price"].sum().reset_index()

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    for cat in selected_cats:
        d = monthly[monthly["product_category_name_english"] == cat]
        if not d.empty:
            ax2.plot(d["month"], d["price"], marker="o", markersize=4, label=cat)
    ax2.set_title("Tren Revenue Bulanan per Kategori", fontweight="bold")
    ax2.set_ylabel("Revenue (R$)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_currency(x)))
    ax2.legend(fontsize=8)
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()
else:
    st.info("Pilih minimal 1 kategori di sidebar untuk melihat tren.")

st.markdown("---")

st.header("Pertanyaan 2: Analisis Pertumbuhan Revenue")

main_df_comp = main_df.copy()
available_years = sorted(main_df_comp['order_purchase_timestamp'].dt.year.unique())
available_months = sorted(main_df_comp['order_purchase_timestamp'].dt.to_period('M').unique())

comp_mode = None
if len(available_years) >= 2:
    comp_mode = "Tahunan"
    p_start = available_years[0]
    p_end = available_years[-1]
    main_df_comp['period'] = main_df_comp['order_purchase_timestamp'].dt.year
elif len(available_months) >= 2:
    comp_mode = "Bulanan"
    p_start = available_months[0]
    p_end = available_months[-1]
    
    main_df_comp['period'] = main_df_comp['order_purchase_timestamp'].dt.to_period('M').astype(str)
    p_start = str(p_start)
    p_end = str(p_end)

if comp_mode:
    st.subheader(f"Perbandingan Pertumbuhan ({comp_mode}): {p_start} vs {p_end}")
    
    
    df_comp = main_df_comp[main_df_comp['period'].isin([p_start, p_end])]
    revenue_comparison = df_comp.groupby(['period', 'product_category_name_english'])['price'].sum().reset_index()

    
    pivot_revenue = revenue_comparison.pivot(index='product_category_name_english', columns='period', values='price').fillna(0)
    
    
    if p_start in pivot_revenue.columns and p_end in pivot_revenue.columns:
        pivot_revenue['revenue_growth'] = pivot_revenue[p_end] - pivot_revenue[p_start]
        pivot_revenue = pivot_revenue.sort_values(by='revenue_growth', ascending=False)

        total_s = pivot_revenue[p_start].sum()
        total_e = pivot_revenue[p_end].sum()

        fig_comp, ax_comp = plt.subplots(figsize=(10, 6))
        colors = ['#A3C1AD', '#4682B4']
        ax_comp.bar([str(p_start), str(p_end)], [total_s, total_e], color=colors)

        for i, v in enumerate([total_s, total_e]):
            ax_comp.text(i, v + (max(total_s, total_e) * 0.01), 
                           format_currency(v), ha='center', va='bottom', fontweight='bold')

        ax_comp.set_title(f'Total Revenue: {p_start} vs {p_end}', fontsize=14, pad=20)
        ax_comp.set_ylabel('Total Revenue (R$)', fontsize=12)
        ax_comp.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_currency(x)))
        st.pyplot(fig_comp)
        plt.close()

        st.subheader(f"Top 10 Kategori dengan Kenaikan Terbesar")
        top_growth = pivot_revenue.head(10)

        fig_growth, ax_growth = plt.subplots(figsize=(12, 8))
        sns.barplot(x=top_growth['revenue_growth'], y=top_growth.index, palette='viridis', ax=ax_growth)

        ax_growth.set_title(f'Kenaikan Revenue per Kategori ({p_start} ke {p_end})', fontsize=14)
        ax_growth.set_xlabel('Selisih Revenue (R$)', fontsize=12)
        ax_growth.set_ylabel('Kategori Produk', fontsize=12)
        ax_growth.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_currency(x)))

        for i, v in enumerate(top_growth['revenue_growth']):
            ax_growth.text(v + (top_growth['revenue_growth'].max() * 0.01), i, 
                           f"+{format_currency(v)}", va='center', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig_growth)
        plt.close()

        with st.expander("Lihat Detail Ringkasan"):
            summary_display = top_growth[[p_start, p_end, 'revenue_growth']].copy()
            summary_display[p_start] = summary_display[p_start].map(format_currency)
            summary_display[p_end] = summary_display[p_end].map(format_currency)
            summary_display['revenue_growth'] = summary_display['revenue_growth'].map(lambda x: f"+{format_currency(x)}")
            st.dataframe(summary_display, use_container_width=True, hide_index=True)
    else:
        st.warning("Data perbandingan tidak mencukupi untuk filter yang dipilih.")

else:
    st.subheader("Tren Performa Penjualan & Revenue Harian")
    main_df['day'] = main_df['order_purchase_timestamp'].dt.date
    daily_perf = main_df.groupby("day").agg(
        order_count=("order_id", "nunique"),
        revenue=("price", "sum")
    ).reset_index()

    fig_daily, ax_rev = plt.subplots(figsize=(12, 5))
    ax_order = ax_rev.twinx()

    ax_rev.plot(daily_perf["day"], daily_perf["revenue"], color="#3498db", label="Revenue", linewidth=2)
    ax_order.bar(daily_perf["day"], daily_perf["order_count"], color="#e67e22", alpha=0.3, label="Order Count")

    ax_rev.set_ylabel("Total Revenue (R$)", color="#3498db", fontweight="bold")
    ax_order.set_ylabel("Total Orders", color="#e67e22", fontweight="bold")
    ax_rev.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_currency(x)))

    plt.title("Performa Penjualan & Revenue Harian", fontweight="bold")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig_daily)
    plt.close()
    
    st.info("Pilih rentang waktu minimal 2 bulan untuk melihat analisis perbandingan pertumbuhan.")




st.markdown("---")
st.header("Analisis Tambahan: Loyalitas & RFM")

customer_loyalty = (
    main_df.groupby("customer_unique_id")
    .agg(order_count=("order_id", "nunique"), total_spent=("price", "sum"))
    .reset_index()
)

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Distribusi Frekuensi Order")
    freq_dist = customer_loyalty["order_count"].value_counts().sort_index().head(10)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.bar(freq_dist.index.astype(str), freq_dist.values,
            color=sns.color_palette("Greens_d", len(freq_dist)))
    ax3.set_xlabel("Jumlah Order")
    ax3.set_ylabel("Jumlah Pelanggan")
    ax3.set_title("Distribusi Frekuensi Order per Pelanggan", fontweight="bold", fontsize=11)
    for i, v in enumerate(freq_dist.values):
        ax3.text(i, v + freq_dist.max() * 0.01, f"{v:,}", ha="center", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

with col_b:
    st.subheader("Frekuensi vs Total Pengeluaran")
    multi = customer_loyalty[customer_loyalty["order_count"] > 1]
    if not multi.empty:
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        sc = ax4.scatter(multi["order_count"], multi["total_spent"],
                         alpha=0.55, c=multi["total_spent"], cmap="YlOrRd",
                         edgecolors="white", linewidth=0.3, s=55)
        plt.colorbar(sc, ax=ax4, label="Total Spent (R$)")
        ax4.set_xlabel("Jumlah Order")
        ax4.set_ylabel("Total Pengeluaran (R$)")
        ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_currency(x)))
        ax4.set_title("Loyalitas: Frekuensi vs Total Belanja", fontweight="bold", fontsize=11)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()
    else:
        st.info("Tidak ada data pelanggan dengan lebih dari 1 order pada filter ini.")

st.subheader("Top 10 Pelanggan Paling Loyal")
top_loyal = (
    customer_loyalty.sort_values(["order_count", "total_spent"], ascending=False)
    .head(10).reset_index(drop=True)
)
top_loyal["Rank"] = range(1, len(top_loyal) + 1)
top_loyal["customer_unique_id"] = top_loyal["customer_unique_id"].str[:16] + "..."
top_loyal["total_spent"] = top_loyal["total_spent"].map(lambda x: format_currency(x, 2))
top_loyal = top_loyal.rename(columns={
    "customer_unique_id": "Customer ID",
    "order_count": "Jumlah Order",
    "total_spent": "Total Belanja"
})[["Rank", "Customer ID", "Jumlah Order", "Total Belanja"]]
st.dataframe(top_loyal, use_container_width=True, hide_index=True)

@st.cache_data
def compute_rfm(_df):
    snapshot = _df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = (
        _df.groupby("customer_unique_id")
        .agg(
            recency=("order_purchase_timestamp", lambda x: (snapshot - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("price", "sum")
        )
        .reset_index()
    )
    rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[5,4,3,2,1])
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
    rfm["M"] = pd.qcut(rfm["monetary"], 5, labels=[1,2,3,4,5])
    rfm["RFM_Score"] = rfm["R"].astype(int) + rfm["F"].astype(int) + rfm["M"].astype(int)
    def seg(s):
        if s >= 13: return "Champions"
        elif s >= 10: return "Loyal Customers"
        elif s >= 7:  return "Potential Loyalists"
        elif s >= 4:  return "At Risk"
        else:         return "Lost"
    rfm["Segment"] = rfm["RFM_Score"].apply(seg)
    return rfm

st.subheader("Segmentasi Pelanggan (RFM)")
rfm = compute_rfm(main_df)
seg_counts = rfm["Segment"].value_counts()

col_pie, col_rfm_table = st.columns([2, 3])
with col_pie:
    colors = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#95a5a6"]
    fig5, ax5 = plt.subplots(figsize=(5, 5))
    ax5.pie(seg_counts, labels=seg_counts.index, autopct="%1.1f%%",
            colors=colors[:len(seg_counts)], startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=2))
    ax5.set_title("Proporsi Segmen Pelanggan", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close()

with col_rfm_table:
    st.subheader("Ringkasan per Segmen")
    seg_summary = (
        rfm.groupby("Segment")
        .agg(
            Jumlah_Pelanggan=("customer_unique_id", "count"),
            Avg_Recency=("recency", "mean"),
            Avg_Frequency=("frequency", "mean"),
            Avg_Monetary=("monetary", "mean")
        )
        .reset_index()
    )
    seg_summary["Avg_Recency"]   = seg_summary["Avg_Recency"].map("{:.0f} hari".format)
    seg_summary["Avg_Frequency"] = seg_summary["Avg_Frequency"].map("{:.1f}x".format)
    seg_summary["Avg_Monetary"]  = seg_summary["Avg_Monetary"].map(lambda x: format_currency(x, 2))
    st.dataframe(seg_summary, use_container_width=True, hide_index=True)

st.caption("Dashboard dibuat menggunakan Streamlit · E-Commerce Public Dataset (Olist)")
