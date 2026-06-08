import streamlit as st
import math

# Set judul halaman web
st.set_page_config(page_title="Kalkulator Pipa Bercabang", layout="centered")

st.title("🚰 Analisis Pipa Bercabang (3 Reservoir)")
st.write("Masukkan 3 digit NIM terakhir Anda untuk melihat langkah pengerjaan lengkap.")

# 1. INPUT DARI USER VIA WEB INTERFACE
xyz_str = st.text_input("Masukkan 3 Digit NIM Terakhir (XYZ):", value="089", max_chars=3)

if st.button("Hitung Sekarang"):
    if len(xyz_str) != 3 or not xyz_str.isdigit():
        st.error("Error: Input harus berupa 3 digit angka!")
    else:
        X = int(xyz_str[0])
        Y = int(xyz_str[1])
        Z = int(xyz_str[2])

        a = X + Y
        b = Y + Z

        # 2. PROSES KONVERSI PARAMETER FISIK
        Z_A = float(f"21{Z}.{X}{Y}")
        Z_B = float(f"19{X}.{Z}{Y}")
        Z_D = float(f"18{X}.{Y}{Y}")

        L1 = int(f"1{Y}{X}{Z}")
        L2 = int(f"1{Z}{Y}{X}")
        L3 = int(f"9{X}{Y}")

        D1_cm = 50 + a
        D2_cm = 40 + b
        D3_cm = 30 + b

        D1 = D1_cm / 100.0
        D2 = D2_cm / 100.0
        D3 = D3_cm / 100.0

        f_val = 0.02 + (a / 1000.0)
        g = 9.81
        pi_sq = 9.8696  # Nilai pi^2 sesuai standar pembulatan manual PDF

        # 3. MENGHITUNG HAMBATAN PIPA (K) & ELEVASI RELATIF
        K1 = (8 * f_val * L1) / (g * pi_sq * (D1**5))
        K2 = (8 * f_val * L2) / (g * pi_sq * (D2**5))
        K3 = (8 * f_val * L3) / (g * pi_sq * (D3**5))

        Z_A_rel = Z_A - Z_D
        Z_B_rel = Z_B - Z_D
        Z_D_rel = 0.0

        # Engine Hitung Sistem
        def hitung_sistem(ht):
            if ht > Z_B_rel:
                hf1 = Z_A_rel - ht
                hf2 = ht - Z_B_rel
                hf3 = ht - Z_D_rel
                q1 = math.sqrt(hf1 / K1) if hf1 > 0 else 0
                q2 = math.sqrt(hf2 / K2) if hf2 >
