# Brazilian E-Commerce Analysis Dashboard

## Table of Contents

1. [Introduction](#introduction)
2. [Dataset Overview](#dataset-overview)
3. [Project Objectives](#project-objectives)
4. [Business Questions](#business-questions)
5. [Dashboard Structure](#dashboard-structure)
6. [Installation and Usage](#installation-and-usage)
7. [Author](#author)

---

## Introduction

Dashboard analisis interaktif untuk E-Commerce Public Dataset dari Olist (Brasil). Dashboard ini dibuat menggunakan **Streamlit** dan menyediakan fitur filtering yang memungkinkan pengguna mengeksplorasi data secara dinamis.

---

## Dataset Overview

Dataset berisi sekitar 100.000 pesanan dari Olist (2016–2018) yang mencakup:
- Detail pelanggan dan penjual
- Informasi produk dan kategori
- Status pesanan dan metode pembayaran
- Data geografis

---

## Project Objectives

1. Mengidentifikasi kategori produk terlaris dan paling menguntungkan
2. Menganalisis kinerja penjualan berdasarkan kota/wilayah
3. Memahami tingkat keterlibatan pelanggan (aktif vs. tidak aktif)
4. Menganalisis tren penjualan dari waktu ke waktu
5. Menerapkan **RFM Analysis** untuk segmentasi pelanggan

---

## Business Questions

1. **Apa kategori produk dengan pesanan tertinggi dan paling menguntungkan?**
2. **Wilayah dan kota mana yang memiliki penjualan atau profit tertinggi?**
3. **Di mana wilayah atau kota dengan pelanggan paling aktif atau paling tidak aktif?**
4. **Bagaimana tren penjualan dari waktu ke waktu?**

---

## Dashboard Structure

### Fitur Interaktif (Sidebar)
- **Filter Rentang Tanggal:** Memilih periode tertentu untuk memfilter seluruh visualisasi
- **Filter Status Order:** Memilih status order (delivered, shipped, canceled, dll.)
- **Top-N Selector:** Menentukan jumlah item yang ditampilkan di chart (slider)

### Tab Visualisasi
1. **Kategori Produk** — Top-N kategori berdasarkan total orders dan revenue
2. **Penjualan per Wilayah** — Top-N kota berdasarkan orders/revenue + scatter plot
3. **Pelanggan Aktif/Tidak Aktif** — Distribusi pelanggan per kota
4. **Tren Penjualan** — Monthly & quarterly trends
5. **RFM Analysis** — Segmentasi pelanggan berdasarkan Recency, Frequency, Monetary

---

## Installation and Usage

### Prerequisites
- Python 3.10 atau lebih baru

### Langkah Instalasi

1. Clone repository ini:
   ```bash
   git clone https://github.com/WardiansyahF/e-commerce-dashboard.git
   ```

2. Masuk ke folder submission:
   ```bash
   cd e-commerce-dashboard/submission
   ```

3. (Opsional) Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Siapkan data (merge raw CSV menjadi main_data.csv):
   ```bash
   python prepare_data.py
   ```

6. Jalankan dashboard:
   ```bash
   streamlit run dashboard/dashboard.py
   ```

7. Buka dashboard di browser: `http://localhost:8501`

---

## Author

**Wardiansyah Fauzi Abdillah**

- Mahasiswa Informatika, Universitas Gunadarma
- Email: ardi.dl738@gmail.com
- [LinkedIn](https://linkedin.com/in/wardiansyah-fauzi-abdillah) | [GitHub](https://github.com/WardiansyahF)
