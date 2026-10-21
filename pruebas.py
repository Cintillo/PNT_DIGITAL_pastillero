"""
pruebas.py — comprueba lo que los validadores aceptan y lo que rechazan.

Correr con:  python3 pruebas.py
Debe terminar con: Todas las pruebas pasaron.
"""

from validaciones import (
    validar_dosis,
    validar_forma_solida,
    validar_nombre_paciente,
    validar_unidades_envase,
)


def rechaza(funcion, *argumentos):
    """True si la función lanza ValueError con esos argumentos."""
    try:
        funcion(*argumentos)
    except ValueError:
        return True
    return False


def probar():
    # Lo que SÍ debe aceptar
    assert validar_nombre_paciente("  ana   rojas ") == "Ana Rojas"
    assert validar_dosis("1") == 1
    assert validar_dosis("0,5", "TABLETA") == 0.5
    assert validar_dosis("1/2", "TABLETA") == 0.5
    assert validar_dosis("1 1/2", "TABLETA") == 1.5
    assert validar_unidades_envase(" 30 ") == 30
    assert validar_forma_solida("CÁPSULA") == "CÁPSULA"
    assert validar_forma_solida("GRAGEA") == "GRAGEA"
    assert validar_dosis("12") == 12                           # el máximo por toma

    # Lo que debe RECHAZAR
    assert rechaza(validar_nombre_paciente, "   ")
    assert rechaza(validar_nombre_paciente, "Jo")
    assert rechaza(validar_nombre_paciente, "Ana 123")
    assert rechaza(validar_nombre_paciente, "#$#$@")           # sin letras
    assert rechaza(validar_nombre_paciente, "Ana@Rojas")       # con símbolos
    assert rechaza(validar_dosis, "")
    assert rechaza(validar_dosis, "13")                        # más de 12 por toma
    assert rechaza(validar_dosis, "dos")
    assert rechaza(validar_dosis, "-1")
    assert rechaza(validar_dosis, "0")
    assert rechaza(validar_dosis, "1/0")
    assert rechaza(validar_dosis, "nan")
    assert rechaza(validar_dosis, "0,3")                       # no se parte en tercios
    assert rechaza(validar_dosis, "1/2", "CÁPSULA")            # las cápsulas no se parten
    assert rechaza(validar_dosis, "1/2", "TABLETA DE LIBERACIÓN PROLONGADA")
    assert rechaza(validar_unidades_envase, "30.5")
    assert rechaza(validar_unidades_envase, "-5")
    assert rechaza(validar_unidades_envase, "treinta")
    assert rechaza(validar_forma_solida, "JARABE")
    assert rechaza(validar_forma_solida, "SOLUCIÓN INYECTABLE")

    print("Todas las pruebas pasaron.")


if __name__ == "__main__":
    probar()
