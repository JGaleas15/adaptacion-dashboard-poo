import os
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional


# =========================
#  Utilidades
# =========================
def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\nPresiona Enter para continuar...")


def base_proyecto() -> str:
    return os.path.dirname(os.path.abspath(__file__))


# =========================
#  Dashboard: ver/ejecutar scripts
# =========================
def mostrar_codigo(ruta_script: str) -> Optional[str]:
    ruta_abs = os.path.abspath(ruta_script)
    try:
        with open(ruta_abs, "r", encoding="utf-8") as archivo:
            codigo = archivo.read()
        print(f"\n--- Código de {ruta_abs} ---\n")
        print(codigo)
        return codigo
    except FileNotFoundError:
        print("El archivo no se encontró.")
        return None
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return None


def ejecutar_codigo(ruta_script: str):
    ruta_abs = os.path.abspath(ruta_script)
    if not os.path.exists(ruta_abs):
        print("No existe ese archivo para ejecutar.")
        return

    try:
        if os.name == "nt":
            # En Windows, abrir una nueva consola y ejecutar con py
            subprocess.Popen(["cmd", "/k", "py", ruta_abs])
        else:
            subprocess.Popen(["xterm", "-hold", "-e", "python3", ruta_abs])
    except Exception as e:
        print(f"Ocurrió un error al ejecutar el código: {e}")


def listar_scripts(carpeta: str) -> List[str]:
    if not os.path.isdir(carpeta):
        return []
    archivos = []
    for f in os.listdir(carpeta):
        if f.endswith(".py") and f.lower() != "dashboard.py":
            archivos.append(f)
    archivos.sort()
    return archivos


def menu_unidades(base: str):
    unidades = {
        "1": os.path.join(base, "UNIDAD 1"),
        "2": os.path.join(base, "UNIDAD 2"),
    }

    while True:
        limpiar()
        print("=== UNIDADES ===")
        print("1) UNIDAD 1")
        print("2) UNIDAD 2")
        print("0) Volver")
        op = input("\nOpción: ").strip()

        if op == "0":
            return

        carpeta = unidades.get(op)
        if not carpeta or not os.path.isdir(carpeta):
            print("\nNo existe esa carpeta.")
            pausar()
            continue

        scripts = listar_scripts(carpeta)
        if not scripts:
            print("\nNo hay scripts .py en esa unidad.")
            pausar()
            continue

        while True:
            limpiar()
            print(f"=== UNIDAD {op} ===\n")
            for i, s in enumerate(scripts, 1):
                print(f"{i}) {s}")
            print("0) Volver")

            elec = input("\nElige script: ").strip()
            if elec == "0":
                break

            try:
                idx = int(elec)
                if idx < 1 or idx > len(scripts):
                    raise ValueError
            except ValueError:
                print("\nOpción inválida.")
                pausar()
                continue

            ruta_script = os.path.join(carpeta, scripts[idx - 1])

            while True:
                limpiar()
                print(f"Script: {scripts[idx - 1]}\n")
                print("1) Mostrar código")
                print("2) Ejecutar script")
                print("0) Volver")
                acc = input("\nAcción: ").strip()

                if acc == "1":
                    mostrar_codigo(ruta_script)
                    pausar()
                elif acc == "2":
                    print("\nSe abrirá una consola para ejecutar el script...")
                    ejecutar_codigo(ruta_script)
                    pausar()
                elif acc == "0":
                    break
                else:
                    print("\nOpción inválida.")
                    pausar()


# =========================
#  Gestor de tareas (POO + JSON)
# =========================
@dataclass
class Tarea:
    id: int
    titulo: str
    descripcion: str
    proyecto: str
    prioridad: str            # Alta / Media / Baja
    fecha_limite: str         # YYYY-MM-DD o ""
    completada: bool = False
    creada_en: str = ""

    def __post_init__(self):
        if not self.creada_en:
            self.creada_en = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class GestorTareas:
    def __init__(self, archivo_json: str):
        self.archivo_json = archivo_json
        self.tareas: List[Tarea] = []
        self.cargar()

    def cargar(self):
        if not os.path.exists(self.archivo_json):
            self.tareas = []
            return
        try:
            with open(self.archivo_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tareas = [Tarea(**t) for t in data]
        except Exception:
            self.tareas = []

    def guardar(self):
        with open(self.archivo_json, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.tareas], f, ensure_ascii=False, indent=2)

    def nuevo_id(self) -> int:
        return (max(t.id for t in self.tareas) + 1) if self.tareas else 1

    @staticmethod
    def validar_prioridad(p: str) -> str:
        p = p.strip().capitalize()
        return p if p in ["Alta", "Media", "Baja"] else "Media"

    @staticmethod
    def validar_fecha(fecha: str) -> str:
        fecha = fecha.strip()
        if not fecha:
            return ""
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
            return fecha
        except ValueError:
            return ""

    def agregar(self, titulo: str, descripcion: str, proyecto: str, prioridad: str, fecha_limite: str):
        t = Tarea(
            id=self.nuevo_id(),
            titulo=titulo.strip(),
            descripcion=descripcion.strip(),
            proyecto=proyecto.strip() if proyecto.strip() else "POO",
            prioridad=self.validar_prioridad(prioridad),
            fecha_limite=self.validar_fecha(fecha_limite),
        )
        self.tareas.append(t)
        self.guardar()

    def listar(self, solo_pendientes: bool = False) -> List[Tarea]:
        tareas = self.tareas if not solo_pendientes else [t for t in self.tareas if not t.completada]
        prioridad_orden = {"Alta": 1, "Media": 2, "Baja": 3}
        return sorted(
            tareas,
            key=lambda t: (t.completada, prioridad_orden.get(t.prioridad, 2), t.fecha_limite or "9999-12-31")
        )

    def completar(self, tid: int) -> bool:
        for t in self.tareas:
            if t.id == tid:
                t.completada = True
                self.guardar()
                return True
        return False

    def eliminar(self, tid: int) -> bool:
        antes = len(self.tareas)
        self.tareas = [t for t in self.tareas if t.id != tid]
        if len(self.tareas) != antes:
            self.guardar()
            return True
        return False


def imprimir_tareas(tareas: List[Tarea]):
    limpiar()
    print("=== TAREAS ===\n")
    if not tareas:
        print("No hay tareas registradas.")
        return
    for t in tareas:
        estado = "✅" if t.completada else "⏳"
        limite = t.fecha_limite if t.fecha_limite else "-"
        print(f"[{estado}] ID:{t.id} | {t.titulo}")
        print(f"    Proyecto: {t.proyecto} | Prioridad: {t.prioridad} | Límite: {limite}")
        if t.descripcion:
            print(f"    Desc: {t.descripcion}")
        print(f"    Creada: {t.creada_en}")
        print("-" * 60)


def menu_tareas(gestor: GestorTareas):
    while True:
        limpiar()
        print("=== GESTOR DE TAREAS / PROYECTOS ===")
        print("1) Agregar tarea")
        print("2) Listar todas")
        print("3) Listar pendientes")
        print("4) Marcar como completada")
        print("5) Eliminar tarea")
        print("0) Volver")
        op = input("\nOpción: ").strip()

        if op == "1":
            titulo = input("Título: ")
            descripcion = input("Descripción: ")
            proyecto = input("Proyecto (Unidad 1/Unidad 2/Taller/Examen): ")
            prioridad = input("Prioridad (Alta/Media/Baja): ")
            fecha = input("Fecha límite (YYYY-MM-DD) o vacío: ")
            gestor.agregar(titulo, descripcion, proyecto, prioridad, fecha)
            print("\nTarea agregada.")
            pausar()

        elif op == "2":
            imprimir_tareas(gestor.listar(False))
            pausar()

        elif op == "3":
            imprimir_tareas(gestor.listar(True))
            pausar()

        elif op == "4":
            try:
                tid = int(input("ID a completar: ").strip())
                ok = gestor.completar(tid)
                print("\nCompletada." if ok else "\nNo existe ese ID.")
            except ValueError:
                print("\nID inválido.")
            pausar()

        elif op == "5":
            try:
                tid = int(input("ID a eliminar: ").strip())
                ok = gestor.eliminar(tid)
                print("\nEliminada." if ok else "\nNo existe ese ID.")
            except ValueError:
                print("\nID inválido.")
            pausar()

        elif op == "0":
            break

        else:
            print("\nOpción inválida.")
            pausar()


# =========================
#  MAIN
# =========================
def main():
    base = base_proyecto()
    gestor = GestorTareas(os.path.join(base, "tareas.json"))

    while True:
        limpiar()
        print("=== DASHBOARD - POO ===")
        print("1) Navegar Unidades (ver/ejecutar scripts)")
        print("2) Gestor de Tareas / Proyectos (POO + JSON)")
        print("3) Ver ruta del proyecto")
        print("0) Salir")
        op = input("\nOpción: ").strip()

        if op == "1":
            menu_unidades(base)
        elif op == "2":
            menu_tareas(gestor)
        elif op == "3":
            print(f"\nRuta:\n{base}")
            pausar()
        elif op == "0":
            break
        else:
            print("\nOpción inválida.")
            pausar()


if __name__ == "__main__":
    main()
