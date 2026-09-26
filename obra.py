# -*- coding: utf-8 -*-
"""
OBRASEGURA - Versión Streamlit
Empresas, Trabajadores, EPP, Equipos de alturas, Estructuras e Inspecciones.
"""

from datetime import date
import streamlit as st

st.set_page_config(page_title="ObraSegura", page_icon="🦺", layout="wide")

CATEGORIAS = ["EPP", "Equipos de alturas", "Estructuras"]

# ============================================================
# ESTADO
# ============================================================
for clave in ["empresas", "trabajadores", "elementos", "inspecciones"]:
    if clave not in st.session_state:
        st.session_state[clave] = []

empresas = st.session_state.empresas
trabajadores = st.session_state.trabajadores
elementos = st.session_state.elementos
inspecciones = st.session_state.inspecciones

st.title("🦺 OBRASEGURA")
st.caption("Sistema de registro e inspección de elementos de seguridad en obra.")
st.info("ℹ️ Los datos viven mientras la app esté abierta en esta sesión. Si recargas la página o el servidor se reinicia, se borran.")

(tab_empresas, tab_trab, tab_epp, tab_alturas,
 tab_estructuras, tab_insp, tab_dash) = st.tabs(
    ["🏢 Empresas", "👷 Trabajadores", "🦺 EPP", "🧗 Equipos de alturas",
     "🏗️ Estructuras", "🔎 Inspecciones", "📊 Dashboard"]
)

# ============================================================
# EMPRESAS
# ============================================================
with tab_empresas:
    with st.form("form_empresa", clear_on_submit=True):
        nit = st.text_input("NIT", placeholder="Ejemplo: 900123456-7")
        nombre_empresa = st.text_input("Nombre de la empresa", placeholder="Ejemplo: Pinturas del Norte")
        if st.form_submit_button("💾 Guardar empresa"):
            if not nit or not nombre_empresa:
                st.warning("⚠️ Debes ingresar el NIT y el nombre de la empresa.")
            else:
                empresas.append({"nit": nit, "nombre": nombre_empresa})
                st.success(f"✅ Empresa registrada: {nombre_empresa} | NIT: {nit}")

    if empresas:
        st.subheader("Empresas registradas")
        st.dataframe(empresas, use_container_width=True, hide_index=True)
    else:
        st.caption("Todavía no hay empresas registradas.")

# ============================================================
# TRABAJADORES
# ============================================================
with tab_trab:
    nombres_empresas = [e["nombre"] for e in empresas]
    if not nombres_empresas:
        st.warning("⚠️ Registra al menos una empresa antes de agregar trabajadores.")
    else:
        with st.form("form_trabajador", clear_on_submit=True):
            documento = st.text_input("Documento", placeholder="Ejemplo: 1020304050")
            nombre_trab = st.text_input("Nombre completo", placeholder="Ejemplo: Juan Gómez")
            empresa_sel = st.selectbox("Empresa", nombres_empresas)
            if st.form_submit_button("💾 Guardar trabajador"):
                if not documento or not nombre_trab:
                    st.warning("⚠️ Debes completar todos los campos.")
                else:
                    empresa_encontrada = next(e for e in empresas if e["nombre"] == empresa_sel)
                    trabajadores.append({
                        "documento": documento, "nombre": nombre_trab,
                        "empresa_nit": empresa_encontrada["nit"]
                    })
                    st.success(f"✅ Trabajador registrado: {nombre_trab} | Empresa: {empresa_sel}")

    if trabajadores:
        st.subheader("Trabajadores registrados")
        st.dataframe(trabajadores, use_container_width=True, hide_index=True)
    else:
        st.caption("Todavía no hay trabajadores registrados.")

# ============================================================
# FUNCIÓN REUTILIZABLE PARA REGISTRAR ELEMENTOS
# ============================================================
def formulario_elementos(categoria, tab):
    with tab:
        with st.form(f"form_{categoria}", clear_on_submit=True):
            nombre_el = st.text_input("Nombre del elemento", placeholder="Ejemplo: Mosquetón de acero")
            serial_el = st.text_input("Serial", placeholder="Dejar vacío si no aplica")
            if st.form_submit_button("💾 Guardar elemento"):
                if not nombre_el:
                    st.warning("⚠️ Debes ingresar el nombre del elemento.")
                else:
                    elementos.append({
                        "nombre": nombre_el, "categoria": categoria,
                        "serial": serial_el if serial_el else "No aplica", "activo": True
                    })
                    st.success(f"✅ Elemento registrado: {nombre_el}")

        elementos_categoria = [el for el in elementos if el["categoria"] == categoria]
        if elementos_categoria:
            st.subheader(f"Elementos registrados — {categoria}")
            st.dataframe(elementos_categoria, use_container_width=True, hide_index=True)
        else:
            st.caption(f"Todavía no hay elementos registrados en {categoria}.")

formulario_elementos("EPP", tab_epp)
formulario_elementos("Equipos de alturas", tab_alturas)
formulario_elementos("Estructuras", tab_estructuras)

# ============================================================
# INSPECCIONES
# ============================================================
with tab_insp:
    # El elemento se elige entre TODAS las categorías juntas (EPP, Equipos de alturas, Estructuras)
    opciones_elementos = [
        f'{el["nombre"]} | {el["categoria"]} | Serial: {el["serial"]}'
        for el in elementos if el["activo"]
    ]

    # El responsable puede ser un trabajador o una empresa, sin importar la categoría del elemento
    opciones_resp = (
        [f'{t["nombre"]} (Trabajador)' for t in trabajadores]
        + [f'{e["nombre"]} (Empresa)' for e in empresas]
    )

    if not opciones_elementos:
        st.warning("⚠️ No hay elementos disponibles todavía. Registra al menos uno en las pestañas 🦺 EPP, 🧗 Equipos de alturas o 🏗️ Estructuras.")
    if not opciones_resp:
        st.warning("⚠️ No hay responsables disponibles. Registra un trabajador o una empresa primero.")

    if opciones_elementos and opciones_resp:
        with st.form("form_inspeccion", clear_on_submit=True):
            fecha_inspeccion = st.date_input("Fecha de inspección", value=date.today())
            responsable = st.selectbox("👤 Responsable", opciones_resp)
            elemento_sel = st.selectbox("🧰 Elemento a inspeccionar", opciones_elementos)
            disponible = st.radio("¿Está disponible?", ["Sí", "No"])
            estado = st.selectbox("Estado", ["Óptimo", "Requiere cambio"])
            observaciones = st.text_area("Observaciones", placeholder="Ejemplo: Costuras sueltas")
            situacion = st.selectbox("Situación", ["En uso", "Repuesto", "Desechado"])
            proxima_inspeccion = st.text_input("Fecha de próxima inspección", placeholder="AAAA-MM-DD")

            if st.form_submit_button("💾 Registrar inspección"):
                elemento_encontrado = next(
                    el for el in elementos
                    if f'{el["nombre"]} | {el["categoria"]} | Serial: {el["serial"]}' == elemento_sel
                )
                fecha_reposicion = fecha_inspeccion.isoformat() if estado == "Requiere cambio" else ""

                inspecciones.append({
                    "fecha_inspeccion": fecha_inspeccion.isoformat(), "categoria": elemento_encontrado["categoria"],
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
    c3.metric("🧰 Elementos", len(elementos),
              delta=f"-{total_bloqueados} fuera de servicio" if total_bloqueados else None)
    c4.metric("🔎 Inspecciones", len(inspecciones))

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Elementos por categoría")
        if elementos:
            conteo_cat = {}
            for el in elementos:
                conteo_cat[el["categoria"]] = conteo_cat.get(el["categoria"], 0) + 1
            st.bar_chart(conteo_cat)
        else:
            st.caption("Aún no hay elementos registrados.")

    with col_b:
        st.subheader("Inspecciones por estado")
        if inspecciones:
            conteo_estado = {}
            for i in inspecciones:
                conteo_estado[i["estado"]] = conteo_estado.get(i["estado"], 0) + 1
            st.bar_chart(conteo_estado)
        else:
            st.caption("Aún no hay inspecciones registradas.")

    st.subheader("Inspecciones por categoría")
    if inspecciones:
        conteo_cat_insp = {}
        for i in inspecciones:
            conteo_cat_insp[i["categoria"]] = conteo_cat_insp.get(i["categoria"], 0) + 1
        st.bar_chart(conteo_cat_insp)
    else:
        st.caption("Aún no hay inspecciones registradas.")

    # ============================================================
    # REPORTE PDF
    # ============================================================
    st.divider()
    st.subheader("📄 Reporte en PDF")

    def generar_pdf():
        from fpdf import FPDF
        from datetime import datetime

        def limpio(texto):
            # Evita caracteres que la fuente básica del PDF no puede dibujar
            return str(texto).encode("latin-1", "replace").decode("latin-1")

        ahora = datetime.now()
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        ancho = pdf.epw  # ancho útil de la página (ya descuenta los márgenes)

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(ancho, 10, limpio("Reporte ObraSegura"), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(ancho, 8, limpio(f"Generado el: {ahora.strftime('%Y-%m-%d %H:%M:%S')}"), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(6)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(ancho, 8, limpio("Resumen general"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(ancho, 7, limpio(f"Empresas registradas: {len(empresas)}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(ancho, 7, limpio(f"Trabajadores registrados: {len(trabajadores)}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(ancho, 7, limpio(f"Elementos registrados: {len(elementos)} ({total_bloqueados} fuera de servicio)"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(ancho, 7, limpio(f"Inspecciones realizadas: {len(inspecciones)}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

        if inspecciones:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(ancho, 8, limpio("Detalle de inspecciones"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            for i in inspecciones:
                linea = (
                    f"{i['fecha_inspeccion']} | {i['categoria']} | {i['elemento']} "
                    f"(Serial: {i['serial']}) | Responsable: {i['responsable']} | Estado: {i['estado']}"
                )
                pdf.multi_cell(ancho, 6, limpio(linea))
            pdf.ln(4)

        if elementos:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(ancho, 8, limpio("Elementos registrados"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            for el in elementos:
                estado_el = "Activo" if el["activo"] else "Fuera de servicio"
                pdf.multi_cell(ancho, 6, limpio(f"{el['nombre']} | {el['categoria']} | Serial: {el['serial']} | {estado_el}"))

        return bytes(pdf.output())

    if st.button("🧾 Generar reporte PDF"):
        pdf_bytes = generar_pdf()
        st.download_button(
            "⬇️ Descargar PDF",
            data=pdf_bytes,
            file_name=f"reporte_obrasegura_{date.today().isoformat()}.pdf",
            mime="application/pdf"
        )
