import tkinter as tk
from tkinter import messagebox, font, ttk   # ttk se mantiene por si en el futuro usas widgets ttk

# ------------------- CLASE NODO -------------------
class Nodo:
    def __init__(self, codigo, nombre, categoria, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.siguiente = None

# ------------------- CLASE LISTA ENLAZADA -------------------
class ListaEnlazada:
    def __init__(self):
        self.cabeza = None

    # ---------- CRUD ----------
    def insertar_producto(self, codigo, nombre, categoria, precio, stock):
        """Inserta un nuevo producto al final de la lista."""
        nuevo = Nodo(codigo, nombre, categoria, precio, stock)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo

    def buscar_nodo(self, codigo):
        actual = self.cabeza
        while actual:
            if actual.codigo == codigo:
                return actual
            actual = actual.siguiente
        return None

    def actualizar_producto(self, codigo, nombre=None, categoria=None,
                            precio=None, stock=None):
        nodo = self.buscar_nodo(codigo)
        if not nodo:
            return False
        if nombre is not None:
            nodo.nombre = nombre
        if categoria is not None:
            nodo.categoria = categoria
        if precio is not None:
            nodo.precio = precio
        if stock is not None:
            nodo.stock = stock
        return True

    def eliminar_producto(self, codigo):
        actual, anterior = self.cabeza, None
        while actual:
            if actual.codigo == codigo:
                if anterior:
                    anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                return True
            anterior, actual = actual, actual.siguiente
        return False

    # ---------- Inventario ----------
    def ajustar_stock(self, codigo, cantidad):
        """Suma (entrada) o resta (salida) stock."""
        nodo = self.buscar_nodo(codigo)
        if not nodo:
            return False
        if nodo.stock + cantidad < 0:
            return False
        nodo.stock += cantidad
        return True

    # ---------- Helper para UI ----------
    def _to_list(self):
        productos, actual = [], self.cabeza
        while actual:
            productos.append({
                "codigo": actual.codigo,
                "nombre": actual.nombre,
                "categoria": actual.categoria,
                "precio": actual.precio,
                "stock": actual.stock
            })
            actual = actual.siguiente
        return productos

    # ---------- Ordenar ----------
    def ordenar(self, criterio):
        productos = self._to_list()
        if criterio == "nombre":
            productos.sort(key=lambda x: x["nombre"].lower())
        elif criterio == "precio":
            productos.sort(key=lambda x: x["precio"])
        elif criterio == "categoria":
            productos.sort(key=lambda x: x["categoria"].lower())
        elif criterio == "stock":
            productos.sort(key=lambda x: x["stock"])
        return productos

    # ---------- Filtrar ----------
    def filtrar(self, nombre_substr="", categoria=""):
        nombre_substr, categoria = nombre_substr.lower(), categoria.lower()
        return [
            p for p in self._to_list()
            if (nombre_substr in p["nombre"].lower())
            and (categoria in p["categoria"].lower())
        ]

# ------------------- CLASE APP TKINTER -------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Productos Escolares")
        self.root.configure(bg="#1a1a1a")
        self.root.option_add("*Font", "Helvetica 11")

        self.lista = ListaEnlazada()
        self.titulo_font = font.Font(family="Helvetica", size=16, weight="bold")

        tk.Label(root, text="GESTOR DE PRODUCTOS ESCOLARES",
                 fg="#00ffcc", bg="#1a1a1a", font=self.titulo_font).pack(pady=10)

        # --------- Área de resultados ---------
        self.resultado = tk.Text(root, height=13, width=80,
                                 bg="#262626", fg="#00ffcc",
                                 insertbackground="white")
        self.resultado.pack(pady=10)

        # --------- Barra de botones principal ---------
        barra = tk.Frame(root, bg="#1a1a1a")
        barra.pack(pady=5)

        self._btn(barra, "Insertar", self.ventana_insertar)
        self._btn(barra, "Editar", self.ventana_editar)
        self._btn(barra, "Mostrar", self.mostrar_productos)
        self._btn(barra, "Eliminar", self.ventana_eliminar)
        self._btn(barra, "Entrada Stock", self.ventana_entrada)
        self._btn(barra, "Salida Stock", self.ventana_salida)
        self._btn(barra, "Filtrar", self.ventana_filtrar)

        # Ordenamientos
        self._btn(barra, "Ord. Nombre", lambda: self.ordenar("nombre"), bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Precio", lambda: self.ordenar("precio"), bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Categoría", lambda: self.ordenar("categoria"), bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Stock", lambda: self.ordenar("stock"), bg="#0099cc", fg="white")

        # --------- Contenedor para formularios dinámicos ---------
        self.frm = tk.Frame(root, bg="#1a1a1a")
        self.frm.pack(pady=10)

    # ------------ UTILS ------------
    def _btn(self, parent, text, cmd, bg="#00cc99", fg="black"):
        """Botón de la barra principal (usa pack)."""
        tk.Button(parent, text=text, command=cmd, width=12, bg=bg, fg=fg).pack(side=tk.LEFT, padx=4)

    def _vaciar_frm(self):
        for w in self.frm.winfo_children():
            w.destroy()

    def _mostrar_lista(self, lista):
        self.resultado.delete(1.0, tk.END)
        if not lista:
            self.resultado.insert(tk.END, "No hay productos.")
        else:
            for p in lista:
                self.resultado.insert(
                    tk.END,
                    f"Código: {p['codigo']} | Nombre: {p['nombre']} | "
                    f"Categoría: {p['categoria']} | "
                    f"Precio: ${p['precio']:.2f} | Stock: {p['stock']}\n"
                )

    # ------------ CRUD ------------
    def ventana_insertar(self):
        self._vaciar_frm()

        labels = ["Código (numérico):", "Nombre:", "Categoría:",
                  "Precio (decimal):", "Stock (entero):"]
        entries = []
        for i, lbl in enumerate(labels):
            tk.Label(self.frm, text=lbl, bg="#1a1a1a", fg="white")\
              .grid(row=i, column=0, sticky="e", padx=4, pady=4)
            e = tk.Entry(self.frm, width=25)
            e.grid(row=i, column=1, padx=4, pady=4)
            entries.append(e)

        def insertar():
            codigo, nombre, categoria, precio_t, stock_t = [e.get().strip() for e in entries]

            if not all([codigo, nombre, categoria, precio_t, stock_t]):
                messagebox.showerror("Error", "Todos los datos son obligatorios.")
                return
            if not codigo.isdigit():
                messagebox.showerror("Error", "Código numérico inválido.")
                return
            if not stock_t.isdigit():
                messagebox.showerror("Error", "Stock debe ser entero.")
                return
            try:
                precio = float(precio_t)
            except ValueError:
                messagebox.showerror("Error", "Precio inválido.")
                return

            self.lista.insertar_producto(codigo, nombre, categoria, precio, int(stock_t))
            messagebox.showinfo("Éxito", "Producto agregado.")
            for e in entries: e.delete(0, tk.END)

        # Botón "Agregar Producto" (GRID para no mezclar gestores)
        btn_insertar = tk.Button(self.frm, text="Agregar Producto",
                                 bg="#00cc99", fg="black", width=20,
                                 command=insertar)
        btn_insertar.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def ventana_editar(self):
        self._vaciar_frm()

        tk.Label(self.frm, text="Código del producto:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ent_codigo = tk.Entry(self.frm, width=25)
        ent_codigo.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Nuevo Nombre:", bg="#1a1a1a", fg="white")\
          .grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ent_nombre = tk.Entry(self.frm, width=25)
        ent_nombre.grid(row=1, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Nueva Categoría:", bg="#1a1a1a", fg="white")\
          .grid(row=2, column=0, sticky="e", padx=4, pady=4)
        ent_categoria = tk.Entry(self.frm, width=25)
        ent_categoria.grid(row=2, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Nuevo Precio:", bg="#1a1a1a", fg="white")\
          .grid(row=3, column=0, sticky="e", padx=4, pady=4)
        ent_precio = tk.Entry(self.frm, width=25)
        ent_precio.grid(row=3, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Nuevo Stock:", bg="#1a1a1a", fg="white")\
          .grid(row=4, column=0, sticky="e", padx=4, pady=4)
        ent_stock = tk.Entry(self.frm, width=25)
        ent_stock.grid(row=4, column=1, padx=4, pady=4)

        def editar():
            codigo = ent_codigo.get().strip()
            if not codigo:
                messagebox.showerror("Error", "Código requerido.")
                return
            if not codigo.isdigit():
                messagebox.showerror("Error", "Código numérico inválido.")
                return

            kwargs = {}
            if ent_nombre.get().strip():
                kwargs["nombre"] = ent_nombre.get().strip()
            if ent_categoria.get().strip():
                kwargs["categoria"] = ent_categoria.get().strip()
            if ent_precio.get().strip():
                try:
                    kwargs["precio"] = float(ent_precio.get().strip())
                except ValueError:
                    messagebox.showerror("Error", "Precio inválido.")
                    return
            if ent_stock.get().strip():
                if not ent_stock.get().strip().isdigit():
                    messagebox.showerror("Error", "Stock debe ser entero.")
                    return
                kwargs["stock"] = int(ent_stock.get().strip())

            if not kwargs:
                messagebox.showinfo("Aviso", "Nada que actualizar.")
                return

            if self.lista.actualizar_producto(codigo, **kwargs):
                messagebox.showinfo("Éxito", "Producto actualizado.")
                self.mostrar_productos()
            else:
                messagebox.showerror("Error", "Producto no encontrado.")

        btn_act = tk.Button(self.frm, text="Actualizar",
                            bg="#00cc99", fg="black", width=20,
                            command=editar)
        btn_act.grid(row=5, column=0, columnspan=2, pady=10)

    def ventana_eliminar(self):
        self._vaciar_frm()
        tk.Label(self.frm, text="Código a eliminar:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ent_codigo = tk.Entry(self.frm, width=25)
        ent_codigo.grid(row=0, column=1, padx=4, pady=4)

        def eliminar():
            codigo = ent_codigo.get().strip()
            if not codigo or not codigo.isdigit():
                messagebox.showerror("Error", "Código inválido.")
                return
            if messagebox.askyesno("Confirmar", "¿Eliminar producto?"):
                if self.lista.eliminar_producto(codigo):
                    messagebox.showinfo("Éxito", "Producto eliminado.")
                    self.mostrar_productos()
                else:
                    messagebox.showerror("Error", "Producto no encontrado.")

        btn_del = tk.Button(self.frm, text="Eliminar",
                            bg="#00cc99", fg="black", width=20,
                            command=eliminar)
        btn_del.grid(row=1, column=0, columnspan=2, pady=10)

    # ------------ INVENTARIO ------------
    def ventana_entrada(self):   # aumentar stock
        self._ajustar_stock("+ Entrada", +1)

    def ventana_salida(self):    # disminuir stock
        self._ajustar_stock("- Salida", -1)

    def _ajustar_stock(self, titulo, signo):
        self._vaciar_frm()
        tk.Label(self.frm, text=f"Código ({titulo}):", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ent_codigo = tk.Entry(self.frm, width=25)
        ent_codigo.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Cantidad:", bg="#1a1a1a", fg="white")\
          .grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ent_cant = tk.Entry(self.frm, width=25)
        ent_cant.grid(row=1, column=1, padx=4, pady=4)

        def ajustar():
            codigo = ent_codigo.get().strip()
            cant = ent_cant.get().strip()
            if not codigo.isdigit() or not cant.isdigit():
                messagebox.showerror("Error", "Datos numéricos inválidos.")
                return
            cantidad = int(cant) * signo
            if self.lista.ajustar_stock(codigo, cantidad):
                messagebox.showinfo("Éxito", "Stock actualizado.")
                self.mostrar_productos()
            else:
                messagebox.showerror("Error", "Operación no válida.")

        btn_apl = tk.Button(self.frm, text="Aplicar",
                            bg="#00cc99", fg="black", width=20,
                            command=ajustar)
        btn_apl.grid(row=2, column=0, columnspan=2, pady=10)

    # ------------ FILTRO ------------
    def ventana_filtrar(self):
        self._vaciar_frm()
        tk.Label(self.frm, text="Nombre contiene:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ent_nombre = tk.Entry(self.frm, width=25)
        ent_nombre.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Categoría contiene:", bg="#1a1a1a", fg="white")\
          .grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ent_categoria = tk.Entry(self.frm, width=25)
        ent_categoria.grid(row=1, column=1, padx=4, pady=4)

        def filtrar():
            nombre_s = ent_nombre.get().strip()
            cat_s = ent_categoria.get().strip()
            productos = self.lista.filtrar(nombre_s, cat_s)
            self._mostrar_lista(productos)

        btn_fil = tk.Button(self.frm, text="Filtrar",
                            bg="#00cc99", fg="black", width=20,
                            command=filtrar)
        btn_fil.grid(row=2, column=0, columnspan=2, pady=10)

    # ------------ ORDENAR / MOSTRAR ------------
    def ordenar(self, criterio):
        self._vaciar_frm()
        self._mostrar_lista(self.lista.ordenar(criterio))

    def mostrar_productos(self):
        self._vaciar_frm()
        self._mostrar_lista(self.lista._to_list())

# ------------------- EJECUTAR APP -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
