import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

KURS = 3000 

def format_idr(val, decimals=0):
    if decimals == 0:
        return f"Rp {val:,.0f}".replace(",", ".")
    return f"Rp {val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
top_n = st.sidebar.slider("Tampilkan Top N Kategori", min_value=5, max_value=20, value=10)

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
    "**ID Dicoding:** CDCC005D6X2688"
)
st.markdown("---")

total_rev    = df["price"].sum()
total_orders = df["order_id"].nunique()
total_cust   = df["customer_unique_id"].nunique()
avg_order    = total_rev / total_orders

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", format_idr(total_rev))
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Unique Customers", f"{total_cust:,}")
col4.metric("Avg Order Value", format_idr(avg_order, 2))

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
                 format_idr(w), va="center", fontsize=8)
    ax1.set_title(f"Top {top_n} Kategori Produk — Revenue", fontweight="bold", fontsize=12)
    ax1.set_xlabel("Total Revenue (Rp)")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_idr(x)))
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close()

with col_right:
    st.subheader("Tabel Revenue")
    show_df = revenue_by_cat.head(top_n).copy()
    show_df["total_revenue"] = show_df["total_revenue"].map(lambda x: format_idr(x, 2))
    show_df.columns = ["Kategori", "Total Revenue"]
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    st.subheader("Kontribusi Top 5")
    top5_share = revenue_by_cat.head(5)["total_revenue"].sum() / total_rev * 100
    st.metric("Top 5 kategori menyumbang", f"{top5_share:.1f}% dari total revenue")

st.subheader("Tren Revenue Bulanan")
if selected_cats:
    df_trend = df[df["product_category_name_english"].isin(selected_cats)]
    monthly = df_trend.groupby(["month", "product_category_name_english"])["price"].sum().reset_index()

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    for cat in selected_cats:
        d = monthly[monthly["product_category_name_english"] == cat]
        ax2.plot(d["month"], d["price"], marker="o", markersize=4, label=cat)
    ax2.set_title("Tren Revenue Bulanan per Kategori", fontweight="bold")
    ax2.set_ylabel("Revenue (Rp)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_idr(x)))
    ax2.legend(fontsize=8)
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()
else:
    st.info("Pilih minimal 1 kategori di sidebar untuk melihat tren.")

st.markdown("---")

st.header("Pertanyaan 2: Pelanggan Paling Loyal")

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
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    sc = ax4.scatter(multi["order_count"], multi["total_spent"],
                     alpha=0.55, c=multi["total_spent"], cmap="YlOrRd",
                     edgecolors="white", linewidth=0.3, s=55)
    plt.colorbar(sc, ax=ax4, label="Total Spent (Rp)")
    ax4.set_xlabel("Jumlah Order")
    ax4.set_ylabel("Total Pengeluaran (Rp)")
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_idr(x)))
    ax4.set_title("Loyalitas: Frekuensi vs Total Belanja", fontweight="bold", fontsize=11)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

st.subheader("Top 10 Pelanggan Paling Loyal")
top_loyal = (
    customer_loyalty.sort_values(["order_count", "total_spent"], ascending=False)
    .head(10).reset_index(drop=True)
)
top_loyal["Rank"] = range(1, 11)
top_loyal["customer_unique_id"] = top_loyal["customer_unique_id"].str[:16] + "..."
top_loyal["total_spent"] = top_loyal["total_spent"].map(lambda x: format_idr(x, 2))
top_loyal = top_loyal.rename(columns={
    "customer_unique_id": "Customer ID",
    "order_count": "Jumlah Order",
    "total_spent": "Total Belanja"
})[["Rank", "Customer ID", "Jumlah Order", "Total Belanja"]]
st.dataframe(top_loyal, use_container_width=True, hide_index=True)

st.markdown("---")
st.header("Analisis Lanjutan: RFM Segmentasi")

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

rfm = compute_rfm(df)
seg_counts = rfm["Segment"].value_counts()

col_pie, col_rfm_table = st.columns([2, 3])
with col_pie:
    colors = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c", "#95a5a6"]
    fig5, ax5 = plt.subplots(figsize=(5, 5))
    ax5.pie(seg_counts, labels=seg_counts.index, autopct="%1.1f%%",
            colors=colors[:len(seg_counts)], startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=2))
    ax5.set_title("Segmentasi Pelanggan (RFM)", fontweight="bold")
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
    seg_summary["Avg_Monetary"]  = seg_summary["Avg_Monetary"].map(lambda x: format_idr(x, 2))
    st.dataframe(seg_summary, use_container_width=True, hide_index=True)

st.markdown("---")
st.header("Kesimpulan")
st.markdown("""
**Pertanyaan 1 — Kategori produk dengan revenue tertinggi:**
> Dari hasil analisis, kategori **health_beauty** jadi yang paling tinggi revenue-nya, sekitar Rp3,7 Miliar.  
> Setelah itu disusul sama **watches_gifts** dan **bed_bath_table**.  
> Kalau dilihat, 5 kategori teratas ini nyumbang lebih dari 35% total revenue keseluruhan.  
> Selain itu, trennya juga kelihatan naik secara konsisten dari tahun 2017 sampai 2018.

**Pertanyaan 2 — Pelanggan paling loyal:**
> Dari data yang ada, sekitar **97% pelanggan cuma beli 1 kali aja**, jadi bisa dibilang tingkat loyalitasnya masih rendah.  
> Berdasarkan analisis RFM, mayoritas pelanggan masuk ke kategori *At Risk* atau *Lost*.  
> Artinya, banyak pelanggan yang berpotensi nggak balik lagi.  
> Jadi, penting banget buat bikin program loyalitas atau strategi re-engagement biar mereka tertarik buat belanja lagi.
""")

st.caption("Dashboard dibuat menggunakan Streamlit · E-Commerce Public Dataset (Olist)")
