"""
app.py — Pastillero semanal con el catálogo LOMET

App de Streamlit para armar el pastillero semanal de un paciente usando
el Listado Oficial de Medicamentos (LOMET) del Ministerio de Salud de
Costa Rica, corte diciembre 2024. Calcula para cuántos días alcanzan las
tabletas que tiene el paciente y qué fecha toca reponer.

Para correrla en su computadora:
    streamlit run app.py

Regla de oro: se valida en la entrada (validaciones.py) y adentro se confía.
"""

import csv
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from validaciones import (
    es_forma_solida,
    normalizar,
    validar_dosis,
    validar_forma_solida,
    validar_no_repetido,
    validar_nombre_paciente,
    validar_seleccion,
    validar_unidades_envase,
)

RUTA_CATALOGO = Path(__file__).parent / "datos" / "lomet_dic_2024.csv"
TOMAS = ["Desayuno", "Almuerzo", "Cena", "Noche"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
FRACCIONES = {0.25: "¼", 0.5: "½", 0.75: "¾"}


# ---------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------
@st.cache_data
def cargar_catalogo(ruta):
    """
    Lee el CSV del LOMET y devuelve un diccionario {registro_sanitario: fila},
    ordenado por principio activo. Solo deja los sólidos orales que caben en
    el SPD (tabletas, comprimidos, cápsulas, grageas) y omite los productos
    marcados como vencidos o descontinuados.
    """
    catalogo = {}
    with open(ruta, encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            notas = normalizar(fila["notas"])
            if "vencido" in notas or "descontinu" in notas:
                continue
            if not es_forma_solida(fila["forma_farmaceutica"]):
                continue
            catalogo[fila["registro_sanitario"]] = fila
    return dict(sorted(catalogo.items(),
                       key=lambda par: (normalizar(par[1]["principio_activo"]), par[1]["nombre_comercial"])))


def etiqueta_medicamento(fila):
    """Texto que se ve (y se busca) en la barra: principio activo, nombre comercial y forma."""
    return f"{fila['principio_activo']} — {fila['nombre_comercial']} ({fila['forma_farmaceutica'].lower()})"


# ---------------------------------------------------------------------
# Cálculos (aquí los datos ya vienen validados)
# ---------------------------------------------------------------------
def formatear_dosis(dosis):
    """1.5 -> '1½', 0.25 -> '¼', 2.0 -> '2'."""
    entero = int(dosis)
    fraccion = FRACCIONES.get(dosis - entero, "")
    if entero == 0:
        return fraccion
    return f"{entero}{fraccion}"


def construir_grilla(pastillero):
    """Arma la tabla del pastillero: una fila por toma, una columna por día."""
    grilla = {"Toma": TOMAS}
    for dia in DIAS:
        columna = []
        for toma in TOMAS:
            contenido = [
                f"{m['nombre_corto']} ({formatear_dosis(m['dosis'])})"
                for m in pastillero
                if toma in m["tomas"] and dia in m["dias"]
            ]
            columna.append(", ".join(contenido) if contenido else "—")
        grilla[dia] = columna
    return grilla


def dias_que_alcanza(medicamento):
    """Cuántos días alcanzan las unidades que tiene el paciente."""
    unidades_por_semana = medicamento["dosis"] * len(medicamento["tomas"]) * len(medicamento["dias"])
    return medicamento["unidades"] / (unidades_por_semana / 7)


# ---------------------------------------------------------------------
# Pantalla
# ---------------------------------------------------------------------
st.set_page_config(page_title="Pastillero LOMET", page_icon="💊")
st.title("💊 Pastillero semanal con el catálogo LOMET")
st.write(
    "Para farmacias y cuidadores en Costa Rica: busque los medicamentos del paciente en el "
    "**Listado Oficial de Medicamentos (LOMET)** del Ministerio de Salud, arme su pastillero "
    "de la semana y vea para cuántos días le alcanzan las tabletas y cuándo reponer."
)
st.caption("Herramienta de apoyo. No sustituye la indicación del médico ni del farmacéutico.")

if "pastillero" not in st.session_state:
    st.session_state.pastillero = []

try:
    catalogo = cargar_catalogo(RUTA_CATALOGO)
except FileNotFoundError:
    st.error("No encontré el catálogo LOMET (datos/lomet_dic_2024.csv). Revise que el archivo esté en el repositorio.")
    st.stop()
except UnicodeDecodeError:
    st.error("El catálogo LOMET no está guardado en UTF-8. Vuelva a guardarlo como 'CSV UTF-8'.")
    st.stop()
except KeyError as columna:
    st.error(f"Al catálogo LOMET le falta la columna {columna}. Use el archivo original del Ministerio.")
    st.stop()


def seccion_paciente():
    """Paso 1: nombre del paciente. Devuelve el nombre o None si todavía no sirve."""
    st.subheader("1. Paciente")
    texto = st.text_input("Nombre del paciente", placeholder="Ej.: Ana Rojas")
    if texto.strip() == "":
        st.info("Escriba el nombre del paciente para empezar.")
        return None
    try:
        return validar_nombre_paciente(texto)
    except ValueError as error:
        st.error(str(error))
        return None


def seccion_agregar_medicamento():
    """Paso 2: buscar en el LOMET, pedir dosis, tomas, días y unidades, y agregar."""
    st.subheader("2. Agregar medicamento")
    # Barra con texto predictivo: al escribir, Streamlit filtra las opciones.
    registro = st.selectbox(
        "Buscar en el LOMET (principio activo o nombre comercial)",
        list(catalogo),
        index=None,
        placeholder="Escriba para buscar. Ej.: irbesartan, eutirox, atorvastatina",
        format_func=lambda r: etiqueta_medicamento(catalogo[r]),
    )
    st.caption(f"El catálogo tiene {len(catalogo)} presentaciones vigentes de sólidos orales "
               "(tabletas, comprimidos, cápsulas y grageas).")
    if registro is None:
        return

    try:
        fila = catalogo[registro]
        validar_forma_solida(fila["forma_farmaceutica"])
    except KeyError:
        st.error("Esa presentación ya no está en el catálogo. Vuelva a buscarla.")
        return
    except ValueError as error:
        st.error(str(error))
        return

    with st.form("formulario_medicamento", clear_on_submit=True):
        dosis_texto = st.text_input("Unidades por toma", placeholder="Ej.: 1, 2, 1/2 o 0,5")
        tomas = st.multiselect("¿En qué tomas?", TOMAS)
        dias = st.multiselect("¿Qué días?", DIAS, default=DIAS)
        unidades_texto = st.text_input("¿Cuántas tabletas o cápsulas tiene el paciente?", placeholder="Ej.: 30")
        agregar = st.form_submit_button("Agregar al pastillero")

    if not agregar:
        return

    try:
        validar_no_repetido(registro, st.session_state.pastillero)
        dosis = validar_dosis(dosis_texto, fila["forma_farmaceutica"])
        validar_seleccion(tomas, "una toma (desayuno, almuerzo, cena o noche)")
        validar_seleccion(dias, "un día de la semana")
        unidades = validar_unidades_envase(unidades_texto)
    except ValueError as error:
        st.error(str(error))
        return

    st.session_state.pastillero.append({
        "registro": registro,
        "nombre": fila["nombre_comercial"],
        "nombre_corto": fila["principio_activo"].title(),
        "dosis": dosis,
        "tomas": tomas,
        "dias": dias,
        "unidades": unidades,
    })
    st.success(f"Agregué {fila['principio_activo'].title()} al pastillero.")


def seccion_pastillero(paciente):
    """Paso 3: muestra la grilla semanal y cuándo reponer cada medicamento."""
    st.subheader(f"3. Pastillero de {paciente}")
    pastillero = st.session_state.pastillero
    if not pastillero:
        st.info("El pastillero está vacío. Agregue el primer medicamento arriba.")
        return

    st.dataframe(construir_grilla(pastillero), hide_index=True, width="stretch")

    st.markdown("**¿Cuándo reponer?**")
    hoy = date.today()
    for medicamento in pastillero:
        try:
            dias = dias_que_alcanza(medicamento)
        except ZeroDivisionError:
            st.warning(f"{medicamento['nombre_corto']}: no tiene tomas asignadas, no puedo calcular la reposición.")
            continue
        fecha = hoy + timedelta(days=int(dias))
        texto = (f"**{medicamento['nombre_corto']}** — {medicamento['unidades']} unidades alcanzan "
                 f"para {int(dias)} días. Reponer antes del **{fecha:%d/%m/%Y}**.")
        if dias < 7:
            st.warning(texto + " No alcanza para la semana completa.")
        else:
            st.write(texto)

    if st.button("Vaciar pastillero"):
        st.session_state.pastillero = []
        st.rerun()


paciente = seccion_paciente()
if paciente:
    seccion_agregar_medicamento()
    seccion_pastillero(paciente)

st.divider()
st.caption("Fuente: LOMET, Ministerio de Salud de Costa Rica, corte 31/12/2024.")
