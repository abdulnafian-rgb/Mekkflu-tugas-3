import streamlit as st
import math

# Set judul halaman web
st.set_page_config(page_title="Kalkulator Pipa Bercabang", layout="centered")

st.title("🚰 Analisis Pipa Bercabang (3 Reservoir)")
# Watermark 1: Teks di bawah judul
st.caption("Thanks To: **Anwar N**")

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
                q2 = math.sqrt(hf2 / K2) if hf2 > 0 else 0
                q3 = math.sqrt(hf3 / K3) if hf3 > 0 else 0
                diff = q1 - (q2 + q3)
            else:
                hf1 = Z_A_rel - ht
                hf2 = Z_B_rel - ht
                hf3 = ht - Z_D_rel
                q1 = math.sqrt(hf1 / K1) if hf1 > 0 else 0
                q2 = math.sqrt(hf2 / K2) if hf2 > 0 else 0
                q3 = math.sqrt(hf3 / K3) if hf3 > 0 else 0
                diff = (q1 + q2) - q3
            return q1, q2, q3, diff, hf1, hf2, hf3

        # =====================================================================
        # PROSES GENERASI TRIAL SECARA REAL (SImulasi Langkah Manual)
        # =====================================================================
        HT_list = []
        dQ_list = []

        # Trial 1: Asumsi h_T = Z_B_rel
        ht_0 = Z_B_rel
        _, _, _, dq_0, _, _, _ = hitung_sistem(ht_0)
        HT_list.append(ht_0)
        dQ_list.append(dq_0)

        # Trial 2: Asumsi h_T = Rata-rata dari Z_A dan Z_B
        ht_1 = float(round((Z_A_rel + Z_B_rel) / 2.0))
        _, _, _, dq_1, _, _, _ = hitung_sistem(ht_1)
        HT_list.append(ht_1)
        dQ_list.append(dq_1)

        # Trial 3 dan seterusnya menggunakan interpolasi linier asli
        while abs(dQ_list[-1]) >= 0.0005 and len(HT_list) < 10:
            if (dQ_list[-2] - dQ_list[-1]) == 0:
                break
            next_ht = HT_list[-2] + (dQ_list[-2] / (dQ_list[-2] - dQ_list[-1])) * (HT_list[-1] - HT_list[-2])
            # Fail-safe batas elevasi
            next_ht = max(0.001, min(Z_A_rel - 0.001, next_ht))
            _, _, _, next_dq, _, _, _ = hitung_sistem(next_ht)
            HT_list.append(next_ht)
            dQ_list.append(next_dq)

        # =====================================================================
        # TAMPILAN JABARAN PROSES MANUAl (MARKDOWN & LATEX)
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
        * **Parameter Lain:** $f = {f_val:.3f}$ ; $g = {g}\\text{{ m/s}}^2$ ; $\\pi^2 = {pi_sq}$
        """)

        st.markdown(f"""
        **Langkah 2: Menghitung Hambatan Pipa ($K$)**
        * $K_1 = \\frac{{8 \\cdot f \\cdot L_1}}{{g \\cdot \\pi^2 \\cdot D_1^5}} = \\frac{{8 \\cdot {f_val:.4f} \\cdot {L1}}}{{{g} \\cdot {pi_sq} \\cdot {D1:.2f}^5}} = {K1:.4f}$
        * $K_2 = \\frac{{8 \\cdot f \\cdot L_2}}{{g \\cdot \\pi^2 \\cdot D_2^5}} = \\frac{{8 \\cdot {f_val:.4f} \\cdot {L2}}}{{{g} \\cdot {pi_sq} \\cdot {D2:.2f}^5}} = {K2:.4f}$
        * $K_3 = \\frac{{8 \\cdot f \\cdot L_3}}{{g \\cdot \\pi^2 \\cdot D_3^5}} = \\frac{{8 \\cdot {f_val:.4f} \\cdot {L3}}}{{{g} \\cdot {pi_sq} \\cdot {D3:.2f}^5}} = {K3:.4f}$
        """)

        st.markdown(f"""
        **Langkah 3: Elevasi Relatif (Referensi $Z_D = 0$)**
        * $Z_A\\text{{ (relatif)}} = {Z_A_rel:.4f}\\text{{ m}}$
        * $Z_B\\text{{ (relatif)}} = {Z_B_rel:.4f}\\text{{ m}}$
        * $Z_D\\text{{ (relatif)}} = 0.0000\\text{{ m}}$
        """)

        st.divider()
        st.markdown(f"### **Langkah 4: Proses Iterasi (*Trial & Error*)**")

        # LOOPING UNTUK MENAMPILKAN SEMUA TRIAL SECARA DETAIL SEPERTI PDF
        for i in range(len(HT_list)):
            idx = i + 1
            ht_val = HT_list[i]
            q1, q2, q3, dq, hf1, hf2, hf3 = hitung_sistem(ht_val)
            flow_case_trial = 1 if ht_val > Z_B_rel else 2

            st.markdown(f"### **Trial {idx}**")
            
            # Tampilkan Tabel Pembantu Interpolasi jika sudah masuk Trial 3 dst.
            if idx == 1:
                st.info(f"**Asumsi 1:** Tinggi tekan di titik T ($h_T$) diasumsikan sejajar dengan elevasi relatif kolam B.")
            elif idx == 2:
                st.info(f"**Asumsi 2:** Tinggi tekan di titik T ($h_T$) diambil dari nilai tengah rata-rata antara kolam A dan B.")
            else:
                st.markdown("**Rumus Interpolasi Linear:**")
                xy_table = {
                    "X ($h_T$)": [f"{HT_list[i-2]:.4f}", f"{HT_list[i-1]:.4f}", f"{ht_val:.4f}"],
                    "Y ($\\Delta Q$)": [f"{dQ_list[i-2]:.4f}", f"{dQ_list[i-1]:.4f}", "0.0000"]
                }
                st.table(xy_table)

            # Bagian Cek Trial
            st.markdown(f"#### **Cek Trial {idx}**")
            if flow_case_trial == 1:
                st.write(f"Asumsi tinggi tekan $h_T = {ht_val:.4f}\\text{{ m}}$ berada di atas kolam B ($h_T > Z_B$).")
            else:
                st.write(f"Asumsi tinggi tekan $h_T = {ht_val:.4f}\\text{{ m}}$ berada di bawah kolam B ($h_T < Z_B$).")

            st.markdown(r"**1. Menghitung Kehilangan Energi ($h_f$):**")
            if flow_case_trial == 1:
                st.markdown(f"""
                * $hf_1 = Z_A - h_T = {Z_A_rel:.4f} - {ht_val:.4f} = {hf1:.4f}\\text{{ m}}$
                * $hf_2 = h_T - Z_B = {ht_val:.4f} - {Z_B_rel:.4f} = {hf2:.4f}\\text{{ m}}$
                * $hf_3 = h_T - Z_D = {ht_val:.4f} - 0.0000 = {hf3:.4f}\\text{{ m}}$
                """)
            else:
                st.markdown(f"""
                * $hf_1 = Z_A - h_T = {Z_A_rel:.4f} - {ht_val:.4f} = {hf1:.4f}\\text{{ m}}$
                * $hf_2 = Z_B - h_T = {Z_B_rel:.4f} - {ht_val:.4f} = {hf2:.4f}\\text{{ m}}$
                * $hf_3 = h_T - Z_D = {ht_val:.4f} - 0.0000 = {hf3:.4f}\\text{{ m}}$
                """)

            st.markdown(r"**2. Substitusi Rumus dan Menghitung Debit ($Q$):**")
            st.markdown(r"$$h_f = \frac{8 \cdot f \cdot L \cdot Q^2}{g \cdot \pi^2 \cdot D^5}$$")
            
            # Tampilan Detail Rumus Pecahan untuk Pipa 1
            num1 = 8 * f_val * L1
            den1 = g * pi_sq * (D1**5)
            st.markdown(f"""
            * **Pipa 1:**
              $$\\frac{{8 \\cdot {f_val:.4f} \\cdot {L1} \\cdot Q_1^2}}{{{g} \\cdot {pi_sq} \\cdot {D1:.2f}^5}} = {hf1:.4f}$$
              $$\\frac{{{num1:.4f}}}{{{den1:.4f}}} \\cdot Q_1^2 = {hf1:.4f}$$
              $${K1:.4f} \\cdot Q_1^2 = {hf1:.4f} \\implies Q_1^2 = {hf1/K1:.4f}$$
              $$Q_1 = \\sqrt{{{hf1/K1:.4f}}} = \\mathbf{{{q1:.4f}\\text{{ m}}^3\\text{{/s}}}}$$
            """)

            # Tampilan Detail Rumus Pecahan untuk Pipa 2
            num2 = 8 * f_val * L2
            den2 = g * pi_sq * (D2**5)
            st.markdown(f"""
            * **Pipa 2:**
              $$\\frac{{8 \\cdot {f_val:.4f} \\cdot {L2} \\cdot Q_2^2}}{{{g} \\cdot {pi_sq} \\cdot {D2:.2f}^5}} = {hf2:.4f}$$
              $$\\frac{{{num2:.4f}}}{{{den2:.4f}}} \\cdot Q_2^2 = {hf2:.4f}$$
              $${K2:.4f} \\cdot Q_2^2 = {hf2:.4f} \\implies Q_2^2 = {hf2/K2 if K2 > 0 else 0:.4f}$$
              $$Q_2 = \\sqrt{{{hf2/K2 if K2 > 0 else 0:.4f}}} = \\mathbf{{{q2:.4f}\\text{{ m}}^3\\text{{/s}}}}$$
            """)

            # Tampilan Detail Rumus Pecahan untuk Pipa 3
            num3 = 8 * f_val * L3
            den3 = g * pi_sq * (D3**5)
            st.markdown(f"""
            * **Pipa 3:**
              $$\\frac{{8 \\cdot {f_val:.4f} \\cdot {L3} \\cdot Q_3^2}}{{{g} \\cdot {pi_sq} \\cdot {D3:.2f}^5}} = {hf3:.4f}$$
              $$\\frac{{{num3:.4f}}}{{{den3:.4f}}} \\cdot Q_3^2 = {hf3:.4f}$$
              $${K3:.4f} \\cdot Q_3^2 = {hf3:.4f} \\implies Q_3^2 = {hf3/K3:.4f}$$
              $$Q_3 = \\sqrt{{{hf3/K3:.4f}}} = \\mathbf{{{q3:.4f}\\text{{ m}}^3\\text{{/s}}}}$$
            """)

            st.markdown(r"**3. Cek Persamaan Kontinuitas:**")
            if flow_case_trial == 1:
                q_masuk = q1
                q_keluar = q2 + q3
                st.markdown(f"""
                * $Q_{{MASUK}} = Q_1 = \\mathbf{{{q_masuk:.4f}}}$
                * $Q_{{KELUAR}} = Q_2 + Q_3 = {q2:.4f} + {q3:.4f} = \\mathbf{{{q_keluar:.4f}}}$
                * $\\Delta Q = Q_{{MASUK}} - Q_{{KELUAR}} = {q_masuk:.4f} - {q_keluar:.4f} = \\mathbf{{{dq:+.4f}}}$
                """)
            else:
                q_masuk = q1 + q2
                q_keluar = q3
                st.markdown(f"""
                * $Q_{{MASUK}} = Q_1 + Q_2 = {q1:.4f} + {q2:.4f} = \\mathbf{{{q_masuk:.4f}}}$
                * $Q_{{KELUAR}} = Q_3 = \\mathbf{{{q_keluar:.4f}}}$
                * $\\Delta Q = Q_{{MASUK}} - Q_{{KELUAR}} = {q_masuk:.4f} - {q_keluar:.4f} = \\mathbf{{{dq:+.4f}}}$
                """)

            # Tanda status keseimbangan tingkat presisi
            if abs(dq) <= 0.0005:
                st.success(f"✅ **SEIMBANG! Selisih $\\Delta Q$ sangat kecil ({dq:.4f} $\\approx$ 0). Iterasi dihentikan.**")
            else:
                st.error(f"❌ **Belum Seimbang (Selisih: {dq:+.4f} $\\neq$ 0). Lanjut ke tebakan berikutnya.**")
            
            st.divider()

        # =====================================================================
        # HASIL AKHIR KESIMPULAN
        # =====================================================================
        H_T_sol = HT_list[-1]
        Q1_fin, Q2_fin, Q3_fin, _, _, _, _ = hitung_sistem(H_T_sol)
        arah_Q2 = "dari Titik T -> ke Reservoir B" if H_T_sol > Z_B_rel else "dari Reservoir B -> ke Titik T"
        
        st.success(f"""
        **🎯 HASIL AKHIR KESIMPULAN:**
        1. **Tinggi Energi Absolut Titik T ($H_T$):** ${H_T_sol + Z_D:.4f}\\text{{ m}}$
        2. **Debit Pipa 1 ($Q_1$):** ${Q1_fin:.4f}\\text{{ m}}^3/s$ (Reservoir A $\\rightarrow$ Titik T)
        3. **Debit Pipa 2 ($Q_2$):** ${Q2_fin:.4f}\\text{{ m}}^3/s$ (Mengalir {arah_Q2})
        4. **Debit Pipa 3 ($Q_3$):** ${Q3_fin:.4f}\\text{{ m}}^3/s$ (Titik T $\\rightarrow$ Reservoir D)
        """)

# Watermark 2: Melayang secara permanen di sudut kanan bawah layar
st.markdown(
    """
    <style>
    .floating-watermark {
        position: fixed;
        bottom: 15px;
        right: 15px;
        opacity: 0.5;
        font-size: 13px;
        color: #888888;
        z-index: 9999;
        font-weight: bold;
        background-color: rgba(0,0,0,0.1);
        padding: 4px 8px;
        border-radius: 4px;
    }
    </style>
    <div class="floating-watermark">© Anwar N</div>
    """,
    unsafe_allow_html=True
)
