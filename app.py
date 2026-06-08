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
        # UPDATE: PROSES LOGIKA INTERPOLASI SESUAI INSTRUKSI BARU
        # =====================================================================
        HT_list = []
        dQ_list = []

        # Asumsi 1: HT = ZB
        ht_0 = Z_B_rel
        _, _, _, dq_0 = hitung_sistem(ht_0)
        HT_list.append(ht_0)
        dQ_list.append(dq_0)

        # Asumsi 2: HT = Rata-rata dari ZA dan ZB dibulatkan (misal: 10.1 + 38.2 = 24)
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

        # Hasil Konvergen
        H_T_sol = HT_list[-1]
        Q1_fin, Q2_fin, Q3_fin, dQ_fin = hitung_sistem(H_T_sol)
        flow_case = 1 if H_T_sol > Z_B_rel else 2

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

        # =====================================================================
        # LANGKAH 4 BARU: FORMAT PDF
        # =====================================================================
        st.markdown(f"**Langkah 4: Proses Iterasi Interpolasi Linear**")
        st.markdown(f"**Trial {len(HT_list)} Interpolasi**")
        st.write("Rumus interpolasi Linear")
        
        # Tabel X Y persis seperti di PDF
        xy_table = {
            "X": [f"{x:.4f}" for x in HT_list],
            "Y": [f"{y:.4f}" for y in dQ_list]
        }
        st.table(xy_table)

        st.markdown(f"**Cek Trial {len(HT_list)}**")
        if flow_case == 1:
            st.write("Asumsi tinggi tekan di titik T ($h_T$) lebih tinggi dari asumsi Trial 1 namun masih di bawah kolam A.")
            hf1 = Z_A_rel - H_T_sol
            hf2 = H_T_sol - Z_B_rel
            hf3 = H_T_sol - Z_D_rel
        else:
            st.write("Asumsi tinggi tekan di titik T ($h_T$) lebih rendah dari asumsi Trial 1 namun di atas kolam D.")
            hf1 = Z_A_rel - H_T_sol
            hf2 = Z_B_rel - H_T_sol
            hf3 = H_T_sol - Z_D_rel

        st.markdown(f"""
        $h_T$ = **{H_T_sol:.4f} m**
        
        * $hf_1 = Z_A - h_T = {Z_A_rel:.4f} - {H_T_sol:.4f} = {hf1:.4f}\\text{{ m}}$
        * $hf_2 = |h_T - Z_B| = |{H_T_sol:.4f} - {Z_B_rel:.4f}| = {hf2:.4f}\\text{{ m}}$
        * $hf_3 = h_T - Z_D = {H_T_sol:.4f} - 0.0000 = {hf3:.4f}\\text{{ m}}$
        """)

        st.markdown("**Sehingga debit masing-masing pipa:**")
        st.markdown(r"$h_f = f \frac{L}{D} \frac{V^2}{2g} = \frac{8 f L Q^2}{g \pi^2 D^5} = K \cdot Q^2$")
        
        st.markdown(f"""
        * **Pipa 1:**
          $hf_1 = K_1 \\cdot Q_1^2 \\implies {hf1:.4f} = {K1:.4f} \\cdot Q_1^2$
          $Q_1^2 = {hf1/K1:.4f} \\implies Q_1 = \\mathbf{{{Q1_fin:.4f}\\text{{ m}}^3\\text{{/s}}}}$
          
        * **Pipa 2:**
          $hf_2 = K_2 \\cdot Q_2^2 \\implies {hf2:.4f} = {K2:.4f} \\cdot Q_2^2$
          $Q_2^2 = {hf2/K2:.4f} \\implies Q_2 = \\mathbf{{{Q2_fin:.4f}\\text{{ m}}^3\\text{{/s}}}}$
          
        * **Pipa 3:**
          $hf_3 = K_3 \\cdot Q_3^2 \\implies {hf3:.4f} = {K3:.4f} \\cdot Q_3^2$
          $Q_3^2 = {hf3/K3:.4f} \\implies Q_3 = \\mathbf{{{Q3_fin:.4f}\\text{{ m}}^3\\text{{/s}}}}$
        """)

        st.markdown("**Cek persamaan kontinuitas**")
        if flow_case == 1:
            q_masuk = Q1_fin
            q_keluar = Q2_fin + Q3_fin
            st.markdown(f"""
            * $Q_{{MASUK}} = Q_1 = \\mathbf{{{q_masuk:.4f}}}$
            * $Q_{{KELUAR}} = Q_2 + Q_3 = {Q2_fin:.4f} + {Q3_fin:.4f} = \\mathbf{{{q_keluar:.4f}}}$
            * $\\Delta Q = Q_{{MASUK}} - Q_{{KELUAR}} = {q_masuk:.4f} - {q_keluar:.4f} = \\mathbf{{{dQ_fin:.4f}}}$
            """)
        else:
            q_masuk = Q1_fin + Q2_fin
            q_keluar = Q3_fin
            st.markdown(f"""
            * $Q_{{MASUK}} = Q_1 + Q_2 = {Q1_fin:.4f} + {Q2_fin:.4f} = \\mathbf{{{q_masuk:.4f}}}$
            * $Q_{{KELUAR}} = Q_3 = \\mathbf{{{q_keluar:.4f}}}$
            * $\\Delta Q = Q_{{MASUK}} - Q_{{KELUAR}} = {q_masuk:.4f} - {q_keluar:.4f} = \\mathbf{{{dQ_fin:.4f}}}$
            """)

        arah_Q2 = "dari Titik T -> ke Reservoir B" if H_T_sol > Z_B_rel else "dari Reservoir B -> ke Titik T"
        st.success(f"""
        **🎯 HASIL AKHIR KESIMPULAN:**
        1. **Tinggi Energi Absolut Titik T ($H_T$):** ${H_T_sol + Z_D:.4f}\\text{{ m}}$
        2. **Debit Pipa 1 ($Q_1$):** ${Q1_fin:.4f}\\text{{ m}}^3/s$ (Reservoir A $\\rightarrow$ Titik T)
        3. **Debit Pipa 2 ($Q_2$):** ${Q2_fin:.4f}\\text{{ m}}^3/s$ (Mengalir {arah_Q2})
        4. **Debit Pipa 3 ($Q_3$):** ${Q3_fin:.4f}\\text{{ m}}^3/s$ (Titik T $\\rightarrow$ Reservoir D)
        """)
