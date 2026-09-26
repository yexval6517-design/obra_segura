# -*- coding: utf-8 -*-
"""
OBRASEGURA - Versión Streamlit
Registro de empresas, trabajadores, elementos de seguridad e inspecciones.
"""

from datetime import date
import streamlit as st

st.set_page_config(page_title="ObraSegura", page_icon="🦺", layout="wide")

# ============================================================
# ESTADO (persiste mientras la app esté abierta en el navegador)
# ============================================================
if "empresas" not in st.session_state:
    st.session_state.empresas = []
if "trabajadores" not in st.session_state:
    st.session_state.trabajadores = []
if "elementos" not in st.session_state:
    st.session_state.elementos = []
if "inspecciones" not in st.session_state:
    st.session_state.inspecciones = []

empresas = st.session_state.empresas
trabajadores = st.session_state.trabajadores
elementos = st.session_state.elementos
inspecciones = st.session_state.inspecciones

st.title("🦺 OBRASEGURA")
st.caption("Sistema de registro e inspección de elementos de seguridad en obra.")

tab_empresas, tab_trab, tab_el, tab_insp, tab_dash = st.tabs(
    ["🏢 Empresas", "👷 Trabajadores", "🧰 Elementos", "🔎 Inspecciones", "📊 Dashboard"]
)

# ============================================================
# EMPRESAS
# ============================================================
with tab_empresas:
    with st.form("form_empresa", clear_on_submit=True):
        nit = st.text_input("NIT", placeholder="Ejemplo: 900123456-7")
        nombre_empresa = st.text_input("Nombre de la empresa", placeholder="Ejemplo: Pinturas del Norte")
        enviado = st.form_submit_button("💾 Guardar empresa")
        if enviado:
            if not nit or not nombre_empresa:
                st.warning("⚠️ Debes ingresar el NIT y el nombre de la empresa.")
            else:
                empresas.append({"nit": nit, "nombre": nombre_empresa})
                st.success(f"✅ Empresa registrada: {nombre_empresa} | NIT: {nit}")

    if empresas:
        st.subheader("Empresas registradas")
        st.dataframe(empresas, use_container_width=True, hide_index=True)

# ============================================================
# TRABAJADORES
# ============================================================
with tab_trab:
    nombres_empresas = [e["nombre"] for e in empresas]
    with st.form("form_trabajador", clear_on_submit=True):
        documento = st.text_input("Documento", placeholder="Ejemplo: 1020304050")
        nombre_trab = st.text_input("Nombre completo", placeholder="Ejemplo: Juan Gómez")
        empresa_sel = st.selectbox("Empresa", nombres_empresas if nombres_empresas else ["Registra una empresa primero"])
        enviado = st.form_submit_button("💾 Guardar trabajador")
        if enviado:
            if not documento or not nombre_trab or not nombres_empresas:
                st.warning("⚠️ Debes completar todos los campos y tener al menos una empresa registrada.")
            else:
                empresa_encontrada = next((e for e in empresas if e["nombre"] == empresa_sel), None)
                trabajadores.append({
                    "documento": documento, "nombre": nombre_trab,
                    "empresa_nit": empresa_encontrada["nit"]
                })
                st.success(f"✅ Trabajador registrado: {nombre_trab} | Empresa: {empresa_sel}")

    if trabajadores:
        st.subheader("Trabajadores registrados")
        st.dataframe(trabajadores, use_container_width=True, hide_index=True)

# ============================================================
# ELEMENTOS
# ============================================================
with tab_el:
    with st.form("form_elemento", clear_on_submit=True):
        nombre_el = st.text_input("Nombre del elemento", placeholder="Ejemplo: Mosquetón de acero")
        categoria_el = st.selectbox("Categoría", ["EPP trabajador", "Equipos de alturas", "Estructuras"])
        serial_el = st.text_input("Serial", placeholder="Dejar vacío si no aplica")
        enviado = st.form_submit_button("💾 Guardar elemento")
        if enviado:
            if not nombre_el:
                st.warning("⚠️ Debes ingresar el nombre del elemento.")
            else:
                elementos.append({
                    "nombre": nombre_el, "categoria": categoria_el,
                    "serial": serial_el if serial_el else "No aplica", "activo": True
                })
                st.success(f"✅ Elemento registrado: {nombre_el} ({categoria_el})")

    if elementos:
        st.subheader("Elementos registrados")
        st.dataframe(elementos, use_container_width=True, hide_index=True)

# ============================================================
# INSPECCIONES
# ============================================================
with tab_insp:
    categoria_insp = st.selectbox(
        "¿Qué se va a inspeccionar?",
        ["EPP trabajador", "Equipos de alturas", "Estructuras"],
        key="cat_insp"
    )

    if categoria_insp == "EPP trabajador":
        opciones_resp = [t["nombre"] for t in trabajadores]
    else:
        opciones_resp = [e["nombre"] for e in empresas]

    opciones_elementos = [
        f'{el["nombre"]} | Serial: {el["serial"]}'
        for el in elementos if el["categoria"] == categoria_insp and el["activo"]
    ]

    with st.form("form_inspeccion", clear_on_submit=True):
        fecha_inspeccion = st.date_input("Fecha de inspección", value=date.today())
        responsable = st.selectbox("👤 Responsable", opciones_resp if opciones_resp else ["No hay registros"])
        elemento_sel = st.selectbox("🧰 Elemento", opciones_elementos if opciones_elementos else ["No hay elementos disponibles"])
        disponible = st.radio("¿Está disponible?", ["Sí", "No"])
        estado = st.selectbox("Estado", ["Óptimo", "Requiere cambio"])
        observaciones = st.text_area("Observaciones", placeholder="Ejemplo: Costuras sueltas")
        situacion = st.selectbox("Situación", ["En uso", "Repuesto", "Desechado"])
        proxima_inspeccion = st.text_input("Fecha de próxima inspección", placeholder="AAAA-MM-DD")

        enviado = st.form_submit_button("💾 Registrar inspección")

        if enviado:
            if not opciones_resp or not opciones_elementos:
                st.warning("⚠️ Necesitas responsables y elementos disponibles registrados para esa categoría.")
            else:
                elemento_encontrado = next(
                    (el for el in elementos if f'{el["nombre"]} | Serial: {el["serial"]}' == elemento_sel), None
                )
                fecha_reposicion = fecha_inspeccion.isoformat() if estado == "Requiere cambio" else ""

                inspecciones.append({
                    "fecha_inspeccion": fecha_inspeccion.isoformat(), "categoria": categoria_insp,
                    "responsable": responsable, "elemento": elemento_encontrado["nombre"],
                    "serial": elemento_encontrado["serial"], "disponible": disponible,
                    "estado": estado, "observaciones": observaciones,
                    "fecha_reposicion": fecha_reposicion, "situacion": situacion,
                    "proxima_inspeccion": proxima_inspeccion
                })

                if estado == "Requiere cambio":
                    elemento_encontrado["activo"] = False

                st.success(f"✅ Inspección registrada para {elemento_encontrado['nombre']} — Estado: {estado}")

    if inspecciones:
        st.subheader("Inspecciones registradas")
        st.dataframe(inspecciones, use_container_width=True, hide_index=True)

# ============================================================
# DASHBOARD
# ============================================================
with tab_dash:
    total_bloqueados = sum(1 for e in elementos if not e["activo"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏢 Empresas", len(empresas))
    c2.metric("👷 Trabajadores", len(trabajadores))
    c3.metric("🧰 Elementos", len(elementos), delta=f"-{total_bloqueados} fuera de servicio" if total_bloqueados else None)
    c4.metric("🔎 Inspecciones", len(inspecciones))

    if inspecciones:
        st.subheader("Inspecciones por estado")
        conteo_estado = {}
        for i in inspecciones:
            conteo_estado[i["estado"]] = conteo_estado.get(i["estado"], 0) + 1
        st.bar_chart(conteo_estado)
    else:
        st.info("Aún no hay inspecciones registradas para mostrar en el dashboard.")
