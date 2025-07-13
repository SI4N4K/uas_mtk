import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

st.title("Aplikasi Optimasi Produksi (Linear Programming)")

# Input jumlah produk (minimal 2)
num_produk = st.number_input("Masukkan jumlah produk (minimal 2)", min_value=2, max_value=10, value=2, step=1)

# Membuat input dinamis untuk keuntungan/unit, waktu/unit, bahan baku/unit
st.header("Input Data Produk")
produk_names = []
keuntungan = []
waktu = []
bahan_baku = []

for i in range(int(num_produk)):
    produk_names.append(st.text_input(f"Nama Produk ke-{i+1}", value=f"Produk {chr(65+i)}"))
    keuntungan.append(st.number_input(f"Keuntungan per unit {produk_names[-1]}", min_value=0.0, value=5000.0))
    waktu.append(st.number_input(f"Waktu per unit (jam) {produk_names[-1]}", min_value=0.0, value=2.0))
    bahan_baku.append(st.number_input(f"Bahan baku per unit (kg) {produk_names[-1]}", min_value=0.0, value=3.0))

st.header("Input Batasan Sumber Daya")
total_waktu = st.number_input("Total waktu tersedia (jam)", min_value=0.0, value=60.0)
total_bahan = st.number_input("Total bahan baku tersedia (kg)", min_value=0.0, value=40.0)

if st.button("Hitung Solusi Optimal"):
    # Membuat fungsi tujuan (maksimasi keuntungan)
    c = [-k for k in keuntungan]  # linprog untuk minimisasi, jadi negatif

    # Membuat matriks kendala
    A = [
        waktu,
        bahan_baku
    ]
    b = [total_waktu, total_bahan]

    # Batasan variabel x >= 0
    bounds = [(0, None) for _ in range(int(num_produk))]

    # Hitung solusi dengan linprog
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

    if res.success:
        st.subheader("Hasil Optimasi")
        for i in range(int(num_produk)):
            st.write(f"{produk_names[i]}: {res.x[i]:.2f} unit")
        st.write(f"Total keuntungan maksimal: Rp {(-res.fun):,.0f}")

        # Visualisasi hanya jika produk = 2 (karena grafik 2D)
        if int(num_produk) == 2:
            st.subheader("Visualisasi Area Feasible dan Solusi Optimal")
            fig, ax = plt.subplots()

            x1 = np.linspace(0, max(b[0]/waktu[0], b[1]/bahan_baku[0], 20))
            x2_waktu = (total_waktu - waktu[0]*x1) / waktu[1]
            x2_bahan = (total_bahan - bahan_baku[0]*x1) / bahan_baku[1]

            ax.plot(x1, x2_waktu, label='Kendala Waktu')
            ax.plot(x1, x2_bahan, label='Kendala Bahan Baku')

            x2 = np.minimum(x2_waktu, x2_bahan)
            x2 = np.maximum(x2, 0)
            ax.fill_between(x1, 0, x2, where=(x2>0), color='lightgreen', alpha=0.5, label='Area Feasible')

            ax.plot(res.x[0], res.x[1], 'ro', label='Solusi Optimal')

            ax.set_xlabel(produk_names[0])
            ax.set_ylabel(produk_names[1])
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
            ax.legend()
            st.pyplot(fig)
        else:
            st.info("Visualisasi hanya tersedia untuk 2 produk.")
    else:
        st.error("Tidak ditemukan solusi optimal. Periksa kembali input Anda.")
