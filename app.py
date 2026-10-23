import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import io

FAYL_NOMI = 'kassa_malumotlari.json'

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(
    page_title="Sinf Kassasi - Kassa Boshqaruvi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MAXSUS CSS DIZAYNI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Chiroyli card uslubi */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 20px;
        color: #ffffff;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        margin-bottom: 15px;
    }
    
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    .metric-sub {
        font-size: 0.8rem;
        color: #cbd5e1;
        margin-top: 4px;
    }
    
    /* Chek/Kvitansiya qutisi */
    .receipt-box {
        background: #ffffff;
        color: #0f172a;
        padding: 24px;
        border-radius: 12px;
        border: 2px dashed #0284c7;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        max-width: 500px;
        margin: 15px auto;
        font-family: 'Courier New', Courier, monospace;
    }
    
    .receipt-header {
        text-align: center;
        border-bottom: 1px dashed #cbd5e1;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }
    
    .receipt-item {
        display: flex;
        justify-content: space-between;
        margin: 6px 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# --- MA'LUMOTLAR BAZASI BILAN ISHLASH ---
def malumotni_yuklash():
    if os.path.exists(FAYL_NOMI):
        try:
            with open(FAYL_NOMI, 'r', encoding='utf-8') as fayl:
                malumot = json.load(fayl)
                if 'oquvchilar' not in malumot:
                    malumot['oquvchilar'] = {}
                if 'tarix' not in malumot:
                    malumot['tarix'] = []
                if 'yigim_nomi' not in malumot:
                    malumot['yigim_nomi'] = "Ovqat puli"
                if 'belgilangan_summa' not in malumot:
                    malumot['belgilangan_summa'] = 0
                
                # Moslikni tekshirish
                for ism, qiymat in list(malumot['oquvchilar'].items()):
                    if isinstance(qiymat, (int, float)):
                        malumot['oquvchilar'][ism] = {"jami": qiymat, "tarix": []}
                    elif isinstance(qiymat, dict):
                        if 'jami' not in qiymat:
                            qiymat['jami'] = 0
                        if 'tarix' not in qiymat:
                            qiymat['tarix'] = []
                return malumot
        except Exception:
            pass
            
    # Standart boshlang'ich ma'lumot
    boshlangich = {
        "yigim_nomi": "Ovqat puli",
        "belgilangan_summa": 50000,
        "oquvchilar": {
            "Ali Valiyev": {"jami": 50000, "tarix": [{"id": 1, "summa": 50000, "sana": datetime.now().strftime("%Y-%m-%d %H:%M"), "tur": "Naqd", "izoh": "Boshlang'ich to'lov"}]},
            "Bekzod Karimov": {"jami": 30000, "tarix": [{"id": 2, "summa": 30000, "sana": datetime.now().strftime("%Y-%m-%d %H:%M"), "tur": "Karta (Click)", "izoh": "Qisman to'landi"}]},
            "Dilnoza Rahimova": {"jami": 0, "tarix": []}
        },
        "tarix": []
    }
    malumotni_saqlash(boshlangich)
    return boshlangich

def malumotni_saqlash(malumot):
    with open(FAYL_NOMI, 'w', encoding='utf-8') as fayl:
        json.dump(malumot, fayl, ensure_ascii=False, indent=4)

def format_som(qiymat):
    try:
        return f"{int(qiymat):,}".replace(',', ' ') + " so'm"
    except (ValueError, TypeError):
        return f"{qiymat} so'm"

malumot = malumotni_yuklash()

# --- YON MENYU ---
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 10px 0;">
    <h2 style="margin: 0; color: #38bdf8;">🎓 Sinf Kassasi</h2>
    <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">Kassa va to'lovlar boshqaruvi</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.info(f"**📌 Joriy yig'im:** {malumot['yigim_nomi']}\n\n**🎯 Har bir o'quvchiga:** {format_som(malumot['belgilangan_summa'])}")

menyu = st.sidebar.radio(
    "Bo'limni tanlang:",
    [
        "📊 Umumiy Hisobot",
        "💰 To'lov qabul qilish",
        "👥 O'quvchilar ro'yxati",
        "🕒 To'lovlar tarixi",
        "⚙️ Sozlamalar",
        "🔄 Nollashtirish / Yangi yig'im"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 *Sinf o'quvchilari va ota-onalar hisobotini yuritish uchun qulay platforma.*")

# =========================================================
# 1. UMUMIY HISOBOT
# =========================================================
if menyu == "📊 Umumiy Hisobot":
    st.title("📊 Umumiy Hisobot va Statistika")
    
    if not malumot['oquvchilar']:
        st.warning("📭 Hozircha o'quvchilar ro'yxati bo'sh. Iltimos, **👥 O'quvchilar ro'yxati** bo'limiga o'tib o'quvchilarni kiriting.")
    else:
        belgilangan = malumot['belgilangan_summa']
        jami_oquvchilar = len(malumot['oquvchilar'])
        jami_yigildi = sum(oq['jami'] for oq in malumot['oquvchilar'].values())
        kutilayotgan_jami = belgilangan * jami_oquvchilar
        
        # Har bir o'quvchining qarzini hisoblash
        umumiy_haqiqiy_qarz = sum(max(0, belgilangan - oq['jami']) for oq in malumot['oquvchilar'].values())
        
        to_laganlar_soni = sum(1 for oq in malumot['oquvchilar'].values() if oq['jami'] >= belgilangan)
        qarzdorlar_soni = sum(1 for oq in malumot['oquvchilar'].values() if oq['jami'] < belgilangan)
        
        foiz = (jami_yigildi / kutilayotgan_jami * 100) if kutilayotgan_jami > 0 else 0
        foiz = min(100.0, max(0.0, foiz))

        # KPI Ko'rsatkichlar kartalari
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Kassadagi pul</div>
                <div class="metric-value">{format_som(jami_yigildi)}</div>
                <div class="metric-sub">Kutilayotgan: {format_som(kutilayotgan_jami)}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Umumiy qarzlar</div>
                <div class="metric-value" style="color: #f87171;">{format_som(umumiy_haqiqiy_qarz)}</div>
                <div class="metric-sub">Qarzdorlar: {qarzdorlar_soni} nafar</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Yig'ilish jarayoni</div>
                <div class="metric-value" style="color: #4ade80;">{foiz:.1f}%</div>
                <div class="metric-sub">To'liq to'lagan: {to_laganlar_soni} ta</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Jami o'quvchilar</div>
                <div class="metric-value" style="color: #a78bfa;">{jami_oquvchilar} ta</div>
                <div class="metric-sub">Har biridan: {format_som(belgilangan)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.progress(foiz / 100.0, text=f"Yig'ilish darajasi: {foiz:.1f}%")
        
        st.write("---")
        st.subheader("📋 O'quvchilarning to'lov hisob-kitobi")
        
        # Filtrlash va qidiruv
        filter_col1, filter_col2 = st.columns([2, 1])
        with filter_col1:
            qidiruv = st.text_input("🔍 O'quvchini izlash (ism bo'yicha):", placeholder="Masalan: Ali")
        with filter_col2:
            holat_filtri = st.selectbox("📌 Holat bo'yicha filter:", ["Barchasi", "🔴 Qarzi borlar", "🟢 To'liq to'laganlar", "🟡 Ortiqcha to'laganlar"])

        # Jadval uchun ma'lumotlarni yig'ish
        jadval_malumotlari = []
        for ism, oq in sorted(malumot['oquvchilar'].items()):
            tolandi = oq['jami']
            qarz = belgilangan - tolandi
            
            if qarz > 0:
                holat = "🔴 Qarzi bor"
            elif qarz < 0:
                holat = "🟡 Ortiqcha to'lagan"
            else:
                holat = "🟢 To'liq to'langan"
                
            jadval_malumotlari.append({
                "O'quvchi ismi": ism,
                "To'langan summa": tolandi,
                "Qarz miqdori": qarz if qarz > 0 else 0,
                "Ortiqcha summa": abs(qarz) if qarz < 0 else 0,
                "Holati": holat,
                "Oxirgi to'lov": oq['tarix'][-1]['sana'] if oq['tarix'] else "To'lanmagan"
            })
            
        df = pd.DataFrame(jadval_malumotlari)
        
        # Filtrlarni qo'llash
        if qidiruv:
            df = df[df["O'quvchi ismi"].str.contains(qidiruv, case=False, na=False)]
            
        if holat_filtri != "Barchasi":
            df = df[df["Holati"] == holat_filtri]
            
        # Formatlash
        df_display = df.copy()
        df_display["To'langan summa"] = df_display["To'langan summa"].apply(lambda x: f"{x:,}".replace(',', ' ') + " so'm")
        df_display["Qarz miqdori"] = df_display["Qarz miqdori"].apply(lambda x: f"{x:,}".replace(',', ' ') + " so'm")
        df_display["Ortiqcha summa"] = df_display["Ortiqcha summa"].apply(lambda x: f"{x:,}".replace(',', ' ') + " so'm")

        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Excel va CSV eksport
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Jadvalni CSV (Excel) yuklab olish",
                data=csv_data,
                file_name=f"kassa_hisoboti_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_exp2:
            # Excel export in-memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Kassa Hisoboti')
            st.download_button(
                label="📥 Jadvalni Excel (.xlsx) yuklab olish",
                data=output.getvalue(),
                file_name=f"kassa_hisoboti_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# =========================================================
# 2. TO'LOV QABUL QILISH
# =========================================================
elif menyu == "💰 To'lov qabul qilish":
    st.title("💰 To'lov qabul qilish")
    
    if not malumot['oquvchilar']:
        st.error("Avval o'quvchilarni kiriting!")
    else:
        ismlar_royxati = sorted(list(malumot['oquvchilar'].keys()))
        
        tanlangan_ism = st.selectbox("👤 O'quvchini tanlang:", ismlar_royxati)
        
        oq_info = malumot['oquvchilar'][tanlangan_ism]
        joriy_tolangan = oq_info['jami']
        belgilangan = malumot['belgilangan_summa']
        qarz_miqdori = belgilangan - joriy_tolangan
        
        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("Oldin to'lagan", format_som(joriy_tolangan))
        if qarz_miqdori > 0:
            info_col2.metric("Qolgan qarzi", format_som(qarz_miqdori), delta=f"-{qarz_miqdori:,}", delta_color="inverse")
        else:
            info_col2.metric("Qarzi", "Qarzi yo'q 🎉", delta="To'liq to'langan", delta_color="normal")
        info_col3.metric("Belgilangan summa", format_som(belgilangan))
        
        st.write("---")
        
        # Tezkor to'lov tugmalari
        st.markdown("**⚡ Tezkor to'lov summalari:**")
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        
        if 'kiritilgan_summa' not in st.session_state:
            st.session_state.kiritilgan_summa = max(0, qarz_miqdori)
            
        with b_col1:
            if st.button(f"To'liq qarz ({format_som(max(0, qarz_miqdori))})", use_container_width=True):
                st.session_state.kiritilgan_summa = max(0, qarz_miqdori)
        with b_col2:
            if st.button("+ 20 000 so'm", use_container_width=True):
                st.session_state.kiritilgan_summa = 20000
        with b_col3:
            if st.button("+ 50 000 so'm", use_container_width=True):
                st.session_state.kiritilgan_summa = 50000
        with b_col4:
            if st.button("+ 100 000 so'm", use_container_width=True):
                st.session_state.kiritilgan_summa = 100000
                
        with st.form("tolov_formasi", clear_on_submit=False):
            tolov_summasi = st.number_input(
                "Qancha pul olib keldi? (so'm):",
                min_value=1000,
                max_value=10000000,
                value=int(st.session_state.kiritilgan_summa) if st.session_state.kiritilgan_summa > 0 else 10000,
                step=5000
            )
            
            c1, c2 = st.columns(2)
            with c1:
                tolov_turi = st.selectbox("💳 To'lov turi:", ["Naqd pul", "Karta (Click / Payme / Uzum)", "Bank hisobiga o'tkazma", "Boshqa"])
            with c2:
                sana_vaqti = st.text_input("📅 Sana va vaqt:", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
                
            izoh = st.text_input("📝 Izoh (ixtiyoriy):", placeholder="Masalan: Otasi plastikdan tashladi yoki o'zi olib keldi")
            
            tasdiqlash = st.form_submit_button("✅ To'lovni tasdiqlash va kvitansiya chiqarish", use_container_width=True)
            
            if tasdiqlash:
                yangi_id = len(oq_info['tarix']) + 1
                yozuv = {
                    "id": yangi_id,
                    "oquvchi": tanlangan_ism,
                    "summa": int(tolov_summasi),
                    "sana": sana_vaqti,
                    "tur": tolov_turi,
                    "izoh": izoh if izoh else "-"
                }
                
                # O'quvchi ma'lumotlariga qo'shish
                oq_info['jami'] += int(tolov_summasi)
                oq_info['tarix'].append(yozuv)
                
                # Umumiy tarixga ham qo'shish
                malumot['tarix'].insert(0, yozuv)
                
                malumotni_saqlash(malumot)
                
                st.balloons()
                st.success(f"🎉 **{tanlangan_ism}** uchun **{format_som(tolov_summasi)}** to'lov muvaffaqiyatli qabul qilindi!")
                
                # Kvitansiya ko'rsatish
                st.markdown(f"""
                <div class="receipt-box">
                    <div class="receipt-header">
                        <h3 style="margin: 0; color: #0284c7;">SINF KASSASI TO'LOV CHEKI</h3>
                        <p style="margin: 4px 0 0; color: #64748b; font-size: 0.85rem;">{malumot['yigim_nomi']}</p>
                    </div>
                    <div class="receipt-item">
                        <span>O'quvchi:</span>
                        <strong>{tanlangan_ism}</strong>
                    </div>
                    <div class="receipt-item">
                        <span>To'lov summasi:</span>
                        <strong style="color: #16a34a; font-size: 1.1rem;">{format_som(tolov_summasi)}</strong>
                    </div>
                    <div class="receipt-item">
                        <span>To'lov usuli:</span>
                        <span>{tolov_turi}</span>
                    </div>
                    <div class="receipt-item">
                        <span>Sana va vaqt:</span>
                        <span>{sana_vaqti}</span>
                    </div>
                    <div class="receipt-item">
                        <span>Izoh:</span>
                        <span>{izoh if izoh else "-"}</span>
                    </div>
                    <hr style="border: none; border-top: 1px dashed #cbd5e1; margin: 12px 0;">
                    <div class="receipt-item">
                        <span>Jami to'lagan:</span>
                        <strong>{format_som(oq_info['jami'])}</strong>
                    </div>
                    <div class="receipt-item">
                        <span>Qolgan qarz:</span>
                        <strong>{format_som(max(0, belgilangan - oq_info['jami']))}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# 3. O'QUVCHILAR RO'YXATI
# =========================================================
elif menyu == "👥 O'quvchilar ro'yxati":
    st.title("👥 O'quvchilar ro'yxatini boshqarish")
    
    tab1, tab2, tab3 = st.tabs(["➕ Yangi o'quvchi qo'shish", "📑 Ommaviy qo'shish (Bir vaqtda)", "✏️ Tahrirlash va O'chirish"])
    
    with tab1:
        st.subheader("Bittalab o'quvchi qo'shish")
        with st.form("yangi_oquvchi_form"):
            yangi_ism = st.text_input("O'quvchining F.I.Sh (Familiya Ism):", placeholder="Masalan: Sardor Aliyev")
            boshlangich_pul = st.number_input("Boshlang'ich to'langan summa (agar bor bo'lsa):", min_value=0, value=0, step=5000)
            qoshish_btn = st.form_submit_button("➕ Ro'yxatga qo'shish", use_container_width=True)
            
            if qoshish_btn:
                ism_toza = yangi_ism.strip()
                if not ism_toza:
                    st.error("Iltimos, o'quvchi ismini kiriting!")
                elif ism_toza in malumot['oquvchilar']:
                    st.warning(f"Bu ism ro'yxatda allaqachon mavjud: {ism_toza}")
                else:
                    tarix_boshi = []
                    if boshlangich_pul > 0:
                        tarix_boshi.append({
                            "id": 1,
                            "oquvchi": ism_toza,
                            "summa": int(boshlangich_pul),
                            "sana": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "tur": "Boshlang'ich",
                            "izoh": "Ro'yxatga kiritilganda to'langan"
                        })
                    malumot['oquvchilar'][ism_toza] = {
                        "jami": int(boshlangich_pul),
                        "tarix": tarix_boshi
                    }
                    malumotni_saqlash(malumot)
                    st.success(f"✅ **{ism_toza}** muvaffaqiyatli qo'shildi!")
                    st.rerun()

    with tab2:
        st.subheader("📑 Ommaviy qo'shish (Ro'yxatdan nusxa olib qo'yish)")
        st.write("Har bir o'quvchi ismini yangi qatordan yozing:")
        ommaviy_matn = st.text_area("O'quvchilar ro'yxati:", placeholder="Ali Valiyev\nBobur Karimov\nDilshod Rustamov", height=200)
        
        if st.button("🚀 Barchasini birdaniga qo'shish", use_container_width=True):
            satrlar = [s.strip() for s in ommaviy_matn.split("\n") if s.strip()]
            qoshildi_soni = 0
            for ism in satrlar:
                if ism not in malumot['oquvchilar']:
                    malumot['oquvchilar'][ism] = {"jami": 0, "tarix": []}
                    qoshildi_soni += 1
            if qoshildi_soni > 0:
                malumotni_saqlash(malumot)
                st.success(f"✅ {qoshildi_soni} ta yangi o'quvchi ro'yxatga qo'shildi!")
                st.rerun()
            else:
                st.info("Yangi qo'shiladigan o'quvchi topilmadi yoki barchasi avval qo'shilgan.")

    with tab3:
        st.subheader("✏️ O'quvchini tahrirlash yoki o'chirish")
        if not malumot['oquvchilar']:
            st.info("Hozircha o'quvchilar yo'q.")
        else:
            tanlangan_ism = st.selectbox("O'quvchini tanlang:", sorted(list(malumot['oquvchilar'].keys())), key="edit_select")
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.write("**Ismni tahrirlash:**")
                yangi_nom = st.text_input("Yangi ism:", value=tanlangan_ism)
                if st.button("💾 Ismni yangilash"):
                    if yangi_nom.strip() and yangi_nom.strip() != tanlangan_ism:
                        malumot['oquvchilar'][yangi_nom.strip()] = malumot['oquvchilar'].pop(tanlangan_ism)
                        malumotni_saqlash(malumot)
                        st.success(f"Ism o'zgartirildi: {yangi_nom}")
                        st.rerun()
                        
            with col_t2:
                st.write("**O'quvchini o'chirish:**")
                st.warning(f"⚠️ Diqqat: {tanlangan_ism} o'chirilsa, uning barcha to'lovlari ham o'chadi!")
                ochirish_tasdiq = st.checkbox(f"Ha, {tanlangan_ism}ni o'chirishni tasdiqlayman")
                if st.button("🗑️ O'quvchini o'chirish", type="primary"):
                    if ochirish_tasdiq:
                        del malumot['oquvchilar'][tanlangan_ism]
                        malumotni_saqlash(malumot)
                        st.success(f"{tanlangan_ism} ro'yxatdan o'chirildi.")
                        st.rerun()
                    else:
                        st.error("O'chirish uchun yuqoridagi tasdiqlash katakchasini belgilang!")

    st.write("---")
    st.subheader(f"📋 Barcha o'quvchilar ro'yxati ({len(malumot['oquvchilar'])} nafar)")
    if malumot['oquvchilar']:
        barcha_df = pd.DataFrame([
            {"№": idx + 1, "F.I.Sh": ism, "Jami to'lagan": format_som(mal['jami']), "To'lovlar soni": len(mal['tarix'])}
            for idx, (ism, mal) in enumerate(sorted(malumot['oquvchilar'].items()))
        ])
        st.dataframe(barcha_df, use_container_width=True, hide_index=True)

# =========================================================
# 4. TO'LOVLAR TARIXI
# =========================================================
elif menyu == "🕒 To'lovlar tarixi":
    st.title("🕒 Barcha to'lovlar tarixi")
    
    # Barcha o'quvchilar tarixini umumlashtirish
    barcha_tranzaksiyalar = []
    for ism, val in malumot['oquvchilar'].items():
        for t in val.get('tarix', []):
            item = t.copy()
            item['oquvchi'] = ism
            barcha_tranzaksiyalar.append(item)
            
    if not barcha_tranzaksiyalar:
        st.info("📭 Hozircha birorta ham to'lov amalga oshirilmagan.")
    else:
        # Sanasi bo'yicha teskari tartibda (eng yangilari birinchi)
        barcha_tranzaksiyalar.sort(key=lambda x: str(x.get('sana', '')), reverse=True)
        
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            oquvchi_tanlash = st.selectbox("O'quvchi bo'yicha filtrlash:", ["Barchasi"] + sorted(list(malumot['oquvchilar'].keys())))
        with filter_col2:
            turlar = list(set([t.get('tur', 'Noma\'lum') for t in barcha_tranzaksiyalar]))
            tur_tanlash = st.selectbox("To'lov turi bo'yicha filtrlash:", ["Barchasi"] + turlar)
            
        filtr_tarix = barcha_tranzaksiyalar
        if oquvchi_tanlash != "Barchasi":
            filtr_tarix = [t for t in filtr_tarix if t.get('oquvchi') == oquvchi_tanlash]
        if tur_tanlash != "Barchasi":
            filtr_tarix = [t for t in filtr_tarix if t.get('tur') == tur_tanlash]
            
        st.write(f"Topilgan to'lovlar soni: **{len(filtr_tarix)}** ta")
        
        df_tarix = pd.DataFrame([
            {
                "Sana va vaqt": t.get('sana', '-'),
                "O'quvchi": t.get('oquvchi', '-'),
                "Summa": format_som(t.get('summa', 0)),
                "To'lov turi": t.get('tur', '-'),
                "Izoh": t.get('izoh', '-')
            }
            for t in filtr_tarix
        ])
        
        st.dataframe(df_tarix, use_container_width=True, hide_index=True)
        
        # CSV yuklab olish
        csv_tarix = df_tarix.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tarixni yuklab olish (CSV)",
            data=csv_tarix,
            file_name=f"tolovlar_tarixi_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# =========================================================
# 5. SOZLAMALAR
# =========================================================
elif menyu == "⚙️ Sozlamalar":
    st.title("⚙️ Tizim sozlamalari")
    
    with st.form("sozlamalar_formasi"):
        st.subheader("🎯 Yig'im parametrlarini o'zgartirish")
        yangi_nom = st.text_input("Yig'im nomi (maqsad):", value=malumot.get('yigim_nomi', 'Ovqat puli'))
        yangi_summa = st.number_input(
            "Har bir o'quvchi to'lashi kerak bo'lgan summa (so'm):",
            min_value=0,
            value=int(malumot.get('belgilangan_summa', 50000)),
            step=5000
        )
        
        saqlash_btn = st.form_submit_button("💾 Sozlamalarni saqlash", use_container_width=True)
        if saqlash_btn:
            malumot['yigim_nomi'] = yangi_nom.strip()
            malumot['belgilangan_summa'] = int(yangi_summa)
            malumotni_saqlash(malumot)
            st.success("✅ Sozlamalar muvaffaqiyatli saqlandi!")
            st.rerun()

    st.write("---")
    st.subheader("💾 Ma'lumotlarni zaxiralash va qayta tiklash")
    
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.markdown("**1. Ma'lumotlar bazasini yuklab olish (Backup):**")
        baza_json = json.dumps(malumot, ensure_ascii=False, indent=4).encode('utf-8')
        st.download_button(
            label="📥 Zahira nusxasini yuklab olish (.json)",
            data=baza_json,
            file_name=f"kassa_baza_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
        
    with c_b2:
        st.markdown("**2. Zahira faylini qayta yuklash (Restore):**")
        yuklangan_fayl = st.file_uploader("JSON faylni tanlang:", type=["json"])
        if yuklangan_fayl is not None:
            if st.button("📤 Tiklashni tasdiqlash", use_container_width=True):
                try:
                    qayta_baza = json.load(yuklangan_fayl)
                    malumotni_saqlash(qayta_baza)
                    st.success("✅ Ma'lumotlar muvaffaqiyatli tiklandi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Xatolik yuz berdi: {e}")

# =========================================================
# 6. NOLLASHTIRISH / YANGI YIG'IM
# =========================================================
elif menyu == "🔄 Nollashtirish / Yangi yig'im":
    st.title("🔄 Yangi yig'im boshlash yoki Nollashtirish")
    st.warning("⚠️ Bu amallar kassa ma'lumotlariga jiddiy ta'sir ko'rsatadi.")
    
    st.subheader("1. Yangi oy / Yangi yig'im boshlash")
    st.write("O'quvchilar ro'yxati saqlanib qoladi, lekin ularning to'lagan summalari 0 ga tenglashtiriladi (yangi oylik to'lovlar uchun).")
    
    if st.checkbox("Men o'quvchilar to'lovlarini nollashtirishni tasdiqlayman"):
        if st.button("🔄 Yangi oy to'lovlarini boshlash (Nollashtirish)", type="primary"):
            for ism in malumot['oquvchilar']:
                malumot['oquvchilar'][ism]['jami'] = 0
                malumot['oquvchilar'][ism]['tarix'] = []
            malumot['tarix'] = []
            malumotni_saqlash(malumot)
            st.success("✅ To'lovlar yangi oy uchun nollashtirildi!")
            st.rerun()
            
    st.write("---")
    st.subheader("2. Butun tizimni tozalash")
    st.write("Barcha o'quvchilar va to'lovlar butunlay o'chiriladi.")
    tozalash_kodi = st.text_input("Tasdiqlash uchun 'TOZALASH' deb yozing:")
    if st.button("💥 Butun bazani tozalash"):
        if tozalash_kodi == "TOZALASH":
            malumot['oquvchilar'] = {}
            malumot['tarix'] = []
            malumotni_saqlash(malumot)
            st.success("✅ Baza to'liq tozalandi!")
            st.rerun()
        else:
            st.error("Tasdiqlash kodi noto'g'ri kiritildi!")
