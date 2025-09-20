import tkinter as tk
from tkinter import messagebox, font, ttk   # Importamos herramientas para crear ventanas, cuadros de diálogo y estilos.

# ------------------- CLASE NODO -------------------
class Nodo:
    # Esta clase representa un producto individual con sus datos y un enlace al siguiente producto
    def __init__(self, codigo, nombre, categoria, precio, stock):
        self.codigo = codigo        # Código único para identificar el producto
        self.nombre = nombre        # Nombre del producto
        self.categoria = categoria  # Categoría o tipo del producto
        self.precio = precio        # Precio del producto
        self.stock = stock          # Cantidad disponible en inventario
        self.siguiente = None       # Apunta al siguiente producto en la lista (o nada si es el último)

# ------------------- CLASE LISTA ENLAZADA -------------------
class ListaEnlazada:
    # Esta clase administra la lista de productos como una cadena enlazada
    def __init__(self):
        self.cabeza = None  # Aquí se guarda el primer producto de la lista (si hay alguno)

    # ---------- FUNCIONES PARA AGREGAR, BUSCAR, MODIFICAR Y ELIMINAR PRODUCTOS ----------
    def insertar_producto(self, codigo, nombre, categoria, precio, stock):
        """
        Agrega un nuevo producto al final de la lista.
        Si ya existe un producto con ese código, no lo agrega.
        """
        if self.buscar_nodo(codigo):  # Busca si ya existe un producto con ese código
            return False             # Si existe, no se puede agregar (evitar duplicados)

        nuevo = Nodo(codigo, nombre, categoria, precio, stock)  # Crea un nuevo producto
        if self.cabeza is None:
            self.cabeza = nuevo     # Si la lista está vacía, el nuevo producto será el primero
        else:
            actual = self.cabeza
            while actual.siguiente:  # Busca el último producto en la lista
                actual = actual.siguiente
            actual.siguiente = nuevo # Añade el nuevo producto al final
        return True

    def buscar_nodo(self, codigo):
        # Busca un producto por su código, regresando el producto si lo encuentra, sino None
        actual = self.cabeza
        while actual:
            if actual.codigo == codigo:
                return actual
            actual = actual.siguiente
        return None

    def actualizar_producto(self, codigo, nombre=None, categoria=None, precio=None, stock=None):
        # Modifica la información de un producto si existe, cambiando solo los campos que se envían
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
        # Elimina un producto de la lista por su código
        actual, anterior = self.cabeza, None
        while actual:
            if actual.codigo == codigo:
                if anterior:
                    anterior.siguiente = actual.siguiente  # Salta el producto que se elimina
                else:
                    self.cabeza = actual.siguiente  # Si es el primero, cambia la cabeza de la lista
                return True
            anterior, actual = actual, actual.siguiente
        return False

    # ---------- FUNCIONES PARA MANEJAR EL INVENTARIO (SUMAR O RESTAR STOCK) ----------
    def ajustar_stock(self, codigo, cantidad):
        """
        Cambia la cantidad en stock de un producto:
        - si cantidad es positiva, aumenta el stock
        - si es negativa, disminuye el stock, pero no puede quedar negativo
        """
        nodo = self.buscar_nodo(codigo)
        if not nodo:
            return False
        if nodo.stock + cantidad < 0:
            return False
        nodo.stock += cantidad
        return True

    # ---------- FUNCIONES PARA CONVERTIR LA LISTA EN FORMATO USABLE POR LA INTERFAZ ----------
    def _to_list(self):
        # Convierte toda la lista enlazada a una lista normal de diccionarios con datos de productos
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

    # ---------- ORDENAR PRODUCTOS SEGÚN DISTINTO CRITERIO ----------
    def ordenar(self, criterio):
        # Devuelve una lista ordenada según nombre, precio, categoría o stock
        productos = self._to_list()
        if criterio == "nombre":
            productos.sort(key=lambda x: x["nombre"].lower())  # Orden alfabético del nombre
        elif criterio == "precio":
            productos.sort(key=lambda x: x["precio"])         # Orden numérico del precio
        elif criterio == "categoria":
            productos.sort(key=lambda x: x["categoria"].lower())  # Orden alfabético de categoría
        elif criterio == "stock":
            productos.sort(key=lambda x: x["stock"])          # Orden numérico del stock
        return productos

    # ---------- FILTRAR PRODUCTOS POR NOMBRE Y/O CATEGORÍA ----------
    def filtrar(self, nombre_substr="", categoria=""):
        # Devuelve productos cuyo nombre y categoría contienen los textos buscados (no importa mayúsculas)
        nombre_substr, categoria = nombre_substr.lower(), categoria.lower()
        return [
            p for p in self._to_list()
            if (nombre_substr in p["nombre"].lower())
            and (categoria in p["categoria"].lower())
        ]

# ------------------- CLASE APP TKINTER -------------------
class App:
    # Esta clase crea la ventana principal y controla la interacción con el usuario
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Productos Escolares")  # Título de la ventana
        self.root.configure(bg="#1a1a1a")                 # Color de fondo oscuro
        self.root.option_add("*Font", "Helvetica 11")     # Fuente general de texto

        self.lista = ListaEnlazada()                       # Aquí se guardan los productos
        self.titulo_font = font.Font(family="Helvetica", size=16, weight="bold")

        # Texto con el título grande y visible
        tk.Label(root, text="GESTOR DE PRODUCTOS ESCOLARES",
                 fg="#00ffcc", bg="#1a1a1a", font=self.titulo_font).pack(pady=10)

        # Área de texto donde se mostrarán los productos
        self.resultado = tk.Text(root, height=13, width=80,
                                 bg="#262626", fg="#00ffcc",
                                 insertbackground="white")
        self.resultado.pack(pady=10)

        # Barra con botones principales para acciones (insertar, editar, mostrar, etc)
        barra = tk.Frame(root, bg="#1a1a1a")
        barra.pack(pady=5)

        # Botones para distintas acciones
        self._btn(barra, "Insertar", self.ventana_insertar)
        self._btn(barra, "Editar", self.ventana_editar)
        self._btn(barra, "Mostrar", self.mostrar_productos)
        self._btn(barra, "Eliminar", self.ventana_eliminar)
        self._btn(barra, "Entrada Stock", self.ventana_entrada)
        self._btn(barra, "Salida Stock", self.ventana_salida)
        self._btn(barra, "Filtrar", self.ventana_filtrar)

        # Botones para ordenar la lista por diferentes criterios
        self._btn(barra, "Ord. Nombre", lambda: self.ordenar("nombre"), bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Precio", lambda: self.ordenar("precio"), bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Categoría", lambda: self.ordenar("categoria"), bg="#0099cc", fg="white")
        self._btn(barra, "Ord. Stock", lambda: self.ordenar("stock"), bg="#0099cc", fg="white")

        # Espacio donde se mostrarán los formularios para insertar, editar, eliminar, etc.
        self.frm = tk.Frame(root, bg="#1a1a1a")
        self.frm.pack(pady=10)

    # ------------ FUNCIONES AUXILIARES ------------
    def _btn(self, parent, text, cmd, bg="#00cc99", fg="black"):
        """Crea un botón con texto, color y acción definida."""
        tk.Button(parent, text=text, command=cmd, width=12, bg=bg, fg=fg).pack(side=tk.LEFT, padx=4)

    def _vaciar_frm(self):
        """Limpia el espacio donde se muestran los formularios (para que no se mezclen)."""
        for w in self.frm.winfo_children():
            w.destroy()

    def _mostrar_lista(self, lista):
        """Muestra en la ventana la lista de productos que se le pase."""
        self.resultado.delete(1.0, tk.END)  # Borra texto anterior
        if not lista:
            self.resultado.insert(tk.END, "No hay productos.")  # Si no hay productos
        else:
            for p in lista:
                self.resultado.insert(
                    tk.END,
                    f"Código: {p['codigo']} | Nombre: {p['nombre']} | "
                    f"Categoría: {p['categoria']} | "
                    f"Precio: ${p['precio']:.2f} | Stock: {p['stock']}\n"
                )

    # ------------ FUNCIONES PARA CADA VENTANA (INSERTAR, EDITAR, ELIMINAR, ETC.) ------------

    def ventana_insertar(self):
        """Formulario para añadir un nuevo producto."""
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
            # Leer los datos que puso el usuario
            codigo, nombre, categoria, precio_t, stock_t = [e.get().strip() for e in entries]

            # Verificar que no falte nada
            if not all([codigo, nombre, categoria, precio_t, stock_t]):
                messagebox.showerror("Error", "Todos los datos son obligatorios.")
                return
            # Validar que código y stock sean números enteros
            if not codigo.isdigit():
                messagebox.showerror("Error", "Código numérico inválido.")
                return
            if not stock_t.isdigit():
                messagebox.showerror("Error", "Stock debe ser entero.")
                return
            # Validar que precio sea un número decimal válido
            try:
                precio = float(precio_t)
            except ValueError:
                messagebox.showerror("Error", "Precio inválido.")
                return

            # Intentar agregar el producto
            insertado = self.lista.insertar_producto(codigo, nombre, categoria, precio, int(stock_t))
            if not insertado:
                messagebox.showerror("Error", "Ya existe un producto con ese código.")
                return

            messagebox.showinfo("Éxito", "Producto agregado.")
            for e in entries: e.delete(0, tk.END)  # Limpiar los campos
            self.mostrar_productos()

        btn_insertar = tk.Button(self.frm, text="Agregar Producto",
                                 bg="#00cc99", fg="black", width=20,
                                 command=insertar)
        btn_insertar.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def ventana_editar(self):
        """Formulario para modificar los datos de un producto existente."""
        self._vaciar_frm()

        # Pedir código del producto y los nuevos datos (puede dejar vacíos los que no quiera cambiar)
        tk.Label(self.frm, text="Código del producto:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        codigo_e = tk.Entry(self.frm, width=25)
        codigo_e.grid(row=0, column=1, padx=4, pady=4)

        campos = ["Nuevo nombre (opcional):", "Nueva categoría (opcional):",
                  "Nuevo precio (opcional):", "Nuevo stock (opcional):"]
        entries = []
        for i, c in enumerate(campos, start=1):
            tk.Label(self.frm, text=c, bg="#1a1a1a", fg="white")\
              .grid(row=i, column=0, sticky="e", padx=4, pady=4)
            e = tk.Entry(self.frm, width=25)
            e.grid(row=i, column=1, padx=4, pady=4)
            entries.append(e)

        def editar():
            codigo = codigo_e.get().strip()
            if not codigo:
                messagebox.showerror("Error", "Debe ingresar el código.")
                return
            # Tomar nuevos datos, o None si están vacíos
            nombre = entries[0].get().strip() or None
            categoria = entries[1].get().strip() or None
            precio_t = entries[2].get().strip()
            stock_t = entries[3].get().strip()

            precio = None
            if precio_t:
                try:
                    precio = float(precio_t)
                except ValueError:
                    messagebox.showerror("Error", "Precio inválido.")
                    return
            stock = None
            if stock_t:
                if not stock_t.isdigit():
                    messagebox.showerror("Error", "Stock debe ser entero.")
                    return
                stock = int(stock_t)

            actualizado = self.lista.actualizar_producto(codigo, nombre, categoria, precio, stock)
            if not actualizado:
                messagebox.showerror("Error", "Producto no encontrado.")
                return
            messagebox.showinfo("Éxito", "Producto actualizado.")
            self.mostrar_productos()

        btn_editar = tk.Button(self.frm, text="Actualizar Producto",
                               bg="#00cc99", fg="black", width=20,
                               command=editar)
        btn_editar.grid(row=len(campos)+1, column=0, columnspan=2, pady=10)

    def ventana_eliminar(self):
        """Formulario para eliminar un producto por código."""
        self._vaciar_frm()
        tk.Label(self.frm, text="Código del producto a eliminar:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        codigo_e = tk.Entry(self.frm, width=25)
        codigo_e.grid(row=0, column=1, padx=4, pady=4)

        def eliminar():
            codigo = codigo_e.get().strip()
            if not codigo:
                messagebox.showerror("Error", "Debe ingresar el código.")
                return
            eliminado = self.lista.eliminar_producto(codigo)
            if not eliminado:
                messagebox.showerror("Error", "Producto no encontrado.")
                return
            messagebox.showinfo("Éxito", "Producto eliminado.")
            self.mostrar_productos()

        btn_eliminar = tk.Button(self.frm, text="Eliminar Producto",
                                 bg="#cc3300", fg="white", width=20,
                                 command=eliminar)
        btn_eliminar.grid(row=1, column=0, columnspan=2, pady=10)

    def ventana_entrada(self):
        """Formulario para aumentar stock (entrada)."""
        self._vaciar_frm()
        tk.Label(self.frm, text="Código del producto:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        codigo_e = tk.Entry(self.frm, width=25)
        codigo_e.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Cantidad a ingresar:", bg="#1a1a1a", fg="white")\
          .grid(row=1, column=0, sticky="e", padx=4, pady=4)
        cantidad_e = tk.Entry(self.frm, width=25)
        cantidad_e.grid(row=1, column=1, padx=4, pady=4)

        def entrada_stock():
            codigo = codigo_e.get().strip()
            cantidad = cantidad_e.get().strip()
            if not codigo or not cantidad:
                messagebox.showerror("Error", "Datos incompletos.")
                return
            if not cantidad.isdigit():
                messagebox.showerror("Error", "Cantidad inválida.")
                return
            exito = self.lista.ajustar_stock(codigo, int(cantidad))
            if not exito:
                messagebox.showerror("Error", "Producto no encontrado o cantidad inválida.")
                return
            messagebox.showinfo("Éxito", "Stock actualizado.")
            self.mostrar_productos()

        btn_entrada = tk.Button(self.frm, text="Agregar Stock",
                                bg="#00cc99", fg="black", width=20,
                                command=entrada_stock)
        btn_entrada.grid(row=2, column=0, columnspan=2, pady=10)

    def ventana_salida(self):
        """Formulario para disminuir stock (salida)."""
        self._vaciar_frm()
        tk.Label(self.frm, text="Código del producto:", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        codigo_e = tk.Entry(self.frm, width=25)
        codigo_e.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Cantidad a retirar:", bg="#1a1a1a", fg="white")\
          .grid(row=1, column=0, sticky="e", padx=4, pady=4)
        cantidad_e = tk.Entry(self.frm, width=25)
        cantidad_e.grid(row=1, column=1, padx=4, pady=4)

        def salida_stock():
            codigo = codigo_e.get().strip()
            cantidad = cantidad_e.get().strip()
            if not codigo or not cantidad:
                messagebox.showerror("Error", "Datos incompletos.")
                return
            if not cantidad.isdigit():
                messagebox.showerror("Error", "Cantidad inválida.")
                return
            exito = self.lista.ajustar_stock(codigo, -int(cantidad))
            if not exito:
                messagebox.showerror("Error", "Producto no encontrado o cantidad inválida.")
                return
            messagebox.showinfo("Éxito", "Stock actualizado.")
            self.mostrar_productos()

        btn_salida = tk.Button(self.frm, text="Retirar Stock",
                               bg="#cc3300", fg="white", width=20,
                               command=salida_stock)
        btn_salida.grid(row=2, column=0, columnspan=2, pady=10)

    def ventana_filtrar(self):
        """Formulario para filtrar productos por nombre y categoría."""
        self._vaciar_frm()
        tk.Label(self.frm, text="Buscar por nombre (texto):", bg="#1a1a1a", fg="white")\
          .grid(row=0, column=0, sticky="e", padx=4, pady=4)
        nombre_e = tk.Entry(self.frm, width=25)
        nombre_e.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self.frm, text="Filtrar por categoría (texto):", bg="#1a1a1a", fg="white")\
          .grid(row=1, column=0, sticky="e", padx=4, pady=4)
        categoria_e = tk.Entry(self.frm, width=25)
        categoria_e.grid(row=1, column=1, padx=4, pady=4)

        def filtrar():
            nombre = nombre_e.get().strip()
            categoria = categoria_e.get().strip()
            productos_filtrados = self.lista.filtrar(nombre, categoria)
            self._vaciar_frm()
            self._mostrar_lista(productos_filtrados)

        btn_filtrar = tk.Button(self.frm, text="Filtrar",
                                bg="#0099cc", fg="white", width=20,
                                command=filtrar)
        btn_filtrar.grid(row=2, column=0, columnspan=2, pady=10)

    # ------------ FUNCIONES DE MOSTRAR Y ORDENAR ------------
    def mostrar_productos(self):
        """Muestra todos los productos sin ordenar ni filtrar."""
        self._vaciar_frm()
        productos = self.lista._to_list()
        self._mostrar_lista(productos)

    def ordenar(self, criterio):
        """Muestra los productos ordenados por el criterio dado."""
        self._vaciar_frm()
        productos = self.lista.ordenar(criterio)
        self._mostrar_lista(productos)

# ------------------- EJECUCIÓN -------------------
if __name__ == "__main__":
    root = tk.Tk()    # Crea la ventana principal
    app = App(root)   # Crea la aplicación dentro de esa ventana
    root.mainloop()   # Inicia el ciclo para mostrar la ventana y esperar acciones del usuario