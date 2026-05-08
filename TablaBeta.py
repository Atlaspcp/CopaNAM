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
    .grid-goleadores { display: grid; grid-template-columns: 50px 250px 1fr 80px; align-items: center; padding: 12px 20px; gap: 15px; white-space: nowrap; }
    .top-scorer-card { background: linear-gradient(90deg, rgba(255, 215, 0, 0.15) 0%, rgba(0, 20, 80, 0.6) 100%); border: 2px solid #FFD700 !important; margin: 10px 0 !important; border-radius: 10px !important; }
    .top-scorer-name { font-size: 1.4em !important; color: #FFD700 !important; text-shadow: 0 0 8px rgba(255, 215, 0, 0.3); font-weight: 900 !important; }
    .top-scorer-goals { font-size: 1.8em !important; color: #FFD700 !important; font-weight: 900 !important; }
    
    /* Fase Final */
    .bracket-scroll { overflow-x: auto; width: 100%; padding: 20px 0; }
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; min-width: 1150px; padding: 20px 0; margin: 0 auto; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 550px; width: 240px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 8px; border: 1px solid #FFD70044; padding: 10px; margin: 15px 0; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 30px; height: 26px; text-align: center; border-radius: 3px; display: flex; align-items: center; justify-content: center; }
    .final-center { width: 340px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .logo-epico { filter: drop-shadow(0 0 20px #FFD700); margin-bottom: 10px; }
    
    /* Tablas y Resultados */
    .header-grid { background: rgba(0, 0, 0, 0.3); border-bottom: 2px solid #FFD700; font-weight: 900; text-transform: uppercase; }
    .stat-cell { text-align: center; font-weight: bold; color: #ffffff !important; }
    .grid-posiciones { display: grid; grid-template-columns: 300px repeat(8, 42px); align-items: center; padding: 10px 12px; }
    .team-row { border-bottom: 1px solid rgba(125, 177, 255, 0.15); }
    .date-divider { background: #FFD700; color: black; padding: 5px 20px; font-weight: 900; border-radius: 4px; margin: 25px 0 10px 0; display: inline-block; }
    .res-team-box { display: flex; align-items: center; gap: 12px; width: 280px; white-space: nowrap; }
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
            <div style="display:flex;align-items:center;"><img src="{img1}" style="width:22px;margin-right:8px;"><span style="font-size:0.85em;font-weight:700;color:white;">{t1["nombre"] or "---"}</span></div>
            <span class="ko-score">{gl_disp}</span>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div style="display:flex;align-items:center;"><img src="{img2}" style="width:22px;margin-right:8px;"><span style="font-size:0.85em;font-weight:700;color:white;">{t2["nombre"] or "---"}</span></div>
            <span class="ko-score">{gv_disp}</span>
        </div>
    </div>'''

def calcular_tablas():
    stats = {info['nombre']: {"nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']} for info in st.session_state.equipos.values() if info['grupo'] != "SIN GRUPO"}
    for p in st.session_state.partidos:
        gl_v, gv_v = p.get('goles_l'), p.get('goles_v')
        if gl_v is not None and not (isinstance(gl_v, float) and np.isnan(gl_v)):
            l, v = p['local'], p['visitante']
            if l in stats and v in stats:
                gl, gv = int(float(gl_v)), int(float(gv_v))
                stats[l]["PJ"] += 1; stats[v]["PJ"] += 1
                stats[l]["GF"] += gl; stats[l]["GC"] += gv
                stats[v]["GF"] += gv; stats[v]["GC"] += gl
                stats[l]["DG"] = stats[l]["GF"] - stats[l]["GC"]
                stats[v]["DG"] = stats[v]["GF"] - stats[v]["GC"]
                if gl > gv: stats[l]["G"] += 1; stats[l]["PTS"] += 3; stats[v]["P"] += 1
                elif gv > gl: stats[v]["G"] += 1; stats[v]["PTS"] += 3; stats[l]["P"] += 1
                else: stats[l]["E"] += 1; stats[l]["PTS"] += 1; stats[v]["E"] += 1; stats[v]["PTS"] += 1
    return stats

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
    
    with t_pos:
        stats_data = calcular_tablas()
        grupos_activos = sorted(list(set(eq['grupo'] for eq in stats_data.values() if eq['grupo'] != "SIN GRUPO")))
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        for g in grupos_activos:
            eq_g = sorted([s for s in stats_data.values() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG'], x['GF']), reverse=True)
            html = f'<div class="main-card"><div class="grid-posiciones header-grid"><span style="color:#FFD700">GRUPO {g}</span><span class="stat-cell">PJ</span><span class="stat-cell">G</span><span class="stat-cell">E</span><span class="stat-cell">P</span><span class="stat-cell">GF</span><span class="stat-cell">GC</span><span class="stat-cell">DG</span><span class="stat-cell">PTS</span></div>'
            for eq in eq_g:
                img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html += f'<div class="grid-posiciones team-row"><div style="display:flex;align-items:center;gap:8px;"><img src="{img}" width="24"><span style="font-weight:700;">{eq["nombre"]}</span></div><span class="stat-cell">{eq["PJ"]}</span><span class="stat-cell">{eq["G"]}</span><span class="stat-cell">{eq["E"]}</span><span class="stat-cell">{eq["P"]}</span><span class="stat-cell">{eq["GF"]}</span><span class="stat-cell">{eq["GC"]}</span><span class="stat-cell">{eq["DG"]}</span><span class="pts-cell">{eq["PTS"]}</span></div>'
            st.markdown(html + '</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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

    with t_res:
        if st.session_state.partidos:
            df = pd.DataFrame(st.session_state.partidos)
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for f in sorted(df['fecha'].unique(), reverse=True):
                st.markdown(f'<div class="date-divider">{f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                html_res = '<div class="main-card" style="min-width: 720px;">'
                for _, p in df[df['fecha'] == f].iterrows():
                    s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    res_l, res_v = format_score(p["goles_l"]), format_score(p["goles_v"])
                    sep = "-" if (res_l != "" or res_v != "") else "VS"
                    html_res += f'''
                    <div style="display:flex; align-items:center; justify-content:center; padding:15px 30px; border-bottom:1px solid #ffffff11; gap:20px;">
                        <div class="res-team-box" style="justify-content: flex-end;">
                            <span style="font-weight:700; text-align: right; overflow:hidden;">{p["local"]}</span>
                            <img src="{s_l}" width="24">
                        </div>
                        <div style="width:100px; text-align:center; color:#FFD700; font-weight:900; font-size:1.4em;">
                            {res_l} {sep} {res_v}
                        </div>
                        <div class="res-team-box" style="justify-content: flex-start;">
                            <img src="{s_v}" width="24">
                            <span style="font-weight:700; text-align: left; overflow:hidden;">{p["visitante"]}</span>
                        </div>
                    </div>'''
                st.markdown(html_res + '</div></div>', unsafe_allow_html=True)

    with t_gol:
        if st.session_state.goleadores:
            gols = sorted(st.session_state.goleadores, key=lambda x: int(x.get('goles', 0)), reverse=True)
            logo_map = {info['nombre']: info['logo'] for info in st.session_state.equipos.values()}
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            html_gol = f'<div class="main-card" style="min-width: 820px;"><div class="grid-goleadores header-grid"><span></span><span class="txt-white">EQUIPO</span><span class="txt-gold">JUGADOR</span><span class="stat-cell">GOLES</span></div>'
            for idx, g in enumerate(gols):
                team_logo = logo_map.get(g["equipo"])
                img_str = f"data:image/png;base64,{img_to_base64(team_logo)}" if team_logo else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                is_top = "top-scorer-card" if idx == 0 else ""
                html_gol += f'''
                <div class="grid-goleadores {is_top}" style="border-bottom:1px solid #ffffff10;">
                    <div style="display:flex; justify-content:center; align-items:center;">
                        <img src="{img_str}" style="width: {"40px" if idx==0 else "30px"}; object-fit: contain;">
                    </div>
                    <span style="color:#7db1ff; font-weight:{"900" if idx==0 else "400"}; overflow:hidden;">{g["equipo"]}</span>
                    <span class="{"top-scorer-name" if idx==0 else ""}" style="overflow:hidden;">{g["nombre"]}</span>
                    <span class="{"top-scorer-goals" if idx==0 else "stat-cell"}" style="text-align:center;">{g["goles"]}</span>
                </div>'''
            st.markdown(html_gol + '</div></div>', unsafe_allow_html=True)

# --- 6. PANEL ADMINISTRADOR ---
with st.sidebar:
    st.header("🔐 Zona Administradores")
    if not st.session_state.get('logged_in', False):
        if st.text_input("Clave", type="password") == "organizadores2026":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        adm_t = st.tabs(["LOGOS", "EQ", "GR", "ELIM", "GOL", "💾"])
        eqs_lista = sorted([i['nombre'] for i in st.session_state.equipos.values()])
        
        with adm_t[0]:
            lt, lf = st.file_uploader("Logo Torneo"), st.file_uploader("Logo Final")
            if st.button("Guardar Logos"):
                if lt: st.session_state.logo_torneo = Image.open(lt)
                if lf: st.session_state.logo_final = Image.open(lf)
                save_to_disk(); st.rerun()
        
        with adm_t[1]:
            st.subheader("Equipos y Grupos")
            pos_gr = ["SIN GRUPO", "A", "B", "C", "D", "E"]
            for id_e, inf in st.session_state.equipos.items():
                with st.expander(f"{inf['nombre']}"):
                    nn = st.text_input("Nombre", inf['nombre'], key=f"n{id_e}").upper()
                    ng = st.selectbox("Grupo", pos_gr, index=pos_gr.index(inf['grupo']) if inf['grupo'] in pos_gr else 0, key=f"g{id_e}")
                    nl = st.file_uploader("Logo", key=f"l{id_e}")
                    if st.button("Guardar", key=f"b{id_e}"):
                        st.session_state.equipos[id_e].update({"nombre": nn, "grupo": ng})
                        if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                        save_to_disk(); st.rerun()

        with adm_t[2]:
            st.subheader("Registrar Partido")
            f_p = st.date_input("Fecha")
            l_sel, v_sel = st.selectbox("Local", eqs_lista), st.selectbox("Visitante", eqs_lista)
            t_res = st.checkbox("¿Tiene resultado?")
            gl_i, gv_i = (st.number_input("GL", 0, step=1), st.number_input("GV", 0, step=1)) if t_res else (None, None)
            if st.button("Registrar"):
                st.session_state.partidos.append({"fecha": str(f_p), "local": l_sel, "visitante": v_sel, "goles_l": gl_i, "goles_v": gv_i})
                save_to_disk(); st.rerun()
            st.divider()
            for i, p in enumerate(st.session_state.partidos):
                with st.expander(f"{p['fecha']} | {p['local']} vs {p['visitante']}"):
                    ngl = st.number_input("GL", value=int(p['goles_l']) if p['goles_l'] is not None else 0, key=f"egl{i}")
                    ngv = st.number_input("GV", value=int(p['goles_v']) if p['goles_v'] is not None else 0, key=f"egv{i}")
                    if st.button("💾", key=f"upd{i}"):
                        st.session_state.partidos[i].update({'goles_l': int(ngl), 'goles_v': int(ngv)}); save_to_disk(); st.rerun()
                    if st.button("🗑️", key=f"delp{i}"): st.session_state.partidos.pop(i); save_to_disk(); st.rerun()

        with adm_t[3]:
            st.subheader("Configurar Fase Final")
            eqs_ko = [""] + eqs_lista
            for ft in ["cuartos", "semis", "final"]:
                with st.expander(ft.upper()):
                    matches = st.session_state.fase_final[ft]
                    if isinstance(matches, list):
                        for i, m in enumerate(matches):
                            st.markdown(f"**Partido {i+1}**")
                            m["L"] = st.selectbox(f"L{ft}{i}", eqs_ko, index=eqs_ko.index(m["L"]) if m["L"] in eqs_ko else 0, key=f"l{ft}{i}")
                            m["V"] = st.selectbox(f"V{ft}{i}", eqs_ko, index=eqs_ko.index(m["V"]) if m["V"] in eqs_ko else 0, key=f"v{ft}{i}")
                            has_r = st.checkbox("¿Tiene resultado?", value=(m["gl"] is not None), key=f"r{ft}{i}")
                            if has_r:
                                m["gl"] = st.number_input("GL", value=int(m["gl"]) if m["gl"] is not None else 0, key=f"gl{ft}{i}")
                                m["gv"] = st.number_input("GV", value=int(m["gv"]) if m["gv"] is not None else 0, key=f"gv{ft}{i}")
                            else: m["gl"] = m["gv"] = None
                    else:
                        matches["L"] = st.selectbox("L Final", eqs_ko, index=eqs_ko.index(matches["L"]) if matches["L"] in eqs_ko else 0, key="lfin")
                        matches["V"] = st.selectbox("V Final", eqs_ko, index=eqs_ko.index(matches["V"]) if matches["V"] in eqs_ko else 0, key="vfin")
                        has_rf = st.checkbox("¿Tiene resultado?", value=(matches["gl"] is not None), key="rfin")
                        if has_rf:
                            matches["gl"] = st.number_input("GL", value=int(matches["gl"]) if matches["gl"] is not None else 0, key="glfin")
                            matches["gv"] = st.number_input("GV", value=int(matches["gv"]) if matches["gv"] is not None else 0, key="gvfin")
                        else: matches["gl"] = matches["gv"] = None
            if st.button("Guardar Fase Final"): save_to_disk(); st.rerun()

        with adm_t[4]:
            st.subheader("Goleadores")
            nj_i = st.text_input("Nombre Jugador").upper()
            ej_i = st.selectbox("Equipo Jugador", eqs_lista, key="ad_gol_eq")
            gj_i = st.number_input("Goles", 0, step=1)
            if st.button("➕ Añadir"):
                if nj_i: st.session_state.goleadores.append({"nombre": nj_i, "equipo": ej_i, "goles": int(gj_i)}); save_to_disk(); st.rerun()
            st.divider()
            for idx, g in enumerate(st.session_state.goleadores):
                with st.expander(f"{g['nombre']} ({g['equipo']}) - {g['goles']} Goles"):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1: st.write(f"Goles: {g['goles']}")
                    with c2: 
                        if st.button("➕", key=f"pg{idx}"): st.session_state.goleadores[idx]['goles'] += 1; save_to_disk(); st.rerun()
                    with c3:
                        if st.button("➖", key=f"mg{idx}"): 
                            if g['goles'] > 0: st.session_state.goleadores[idx]['goles'] -= 1; save_to_disk(); st.rerun()
                    if st.button("🗑️", key=f"dg{idx}"): st.session_state.goleadores.pop(idx); save_to_disk(); st.rerun()

        with adm_t[5]:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f_db: st.download_button("📥 Backup", f_db.read(), "torneo.json")
            sub_file = st.file_uploader("Restaurar")
            if sub_file and st.button("🔴 RESTAURAR"):
                with open(DB_FILE, "wb") as f_db: f_db.write(sub_file.getbuffer())
                st.rerun()
