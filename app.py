import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

st.title("Aplikasi Optimasi Produksi (Jumlah Material dan Waktu Terbatas)")

# Input jumlah produk
num_produk = st.number_input(
    "Masukkan jumlah produk (minimal 2)",
    min_value=2,
    max_value=10,
    value=2,
    step=1
)

# Input data produk
produk_names = []
keuntungan = []
waktu = []
bahan_baku = []

for i in range(int(num_produk)):
    produk_names.append(st.text_input(f"Nama Produk ke-{i+1}", value=f"Produk {chr(65+i)}"))
    keuntungan.append(st.number_input(f"Keuntungan per unit {produk_names[-1]}", min_value=0.0, value=5000.0))
    
    produksi_per_jam = st.number_input(
        f"Produksi per jam {produk_names[-1]}",
        min_value=0.1,
        value=360.0
    )
    waktu_per_unit = 1 / produksi_per_jam  # Konversi produksi per jam ke waktu per unit (jam/unit)
    waktu.append(waktu_per_unit)
    
    bahan_baku.append(st.number_input(f"Bahan baku per unit (matrial) {produk_names[-1]}", min_value=0.0, value=2.0))

# Input batasan sumber daya
st.header("Input Batasan Sumber Daya")
total_waktu = st.number_input("Total waktu tersedia (jam)", min_value=0.0, value=8.0)
total_bahan = st.number_input("Total bahan baku tersedia (matrial)", min_value=0.0, value=10000.0)

# Tombol untuk menghitung solusi optimal
if st.button("Hitung Solusi Optimal"):
    # Fungsi tujuan (maksimasi keuntungan) -> linprog minimisasi, jadi negatif
    c = [-k for k in keuntungan]
    
    # Matriks kendala (waktu dan bahan baku)
    A = [waktu, bahan_baku]
    b = [total_waktu, total_bahan]
    
    # Batasan variabel x >= 0
    bounds = [(0, None) for _ in range(int(num_produk))]
    
    # Hitung solusi optimal dengan metode Simplex (highs)
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    
    if res.success:
        st.subheader("Hasil Optimasi")
        for i in range(int(num_produk)):
            st.write(f"{produk_names[i]}: {res.x[i]:.2f} unit")
        st.write(f"Total keuntungan maksimal: Rp {(-res.fun):,.0f}")
        
        # Hitung dan tampilkan sisa bahan baku
        total_bahan_terpakai = sum(res.x[i] * bahan_baku[i] for i in range(int(num_produk)))
        sisa_bahan = total_bahan - total_bahan_terpakai
        st.write(f"Sisa bahan baku setelah produksi: {sisa_bahan:.2f} matrial")
        
        # Visualisasi area feasible dan solusi optimal jika produk = 2
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
            ax.fill_between(x1, 0, x2, where=(x2>0), color='magenta', alpha=0.5, label='Area Feasible')
            
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
