import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def resolver_sistema(A, b):
    # Gauss-Jordan
    n = len(b)
    M = [A[i][:] + [b[i]] for i in range(n)]

    for col in range(n):
        # pivote mas grande para no dividir por cero
        fila_max = col
        for i in range(col + 1, n):
            if abs(M[i][col]) > abs(M[fila_max][col]):
                fila_max = i
        if abs(M[fila_max][col]) < 1e-12:
            raise ValueError("El sistema no tiene solucion unica")
        M[col], M[fila_max] = M[fila_max], M[col]

        piv = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= piv

        for i in range(n):
            if i != col:
                factor = M[i][col]
                for j in range(col, n + 1):
                    M[i][j] -= factor * M[col][j]

    return [M[i][n] for i in range(n)]


def regresion(xs, ys, grado):
    n = grado + 1
    A = [[sum(x ** (i + j) for x in xs) for j in range(n)] for i in range(n)]
    b = [sum(y * x ** i for x, y in zip(xs, ys)) for i in range(n)]
    return resolver_sistema(A, b)


def evaluar(coef, x):
    r = 0
    for c in reversed(coef):
        r = r * x + c
    return r


def coef_determinacion(xs, ys, coef):
    media = sum(ys) / len(ys)
    St = sum((y - media) ** 2 for y in ys)
    Sr = sum((y - evaluar(coef, x)) ** 2 for x, y in zip(xs, ys))
    if St == 0:
        return 1.0
    return (St - Sr) / St


def texto_funcion(coef):
    partes = []
    for i, c in enumerate(coef):
        signo = "-" if c < 0 else "+"
        valor = abs(c)
        if i == 0:
            t = f"{valor:.4f}"
        elif i == 1:
            t = f"{valor:.4f}x"
        else:
            t = f"{valor:.4f}x^{i}"
        partes.append((signo, t))
    s = ("-" if partes[0][0] == "-" else "") + partes[0][1]
    for signo, t in partes[1:]:
        s += f" {signo} {t}"
    return "y = " + s


class App:
    def __init__(self, root):
        self.root = root
        root.title("Proyecto de Reposicion - Matematicas Computacionales")
        root.geometry("900x650")

        arriba = ttk.Frame(root, padding=10)
        arriba.pack(fill="x")

        ttk.Label(arriba, text="Ingresa los puntos (uno por linea, formato x,y):").pack(anchor="w")

        self.caja = tk.Text(arriba, height=8, width=30)
        self.caja.pack(side="left", pady=5)
        self.caja.insert("1.0", "1,2.1\n2,3.9\n3,9.2\n4,15.8\n5,26.1\n6,37.9\n7,52.3")

        botones = ttk.Frame(arriba, padding=10)
        botones.pack(side="left", anchor="n")
        ttk.Button(botones, text="Calcular regresiones", command=self.calcular).pack(fill="x", pady=2)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(fill="x", pady=2)

        self.pestanas = ttk.Notebook(root)
        self.pestanas.pack(fill="both", expand=True, padx=10, pady=10)

    def limpiar(self):
        self.caja.delete("1.0", "end")
        for tab in self.pestanas.tabs():
            self.pestanas.forget(tab)

    def leer_puntos(self):
        xs, ys = [], []
        for num, linea in enumerate(self.caja.get("1.0", "end").splitlines(), 1):
            linea = linea.strip()
            if not linea:
                continue
            try:
                a, b = linea.replace(";", ",").split(",")
                xs.append(float(a))
                ys.append(float(b))
            except ValueError:
                raise ValueError(f"La linea {num} no es valida: '{linea}'")
        if len(xs) < 6:
            raise ValueError("Necesitas minimo 6 puntos")
        return xs, ys

    def calcular(self):
        try:
            xs, ys = self.leer_puntos()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        for tab in self.pestanas.tabs():
            self.pestanas.forget(tab)

        max_grado = len(set(xs)) - 1
        llego = False

        for grado in range(1, max_grado + 1):
            try:
                coef = regresion(xs, ys, grado)
            except ValueError as e:
                messagebox.showwarning("Aviso", f"Grado {grado}: {e}")
                break
            r2 = coef_determinacion(xs, ys, coef)
            self.mostrar_resultado(xs, ys, coef, grado, r2)
            if r2 >= 0.95:
                llego = True
                break

        if llego:
            self.pestanas.select(len(self.pestanas.tabs()) - 1)
        else:
            messagebox.showinfo("Resultado", "No se alcanzo R2 >= 0.95 con los grados posibles.")

    def mostrar_resultado(self, xs, ys, coef, grado, r2):
        tab = ttk.Frame(self.pestanas)
        self.pestanas.add(tab, text=f"Grado {grado}")

        ttk.Label(tab, text=texto_funcion(coef), font=("Arial", 12, "bold")).pack(pady=(10, 0))
        ttk.Label(tab, text=f"Coeficiente de determinacion R2 = {r2:.6f}", font=("Arial", 11)).pack()

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(xs, ys, color="red", label="Puntos", zorder=3)

        xmin, xmax = min(xs), max(xs)
        paso = (xmax - xmin) / 200
        cx = [xmin + i * paso for i in range(201)]
        cy = [evaluar(coef, x) for x in cx]
        ax.plot(cx, cy, label=f"Polinomio grado {grado}")

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(f"Regresion de grado {grado}")
        ax.grid(True, alpha=0.3)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()