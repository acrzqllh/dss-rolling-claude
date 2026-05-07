import streamlit as st
import random
import pandas as pd
from datetime import date

# ─────────────────────────────────────────────
# KONFIGURASI DATA
# ─────────────────────────────────────────────
TELLERS = ["Teller A", "Teller B", "Teller C", "Teller D",
           "Teller E", "Teller F", "Teller G", "Teller H"]

# Posisi: "induk" membutuhkan 2 slot → kita representasikan sebagai 2 entry
POSITIONS_SINGLE = ["galbar", "galsel", "galtim", "sumpang", "cepat", "mpp"]
POSITIONS_DOUBLE = ["induk"]  # butuh 2 teller

# Constraint khusus Teller D
TELLER_D_FORBIDDEN = {"galbar", "mpp", "galtim"}
TELLER_D_NAME = "Teller D"

# Warna pastel per posisi untuk tampilan kartu
POS_COLORS = {
    "galbar":  "#FFD6D6",
    "galsel":  "#D6EAFF",
    "galtim":  "#D6FFE4",
    "sumpang": "#FFF4D6",
    "cepat":   "#EDD6FF",
    "induk":   "#FFE8D6",
    "mpp":     "#D6F9FF",
}

POS_ICONS = {
    "galbar":  "🏦",
    "galsel":  "🏢",
    "galtim":  "🏬",
    "sumpang": "🏗️",
    "cepat":   "⚡",
    "induk":   "🏛️",
    "mpp":     "🏤",
}

# ─────────────────────────────────────────────
# ALGORITMA PENJADWALAN (Constraint-First)
# ─────────────────────────────────────────────
def generate_schedule():
    """
    Menghasilkan jadwal rotasi acak yang memenuhi semua constraint.
    Strategi: Tempatkan Teller D lebih dahulu ke posisi yang valid,
    lalu acak sisa teller ke sisa slot. Dijamin O(n), tidak ada infinite loop.
    """
    # Buat semua slot: 6 posisi single + 2 slot untuk induk
    all_slots = POSITIONS_SINGLE + ["induk", "induk"]

    # ── LANGKAH 1: Tentukan posisi valid untuk Teller D ──
    valid_for_d = [pos for pos in set(all_slots) if pos not in TELLER_D_FORBIDDEN]

    # ── LANGKAH 2: Pilih SATU posisi acak untuk Teller D ──
    chosen_for_d = random.choice(valid_for_d)

    # ── LANGKAH 3: Buat list slot yang tersisa setelah Teller D ditempatkan ──
    remaining_slots = all_slots.copy()
    remaining_slots.remove(chosen_for_d)  # Hapus satu instance posisi tersebut

    # ── LANGKAH 4: Acak sisa 7 teller ke sisa 7 slot ──
    other_tellers = [t for t in TELLERS if t != TELLER_D_NAME]
    random.shuffle(other_tellers)

    # ── LANGKAH 5: Susun jadwal akhir ──
    schedule_raw = [(chosen_for_d, TELLER_D_NAME)]
    for slot, teller in zip(remaining_slots, other_tellers):
        schedule_raw.append((slot, teller))

    # ── LANGKAH 6: Kelompokkan ke dalam dict posisi → [teller, ...] ──
    schedule = {}
    for pos, teller in schedule_raw:
        schedule.setdefault(pos, []).append(teller)

    return schedule


def validate_schedule(schedule):
    """Validasi jadwal: kembalikan list pelanggaran constraint."""
    issues = []
    for pos, tellers in schedule.items():
        if TELLER_D_NAME in tellers and pos in TELLER_D_FORBIDDEN:
            issues.append(
                f"⚠️ Pelanggaran: {TELLER_D_NAME} ditempatkan di pos '{pos}' (pos terlarang)!"
            )
    induk_count = len(schedule.get("induk", []))
    if induk_count != 2:
        issues.append(f"⚠️ Pos 'induk' harus diisi 2 Teller, saat ini: {induk_count}.")
    return issues


# ─────────────────────────────────────────────
# TAMPILAN STREAMLIT
# ─────────────────────────────────────────────
def render_position_card(pos, tellers):
    """Render satu kartu posisi dengan HTML kustom."""
    color = POS_COLORS.get(pos, "#F0F0F0")
    icon  = POS_ICONS.get(pos, "📌")
    teller_html = "".join(
        f'<div class="teller-badge">{t}</div>' for t in tellers
    )
    card = f"""
    <div class="pos-card" style="background:{color};">
        <div class="pos-header">
            <span class="pos-icon">{icon}</span>
            <span class="pos-name">{pos.upper()}</span>
        </div>
        <div class="teller-list">{teller_html}</div>
    </div>
    """
    return card


def inject_css():
    st.markdown("""
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* ── Header utama ── */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 800;
        color: #1a2940;
        margin: 0;
    }
    .main-header p {
        color: #5a7194;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    .badge-date {
        display: inline-block;
        background: #1a2940;
        color: #fff;
        border-radius: 20px;
        padding: 0.25rem 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
        letter-spacing: 0.05em;
    }

    /* ── Kartu posisi ── */
    .pos-card {
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.07);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .pos-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.12);
    }
    .pos-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.6rem;
    }
    .pos-icon {
        font-size: 1.4rem;
    }
    .pos-name {
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        color: #1a2940;
    }
    .teller-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
    }
    .teller-badge {
        background: rgba(255,255,255,0.75);
        border: 1.5px solid rgba(0,0,0,0.1);
        border-radius: 8px;
        padding: 0.2rem 0.65rem;
        font-size: 0.82rem;
        font-weight: 600;
        color: #1a2940;
    }

    /* ── Tombol Streamlit dikustom ── */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1a2940 0%, #2d4a7a 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 700;
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: 0.04em;
        cursor: pointer;
        transition: opacity 0.2s;
        box-shadow: 0 4px 14px rgba(26,41,64,0.3);
    }
    div.stButton > button:hover {
        opacity: 0.9;
    }

    /* ── Section divider ── */
    .section-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        color: #8a9dba;
        text-transform: uppercase;
        margin: 1.5rem 0 0.75rem 0;
    }

    /* ── Info box constraint ── */
    .constraint-box {
        background: #fff8e6;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: #78530a;
        margin-bottom: 1rem;
    }

    /* ── Tabel ringkasan ── */
    .summary-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
    }
    .summary-table th {
        background: #1a2940;
        color: white;
        padding: 0.6rem 0.9rem;
        text-align: left;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .summary-table td {
        padding: 0.55rem 0.9rem;
        border-bottom: 1px solid #e8ecf3;
        color: #2d3748;
    }
    .summary-table tr:nth-child(even) td {
        background: #f8f9fc;
    }
    .summary-table tr:hover td {
        background: #eef2ff;
    }
    th:first-child  { border-radius: 8px 0 0 0; }
    th:last-child   { border-radius: 0 8px 0 0; }

    /* ── Sembunyikan elemen Streamlit default ── */
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="DSS Rotasi Teller",
        page_icon="🏦",
        layout="centered",
    )

    inject_css()

    # ── Header ──
    today_str = date.today().strftime("%A, %d %B %Y")
    st.markdown(f"""
    <div class="main-header">
        <h1>🏦 DSS Rotasi Teller</h1>
        <p>Sistem Penjadwalan Otomatis Penempatan Teller Harian</p>
        <span class="badge-date">📅 {today_str}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Panel Aturan Bisnis (sidebar ringkas) ──
    with st.expander("📋 Lihat Aturan & Constraint Sistem", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**👥 Daftar Teller (8 orang)**")
            for t in TELLERS:
                marker = " 🔒" if t == TELLER_D_NAME else ""
                st.markdown(f"- {t}{marker}")
        with col2:
            st.markdown("**📍 Daftar Posisi/Loket**")
            for p in POSITIONS_SINGLE:
                st.markdown(f"- {p} *(1 teller)*")
            st.markdown("- induk *(2 teller)*")

        st.markdown("""
        <div class="constraint-box">
            🔒 <strong>Constraint Khusus:</strong> Teller D <u>tidak boleh</u>
            ditempatkan di posisi: <strong>galbar, mpp, galtim</strong>.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ── Tombol Generate ──
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        generate = st.button("🎲  Generate Jadwal Baru")

    # ── State management ──
    if "schedule" not in st.session_state:
        st.session_state.schedule = None
        st.session_state.iteration = 0

    if generate:
        st.session_state.schedule  = generate_schedule()
        st.session_state.iteration += 1

    # ── Tampilkan Hasil ──
    if st.session_state.schedule is not None:
        schedule = st.session_state.schedule
        iteration = st.session_state.iteration

        # Validasi
        issues = validate_schedule(schedule)
        if issues:
            for issue in issues:
                st.error(issue)
        else:
            st.success(f"✅ Jadwal #{iteration} berhasil dibuat — semua constraint terpenuhi!")

        st.markdown('<p class="section-label">Penempatan per Loket</p>', unsafe_allow_html=True)

        # Render kartu dalam 2 kolom
        positions_ordered = ["galbar", "galsel", "galtim", "sumpang", "cepat", "mpp", "induk"]
        col_left, col_right = st.columns(2)

        for i, pos in enumerate(positions_ordered):
            tellers_at_pos = schedule.get(pos, [])
            card_html = render_position_card(pos, tellers_at_pos)
            if i % 2 == 0:
                with col_left:
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                with col_right:
                    st.markdown(card_html, unsafe_allow_html=True)

        # ── Tabel Ringkasan ──
        st.markdown('<p class="section-label">Tabel Ringkasan (Teller → Posisi)</p>',
                    unsafe_allow_html=True)

        rows = []
        for pos, tellers_list in schedule.items():
            for teller in tellers_list:
                is_constrained = (teller == TELLER_D_NAME)
                constraint_note = "🔒 Constraint aktif" if is_constrained else ""
                rows.append({
                    "Teller": teller,
                    "Posisi / Loket": pos.upper(),
                    "Keterangan": constraint_note
                })

        df = pd.DataFrame(rows).sort_values("Teller").reset_index(drop=True)

        # Tampilkan sebagai tabel HTML kustom
        table_rows = ""
        for _, row in df.iterrows():
            table_rows += (
                f"<tr>"
                f"<td>{row['Teller']}</td>"
                f"<td>{row['Posisi / Loket']}</td>"
                f"<td>{row['Keterangan']}</td>"
                f"</tr>"
            )
        st.markdown(f"""
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Teller</th>
                    <th>Posisi / Loket</th>
                    <th>Keterangan</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

        # ── Export CSV ──
        st.markdown("")
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Unduh Jadwal sebagai CSV",
            data=csv_data,
            file_name=f"jadwal_teller_{date.today().isoformat()}_v{iteration}.csv",
            mime="text/csv",
        )

    else:
        # Placeholder sebelum generate
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: #8a9dba;">
            <div style="font-size:3rem;">📋</div>
            <div style="font-weight:600; margin-top:0.5rem;">
                Klik tombol <em>Generate Jadwal Baru</em> untuk mulai
            </div>
            <div style="font-size:0.85rem; margin-top:0.3rem;">
                Sistem akan mengacak penempatan secara otomatis sesuai aturan bisnis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#b0bec5; font-size:0.78rem;'>"
        "DSS Rotasi Teller · Dibangun dengan Python & Streamlit · "
        "Algoritma: Constraint-First Assignment"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
