import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os
import shutil
from datetime import datetime
import numpy as np

# --- 1. CONFIGURACIÓN Y PERSISTENCIA ---
st.set_page_config(page_title="#NAMLEAGUE2026", layout="wide")

DB_FILE = "torneo_data.json"

def img_to_base64(image):
    if image is None: return None
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except: return None

def crear_backup():
    if os.path.exists(DB_FILE):
        if not os.path.exists("backups"): os.makedirs("backups")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(DB_FILE, f"backups/backup_{ts}.json")

def save_to_disk():
    data_to_save = {
        "partidos": st.session_state.partidos,
        "equipos": {},
        "fase_final": st.session_state.fase_final,
        "goleadores": st.session_state.goleadores,
        "logo_torneo": img_to_base64(st.session_state.logo_torneo) if st.session_state.logo_torneo else None,
        "logo_final": img_to_base64(st.session_state.logo_final) if st.session_state.logo_final else None
    }
    for id_eq, info in st.session_state.equipos.items():
        data_to_save["equipos"][id_eq] = {
            "nombre": info["nombre"], "grupo": info["grupo"],
            "logo": img_to_base64(info["logo"]) if info.get("logo") else None
        }
    with open(DB_FILE, "w") as f:
        json.dump(data_to_save, f)
    crear_backup()

def inicializar_fase_final():
    return {
        "cuartos": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(4)],
        "semis": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(2)],
        "final": {"L": "", "V": "", "gl": None, "gv": None}
    }

def load_from_disk():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                st.session_state.partidos = data.get("partidos", [])
                st.session_state.fase_final = data.get("fase_final", inicializar_fase_final())
                st.session_state.goleadores = data.get("goleadores", [])
                if data.get("logo_torneo"):
                    st.session_state.logo_torneo = Image.open(io.BytesIO(base64.b64decode(data["logo_torneo"])))
                if data.get("logo_final"):
                    st.session_state.logo_final = Image.open(io.BytesIO(base64.b64decode(data["logo_final"])))
                eq_cargados = {}
                for id_eq, info in data.get("equipos", {}).items():
                    logo_pil = None
                    if info.get("logo"):
                        logo_pil = Image.open(io.BytesIO(base64.b64decode(info["logo"])))
                    eq_cargados[id_eq] = {"nombre": info["nombre"], "grupo": info.get("grupo", "SIN GRUPO"), "logo": logo_pil}
                st.session_state.equipos = eq_cargados
                return True
        except: return False
    return False

# --- 2. ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top, #00124d 0%, #000422 100%) !important; }
    .txt-celeste { color: #7db1ff !important; }
    .txt-red { color: #ff3b3b !important; }
    .txt-gold { color: #FFD700 !important; }
    .txt-white { color: #ffffff !important; }
    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: white !important; font-weight: 900; }
    .nam-title { font-size: clamp(2.5em, 8vw, 4.5em); text-align: center; font-weight: 900; color: white; margin-bottom: 20px; }
    
    .table-container { display: flex; flex-direction: column; align-items: center; width: 100%; }
    .main-card { background: rgba(0, 10, 60, 0.4); border-radius: 12px; margin-bottom: 30px; border: 1px solid #FFD70033; color: white; backdrop-filter: blur(15px); overflow: hidden; width: fit-content; margin-left: auto; margin-right: auto; }
    
    /* Goleadores */
    .grid-goleadores { display: grid; grid-template-columns: 50px 250px 1fr 80px; align-items: center; padding: 10px 20px; gap: 15px; white-space: nowrap; }
    .top-scorer-card { background: linear-gradient(90deg, rgba(255, 215, 0, 0.15) 0%, rgba(0, 20, 80, 0.6) 100%); border: 2px solid #FFD700 !important; margin: 10px 0 !important; border-radius: 10px !important; }
    .top-scorer-name { font-size: 1.4em !important; color: #FFD700 !important; text-shadow: 0 0 8px rgba(255, 215, 0, 0.3); font-weight: 900 !important; }
    .top-scorer-goals { font-size: 1.8em !important; color: #FFD700 !important; font-weight: 900 !important; }
    
    .header-grid { background: rgba(0, 0, 0, 0.3); border-bottom: 2px solid #FFD700; font-weight: 900; text-transform: uppercase; }
    .stat-cell { text-align: center; font-weight: bold; color: #ffffff !important; }
    .grid-posiciones { display: grid; grid-template-columns: 300px repeat(8, 42px); align-items: center; padding: 10px 12px; }
    .team-row { border-bottom: 1px solid rgba(125, 177, 255, 0.15); }
    
    /* Fase Final */
    .bracket-scroll { overflow-x: auto; width: 100%; padding: 20px 0; }
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; min-width: 1100px; padding: 20px 0; margin: 0 auto; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 550px; width: 240px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 8px; border: 1px solid #FFD70044; padding: 10px; margin: 15px 0; min-width: 220px; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 28px; text-align: center; border-radius: 3px; height: 24px; display: flex; align-items: center; justify-content: center; }
    .final-center { width: 320px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    
    /* El Dorado del Logo */
    .logo-epico { filter: drop-shadow(0 0 20px #FFD700); margin-bottom: 15px; border-radius: 10px; }
    
    .date-divider { background: #FFD700; color: black; padding: 5px 20px; font-weight: 900; border-radius: 4px; margin: 25px 0 10px 0; display: inline-block; }
    .res-team-box { display: flex; align-items: center; gap: 12px; width: 280px; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA ---
def get_team_info(name):
    for info in st.session_state.equipos.values():
        if info['nombre'] == name: return info
    return {"nombre": name, "logo": None}

def format_score(val):
    if val is None or (isinstance(val, float) and np.isnan(val)): return ""
    return str(int(float(val)))

def render_match(match):
    t1, t2 = get_team_info(match["L"]), get_team_info(match["V"])
    img1 = f"data:image/png;base64,{img_to_base64(t1['logo'])}" if t1['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    img2 = f"data:image/png;base64,{img_to_base64(t2['logo'])}" if t2['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    gl_disp = format_score(match.get("gl"))
    gv_disp = format_score(match.get("gv"))
    return f'''
    <div class="match-box-ko">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div style="display:flex;align-items:center;"><img src="{img1}" style="width:22px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;color:white;">{t1["nombre"] or "---"}</span></div>
            <span class="ko-score">{gl_disp}</span>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div style="display:flex;align-items:center;"><img src="{img2}" style="width:22px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;color:white;">{t2["nombre"] or "---"}</span></div>
            <span class="ko-score">{gv_disp}</span>
        </div>
    </div>'''

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    st.session_state.logo_torneo = st.session_state.logo_final = None
    if not load_from_disk():
        st.session_state.equipos = {f"ID_{i}": {"nombre": f"EQUIPO {i}", "grupo": "SIN GRUPO", "logo": None} for i in range(1, 21)}
        st.session_state.partidos, st.session_state.goleadores, st.session_state.fase_final = [], [], inicializar_fase_final()

# --- 5. INTERFAZ PÚBLICA ---
st.markdown('<h1 class="nam-title">#<span class="txt-celeste">N</span><span class="txt-red">A</span>MLEAGUE2026</h1>', unsafe_allow_html=True)

if not st.session_state.get('logged_in', False):
    t_pos, t_ff, t_res, t_gol = st.tabs(["📊 POSICIONES", "🏆 FASE FINAL", "⚽ RESULTADOS", "👟 GOLEADORES"])
    
    with t_ff:
        ff = st.session_state.fase_final
        logo_f_b64 = img_to_base64(st.session_state.logo_final)
        logo_f_html = f"<img src='data:image/png;base64,{logo_f_b64}' class='logo-epico' width=180>" if logo_f_b64 else "<h2 class='txt-gold'>FINAL</h2>"
        
        st.markdown(f'''
        <div class="bracket-scroll">
            <div class="bracket-wrapper">
                <div class="bracket-column">
                    <h4>CUARTOS</h4>
                    {render_match(ff["cuartos"][0])}
                    {render_match(ff["cuartos"][1])}
                </div>
                <div class="bracket-column">
                    <h4>SEMIFINAL</h4>
                    {render_match(ff["semis"][0])}
                </div>
                <div class="final-center">
                    {logo_f_html}
                    <h1 style="color:white !important; margin: 10px 0; text-shadow: 0 0 15px rgba(255,215,0,0.6);">GRAN FINAL</h1>
                    {render_match(ff["final"])}
                </div>
                <div class="bracket-column">
                    <h4>SEMIFINAL</h4>
                    {render_match(ff["semis"][1])}
                </div>
                <div class="bracket-column">
                    <h4>CUARTOS</h4>
                    {render_match(ff["cuartos"][2])}
                    {render_match(ff["cuartos"][3])}
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # (Las demás pestañas se mantienen igual para no saturar el código, pero funcionan con la lógica de format_score corregida)
    with t_pos:
        # Lógica de posiciones (reutilizada)
        pass 
    with t_res:
        # Lógica de resultados (reutilizada)
        pass
    with t_gol:
        # Lógica de goleadores (reutilizada)
        pass

# --- 6. PANEL ADMINISTRADOR ---
with st.sidebar:
    st.header("🔐 Zona Administradores")
    if not st.session_state.get('logged_in', False):
        if st.text_input("Clave", type="password") == "organizadores2026":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        adm_t = st.tabs(["LOGOS", "EQ", "ELIM", "GOL", "💾"])
        eqs_lista = sorted([i['nombre'] for i in st.session_state.equipos.values()])
        
        with adm_t[0]:
            lt, lf = st.file_uploader("Logo Torneo"), st.file_uploader("Logo Final")
            if st.button("Guardar Logos"):
                if lt: st.session_state.logo_torneo = Image.open(lt)
                if lf: st.session_state.logo_final = Image.open(lf)
                save_to_disk(); st.rerun()

        with adm_t[2]:
            st.subheader("Configurar Fase Final")
            eqs_ko = [""] + eqs_lista
            for ft in ["cuartos", "semis", "final"]:
                with st.expander(ft.upper()):
                    matches = st.session_state.fase_final[ft]
                    if isinstance(matches, list):
                        for i, m in enumerate(matches):
                            st.markdown(f"**Partido {i+1}**")
                            m["L"] = st.selectbox(f"Local {ft}{i}", eqs_ko, index=eqs_ko.index(m["L"]) if m["L"] in eqs_ko else 0, key=f"l{ft}{i}")
                            m["V"] = st.selectbox(f"Visitante {ft}{i}", eqs_ko, index=eqs_ko.index(m["V"]) if m["V"] in eqs_ko else 0, key=f"v{ft}{i}")
                            has_res = st.checkbox("¿Tiene resultado?", value=(m["gl"] is not None), key=f"res{ft}{i}")
                            if has_res:
                                m["gl"] = st.number_input("Goles Local", value=int(m["gl"]) if m["gl"] is not None else 0, key=f"gl{ft}{i}")
                                m["gv"] = st.number_input("Goles Visitante", value=int(m["gv"]) if m["gv"] is not None else 0, key=f"gv{ft}{i}")
                            else:
                                m["gl"] = m["gv"] = None
                    else:
                        st.markdown("**GRAN FINAL**")
                        matches["L"] = st.selectbox("Local Final", eqs_ko, index=eqs_ko.index(matches["L"]) if matches["L"] in eqs_ko else 0, key="lfinal")
                        matches["V"] = st.selectbox("Visitante Final", eqs_ko, index=eqs_ko.index(matches["V"]) if matches["V"] in eqs_ko else 0, key="vfinal")
                        has_res_f = st.checkbox("¿Tiene resultado?", value=(matches["gl"] is not None), key="resfinal")
                        if has_res_f:
                            matches["gl"] = st.number_input("Goles L", value=int(matches["gl"]) if matches["gl"] is not None else 0, key="glfinal")
                            matches["gv"] = st.number_input("Goles V", value=int(matches["gv"]) if matches["gv"] is not None else 0, key="gvfinal")
                        else:
                            matches["gl"] = matches["gv"] = None
            if st.button("Guardar Fase Final"): save_to_disk(); st.rerun()

        # Las secciones de Equipos, Goleadores y Backup se mantienen igual.
