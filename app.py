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
                q2 = math.sqrt((ht - Z_B_rel) / K2)
                q3 = math.sqrt((ht - Z_D_rel) / K3) if ht > Z_D_rel else 0
                diff = q1 - (q2 + q3)
            else:
                q1 = math.sqrt((Z_A_rel - ht) / K1) if Z_A_rel > ht else 0
                q2 = math.sqrt((Z_B_rel - ht) / K2)
                q3 = math.sqrt((ht - Z_D_rel) / K3) if ht > Z_D_rel else 0
                diff = (q1 + q2) - q3
            return q1, q2, q3, diff

        Q1_test = math.sqrt((Z_A_rel - Z_B_rel) / K1)
        Q3_test = math.sqrt((Z_B_rel - Z_D_rel) / K3)
        flow_case = 1 if Q1_test > Q3_test else 2

        low, high = 0.0, Z_A_rel
        for _ in range(100):
            mid = (low + high) / 2.0
            _, _, _, F = hitung_sistem(mid)
            if abs(F) < 1e-7:
                break
            if F > 0:
                low = mid
            else:
                high = mid
        H_T_sol = (low + high) / 2.0
        Q1_fin, Q2_fin, Q3_fin, _ = hitung_sistem(H_T_sol)

        base = round(H_T_sol)
        trial_points = sorted(list(set([max(0.0, min(Z_A_rel, float(base-2))), max(0.0, min(Z_A_rel, float(base-1))), max(0.0, min(Z_A_rel, float(base+1)))])))

        # =====================================================================
        # 5. TAMPILAN OUTPUT WEB YANG RAPI (MENGGUNAKAN MARKDOWN)
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

        st.markdown(f"**Langkah 4: Uji Kondisi Batas (Arah Aliran)**")
        st.write(f"Andaikan $H_T = Z_B\\text{{ relatif}} = {Z_B_rel:.4f}\\text{{ m}}$, didapatkan $Q_1 = {Q1_test:.4f}\\text{{ m}}^3/s$ dan $Q_3 = {Q3_test:.4f}\\text{{ m}}^3/s$.")
        if flow_case == 1:
            st.info(f"Karena $Q_1 > Q_3$, air masuk berlebih. Sisa air dialirkan KELUAR ke Reservoir B ($H_T > Z_B$). Persamaan: $Q_1 - Q_2 - Q_3 = 0$")
            header_diff = "Q1 - (Q2 + Q3)"
        else:
            st.info(f"Karena $Q_1 < Q_3$, air masuk kurang. Kekurangan dipasok MASUK dari Reservoir B ($H_T < Z_B$). Persamaan: $Q_1 + Q_2 - Q_3 = 0$")
            header_diff = "(Q1 + Q2) - Q3"

        st.markdown("**Langkah 5: Tabel Iterasi (Trial & Error)**")
        
        # Membuat tabel data untuk ditampilkan di web
        rows = []
        for idx, tp in enumerate(trial_points, 1):
            q1, q2, q3, diff = hitung_sistem(tp)
            kes = "HT kurang besar" if diff > 0 else "HT terlalu besar"
            rows.append([f"{idx}", f"{tp:.4f}", f"{q1:.4f}", f"{q2:.4f}", f"{q3:.4f}", f"{diff:+.4f}", kes])
        rows.append([f"{len(trial_points)+1}", f"{H_T_sol:.4f}", f"{Q1_fin:.4f}", f"{Q2_fin:.4f}", f"{Q3_fin:.4f}", "0.0000", "SEIMBANG!"])
        
        st.table({
            "Trial": [r[0] for r in rows],
            "HT Rel (m)": [r[1] for r in rows],
            "Q1 (m3/s)": [r[2] for r in rows],
            "Q2 (m3/s)": [r[3] for r in rows],
            "Q3 (m3/s)": [r[4] for r in rows],
            f"dQ ({header_diff})": [r[5] for r in rows],
            "Kesimpulan": [r[6] for r in rows]
        })

        arah_Q2 = "dari Titik T -> ke Reservoir B" if H_T_sol > Z_B_rel else "dari Reservoir B -> ke Titik T"
        st.success(f"""
        **🎯 HASIL AKHIR KESIMPULAN:**
        1. **Tinggi Energi Absolut Titik T ($H_T$):** ${H_T_sol + Z_D:.4f}\\text{{ m}}$
        2. **Debit Pipa 1 ($Q_1$):** ${Q1_fin:.4f}\\text{{ m}}^3/s$ (Reservoir A $\\rightarrow$ Titik T)
        3. **Debit Pipa 2 ($Q_2$):** ${Q2_fin:.4f}\\text{{ m}}^3/s$ (Mengalir {arah_Q2})
        4. **Debit Pipa 3 ($Q_3$):** ${Q3_fin:.4f}\\text{{ m}}^3/s$ (Titik T $\\rightarrow$ Reservoir D)
        """)