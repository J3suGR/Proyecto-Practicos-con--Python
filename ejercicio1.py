import tkinter as tk
from tkinter import messagebox, font, ttk   # Herramientas GUI (ttk reservado para futuras mejoras)

# ======================================================================
#  CLASE NODO
# ======================================================================
class Nodo:
    """Representa un producto y su enlace al siguiente nodo."""
    def __init__(self, codigo, nombre, categoria, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.siguiente = None   # Apuntará al siguiente producto


# ======================================================================
#  CLASE LISTA ENLAZADA
# ======================================================================
class ListaEnlazada:
    """Gestiona los productos mediante una lista enlazada simple."""
    def __init__(self):
        self.cabeza = None   # Primer nodo

    # ----------------------- CRUD -----------------------
    def insertar_producto(self, codigo, nombre, categoria, precio, stock):
        """
        Inserta un producto al final. Devuelve False si el código ya existe.
        """
        if self.buscar_nodo(codigo):
            return False
        nuevo = Nodo(codigo, nombre, categoria, precio, stock)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        return True

    def buscar_nodo(self, codigo):
        """Devuelve el nodo con ese código o None."""
        actual = self.cabeza
        while actual:
            if actual.codigo == codigo:
                return actual
            actual = actual.siguiente
        return None

    def actualizar_producto(self, codigo, nombre=None, categoria=None,
                            precio=None, stock=None):
        """Actualiza campos indicados del producto."""
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
        """Elimina un producto por su código."""
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

    # -------------------- Inventario --------------------
    def ajustar_stock(self, codigo, cantidad):
        """
        Modifica el stock (positivo: entrada, negativo: salida).
        Evita cantidades negativas.
        """
        nodo = self.buscar_nodo(codigo)
        if not nodo or nodo.stock + cantidad < 0:
            return False
        nodo.stock += cantidad
        return True

    # ------------------- Conversión -------------------
    def _to_list(self):
        """Devuelve los productos como lista de diccionarios."""
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

    # --------------------- Ordenar ---------------------
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

    # --------------------- Filtrar ---------------------
    def filtrar(self, codigo_substr="", nombre_substr="", categoria_substr=""):
        """
        Filtra productos cuyos campos contienen las subcadenas dadas.
        La búsqueda no distingue mayúsculas/minúsculas.
        """
        codigo_substr = codigo_substr.lower()
        nombre_substr = nombre_substr.lower()
        categoria_substr = categoria_substr.lower()

        return [
            p for p in self._to_list()
            if (codigo_substr in p["codigo"].lower())
            and (nombre_substr in p["nombre"].lower())
            and (categoria_substr in p["categoria"].lower())
        ]


# ======================================================================
#  CLASE APP (INTERFAZ GRÁFICA)
# ======================================================================
class App:
    def __init__(self, root):
        # -------- Configuración ventana --------
        self.root = root
        self.root.title("Gestor de Productos Escolares")
        self.root.configure(bg="#1a1a1a")
        self.root.option_add("*Font", "Helvetica 11")

        self.lista = ListaEnlazada()
        self.titulo_font = font.Font(family="Helvetica", size=16, weight="bold")

        # -------- Título ----------
        tk.Label(root, text="GESTOR DE PRODUCTOS ESCOLARES",
                 fg="#00ffcc", bg="#1a1a1a", font=self.titulo_font).pack(pady=10)

        # -------- Área de resultados ----------
        self.resultado = tk.Text(root, height=13, width=80,
                                 bg="#262626", fg="#00ffcc",
                                 insertbackground="white")
        self.resultado.pack(pady=10)

        # -------- Barra de botones ----------
        barra = tk.Frame(root, bg="#1a1a1a")
        barra.pack(pady=5)

        self._btn(barra, "Insertar", self.ventana_insertar)
        self._btn(barra, "Editar", self.ventana_editar)
        self._btn(barra, "Mostrar", self.mostrar_productos)
        self._btn(barra, "Eliminar", self.ventana_eliminar)
        self._btn(barra, "Entrada Stock", self.ventana_entrada)
        self._btn(barra, "Salida Stock", self.ventana_salida)
        self._btn(barra, "Filtrar", self.ventana_filtrar)

        self._btn(barra, "Ord. Nombre", lambda: self.ordenar("nombre"),
                  bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Precio", lambda: self.ordenar("precio"),
                  bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Categoría", lambda: self.ordenar("categoria"),
                  bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Stock", lambda: self.ordenar("stock"),
                  bg="#0099cc", fg="white")

        # -------- Marco para formularios ----------
        self.frm = tk.Frame(root, bg="#1a1a1a")
        self.frm.pack(pady=10)

    # ------------------ Auxiliares ------------------
    def _btn(self, parent, texto, comando, bg="#00cc99", fg="black"):
        tk.Button(parent, text=texto, command=comando, width=12, bg=bg, fg=fg)\
          .pack(side=tk.LEFT, padx=4)

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

    # ==================================================================
    #  Ventana Insertar
    # ==================================================================
    def ventana_insertar(self):
        self._vaciar_frm()
        etiquetas = ["Código (numérico):", "Nombre:", "Categoría:",
                     "Precio (decimal):", "Stock (entero):"]
        entradas = []
        for i, et in enumerate(etiquetas):
            tk.Label(self.frm, text=et, bg="#1a1a1a", fg="white")\
              .grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ent = tk.Entry(self.frm, width=25)
            ent.grid(row=i, column=1, padx=4, pady=4)
            entradas.append(ent)

        def insertar():
            codigo, nombre, categoria, precio_t, stock_t = [e.get().strip() for e in entradas]
            if not all([codigo, nombre, categoria, precio_t, stock_t]):
                messagebox.showerror("Error", "Todos los datos son obligatorios."); return
            if not codigo.isdigit():
                messagebox.showerror("Error", "Código numérico inválido."); return
            if not stock_t.isdigit():
                messagebox.showerror("Error", "Stock debe ser entero."); return
            try:
                precio = float(precio_t)
            except ValueError:
                messagebox.showerror("Error", "Precio inválido."); return
            if not self.lista.insertar_producto(codigo, nombre, categoria, precio, int(stock_t)):
                messagebox.showerror("Error", "Código duplicado."); return

            messagebox.showinfo("Éxito", "Producto agregado.")
            for e in entradas: e.delete(0, tk.END)
            self.mostrar_productos()

        tk.Button(self.frm, text="Agregar Producto", width=20,
                  bg="#00cc99", fg="black", command=insertar)\
          .grid(row=len(etiquetas), column=0, columnspan=2, pady=10)

    # ==================================================================
    #  Ventana Editar
    # ==================================================================
    def ventana_editar(self):
        self._vaciar_frm()
        tk.Label(self.frm, text="Código del producto:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        cod_e = tk.Entry(self.frm, width=25)
        cod_e.grid(row=0, column=1, padx=4, pady=4)

        labs = ["Nuevo nombre:", "Nueva categoría:", "Nuevo precio:", "Nuevo stock:"]
        ents = []
        for i, lab in enumerate(labs, start=1):
            tk.Label(self.frm, text=lab, bg="#1a1a1a", fg="white")\
              .grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ent = tk.Entry(self.frm, width=25)
            ent.grid(row=i, column=1, padx=4, pady=4)
            ents.append(ent)

        def editar():
            codigo = cod_e.get().strip()
            if not codigo:
                messagebox.showerror("Error", "Ingrese el código."); return
            nombre = ents[0].get().strip() or None
            categoria = ents[1].get().strip() or None
            precio = None
            if ents[2].get().strip():
                try: precio = float(ents[2].get().strip())
                except ValueError:
                    messagebox.showerror("Error", "Precio inválido."); return
            stock = None
            if ents[3].get().strip():
                if not ents[3].get().strip().isdigit():
                    messagebox.showerror("Error", "Stock debe ser entero."); return
                stock = int(ents[3].get().strip())

            if self.lista.actualizar_producto(codigo, nombre, categoria, precio, stock):
                messagebox.showinfo("Éxito", "Producto actualizado.")
                self.mostrar_productos()
            else:
                messagebox.showerror("Error", "Producto no encontrado.")

        tk.Button(self.frm, text="Actualizar", width=20,
                  bg="#00cc99", fg="black", command=editar)\
          .grid(row=len(labs)+1, column=0, columnspan=2, pady=10)

    # ==================================================================
    #  Ventana Eliminar
    # ==================================================================
    def ventana_eliminar(self):
        self._vaciar_frm()
        tk.Label(self.frm, text="Código a eliminar:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        cod_e = tk.Entry(self.frm, width=25)
        cod_e.grid(row=0, column=1, padx=4, pady=4)

        def eliminar():
            codigo = cod_e.get().strip()
            if not codigo:
                messagebox.showerror("Error", "Ingrese el código."); return
            if self.lista.eliminar_producto(codigo):
                messagebox.showinfo("Éxito", "Producto eliminado.")
                self.mostrar_productos()
            else:
                messagebox.showerror("Error", "Producto no encontrado.")

        tk.Button(self.frm, text="Eliminar", width=20,
                  bg="#cc3300", fg="white", command=eliminar)\
          .grid(row=1, column=0, columnspan=2, pady=10)

    # ==================================================================
    #  Formularios de Stock (Entrada / Salida)
    # ==================================================================
    def _form_stock(self, titulo_btn, signo):
        self._vaciar_frm()
        tk.Label(self.frm, text="Código:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        cod_e = tk.Entry(self.frm, width=25)
        cod_e.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Cantidad:", bg="#1a1a1a", fg="white")\
          .grid(row=1, column=0, sticky="e", padx=4, pady=4)
        cant_e = tk.Entry(self.frm, width=25)
        cant_e.grid(row=1, column=1, padx=4, pady=4)

        def ajustar():
            codigo, cant = cod_e.get().strip(), cant_e.get().strip()
            if not codigo or not cant or not cant.isdigit():
                messagebox.showerror("Error", "Datos inválidos."); return
            if self.lista.ajustar_stock(codigo, signo * int(cant)):
                messagebox.showinfo("Éxito", "Stock actualizado.")
                self.mostrar_productos()
            else:
                messagebox.showerror("Error", "Producto no encontrado o cantidad inválida.")

        tk.Button(self.frm, text=titulo_btn, width=20,
                  bg="#00cc99" if signo > 0 else "#cc3300",
                  fg="black" if signo > 0 else "white", command=ajustar)\
          .grid(row=2, column=0, columnspan=2, pady=10)

    def ventana_entrada(self):  # Aumentar
        self._form_stock("Agregar Stock", +1)

    def ventana_salida(self):   # Disminuir
        self._form_stock("Retirar Stock", -1)

    # ==================================================================
    #  Ventana Filtrar
    # ==================================================================
    def ventana_filtrar(self):
        self._vaciar_frm()
        labs = ["Código contiene:", "Nombre contiene:", "Categoría contiene:"]
        ents = []
        for i, lab in enumerate(labs):
            tk.Label(self.frm, text=lab, bg="#1a1a1a", fg="white")\
              .grid(row=i, column=0, sticky="e", padx=4, pady=4)
            ent = tk.Entry(self.frm, width=25)
            ent.grid(row=i, column=1, padx=4, pady=4)
            ents.append(ent)

        def filtrar():
            codigo_s = ents[0].get().strip()
            nombre_s = ents[1].get().strip()
            cat_s = ents[2].get().strip()
            filtrados = self.lista.filtrar(codigo_s, nombre_s, cat_s)
            self._mostrar_lista(filtrados)

        tk.Button(self.frm, text="Filtrar", width=20,
                  bg="#0099cc", fg="white", command=filtrar)\
          .grid(row=len(labs), column=0, columnspan=2, pady=10)

    # ==================================================================
    #  Mostrar y Ordenar
    # ==================================================================
    def mostrar_productos(self):
        self._vaciar_frm()
        self._mostrar_lista(self.lista._to_list())

    def ordenar(self, criterio):
        self._vaciar_frm()
        self._mostrar_lista(self.lista.ordenar(criterio))


# ======================================================================
#  EJECUCIÓN
# ======================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
