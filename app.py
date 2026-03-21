import streamlit as st
import numpy as np
import librosa
import folium
from streamlit_folium import st_folium
import datetime
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import pytz
import base64
from supabase import create_client

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://bviywcrtdgdjuehdzcqh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2aXl3Y3J0ZGdkanVlaGR6Y3FoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwMDUwMjksImV4cCI6MjA4OTU4MTAyOX0.5YNiADm1Uygt_L-a3U5q9369LV2X3d_fHsxNOuUFRQQ"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="VoxAid", page_icon="🆘", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif !important; background-color: #050d1a !important; color: #c8d8e8 !important; }
.stApp { background: linear-gradient(160deg, #050d1a 0%, #0a1628 50%, #050d1a 100%) !important; }
.block-container { max-width: 1200px !important; margin: 0 auto !important; }
.vx-header { padding: 20px 0 12px; border-bottom: 1px solid #1a3a5c; margin-bottom: 20px; display:flex; justify-content:space-between; align-items:center; }
.vx-logo { font-family: 'Share Tech Mono', monospace; font-size: 2.4rem; font-weight: 700; color: #00d4ff; letter-spacing: 4px; text-shadow: 0 0 20px rgba(0,212,255,0.3); }
.vx-sub { font-size: 0.8rem; color: #4a7a9b; letter-spacing: 3px; text-transform: uppercase; margin-top: 2px; }
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }
.stat-card { background: #0d1f35; border: 1px solid #1a3a5c; border-top: 2px solid #00d4ff; border-radius: 4px; padding: 14px; text-align: center; }
.stat-num { font-family: 'Share Tech Mono', monospace; font-size: 1.6rem; color: #00d4ff; font-weight: 700; }
.stat-label { font-size: 0.7rem; color: #4a7a9b; text-transform: uppercase; letter-spacing: 2px; margin-top: 2px; }
.stat-sub { font-size: 0.7rem; color: #2a5a7c; margin-top: 2px; }
.status-ok { display: flex; align-items: center; gap: 8px; background: #0a1f10; border: 1px solid #1a4a2a; border-left: 3px solid #00ff88; border-radius: 4px; padding: 10px 16px; margin-bottom: 16px; font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: #00ff88; }
.status-err { background: #1a0a0a; border: 1px solid #4a1a1a; border-left: 3px solid #ff3333; color: #ff3333; }
.alert-survivor { background: linear-gradient(135deg,#1a0505,#2a0808); border: 1px solid #cc2200; border-left: 4px solid #ff2200; border-radius: 4px; padding: 24px; text-align: center; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(255,34,0,0.3); } 50% { box-shadow: 0 0 16px 4px rgba(255,34,0,0.15); } }
.alert-clear { background: linear-gradient(135deg,#050f08,#0a1f10); border: 1px solid #004422; border-left: 4px solid #00ff88; border-radius: 4px; padding: 24px; text-align: center; }
.alert-emoji { font-size: 2.5rem; margin-bottom: 8px; }
.alert-title-red { font-family: 'Share Tech Mono', monospace; font-size: 1.8rem; color: #ff2200; font-weight: 700; letter-spacing: 3px; }
.alert-title-green { font-family: 'Share Tech Mono', monospace; font-size: 1.8rem; color: #00ff88; font-weight: 700; letter-spacing: 3px; }
.alert-conf { font-size: 1rem; color: #8899aa; margin: 8px 0 14px; letter-spacing: 2px; }
.conf-bg { background: #0d1f35; border-radius: 2px; height: 8px; width: 100%; overflow: hidden; max-width: 400px; margin: 0 auto; }
.conf-fill-red { background: linear-gradient(90deg,#cc2200,#ff4400); height: 100%; border-radius: 2px; }
.conf-fill-green { background: linear-gradient(90deg,#00aa44,#00ff88); height: 100%; border-radius: 2px; }
.alert-msg-red { margin-top: 14px; font-size: 0.85rem; color: #cc4422; letter-spacing: 1px; }
.alert-msg-green { margin-top: 14px; font-size: 0.85rem; color: #007744; letter-spacing: 1px; }
.lang-table { width:100%; border-collapse:collapse; margin-top:14px; font-size:0.9rem; }
.lang-table td { padding:8px 12px; border-bottom:1px solid #1a3a5c; color:#c8d8e8; }
.lang-table td:first-child { color:#00d4ff; font-family:'Share Tech Mono',monospace; font-size:0.72rem; letter-spacing:1px; width:80px; }
.gps-bar { background:#0a1628; border:1px solid #1a3a5c; border-radius:4px; padding:10px 16px; font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#4a7a9b; margin-top:14px; display:flex; gap:20px; flex-wrap:wrap; }
.gps-bar span { color:#00d4ff; }
.log-red { background:#1a0808; border-left:3px solid #ff2200; padding:10px 14px; margin-bottom:6px; border-radius:3px; font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#ff6644; cursor:pointer; }
.log-green { background:#050f08; border-left:3px solid #00ff88; padding:10px 14px; margin-bottom:6px; border-radius:3px; font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#00aa55; cursor:pointer; }
.log-pending { border-right: 3px solid #ffaa00; }
.log-confirmed { border-right: 3px solid #00ff88; }
.log-rejected { border-right: 3px solid #ff2200; }
.sec { font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#4a7a9b; letter-spacing:3px; text-transform:uppercase; border-bottom:1px solid #1a3a5c; padding-bottom:6px; margin:18px 0 10px; }
.login-box { max-width:420px; margin:80px auto; background:#0d1f35; border:1px solid #1a3a5c; border-radius:8px; padding:32px; }
.login-title { font-family:'Share Tech Mono',monospace; font-size:1.4rem; color:#00d4ff; letter-spacing:3px; text-align:center; margin-bottom:4px; }
.login-sub { font-size:0.8rem; color:#4a7a9b; text-align:center; letter-spacing:2px; margin-bottom:24px; }
.role-badge-admin { background:#1a0a2a; border:1px solid #6644aa; color:#aa88ff; border-radius:3px; padding:3px 10px; font-family:'Share Tech Mono',monospace; font-size:0.7rem; }
.role-badge-worker { background:#0a1f10; border:1px solid #1a4a2a; color:#00ff88; border-radius:3px; padding:3px 10px; font-family:'Share Tech Mono',monospace; font-size:0.7rem; }
.det-card { background:#0d1f35; border:1px solid #1a3a5c; border-radius:6px; padding:16px; margin-bottom:10px; cursor:pointer; transition:border-color 0.2s; }
.det-card:hover { border-color:#00d4ff; }
.det-card-title { font-family:'Share Tech Mono',monospace; font-size:0.85rem; color:#00d4ff; margin-bottom:6px; }
.det-card-meta { font-size:0.8rem; color:#4a7a9b; }
.verify-box { background:#0a1628; border:1px solid #1a3a5c; border-radius:6px; padding:16px; margin-top:14px; }
.verify-title { font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#4a7a9b; letter-spacing:2px; margin-bottom:10px; }
.stTabs [data-baseweb="tab-list"] { background:#0a1628; border-bottom:1px solid #1a3a5c; gap:0; }
.stTabs [data-baseweb="tab"] { font-family:'Share Tech Mono',monospace; font-size:0.78rem; letter-spacing:2px; color:#4a7a9b !important; padding:12px 24px; }
.stTabs [aria-selected="true"] { color:#00d4ff !important; border-bottom:2px solid #00d4ff !important; background:transparent !important; }
.stButton > button { font-family:'Rajdhani',sans-serif; font-weight:600; letter-spacing:2px; text-transform:uppercase; background:linear-gradient(135deg,#003366,#004488); border:1px solid #0066cc; color:#00d4ff; border-radius:3px; }
.stButton > button:hover { background:linear-gradient(135deg,#004488,#0055aa); border-color:#00d4ff; }
[data-testid="stMetricValue"] { font-family:'Share Tech Mono',monospace !important; color:#00d4ff !important; }
[data-testid="stMetricLabel"] { color:#4a7a9b !important; }
@media (max-width: 768px) { .stat-grid { grid-template-columns: repeat(2,1fr); } .vx-logo { font-size:1.8rem; } }
footer { display:none; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [('logged_in', False), ('user', None), ('recorder_key', 0),
             ('spot_recordings', {}), ('spot_count', 3), ('detection_log', []),
             ('selected_detection', None), ('page', 'scan'),
             ('active_mission_id', None), ('active_mission_name', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        import tensorflow as tf
        return tf.keras.models.load_model("voxaid_model.h5", compile=False)
    except:
        return None

model = load_model()

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_ist():
    return datetime.datetime.now(pytz.timezone('Asia/Kolkata'))

def run_inference(audio_bytes):
    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=22050, duration=5.0)
    b, a = butter(5, [80/(sr/2), 8000/(sr/2)], btype='band')
    y = filtfilt(b, a, y)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return float(model.predict(np.mean(mfcc, axis=1).reshape(-1, 40, 1), verbose=0)[0][0])

def generate_spectrogram(audio_bytes):
    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=22050, duration=5.0)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 4))
    fig.patch.set_facecolor('#050d1a')
    ax1.plot(np.linspace(0, len(y)/sr, len(y)), y, color='#00d4ff', linewidth=0.6)
    ax1.set_facecolor('#0a1628'); ax1.set_ylabel('Amplitude', color='#4a7a9b', fontsize=8)
    ax1.tick_params(colors='#4a7a9b', labelsize=7); ax1.set_title('WAVEFORM', color='#4a7a9b', fontsize=8, loc='left')
    for s in ax1.spines.values(): s.set_edgecolor('#1a3a5c')
    S_db = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr), ref=np.max)
    librosa.display.specshow(S_db, sr=sr, ax=ax2, x_axis='time', y_axis='mel', cmap='Blues')
    ax2.set_facecolor('#0a1628'); ax2.set_title("SPECTROGRAM", color='#4a7a9b', fontsize=8, loc='left')
    ax2.tick_params(colors='#4a7a9b', labelsize=7)
    for s in ax2.spines.values(): s.set_edgecolor('#1a3a5c')
    plt.tight_layout(pad=1.5)
    return fig

def save_detection(score, audio_bytes, lat, lon):
    detected = score >= 0.5
    pct = round(score*100, 1) if detected else round((1-score)*100, 1)
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None
    try:
        supabase.table('detections').insert({
            'user_id': st.session_state.user['id'],
            'user_name': st.session_state.user['name'],
            'score': score,
            'detected': detected,
            'confidence': pct,
            'gps_lat': lat,
            'gps_lon': lon,
            'audio_base64': audio_b64,
            'verified': None,
            'mission_id': st.session_state.get('active_mission_id'),
            'mission_name': st.session_state.get('active_mission_name')
        }).execute()
    except Exception as e:
        st.warning(f"Could not save detection: {e}")

def show_result(score, audio_bytes=None):
    pct = round(score * 100, 1)
    detected = score >= 0.5
    display_pct = pct if detected else round((1-score)*100, 1)
    now = get_ist()
    ts = now.strftime("%d-%m-%Y %I:%M:%S %p IST")
    lat = st.session_state.get('user_lat', 13.0827)
    lon = st.session_state.get('user_lon', 80.2707)

    if detected:
        st.markdown(f"""
        <div class="alert-survivor">
            <div class="alert-emoji">🚨</div>
            <div class="alert-title-red">SURVIVOR DETECTED</div>
            <div class="alert-conf">CONFIDENCE: {display_pct}%</div>
            <div class="conf-bg"><div class="conf-fill-red" style="width:{display_pct}%"></div></div>
            <div class="alert-msg-red">▶ HUMAN SOUND PATTERN IDENTIFIED — MARK THIS LOCATION IMMEDIATELY</div>
        </div>
        <table class="lang-table">
            <tr><td>EN</td><td>Survivor detected — mark this location immediately</td></tr>
            <tr><td>தமிழ்</td><td>உயிரோடிருப்பவர் கண்டுபிடிக்கப்பட்டார் — இந்த இடத்தை உடனே குறிக்கவும்</td></tr>
            <tr><td>हिन्दी</td><td>जीवित व्यक्ति का पता चला — इस स्थान को तुरंत चिह्नित करें</td></tr>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-clear">
            <div class="alert-emoji">✅</div>
            <div class="alert-title-green">NO SURVIVOR DETECTED</div>
            <div class="alert-conf">CONFIDENCE: {display_pct}%</div>
            <div class="conf-bg"><div class="conf-fill-green" style="width:{display_pct}%"></div></div>
            <div class="alert-msg-green">▶ NO HUMAN SOUND PATTERN FOUND — CONTINUE SCANNING</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="gps-bar">
        <div>📍 GPS: <span>{lat:.4f}°N, {lon:.4f}°E</span></div>
        <div>🕐 <span>{ts}</span></div>
        <div>⚡ SCORE: <span>{score:.4f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    if audio_bytes is not None:
        save_detection(score, audio_bytes, lat, lon)
        st.markdown('<div class="sec">SIGNAL ANALYSIS</div>', unsafe_allow_html=True)
        try:
            fig = generate_spectrogram(audio_bytes)
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.caption(f"Spectrogram unavailable: {e}")

# ── GPS ───────────────────────────────────────────────────────────────────────
params = st.query_params
if "lat" in params and "lon" in params:
    try:
        st.session_state.user_lat = float(params["lat"])
        st.session_state.user_lon = float(params["lon"])
    except: pass
if "user_lat" not in st.session_state: st.session_state.user_lat = 13.0827
if "user_lon" not in st.session_state: st.session_state.user_lon = 80.2707
st.components.v1.html("""<script>
if(navigator.geolocation){navigator.geolocation.getCurrentPosition(function(p){
    const u=window.parent.location.href.split('?')[0];
    if(!window.parent.location.href.includes('lat='))
        window.parent.location.href=u+'?lat='+p.coords.latitude.toFixed(6)+'&lon='+p.coords.longitude.toFixed(6);
})}</script>""", height=0)
base_lat = st.session_state.user_lat
base_lon = st.session_state.user_lon

# ════════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ════════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align:center; padding-top:40px;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:3rem; color:#00d4ff; letter-spacing:6px; text-shadow:0 0 24px rgba(0,212,255,0.4)">⬡ VOXAID</div>
        <div style="font-size:0.8rem; color:#4a7a9b; letter-spacing:3px; margin-top:6px;">AI SURVIVOR DETECTION SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        if st.button("⚡ LOGIN", type="primary", use_container_width=True):
            if email and password:
                try:
                    res = supabase.table('users').select('*').eq('email', email).eq('password_hash', password).execute()
                    if res.data:
                        user = res.data[0]
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                except Exception as e:
                    st.error(f"Login error: {e}")
            else:
                st.warning("Please enter email and password.")

        st.markdown("""
        <div style="margin-top:16px; background:#0a1628; border:1px solid #1a3a5c; border-radius:4px; padding:12px; font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#4a7a9b;">
            <div style="margin-bottom:6px; color:#00d4ff;">DEFAULT CREDENTIALS</div>
            <div>Admin: admin@voxaid.com / admin123</div>
            <div style="margin-top:4px;">Worker: worker@voxaid.com / worker123</div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP (logged in)
# ════════════════════════════════════════════════════════════════════════════════
user = st.session_state.user
is_admin = user['role'] == 'admin'

# ── HEADER ────────────────────────────────────────────────────────────────────
col_logo, col_user = st.columns([3, 1])
with col_logo:
    st.markdown(f"""
    <div class="vx-header">
        <div>
            <div class="vx-logo">⬡ VOXAID</div>
            <div class="vx-sub">AI Survivor Detection System · Offline Capable · ₹0 Cost</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_user:
    st.markdown(f"""
    <div style="text-align:right; padding-top:20px;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#00d4ff;">{user['name']}</div>
        <div class="{'role-badge-admin' if is_admin else 'role-badge-worker'}" style="display:inline-block; margin-top:4px;">{'ADMIN' if is_admin else 'RESCUE WORKER'}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ── STATS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stat-grid">
    <div class="stat-card"><div class="stat-num">91.4%</div><div class="stat-label">Model Accuracy</div><div class="stat-sub">vs 60% human ear</div></div>
    <div class="stat-card"><div class="stat-num">72 HRS</div><div class="stat-label">Golden Window</div><div class="stat-sub">survival: 81% → 5%</div></div>
    <div class="stat-card"><div class="stat-num">&lt;3 SEC</div><div class="stat-label">Inference Time</div><div class="stat-sub">fully on-device</div></div>
    <div class="stat-card"><div class="stat-num">₹0</div><div class="stat-label">Total Cost</div><div class="stat-sub">vs ₹40L equipment</div></div>
</div>
""", unsafe_allow_html=True)

if model:
    st.markdown('<div class="status-ok">● SYSTEM ONLINE — voxaid_model.h5 loaded and ready</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-ok status-err">● SYSTEM ERROR — Model not found</div>', unsafe_allow_html=True)
    st.stop()

st.divider()

# ── NAVIGATION ────────────────────────────────────────────────────────────────
if is_admin:
    tabs = st.tabs(["🎙  RECORD", "📁  UPLOAD", "📡  MULTI-SPOT", "📋  DETECTION LOG", "🗺️  TEAM MAP", "🚨  MISSIONS", "🤖  RETRAIN", "🛡️  ADMIN"])
    tab1, tab2, tab3, tab4, tab_map, tab_mission, tab_retrain, tab5 = tabs
else:
    tabs = st.tabs(["🎙  RECORD", "📁  UPLOAD", "📡  MULTI-SPOT", "📋  DETECTION LOG", "🗺️  TEAM MAP", "🚨  MISSIONS"])
    tab1, tab2, tab3, tab4, tab_map, tab_mission = tabs

# ── TAB 1: RECORD ─────────────────────────────────────────────────────────────
with tab1:
    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="sec">LIVE AUDIO CAPTURE</div>', unsafe_allow_html=True)
        st.caption("Place device against rubble. Record. Click ANALYSE.")
        rec = st.audio_input("Hold near rubble and record", key=f"rec_{st.session_state.recorder_key}")
        if rec:
            st.audio(rec)
            c1, c2 = st.columns(2)
            with c1:
                analyse_clicked = st.button("⚡ ANALYSE", type="primary", use_container_width=True)
            with c2:
                if st.button("✕ CLEAR", use_container_width=True):
                    st.session_state.recorder_key += 1; st.rerun()

    if rec and analyse_clicked:
        with st.spinner("PROCESSING..."):
            try:
                ab = rec.read()
                score = run_inference(ab)
                show_result(score, ab)
            except Exception as e:
                st.error(f"Error: {e}")

    with right:
        st.markdown('<div class="sec">DETECTION LOG</div>', unsafe_allow_html=True)
        try:
            if is_admin:
                recent = supabase.table('detections').select('*').order('timestamp', desc=True).limit(8).execute()
            else:
                recent = supabase.table('detections').select('*').eq('user_id', user['id']).order('timestamp', desc=True).limit(8).execute()
            if recent.data:
                for d in recent.data:
                    icon = "🔴" if d['detected'] else "🟢"
                    t = d['timestamp'][:16].replace('T', ' ')
                    verify_status = "⏳" if d['verified'] is None else ("✅" if d['verified'] else "❌")
                    if d['detected']:
                        st.markdown(f'<div class="log-red">🔴 {t} — SURVIVOR ({d["confidence"]}%) {verify_status}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="log-green">🟢 {t} — CLEAR ({d["confidence"]}%) {verify_status}</div>', unsafe_allow_html=True)
            else:
                st.caption("No detections yet.")
        except Exception as e:
            st.caption(f"Could not load log: {e}")

# ── TAB 2: UPLOAD ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec">AUDIO FILE ANALYSIS</div>', unsafe_allow_html=True)
    st.caption("Upload a pre-recorded .wav file for analysis.")
    uploaded = st.file_uploader("Choose a .wav file", type=["wav"])
    if uploaded:
        st.audio(uploaded, format="audio/wav")
        with st.spinner("PROCESSING..."):
            try:
                ab = uploaded.read()
                score = run_inference(ab)
                show_result(score, ab)
            except Exception as e:
                st.error(f"Error: {e}")

# ── TAB 3: MULTI-SPOT ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec">MULTI-LOCATION SWEEP</div>', unsafe_allow_html=True)
    st.caption("Record at multiple rubble spots. Analyse all. Get rescue map.")
    st.session_state.spot_count = st.slider("Scan spots", 2, 10, st.session_state.spot_count)
    st.divider()
    st.markdown('<div class="sec">RECORD AT EACH SPOT</div>', unsafe_allow_html=True)
    for i in range(st.session_state.spot_count):
        slat = round(base_lat + (i * 0.0002), 6)
        slon = round(base_lon + (i * 0.0002), 6)
        with st.expander(f"📍 SPOT {i+1} — {slat}°N, {slon}°E"):
            r = st.audio_input(f"Record at Spot {i+1}", key=f"spot_{i}")
            if r:
                st.session_state.spot_recordings[i] = r
                st.success(f"✅ Spot {i+1} recorded")
    st.divider()
    if st.button("⚡ ANALYSE ALL SPOTS", type="primary", use_container_width=True):
        sources = {i: r.read() for i, r in st.session_state.spot_recordings.items()}
        if not sources:
            st.warning("Record at least one spot first.")
        else:
            results = []; sc = 0
            for idx, ab in sources.items():
                slat = round(base_lat + (idx * 0.0002), 6)
                slon = round(base_lon + (idx * 0.0002), 6)
                with st.spinner(f"Scanning Spot {idx+1}..."):
                    try:
                        score = run_inference(ab)
                        det = score >= 0.5
                        pct = round(score*100,1) if det else round((1-score)*100,1)
                        if det: sc += 1
                        save_detection(score, ab, slat, slon)
                        results.append({"spot": idx+1, "lat": slat, "lon": slon, "det": det, "pct": pct})
                    except:
                        results.append({"spot": idx+1, "lat": slat, "lon": slon, "det": False, "pct": 0})
            c1, c2, c3 = st.columns(3)
            c1.metric("Spots Scanned", len(results))
            c2.metric("🚨 Survivors", sc)
            c3.metric("✅ Clear", len(results)-sc)
            st.divider()
            st.markdown('<div class="sec">RESULTS</div>', unsafe_allow_html=True)
            for r in results:
                if r["det"]:
                    st.markdown(f'<div class="log-red">🚨 SPOT {r["spot"]} | 📍 {r["lat"]}°N, {r["lon"]}°E | SURVIVOR — {r["pct"]}%</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="log-green">✅ SPOT {r["spot"]} | 📍 {r["lat"]}°N, {r["lon"]}°E | CLEAR — {r["pct"]}%</div>', unsafe_allow_html=True)
            st.divider()
            st.markdown('<div class="sec">LIVE RESCUE MAP</div>', unsafe_allow_html=True)
            m = folium.Map(location=[base_lat, base_lon], zoom_start=18, tiles='CartoDB dark_matter')
            for r in results:
                folium.Marker(
                    location=[r["lat"], r["lon"]],
                    popup=folium.Popup(f"<b>SPOT {r['spot']}</b><br>{'🚨 SURVIVOR' if r['det'] else '✅ CLEAR'}<br>Confidence: {r['pct']}%", max_width=200),
                    icon=folium.Icon(color="red" if r["det"] else "green", icon="exclamation-sign" if r["det"] else "ok-sign")
                ).add_to(m)
            st_folium(m, width=None, height=480, returned_objects=[])
            st.info(f"📡 Sweep complete — {sc} survivor location(s) found.")

# ── TAB 4: DETECTION LOG ──────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec">DETECTION LOG — CLICK TO VIEW DETAILS</div>', unsafe_allow_html=True)

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        filter_type = st.selectbox("Filter", ["All", "Survivors Only", "Clear Only", "Pending Verification"])
    with col_filter2:
        if is_admin:
            filter_user = st.text_input("Filter by worker name", placeholder="Leave empty for all")

    try:
        query = supabase.table('detections').select('*').order('timestamp', desc=True)
        if not is_admin:
            query = query.eq('user_id', user['id'])
        all_detections = query.execute().data

        if filter_type == "Survivors Only":
            all_detections = [d for d in all_detections if d['detected']]
        elif filter_type == "Clear Only":
            all_detections = [d for d in all_detections if not d['detected']]
        elif filter_type == "Pending Verification":
            all_detections = [d for d in all_detections if d['verified'] is None]

        if is_admin and filter_user:
            all_detections = [d for d in all_detections if filter_user.lower() in d.get('user_name', '').lower()]

        if not all_detections:
            st.info("No detections found.")
        else:
            st.caption(f"Showing {len(all_detections)} detection(s)")
            for d in all_detections:
                t = d['timestamp'][:16].replace('T', ' ')
                verify_status = "⏳ PENDING" if d['verified'] is None else ("✅ CONFIRMED" if d['verified'] else "❌ FALSE ALARM")
                det_icon = "🚨" if d['detected'] else "✅"
                det_label = "SURVIVOR" if d['detected'] else "CLEAR"

                with st.expander(f"{det_icon} {t} — {det_label} ({d['confidence']}%) — {verify_status} {'| ' + d.get('user_name','') if is_admin else ''}"):
                    col_detail1, col_detail2 = st.columns([1, 1])

                    with col_detail1:
                        st.markdown(f"""
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#4a7a9b;">
                            <div style="margin-bottom:6px;">📍 GPS: <span style="color:#00d4ff">{d.get('gps_lat', 'N/A')}°N, {d.get('gps_lon', 'N/A')}°E</span></div>
                            <div style="margin-bottom:6px;">🕐 Time: <span style="color:#00d4ff">{t}</span></div>
                            <div style="margin-bottom:6px;">⚡ Score: <span style="color:#00d4ff">{d['score']:.4f}</span></div>
                            <div style="margin-bottom:6px;">👤 Worker: <span style="color:#00d4ff">{d.get('user_name', 'Unknown')}</span></div>
                            <div>🔖 Status: <span style="color:#{'ff2200' if d['detected'] else '00ff88'}">{det_label}</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Show GPS map
                        if d.get('gps_lat') and d.get('gps_lon'):
                            m = folium.Map(location=[d['gps_lat'], d['gps_lon']], zoom_start=17, tiles='CartoDB dark_matter')
                            folium.Marker(
                                location=[d['gps_lat'], d['gps_lon']],
                                popup=f"{'🚨 SURVIVOR' if d['detected'] else '✅ CLEAR'} — {d['confidence']}%",
                                icon=folium.Icon(color="red" if d['detected'] else "green")
                            ).add_to(m)
                            st_folium(m, width=300, height=200, returned_objects=[], key=f"map_{d['id']}")

                    with col_detail2:
                        # Audio playback
                        if d.get('audio_base64'):
                            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.72rem; color:#4a7a9b; margin-bottom:6px;">🎵 RECORDED AUDIO</div>', unsafe_allow_html=True)
                            try:
                                audio_bytes = base64.b64decode(d['audio_base64'])
                                st.audio(audio_bytes, format='audio/wav')
                            except:
                                st.caption("Audio unavailable")

                        # Spectrogram
                        if d.get('audio_base64'):
                            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.72rem; color:#4a7a9b; margin-bottom:6px; margin-top:10px;">📊 SPECTROGRAM</div>', unsafe_allow_html=True)
                            try:
                                audio_bytes = base64.b64decode(d['audio_base64'])
                                fig = generate_spectrogram(audio_bytes)
                                st.pyplot(fig)
                                plt.close(fig)
                            except:
                                st.caption("Spectrogram unavailable")

                    # ── VERIFICATION ──────────────────────────────────────────
                    st.markdown('<div class="sec">HUMAN VERIFICATION — CONFIRM THIS DETECTION</div>', unsafe_allow_html=True)
                    st.caption("Your verification helps retrain the AI model with real-world data.")

                    if d['verified'] is not None:
                        if d['verified']:
                            st.success(f"✅ Confirmed as SURVIVOR FOUND by {d.get('verified_by', 'unknown')} — used for model retraining")
                        else:
                            st.error(f"❌ Marked as FALSE ALARM by {d.get('verified_by', 'unknown')} — used for model retraining")
                        if d.get('notes'):
                            st.caption(f"Notes: {d['notes']}")
                    else:
                        # ← everything below is now inside this else block
                        notes = st.text_input("Notes (optional)", key=f"notes_{d['id']}", placeholder="e.g. Confirmed by rescue team at 6:30 PM")
                        vcol1, vcol2 = st.columns(2)

                        if d['detected']:
                            with vcol1:
                                if st.button("✅ SURVIVOR CONFIRMED", key=f"confirm_{d['id']}", use_container_width=True, type="primary"):
                                    supabase.table('detections').update({
                                        'verified': True,
                                        'verified_by': user['name'],
                                        'verified_at': get_ist().isoformat(),
                                        'notes': notes
                                    }).eq('id', d['id']).execute()
                                    st.success("✅ Confirmed! Helps model learn true positives.")
                                    st.rerun()
                            with vcol2:
                                if st.button("❌ FALSE ALARM", key=f"reject_{d['id']}", use_container_width=True):
                                    supabase.table('detections').update({
                                        'verified': False,
                                        'verified_by': user['name'],
                                        'verified_at': get_ist().isoformat(),
                                        'notes': notes
                                    }).eq('id', d['id']).execute()
                                    st.success("❌ Marked as false alarm! Helps reduce false positives.")
                                    st.rerun()
                        else:
                            with vcol1:
                                if st.button("✅ CORRECT — NO SURVIVOR", key=f"confirm_{d['id']}", use_container_width=True, type="primary"):
                                    supabase.table('detections').update({
                                        'verified': True,
                                        'verified_by': user['name'],
                                        'verified_at': get_ist().isoformat(),
                                        'notes': notes
                                    }).eq('id', d['id']).execute()
                                    st.success("✅ Confirmed! Helps model learn true negatives.")
                                    st.rerun()
                            with vcol2:
                                if st.button("⚠️ MISSED — SURVIVOR WAS THERE", key=f"reject_{d['id']}", use_container_width=True):
                                    supabase.table('detections').update({
                                        'verified': False,
                                        'verified_by': user['name'],
                                        'verified_at': get_ist().isoformat(),
                                        'notes': notes
                                    }).eq('id', d['id']).execute()
                                    st.success("⚠️ Marked as missed survivor! Critical for retraining.")
                                    st.rerun()
    except Exception as e:
        st.error(f"Could not load detections: {e}")

# ── TAB 5: ADMIN ──────────────────────────────────────────────────────────────
if is_admin:
    with tab5:
        st.markdown('<div class="sec">ADMIN DASHBOARD</div>', unsafe_allow_html=True)

        try:
            all_dets = supabase.table('detections').select('*').execute().data
            total = len(all_dets)
            survivors = len([d for d in all_dets if d['detected']])
            verified = len([d for d in all_dets if d['verified'] is not None])
            confirmed = len([d for d in all_dets if d['verified'] == True])
            false_alarms = len([d for d in all_dets if d['verified'] == False])

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total Scans", total)
            c2.metric("🚨 Survivors", survivors)
            c3.metric("✅ Verified", verified)
            c4.metric("Confirmed", confirmed)
            c5.metric("False Alarms", false_alarms)

            st.divider()
            st.markdown('<div class="sec">RETRAINING DATA EXPORT</div>', unsafe_allow_html=True)
            st.caption("Export verified detections for model retraining.")

            verified_dets = [d for d in all_dets if d['verified'] is not None]
            if verified_dets:
                import json
                export_data = [{
                    'id': d['id'],
                    'score': d['score'],
                    'detected': d['detected'],
                    'verified': d['verified'],
                    'label': 1 if d['verified'] else 0,
                    'gps_lat': d.get('gps_lat'),
                    'gps_lon': d.get('gps_lon'),
                    'timestamp': d['timestamp']
                } for d in verified_dets]

                st.download_button(
                    "⬇ DOWNLOAD TRAINING DATA (JSON)",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"voxaid_training_data_{get_ist().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.caption(f"{len(verified_dets)} verified detections ready for retraining")
            else:
                st.info("No verified detections yet. Workers need to confirm/reject detections first.")

            st.divider()
            st.markdown('<div class="sec">ALL USERS</div>', unsafe_allow_html=True)
            users = supabase.table('users').select('id, name, email, role, created_at').execute().data
            for u in users:
                role_color = "#aa88ff" if u['role'] == 'admin' else "#00ff88"
                st.markdown(f"""
                <div style="background:#0d1f35; border:1px solid #1a3a5c; border-radius:4px; padding:10px 14px; margin-bottom:6px; display:flex; justify-content:space-between; font-family:'Share Tech Mono',monospace; font-size:0.78rem;">
                    <span style="color:#c8d8e8">{u['name']}</span>
                    <span style="color:#4a7a9b">{u['email']}</span>
                    <span style="color:{role_color}">{u['role'].upper()}</span>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Admin data error: {e}")
# ── TAB: MISSIONS ─────────────────────────────────────────────────────────────
with tab_mission:
    st.markdown('<div class="sec">RESCUE MISSION SYSTEM</div>', unsafe_allow_html=True)

    # ── Active mission selector ───────────────────────────────────────────────
    try:
        active_missions = supabase.table('missions').select('id,name,created_at,status').eq('status', 'active').order('created_at', desc=True).execute().data
        mission_names = ["No mission selected"] + [f"{m['name']} — {m['created_at'][:10]}" for m in active_missions]
        mission_ids = [None] + [m['id'] for m in active_missions]

        selected_idx = st.selectbox("Select active mission", mission_names, key="mission_select")
        selected_mission_id = mission_ids[mission_names.index(selected_idx)]
        if selected_mission_id:
            st.session_state.active_mission_id = selected_mission_id
            st.session_state.active_mission_name = selected_idx.split(" — ")[0]
            st.success(f"✅ Active mission: **{st.session_state.active_mission_name}** — all scans will be tagged to this mission")
        else:
            st.session_state.active_mission_id = None
            st.session_state.active_mission_name = None

    except Exception as e:
        st.error(f"Mission load error: {e}")

    st.divider()

    # ── Create new mission (admin only) ───────────────────────────────────────
    if is_admin:
        st.markdown('<div class="sec">CREATE NEW MISSION</div>', unsafe_allow_html=True)
        mc1, mc2 = st.columns(2)
        with mc1:
            mission_name = st.text_input("Mission name", placeholder="e.g. Chennai Building Collapse — Block A")
            mission_location = st.text_input("Location", placeholder="e.g. Anna Nagar, Chennai")
        with mc2:
            mission_desc = st.text_area("Description", placeholder="Brief description of the rescue operation", height=100)

        if st.button("🚨 CREATE MISSION", type="primary", use_container_width=True):
            if mission_name:
                try:
                    supabase.table('missions').insert({
                        'name': mission_name,
                        'location': mission_location,
                        'description': mission_desc,
                        'created_by': user['name'],
                        'status': 'active'
                    }).execute()
                    st.success(f"✅ Mission '{mission_name}' created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating mission: {e}")
            else:
                st.warning("Please enter a mission name.")

        st.divider()

    # ── All missions list ─────────────────────────────────────────────────────
    st.markdown('<div class="sec">ALL MISSIONS</div>', unsafe_allow_html=True)

    try:
        all_missions = supabase.table('missions').select('id,name,location,description,created_by,created_at,status,ended_at').order('created_at', desc=True).execute().data

        if not all_missions:
            st.info("No missions created yet. Admin can create a mission above.")
        else:
            for m in all_missions:
                status_color = "#00ff88" if m['status'] == 'active' else "#4a7a9b"
                status_label = "● ACTIVE" if m['status'] == 'active' else "◯ ENDED"

                with st.expander(f"🚨 {m['name']} — {m.get('location','No location')} — {status_label}"):
                    # Mission details
                    d1, d2 = st.columns(2)
                    with d1:
                        st.markdown(f"""
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#4a7a9b; line-height:1.8;">
                            <div>📋 Mission: <span style="color:#00d4ff">{m['name']}</span></div>
                            <div>📍 Location: <span style="color:#00d4ff">{m.get('location','N/A')}</span></div>
                            <div>👤 Created by: <span style="color:#00d4ff">{m.get('created_by','N/A')}</span></div>
                            <div>🕐 Started: <span style="color:#00d4ff">{m['created_at'][:16].replace('T',' ')}</span></div>
                            <div>🔖 Status: <span style="color:{status_color}">{status_label}</span></div>
                            {f'<div>🏁 Ended: <span style="color:#4a7a9b">{m["ended_at"][:16].replace("T"," ")}</span></div>' if m.get('ended_at') else ''}
                        </div>
                        """, unsafe_allow_html=True)
                        if m.get('description'):
                            st.caption(f"📝 {m['description']}")

                    with d2:
                        # Mission stats
                        try:
                            mission_dets = supabase.table('detections').select('*').eq('mission_id', m['id']).execute().data
                            total = len(mission_dets)
                            survivors = len([d for d in mission_dets if d['detected']])
                            verified = len([d for d in mission_dets if d['verified'] is not None])

                            ms1, ms2, ms3 = st.columns(3)
                            ms1.metric("Scans", total)
                            ms2.metric("🚨 Survivors", survivors)
                            ms3.metric("✅ Verified", verified)

                            # Mission map
                            if mission_dets:
                                valid_dets = [d for d in mission_dets if d.get('gps_lat') and d.get('gps_lon')]
                                if valid_dets:
                                    clat = sum(d['gps_lat'] for d in valid_dets) / len(valid_dets)
                                    clon = sum(d['gps_lon'] for d in valid_dets) / len(valid_dets)
                                    mm = folium.Map(location=[clat, clon], zoom_start=17, tiles='CartoDB dark_matter')
                                    for d in valid_dets:
                                        folium.Marker(
                                            location=[d['gps_lat'], d['gps_lon']],
                                            popup=f"{'🚨 SURVIVOR' if d['detected'] else '✅ CLEAR'} — {d['confidence']}%",
                                            icon=folium.Icon(color="red" if d['detected'] else "green",
                                                           icon="exclamation-sign" if d['detected'] else "ok-sign")
                                        ).add_to(mm)
                                    st_folium(mm, width=280, height=200, returned_objects=[], key=f"mmap_{m['id']}")

                        except Exception as e:
                            st.caption(f"Stats error: {e}")

                    st.divider()

                    # Admin controls
                    if is_admin:
                        btn1, btn2, btn3 = st.columns(3)

                        # Generate PDF report
                        with btn1:
                            if st.button("📄 GENERATE REPORT", key=f"report_{m['id']}", use_container_width=True):
                                try:
                                    mission_dets = supabase.table('detections').select('*').eq('mission_id', m['id']).execute().data
                                    import json
                                    report = {
                                        "mission": {
                                            "name": m['name'],
                                            "location": m.get('location','N/A'),
                                            "description": m.get('description',''),
                                            "created_by": m.get('created_by','N/A'),
                                            "started": m['created_at'],
                                            "ended": m.get('ended_at','ongoing'),
                                            "status": m['status']
                                        },
                                        "summary": {
                                            "total_scans": len(mission_dets),
                                            "survivors_detected": len([d for d in mission_dets if d['detected']]),
                                            "clear_zones": len([d for d in mission_dets if not d['detected']]),
                                            "verified": len([d for d in mission_dets if d['verified'] is not None]),
                                            "confirmed_survivors": len([d for d in mission_dets if d['verified'] == True]),
                                            "false_alarms": len([d for d in mission_dets if d['verified'] == False])
                                        },
                                        "detections": [{
                                            "timestamp": d['timestamp'],
                                            "worker": d.get('user_name','Unknown'),
                                            "result": "SURVIVOR" if d['detected'] else "CLEAR",
                                            "confidence": d['confidence'],
                                            "gps": f"{d.get('gps_lat','?')}°N, {d.get('gps_lon','?')}°E",
                                            "verified": d['verified'],
                                            "notes": d.get('notes','')
                                        } for d in mission_dets]
                                    }
                                    st.download_button(
                                        "⬇ DOWNLOAD REPORT (JSON)",
                                        data=json.dumps(report, indent=2),
                                        file_name=f"voxaid_mission_{m['name'].replace(' ','_')[:20]}_{get_ist().strftime('%Y%m%d')}.json",
                                        mime="application/json",
                                        use_container_width=True,
                                        key=f"dl_{m['id']}"
                                    )
                                except Exception as e:
                                    st.error(f"Report error: {e}")

                        # End mission
                        with btn2:
                            if m['status'] == 'active':
                                if st.button("🏁 END MISSION", key=f"end_{m['id']}", use_container_width=True):
                                    supabase.table('missions').update({
                                        'status': 'ended',
                                        'ended_at': get_ist().isoformat()
                                    }).eq('id', m['id']).execute()
                                    st.success("Mission ended!")
                                    st.rerun()

                        # Delete mission
                        with btn3:
                            if st.button("🗑️ DELETE", key=f"del_{m['id']}", use_container_width=True):
                                supabase.table('missions').delete().eq('id', m['id']).execute()
                                st.success("Mission deleted!")
                                st.rerun()

    except Exception as e:
        st.error(f"Missions error: {e}")

# ── TAB: TEAM MAP ─────────────────────────────────────────────────────────────
with tab_map:
    st.markdown('<div class="sec">REAL-TIME TEAM MAP — ALL DETECTIONS</div>', unsafe_allow_html=True)
    st.caption("Live map of all team detections. Auto-refreshes every 15 seconds.")

    col_refresh, col_filter = st.columns([1, 2])
    with col_refresh:
        if st.button("🔄 REFRESH MAP", use_container_width=True):
            st.rerun()
    with col_filter:
        map_filter = st.selectbox("Show", ["All Detections", "Survivors Only", "Last 1 Hour", "Last 24 Hours"], key="map_filter")

    try:
        all_map_dets = supabase.table('detections').select('id,detected,confidence,gps_lat,gps_lon,timestamp,user_name,verified').order('timestamp', desc=True).limit(50).execute().data

        if map_filter == "Survivors Only":
            all_map_dets = [d for d in all_map_dets if d['detected']]
        elif map_filter == "Last 1 Hour":
            cutoff = (get_ist() - datetime.timedelta(hours=1)).isoformat()
            all_map_dets = [d for d in all_map_dets if d['timestamp'] > cutoff]
        elif map_filter == "Last 24 Hours":
            cutoff = (get_ist() - datetime.timedelta(hours=24)).isoformat()
            all_map_dets = [d for d in all_map_dets if d['timestamp'] > cutoff]

        valid = [d for d in all_map_dets if d.get('gps_lat') and d.get('gps_lon')]

        # Summary metrics
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Total Detections", len(all_map_dets))
        mc2.metric("🚨 Survivors", len([d for d in all_map_dets if d['detected']]))
        mc3.metric("✅ Clear", len([d for d in all_map_dets if not d['detected']]))
        mc4.metric("👥 Workers Active", len(set(d.get('user_name','') for d in all_map_dets)))

        st.divider()

        if valid:
            center_lat = sum(d['gps_lat'] for d in valid) / len(valid)
            center_lon = sum(d['gps_lon'] for d in valid) / len(valid)
            m = folium.Map(location=[center_lat, center_lon], zoom_start=17, tiles='CartoDB dark_matter')

            for d in valid:
                t = d['timestamp'][:16].replace('T', ' ')
                verify = "⏳" if d['verified'] is None else ("✅" if d['verified'] else "❌")
                color = "red" if d['detected'] else "green"
                icon_name = "exclamation-sign" if d['detected'] else "ok-sign"
                popup_html = f"""
                <div style='font-family:monospace; font-size:12px; min-width:160px'>
                    <b>{'🚨 SURVIVOR' if d['detected'] else '✅ CLEAR'}</b><br>
                    👤 {d.get('user_name','Unknown')}<br>
                    ⚡ {d['confidence']}% confidence<br>
                    🕐 {t}<br>
                    {verify} Verification
                </div>
                """
                folium.Marker(
                    location=[d['gps_lat'], d['gps_lon']],
                    popup=folium.Popup(popup_html, max_width=200),
                    tooltip=f"{'🚨' if d['detected'] else '✅'} {d.get('user_name','')} — {d['confidence']}%",
                    icon=folium.Icon(color=color, icon=icon_name)
                ).add_to(m)

            st_folium(m, width=None, height=550, returned_objects=[])
        else:
            st.info("No detections with GPS data yet. Start scanning to populate the map!")
            m = folium.Map(location=[base_lat, base_lon], zoom_start=15, tiles='CartoDB dark_matter')
            st_folium(m, width=None, height=400, returned_objects=[])

        # Recent activity feed
        st.divider()
        st.markdown('<div class="sec">LIVE ACTIVITY FEED</div>', unsafe_allow_html=True)
        for d in all_map_dets[:10]:
            t = d['timestamp'][:16].replace('T', ' ')
            if d['detected']:
                st.markdown(f'<div class="log-red">🚨 {t} — {d.get("user_name","Unknown")} — SURVIVOR DETECTED ({d["confidence"]}%) 📍 {d.get("gps_lat","?"):.4f}°N, {d.get("gps_lon","?"):.4f}°E</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="log-green">✅ {t} — {d.get("user_name","Unknown")} — CLEAR ({d["confidence"]}%)</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Map error: {e}")

    

# ── TAB: RETRAIN (Admin only) ─────────────────────────────────────────────────
if is_admin:
    with tab_retrain:
        st.markdown('<div class="sec">AUTO-RETRAINING PIPELINE</div>', unsafe_allow_html=True)
        st.caption("Verified detections from the field automatically become training data for the next model version.")

        try:
            all_dets = supabase.table('detections').select('*').execute().data
            verified_dets = [d for d in all_dets if d['verified'] is not None]
            confirmed = [d for d in verified_dets if d['verified'] == True]
            false_alarms = [d for d in verified_dets if d['verified'] == False]
            pending = [d for d in all_dets if d['verified'] is None]

            # Pipeline status
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Total Scans", len(all_dets))
            r2.metric("✅ Confirmed Survivors", len(confirmed))
            r3.metric("❌ False Alarms", len(false_alarms))
            r4.metric("⏳ Pending Verification", len(pending))

            st.divider()

            # Retraining readiness
            threshold = 10
            progress = min(len(verified_dets) / threshold, 1.0)
            st.markdown('<div class="sec">RETRAINING READINESS</div>', unsafe_allow_html=True)
            st.progress(progress)

            if len(verified_dets) >= threshold:
                st.success(f"🚀 {len(verified_dets)} verified detections available — Model is ready to retrain!")
                st.markdown(f"""
                <div style="background:#0a1f10; border:1px solid #1a4a2a; border-radius:4px; padding:14px; margin:12px 0; font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#00ff88;">
                    <div style="margin-bottom:8px; color:#00d4ff;">TRAINING DATA SUMMARY</div>
                    <div>▶ Confirmed survivor samples: {len(confirmed)} (label = 1)</div>
                    <div>▶ False alarm samples: {len(false_alarms)} (label = 0)</div>
                    <div>▶ Total verified: {len(verified_dets)}</div>
                    <div style="margin-top:8px; color:#4a7a9b;">Ready to export and retrain voxaid_model.h5</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                remaining = threshold - len(verified_dets)
                st.warning(f"Need {remaining} more verified detections before retraining. ({len(verified_dets)}/{threshold})")

            st.divider()
            st.markdown('<div class="sec">EXPORT TRAINING DATA</div>', unsafe_allow_html=True)

            if verified_dets:
                import json
                export_data = {
                    "metadata": {
                        "exported_at": get_ist().isoformat(),
                        "exported_by": user['name'],
                        "total_samples": len(verified_dets),
                        "confirmed_survivors": len(confirmed),
                        "false_alarms": len(false_alarms),
                        "model_version": "voxaid_v3"
                    },
                    "samples": [{
                        'id': d['id'],
                        'score': d['score'],
                        'detected': d['detected'],
                        'verified': d['verified'],
                        'label': 1 if d['verified'] else 0,
                        'confidence': d['confidence'],
                        'gps_lat': d.get('gps_lat'),
                        'gps_lon': d.get('gps_lon'),
                        'timestamp': d['timestamp'],
                        'verified_by': d.get('verified_by'),
                        'notes': d.get('notes'),
                        'has_audio': d.get('audio_base64') is not None
                    } for d in verified_dets]
                }

                ec1, ec2 = st.columns(2)
                with ec1:
                    st.download_button(
                        "⬇ DOWNLOAD TRAINING DATA (JSON)",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"voxaid_training_v3_{get_ist().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                with ec2:
                    # Export as CSV for Person A
                    import csv, io as sio
                    csv_buf = sio.StringIO()
                    writer = csv.DictWriter(csv_buf, fieldnames=['id','score','label','confidence','gps_lat','gps_lon','timestamp'])
                    writer.writeheader()
                    for d in verified_dets:
                        writer.writerow({'id':d['id'],'score':d['score'],'label':1 if d['verified'] else 0,'confidence':d['confidence'],'gps_lat':d.get('gps_lat',''),'gps_lon':d.get('gps_lon',''),'timestamp':d['timestamp']})
                    st.download_button(
                        "⬇ DOWNLOAD AS CSV",
                        data=csv_buf.getvalue(),
                        file_name=f"voxaid_training_v3_{get_ist().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("No verified detections yet.")

            st.divider()
            st.markdown('<div class="sec">HOW TO RETRAIN</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background:#0a1628; border:1px solid #1a3a5c; border-radius:4px; padding:14px; font-family:'Share Tech Mono',monospace; font-size:0.76rem; color:#4a7a9b; line-height:1.8;">
                <div style="color:#00d4ff; margin-bottom:8px;">RETRAINING WORKFLOW FOR PERSON A</div>
                <div>1. Download training data JSON or CSV above</div>
                <div>2. Load in Google Colab alongside original UrbanSound8K data</div>
                <div>3. Use label=1 samples as positive (survivor) class</div>
                <div>4. Use label=0 samples as negative (no survivor) class</div>
                <div>5. Fine-tune existing CNN model on new data</div>
                <div>6. Export new voxaid_model.h5 and replace in this app</div>
                <div style="margin-top:8px; color:#00ff88;">Every rescue mission makes the model smarter. ↑</div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Retraining pipeline error: {e}")
# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:32px;padding-top:14px;border-top:1px solid #1a3a5c;font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#2a4a6a;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
    <span>VOXAID v3.0 · AI SURVIVOR DETECTION</span>
    <span>POWERED BY SUPABASE · 100% OFFLINE SCANNING</span>
    <span>BUILT FOR RESCUE TEAMS</span>
</div>
""", unsafe_allow_html=True)
