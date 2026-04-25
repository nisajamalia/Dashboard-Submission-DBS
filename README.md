# Dashboard DBS Analisis Data

## E-Commerce Public Dataset — Analisis Dashboard

**Nama:** Nisa Jamalia Hanif  
**Email:** 1995nisajamaila@gmail.com
**ID Dicoding:** CDCC005D6X2688

---

## Deskripsi Proyek

Project ini membahas analisis data dari Brazilian E-Commerce Public Dataset by Olist, yang berisi lebih dari 100.000 transaksi e-commerce pada periode 2016–2018.

Fokus analisis pada project ini ada dua pertanyaan utama, yaitu:

Kategori produk apa yang menghasilkan revenue paling tinggi
Siapa saja pelanggan paling loyal dilihat dari frekuensi pembelian dan total belanja

Selain itu, project ini juga dilengkapi dengan analisis RFM Segmentation (Recency, Frequency, Monetary) untuk mengelompokkan pelanggan berdasarkan perilaku mereka, sehingga bisa memberikan insight yang lebih dalam terkait karakteristik tiap segmen pelanggan.

---


```
submission
├── dashboard
│   ├── main_data.csv        
│   └── dashboard.py         
├── data
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── products_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── customers_dataset.csv
│   ├── sellers_dataset.csv
│   └── geolocation_dataset.csv
├── notebook.ipynb          
├── README.md
└── requirements.txt
```

---

## Setup Environment

### Menggunakan pip (Virtual Environment)

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

### Menggunakan Conda

```bash
conda create --name ecommerce-env python=3.11
conda activate ecommerce-env
pip install -r requirements.txt
```

---

## Menjalankan Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

Setelah perintah di atas dijalankan, dashboard akan otomatis terbuka di browser pada alamat:

```
http://localhost:8501
```

---

## Fitur Dashboard

- **KPI Cards** — Total Revenue, Total Orders, Unique Customers, Avg Order Value
- **Top N Kategori** — Bar chart horizontal revenue per kategori produk (filter 5–20)
- **Tren Revenue Bulanan** — Line chart multi-kategori dengan filter interaktif
- **Distribusi Loyalitas** — Histogram frekuensi order dan scatter plot frekuensi vs pengeluaran
- **Top 10 Pelanggan Loyal** — Tabel pelanggan berdasarkan frekuensi dan total belanja
- **RFM Segmentasi** — Pie chart dan tabel ringkasan 5 segmen pelanggan
