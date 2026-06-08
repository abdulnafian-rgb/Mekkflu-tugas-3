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

        # 3. MENGHITUNG HAMBATAN PIPA (K) & ELEVASI RELATIF
        K1 = (8 * f_val * L1) / (math.pi**2 * g * (D1**5))
        K2 = (8 * f_val * L2) / (math.pi**2 * g * (D2**5))
        K3 = (8 * f_val * L3) / (math.pi**2 * g * (D3**5))

        Z_A_rel = Z_A - Z_D
        Z_B_rel = Z_B - Z_D
        Z_D_rel = 0.0

        # 4. ENGINE SOLVER
        def hitung_sistem(ht):
            # Pengkondisian arah aliran untuk menghindari error akar negatif
            if ht > Z_B_rel:
                q1 = math.sqrt((Z_A_rel - ht) / K1) if Z_A_rel > ht else 0
                q2 = math.sqrt((ht - Z_B_rel) / K2) if ht > Z_B_rel else 0
                q3 = math.sqrt((ht - Z_D_rel) / K3) if ht > Z_D_rel else 0
                diff = q1 - (q2 + q3)
            else:
                q1 = math.sqrt((Z_A_rel - ht) / K1) if Z_A_rel > ht else 0
                q2 = math.sqrt((Z_B_rel - ht) / K2) if Z_B_rel > ht else 0
                q3 = math.sqrt((ht - Z_D_rel) / K3) if ht > Z_D_rel else 0
                diff = (q1 + q2) - q3
            return q1, q2, q3, diff

        # =====================================================================
        # PROSES LOGIKA INTERPOLASI SESUAI INSTRUKSI BARU
        # =====================================================================
        HT_list = []
        dQ_list = []

        # Asumsi 1: HT = ZB
        ht_0 = Z_B_rel
        _, _, _, dq_0 = hitung_sistem(ht_0)
        HT_list.append(ht_0)
        dQ_list.append(dq_0)

        # Asumsi 2: HT = Rata-rata dari ZA dan ZB dibulatkan
        ht_1 = float(round((Z_A_rel + Z_B_rel) / 2.0))
        _, _, _, dq_1 = hitung_sistem(ht_1)
        HT_list.append(ht_1)
        dQ_list.append(dq_1)

        # Asumsi 3 dst: Menggunakan Interpolasi Linier hingga presisi 0.0000
        while abs(dQ_list[-1]) >= 0.00005:
            # Pencegah pembagian dengan nol (zero division protection)
            if (dQ_list[-2] - dQ_list[-1]) == 0:
                break
            
            # Rumus Interpolasi Segitiga / Linear
            next_ht = HT_list[-2] + (dQ_list[-2] / (dQ_list[-2] - dQ_list[-1])) * (HT_list[-1] - HT_list[-2])
            _, _, _, next_dq = hitung_sistem(next_ht)
            
            HT_list.append(next_ht)
            dQ_list.append(next_dq)
            
            # Fail-safe batas iterasi (mencegah loop tak terhingga)
            if len(HT_list) > 20: 
                break

        H_T_sol = HT_list[-1]
        Q1_fin, Q2_fin, Q3_fin, _ = hitung_sistem(H_T_sol)

        # =====================================================================
        # 5. TAMPILAN OUTPUT WEB (MENGGUNAKAN MARKDOWN)
        # =====================================================================
        st.divider()
        st.subheader(f"📑 Langkah Pengerjaan Manual (NIM: {xyz_str})")
        
        st.markdown(f"""
        **Langkah 1: Menerjemahkan Variabel Soal**
        * **Elevasi Reservoir:**
          * $Z_A = +21Z,XY = {Z_A:.4f}\\text{{ m}}$
          * $Z_B = +19X,ZY = {Z_B:.4f}\\text{{ m}}$
          * $Z_D = +18X,YY = {Z_D:.4f}\\text{{ m}}$
        * **Dimensi Pipa:**
          * **Pipa 1:** $L_1 = {L1}\\text{{ m}}$ ; $D_1 = {D1_cm}\\text{{ cm}} = {D1:.2f}\\text{{ m}}$
          * **Pipa 2:** $L_2 = {L2}\\text{{ m}}$ ; $D_2 = {D2_cm}\\text{{ cm}} = {D2:.2f}\\text{{ m}}$
          * **Pipa 3:** $L_3 = {L3}\\text{{ m}}$ ; $D_3 = {D3_cm}\\text{{ cm}} = {D3:.2f}\\text{{ m}}$
        * **Parameter Lain:** $f = {f_val:.3f}$ ; $g = {g}\\text{{ m/s}}^2$
        """)

        st.markdown(f"""
        **Langkah 2: Menghitung Hambatan Pipa ($K$)**
        * $K_1 = {K1:.4f}$
        * $K_2 = {K2:.4f}$
        * $K_3 = {K3:.4f}$
        """)

        st.markdown(f"""
        **Langkah 3: Elevasi Relatif (Referensi $Z_D = 0$)**
        * $Z_A\\text{{ (relatif)}} = {Z_A_rel:.4f}\\text{{ m}}$
        * $Z_B\\text{{ (relatif)}} = {Z_B_rel:.4f}\\text{{ m}}$
        * $Z_D\\text{{ (relatif)}} = 0.0000\\text{{ m}}$
        """)

        st.divider()
        st.markdown(f"### **Langkah 4: Proses Iterasi (*Trial & Error*)**")

        # =====================================================================
        # LOOPING UNTUK MENAMPILKAN SEMUA TRIAL SECARA DETAIL
        # =====================================================================
        for i in range(len(HT_list)):
            idx = i + 1
            ht_val = HT_list[i]
            q1, q2, q3, dq = hitung_sistem(ht_val)
            flow_case_trial = 1 if ht_val > Z_B_rel else 2

            st.markdown(f"#### **Trial {idx}**")
            
            # Header Keterangan Interpolasi / Asumsi
            if idx == 1:
                st.info(f"**Asumsi 1:** Tinggi tekan di titik T ($h_T$) sama dengan elevasi kolam B.")
            elif idx == 2:
                st.info(f"**Asumsi 2:** Rata-rata dari $Z_A$ dan $Z_B$ (dibulatkan).")
            else:
                st.info(f"**Trial {idx} Interpolasi**")
                st.write("Rumus interpolasi Linear:")
                # Tabel Interpolasi dari 2 tebakan sebelumnya
                xy_table = {
                    "X": [f"{HT_list[i-2]:.4f}", f"{HT_list[i-1]:.4f}", f"{ht_val:.4f}"],
                    "Y": [f"{dQ_list[i-2]:.4f}", f"{dQ_list[i-1]:.4f}", f"{dq:.4f}"]
                }
                st.table(xy_table)

            # Cek Trial X (Format Persis PDF)
            st.markdown(f"**Cek Trial {idx}**")
            if flow_case_trial == 1:
                if ht_val == Z_B_rel:
                    st.write("Asumsi tinggi tekan di titik T ($h_T$) sejajar dengan elevasi kolam B.")
                else:
                    st.write("Asumsi tinggi tekan di titik T ($h_T$) lebih tinggi dari kolam B namun masih di bawah kolam A.")
                hf1 = Z_A_rel - ht_val
                hf2 = ht_val - Z_B_rel
                hf3 = ht_val - Z_D_rel
            else:
                st.write("Asumsi tinggi tekan di titik T ($h_T$) lebih rendah dari kolam B namun di atas kolam D.")
                hf1 = Z_A
