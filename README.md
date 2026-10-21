# 💊 Pastillero semanal con el catálogo LOMET

App de Streamlit para farmacias y cuidadores en Costa Rica. Permite buscar los
medicamentos de un paciente en el **Listado Oficial de Medicamentos (LOMET)** del
Ministerio de Salud (corte 31/12/2024), armar su pastillero semanal y calcular
para cuántos días alcanzan las tabletas y cuándo hay que reponer.

Tarea corta 3, opción B — Python Express II (FUNDATEC).

## Cómo se blindó

- **Validación con funciones propias** (`validaciones.py`): cada dato tiene su
  función, que lanza `raise ValueError("mensaje claro")` cuando el dato no sirve.
- **Excepciones específicas**: `ValueError`, `KeyError`, `ZeroDivisionError`,
  `FileNotFoundError` y `UnicodeDecodeError`. Nunca `except:` solo.
- **Reglas de farmacia**: el buscador solo ofrece sólidos orales que caben en el
  SPD (tabletas, comprimidos, cápsulas y grageas; no jarabes, inyectables ni
  geles), la dosis va de ¼ a 12 unidades por toma y se parte como máximo en
  cuartos, y las cápsulas o tabletas de liberación prolongada/entéricas no se
  pueden partir.
- **Pruebas**: `python3 pruebas.py` corre los `assert` de los validadores.

## Datos

- `datos/lomet_dic_2024.pdf`: el listado LOMET original del Ministerio de Salud
  (corte 31/12/2024), tal como se publica.
- `datos/lomet_dic_2024.csv`: el mismo listado pasado a CSV, que es lo que lee la app.

## Correrla en su computadora

```
pip install -r requirements.txt
streamlit run app.py
```
