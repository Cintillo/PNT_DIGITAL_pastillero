"""
validaciones.py

Funciones "portero": revisan cada dato que escribe el usuario ANTES de
que entre al pastillero. Si el dato no sirve, lanzan ValueError con un
mensaje que dice qué estuvo mal y cómo escribirlo bien.

Este archivo NO usa Streamlit a propósito: así las funciones se pueden
probar solas desde la terminal (ver pruebas.py).
"""

import math
import unicodedata

# Formas farmacéuticas que sí caben en un pastillero (sólidos orales).
PALABRAS_FORMA_SOLIDA = ("TABLETA", "COMPRIMID", "CAPSULA", "GRAGEA")

# Formas que NO se pueden partir: si se parten, se pierde la protección
# o la liberación lenta del medicamento.
PALABRAS_NO_PARTIBLE = ("LIBERACION PROLONGADA", "ENTERIC", "GASTRORRESI", "CAPSULA")

DOSIS_MAXIMA_POR_TOMA = 12      # unidades por toma
UNIDADES_MAXIMAS_ENVASE = 1000


def normalizar(texto):
    """Quita tildes, espacios de más y pasa a minúscula: ' SAN  JOSÉ ' -> 'san jose'."""
    sin_tildes = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(ch for ch in sin_tildes if unicodedata.category(ch) != "Mn")
    return " ".join(sin_tildes.lower().split())


def validar_nombre_paciente(texto):
    """Acepta solo letras (y espacios, guiones, apóstrofos o puntos), mínimo 3 letras."""
    limpio = " ".join(texto.split())
    if limpio == "":
        raise ValueError("Escriba el nombre del paciente. El campo está en blanco.")
    letras = [ch for ch in limpio if ch.isalpha()]
    if len(letras) == 0:
        raise ValueError(f"'{limpio}' no contiene letras. Escriba el nombre del paciente, por ejemplo: Ana Rojas.")
    if any(ch.isdigit() for ch in limpio):
        raise ValueError(f"El nombre '{limpio}' tiene números. Escriba solo letras, por ejemplo: Ana Rojas.")
    simbolos = [ch for ch in limpio if not ch.isalpha() and ch not in " -'."]
    if simbolos:
        raise ValueError(f"El nombre '{limpio}' tiene símbolos ({' '.join(sorted(set(simbolos)))}). "
                         "Escriba solo letras, por ejemplo: Ana Rojas.")
    if len(letras) < 3:
        raise ValueError(f"El nombre '{limpio}' es muy corto. Escriba al menos 3 letras, por ejemplo: Ana Rojas.")
    return limpio.title()


def es_forma_solida(forma_farmaceutica):
    """True si es tableta, comprimido, cápsula o gragea (lo que cabe en el SPD)."""
    forma = normalizar(forma_farmaceutica).upper()
    return any(palabra in forma for palabra in PALABRAS_FORMA_SOLIDA)


def validar_forma_solida(forma_farmaceutica):
    """Solo los sólidos orales (tabletas, comprimidos, cápsulas) van en el pastillero."""
    if not es_forma_solida(forma_farmaceutica):
        raise ValueError(
            f"Este medicamento es '{forma_farmaceutica.lower()}'. En el pastillero solo van "
            "tabletas, comprimidos, cápsulas o grageas. Elija otra presentación."
        )
    return forma_farmaceutica


def validar_dosis(texto, forma_farmaceutica=""):
    """
    Unidades por toma. Acepta 1, 2, 0.5, 0,5, 1/2, 1 1/2 o 1,5.
    Debe ser múltiplo de 1/4 (lo más pequeño que se puede partir una tableta).
    """
    limpio = " ".join(texto.replace(",", ".").split())
    if limpio == "":
        raise ValueError("Escriba la dosis por toma. Ejemplos: 1, 2, 1/2 o 0,5.")

    try:
        partes = limpio.split(" ")
        if len(partes) > 2:
            raise ValueError
        dosis = 0.0
        for parte in partes:
            if "/" in parte:
                numerador, denominador = parte.split("/")
                dosis += float(numerador) / float(denominador)
            else:
                dosis += float(parte)
    except ZeroDivisionError:
        raise ValueError(f"'{texto}' divide entre cero. Escriba una fracción como 1/2 o 1/4.")
    except ValueError:
        raise ValueError(f"'{texto}' no es una dosis. Escriba un número como 1, 2, 1/2 o 0,5.")

    # float() acepta "nan" e "inf" como números: aquí los cerramos.
    if not math.isfinite(dosis):
        raise ValueError(f"'{texto}' no es una dosis. Escriba un número como 1, 2, 1/2 o 0,5.")
    if dosis <= 0:
        raise ValueError(f"La dosis debe ser mayor que cero. Recibí {texto}.")
    if dosis > DOSIS_MAXIMA_POR_TOMA:
        raise ValueError(f"{texto} unidades por toma es demasiado. El máximo es {DOSIS_MAXIMA_POR_TOMA}.")
    if (dosis * 4) != int(dosis * 4):
        raise ValueError(f"No se puede partir una tableta en {texto}. Use enteros, mitades (1/2) o cuartos (1/4).")

    forma = normalizar(forma_farmaceutica).upper()
    if dosis != int(dosis) and any(palabra in forma for palabra in PALABRAS_NO_PARTIBLE):
        raise ValueError(
            f"Este medicamento es '{forma_farmaceutica.lower()}' y no se debe partir. "
            "Use una dosis entera (1, 2, 3...)."
        )
    return dosis


def validar_unidades_envase(texto):
    """Cuántas unidades (tabletas/cápsulas) tiene el paciente. Entero de 1 a 1000."""
    limpio = texto.strip()
    if limpio == "":
        raise ValueError("Escriba cuántas tabletas o cápsulas tiene el paciente (ej.: 30).")
    try:
        unidades = int(limpio)
    except ValueError:
        raise ValueError(f"'{texto}' no es una cantidad. Escriba un número entero, por ejemplo 30.")
    if unidades <= 0:
        raise ValueError(f"La cantidad debe ser mayor que cero. Recibí {unidades}.")
    if unidades > UNIDADES_MAXIMAS_ENVASE:
        raise ValueError(f"{unidades} unidades es demasiado. El máximo es {UNIDADES_MAXIMAS_ENVASE}.")
    return unidades


def validar_seleccion(lista, que_es):
    """Revisa que el usuario marcó al menos una opción (tomas o días)."""
    if len(lista) == 0:
        raise ValueError(f"Marque al menos {que_es}.")
    return lista


def validar_no_repetido(registro, pastillero):
    """Evita meter dos veces el mismo medicamento en el pastillero."""
    for medicamento in pastillero:
        if medicamento["registro"] == registro:
            raise ValueError(
                f"{medicamento['nombre']} ya está en el pastillero. "
                "Si cambió la dosis, vacíe el pastillero y vuelva a agregarlo."
            )
    return registro
