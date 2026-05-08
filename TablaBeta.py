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

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def formatear_fecha_espanol(fecha_str):
    try:
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")
        return f"{DIAS[dt.weekday()]}, {dt.day} de {MESES[dt.month - 1]}"
    except: return fecha_str

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
    
    /* Título Coloreado */
    .txt-celeste { color: #7db1ff !important; }
    .txt-red { color: #ff3b3b !important; }
    .txt-gold { color: #FFD700 !important; }

    /* Optimización Móvil */
    @media (max-width: 768px) {
        .nam-title { font-size: 2.2em !important; }
        .main-card { width: 98% !important; min-width: 98% !important; }
        .grid-goleadores { grid-template-columns: 40px 100px 1fr 50px !important; gap: 8px !important; padding: 10px !important; }
        .grid-posiciones { grid-template-columns: 110px repeat(8, 30px) !important; font-size: 0.75em !important; overflow-x: auto; }
        .res-team-box { width: 110px !important; font-size: 0.85em !important; }
        .top-scorer-name { font-size: 1.1em !important; }
    }

    .nam-title { font-size: 4em; text-align: center; font-weight: 900; color: white; margin-bottom: 20px; }
    .table-container { display: flex; flex-direction: column; align-items: center; width: 100%; }
    .main-card { background: rgba(0, 10, 60, 0.4); border-radius: 12px; margin-bottom: 25px; border: 1px solid #FFD70033; color: white; backdrop-filter: blur(10px); overflow: hidden; width: fit-content; }
    
    /* Goleadores y Efectos */
    .grid-goleadores { display: grid; grid-template-columns: 50px 250px 1fr 80px; align-items: center; padding: 12px 20px; gap: 15px; white-space: nowrap; }
    .top-scorer-card { background: linear-gradient(90deg, rgba(255, 215, 0, 0.18) 0%, rgba(0, 20, 80, 0.6) 100%); border: 2px solid #FFD700 !important; border-radius: 10px !important; }
    .top-scorer-name { font-size: 1.4em !important; color: #FFD700 !important; text-shadow: 0 0 10px rgba(255, 215, 0, 0.4); font-weight: 900 !important; }
    .top-scorer-goals { font-size: 1.8em !important; color: #FFD700 !important; font-weight: 900 !important; }
    
    /* Fase Final */
    .bracket-scroll { overflow-x: auto; width: 100%; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .bracket-wrapper { display: flex; align-items: center; min-width: 1150px; gap: 20px; margin: 0 auto; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 500px; width: 230px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 8px; border: 1px solid #FFD70044; padding: 10px; margin: 15px 0; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 30px; height: 26px; text-align: center; border-radius: 3px; display: flex; align-items: center; justify-content: center; }
    .logo-epico { filter: drop-shadow(0 0 20px #FFD700); margin-bottom: 10px; }
    
    /* Fechas y Títulos */
    .date-divider { background: #FFD700; color: black; padding: 5px 20px; font-weight: 900; border-radius: 4px 4px 0 0; font-size: 0.85em; display: inline-block; text-transform: uppercase; }
    .jornada-title { background: rgba(255, 215, 0, 0.2); color: #FFD700; padding: 5px 20px; font-weight: 900; border-radius: 0 0 4px 4px; border-left: 4px solid #FFD700; font-size: 1.1em; margin-bottom: 15px; width: fit-content; margin-left: auto; margin-right: auto; }
    .res-team-box { display: flex; align-items: center; gap: 10px; width: 280px; }
    .header-grid { background: rgba(0, 0, 0, 0.3); border-bottom: 2px solid #FFD700; font-weight: 900; text-transform: uppercase; }
    .grid-posiciones { display: grid; grid-template-columns: 300px repeat(8, 42px); align-items: center; padding: 10px 12px; }
    .team-row { border-bottom: 1px solid rgba(125, 177, 255, 0.15); }
    h4 { color: #FFD700 !important; font-weight: 900; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA RENDERIZADO ---
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
    return f'''
    <div class="match-box-ko">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div style="display:flex;align-items:center;"><img src="{img1}" style="width:20px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;color:white;">{t1["nombre"] or "---"}</span></div>
            <span class="ko-score">{format_score(match.get("gl"))}</span>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div style="display:flex;align-items:center;"><img src="{img2}" style="width:20px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;color:white;">{t2["nombre"] or "---"}</span></div>
            <span class="ko-score">{format_score(match.get("gv"))}</span>
        </div>
    </div>'''

def calcular_tablas():
    stats = {info['nombre']: {"nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']} for info in st.session_state.equipos.values() if info['grupo'] != "SIN GRUPO"}
    for p in st.session_state.partidos:
        gl, gv = p.get('goles_l'), p.get('goles_v')
        if gl is not None and not (isinstance(gl, float) and np.isnan(gl)):
            l, v = p['local'], p['visitante']
            if l in stats and v in stats:
                gl, gv = int(float(gl)), int(float(gv))
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

t_pos, t_ff, t_res, t_gol = st.tabs(["📊 POSICIONES", "🏆 FASE FINAL", "⚽ RESULTADOS", "👟 GOLEADORES"])

with t_res:
    if st.session_state.partidos:
        df = pd.DataFrame(st.session_state.partidos)
        l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
        for f in sorted(df['fecha'].unique(), reverse=True):
            p_f = df[df['fecha'] == f]
            tit = p_f.iloc[0].get('titulo', '')
            st.markdown(f'<div style="text-align:center;"><div class="date-divider">{formatear_fecha_espanol(f)}</div>{f"<div class=jornada-title>{tit}</div>" if tit else ""}</div>', unsafe_allow_html=True)
            html_res = '<div class="table-container"><div class="main-card">'
            for _, p in p_f.iterrows():
                s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                rl, rv = format_score(p["goles_l"]), format_score(p["goles_v"])
                sep = "-" if (rl != "" or rv != "") else "VS"
                html_res += f'<div style="display:flex;align-items:center;justify-content:center;padding:12px;border-bottom:1px solid #ffffff11;gap:15px;"><div class="res-team-box" style="justify-content:flex-end;"><span style="font-weight:700;overflow:hidden;">{p["local"]}</span><img src="{s_l}" width="20"></div><div style="width:70px;text-align:center;color:#FFD700;font-weight:900;font-size:1.2em;">{rl} {sep} {rv}</div><div class="res-team-box" style="justify-content:flex-start;"><img src="{s_v}" width="20"><span style="font-weight:700;overflow:hidden;">{p["visitante"]}</span></div></div>'
            st.markdown(html_res + '</div></div>', unsafe_allow_html=True)

with t_ff:
    ff = st.session_state.fase_final
    logo_f = img_to_base64(st.session_state.logo_final)
    st.markdown(f'''
    <div class="bracket-scroll">
        <div class="bracket-wrapper">
            <div class="bracket-column"><h4>CUARTOS</h4>{render_match(ff["cuartos"][0])}{render_match(ff["cuartos"][1])}</div>
            <div class="bracket-column"><h4>SEMIFINAL</h4>{render_match(ff["semis"][0])}</div>
            <div class="final-center">
                {f"<img src='data:image/png;base64,{logo_f}' class='logo-epico' width=160>" if logo_f else "<h2 class='txt-gold'>FINAL</h2>"}
                <h1 style="color:white !important; margin: 10px 0; text-shadow: 0 0 15px rgba(255,215,0,0.6);">GRAN FINAL</h1>
                {render_match(ff["final"])}
            </div>
            <div class="bracket-column"><h4>SEMIFINAL</h4>{render_match(ff["semis"][1])}</div>
            <div class="bracket-column"><h4>CUARTOS</h4>{render_match(ff["cuartos"][2])}{render_match(ff["cuartos"][3])}</div>
        </div>
    </div>''', unsafe_allow_html=True)

with t_gol:
    if st.session_state.goleadores:
        gols = sorted(st.session_state.goleadores, key=lambda x: int(x.get('goles', 0)), reverse=True)
        l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
        html_gol = '<div class="table-container"><div class="main-card"><div class="grid-goleadores header-grid"><span></span><span>EQUIPO</span><span>JUGADOR</span><span style="text-align:center;">GOLES</span></div>'
        for idx, g in enumerate(gols):
            img = f"data:image/png;base64,{img_to_base64(l_map.get(g['equipo']))}" if l_map.get(g['equipo']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
            is_t = "top-scorer-card" if idx == 0 else ""
            html_gol += f'''
            <div class="grid-goleadores {is_t}" style="border-bottom:1px solid #ffffff05;">
                <img src="{img}" width="30">
                <span style="color:#7db1ff;overflow:hidden;">{g["equipo"]}</span>
                <span class="{"top-scorer-name" if idx==0 else ""}" style="font-weight:700;overflow:hidden;">{g["nombre"]}</span>
                <span class="{"top-scorer-goals" if idx==0 else ""}" style="text-align:center;font-weight:900;color:#FFD700;font-size:1.2em;">{g["goles"]}</span>
            </div>'''
        st.markdown(html_gol + '</div></div>', unsafe_allow_html=True)

with t_pos:
    stats = calcular_tablas()
    grupos = sorted(list(set(eq['grupo'] for eq in stats.values() if eq['grupo'] != "SIN GRUPO")))
    for g in grupos:
        eq_g = sorted([s for s in stats.values() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG'], x['GF']), reverse=True)
        html = f'<div class="table-container"><div class="main-card"><div class="grid-posiciones header-grid"><span>GRUPO {g}</span><span>PJ</span><span>G</span><span>E</span><span>P</span><span>GF</span><span>GC</span><span>DG</span><span>PTS</span></div>'
        for eq in eq_g:
            img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
            html += f'<div class="grid-posiciones team-row"><div style="display:flex;align-items:center;gap:8px;overflow:hidden;"><img src="{img}" width="18"><span>{eq["nombre"]}</span></div><span>{eq["PJ"]}</span><span>{eq["G"]}</span><span>{eq["E"]}</span><span>{eq["P"]}</span><span>{eq["GF"]}</span><span>{eq["GC"]}</span><span>{eq["DG"]}</span><span style="color:#FFD700;font-weight:900;">{eq["PTS"]}</span></div>'
        st.markdown(html + '</div></div>', unsafe_allow_html=True)

# --- 6. PANEL ADMINISTRADOR ---
with st.sidebar:
    st.header("🔐 Zona Admin")
    if not st.session_state.get('logged_in', False):
        if st.text_input("Clave", type="password") == "organizadores2026":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        adm_t = st.tabs(["LGS", "EQ", "PART", "ELIM", "GOL", "💾"])
        eqs_lista = sorted([i['nombre'] for i in st.session_state.equipos.values()])
        
        with adm_t[2]:
            f_p = st.date_input("Fecha")
            t_j = st.text_input("Título Jornada").upper()
            l, v = st.selectbox("L", eqs_lista), st.selectbox("V", eqs_lista)
            tr = st.checkbox("¿Resultado?")
            gl, gv = (st.number_input("GL", 0), st.number_input("GV", 0)) if tr else (None, None)
            if st.button("Añadir Partido"):
                st.session_state.partidos.append({"fecha": str(f_p), "titulo": t_j, "local": l, "visitante": v, "goles_l": gl, "goles_v": gv})
                save_to_disk(); st.rerun()
            for i, p in enumerate(st.session_state.partidos):
                with st.expander(f"{p['fecha']} | {p['local']} vs {p['visitante']}"):
                    new_t = st.text_input("Editar Título", p.get('titulo', ''), key=f"t{i}")
                    ngl = st.number_input("GL", value=int(p['goles_l']) if p['goles_l'] is not None else 0, key=f"gl{i}")
                    ngv = st.number_input("GV", value=int(p['goles_v']) if p['goles_v'] is not None else 0, key=f"gv{i}")
                    if st.button("Guardar", key=f"s{i}"):
                        st.session_state.partidos[i].update({"goles_l": ngl, "goles_v": ngv, "titulo": new_t})
                        save_to_disk(); st.rerun()
                    if st.button("Borrar", key=f"d{i}"): st.session_state.partidos.pop(i); save_to_disk(); st.rerun()

        with adm_t[1]:
            for id_e, inf in st.session_state.equipos.items():
                with st.expander(f"{inf['nombre']}"):
                    nn = st.text_input("Nombre", inf['nombre'], key=f"n{id_e}").upper()
                    ng = st.selectbox("Grupo", ["SIN GRUPO","A","B","C","D","E"], index=["SIN GRUPO","A","B","C","D","E"].index(inf['grupo']), key=f"g{id_e}")
                    nl = st.file_uploader("Logo", key=f"l{id_e}")
                    if st.button("Guardar", key=f"b{id_e}"):
                        st.session_state.equipos[id_e].update({"nombre": nn, "grupo": ng})
                        if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                        save_to_disk(); st.rerun()

        with adm_t[3]:
            eqs_ko = [""] + eqs_lista
            for ft in ["cuartos", "semis", "final"]:
                with st.expander(ft.upper()):
                    matches = st.session_state.fase_final[ft]
                    if isinstance(matches, list):
                        for i, m in enumerate(matches):
                            st.write(f"Partido {i+1}")
                            m["L"] = st.selectbox(f"L{ft}{i}", eqs_ko, index=eqs_ko.index(m["L"]) if m["L"] in eqs_ko else 0, key=f"l{ft}{i}")
                            m["V"] = st.selectbox(f"V{ft}{i}", eqs_ko, index=eqs_ko.index(m["V"]) if m["V"] in eqs_ko else 0, key=f"v{ft}{i}")
                            has_r = st.checkbox("¿Tiene resultado?", value=(m["gl"] is not None), key=f"r{ft}{i}")
                            if has_r:
                                m["gl"] = st.number_input("GL", value=int(m["gl"]) if m["gl"] is not None else 0, key=f"gl{ft}{i}")
                                m["gv"] = st.number_input("GV", value=int(m["gv"]) if m["gv"] is not None else 0, key=f"gv{ft}{i}")
                            else: m["gl"] = m["gv"] = None
                    else:
                        matches["L"] = st.selectbox("L Fin", eqs_ko, index=eqs_ko.index(matches["L"]) if matches["L"] in eqs_ko else 0, key="lfin")
                        matches["V"] = st.selectbox("V Fin", eqs_ko, index=eqs_ko.index(matches["V"]) if matches["V"] in eqs_ko else 0, key="vfin")
                        has_rf = st.checkbox("¿Res?", value=(matches["gl"] is not None), key="rfin")
                        if has_rf:
                            matches["gl"] = st.number_input("GL", value=int(matches["gl"]) if matches["gl"] is not None else 0, key="glfin")
                            matches["gv"] = st.number_input("GV", value=int(matches["gv"]) if matches["gv"] is not None else 0, key="gvfin")
                        else: matches["gl"] = matches["gv"] = None
            if st.button("Guardar FF"): save_to_disk(); st.rerun()

        with adm_t[4]:
            nj = st.text_input("Nombre").upper()
            ej = st.selectbox("Equipo", eqs_lista, key="gol_adm")
            gj = st.number_input("Goles", 0)
            if st.button("Añadir"):
                if nj: st.session_state.goleadores.append({"nombre": nj, "equipo": ej, "goles": int(gj)}); save_to_disk(); st.rerun()
            for idx, g in enumerate(st.session_state.goleadores):
                with st.expander(f"{g['nombre']} ({g['goles']})"):
                    if st.button("➕", key=f"pg{idx}"): st.session_state.goleadores[idx]['goles'] += 1; save_to_disk(); st.rerun()
                    if st.button("➖", key=f"mg{idx}"): st.session_state.goleadores[idx]['goles'] -= 1; save_to_disk(); st.rerun()
                    if st.button("Borrar", key=f"bg{idx}"): st.session_state.goleadores.pop(idx); save_to_disk(); st.rerun()
        
        with adm_t[5]:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f: st.download_button("Descargar JSON", f.read(), "torneo.json")
            if st.button("RESET TOTAL") and st.checkbox("Confirmar RESET"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()
