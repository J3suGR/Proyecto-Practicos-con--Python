import sys
import os
import pandas as pd
import numpy as np
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QWidget, QTabWidget, QMainWindow,
    QPushButton, QFormLayout, QLineEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QDateEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from sklearn.linear_model import LinearRegression
import tempfile

matplotlib.use("Qt5Agg")

def generar_datos():
    fechas = pd.date_range(start="2024-01-01", periods=30, freq="W")
    data = {
        "Fecha": fechas,
        "Ingresos": (10000 + 5000 * np.random.rand(len(fechas))).round(2),
        "Crecimiento": (5 + 10 * np.random.rand(len(fechas))).round(2),
        "Usuarios Activos": (500 + 300 * np.random.rand(len(fechas))).astype(int)
    }
    return pd.DataFrame(data)

df = generar_datos()

class Grafico(QWidget):
    def __init__(self, x, y, titulo):
        super().__init__()
        layout = QVBoxLayout(self)
        fig, ax = plt.subplots()
        ax.plot(x, y, marker='o', linestyle='-', color='teal')
        ax.set_title(titulo)
        ax.set_xlabel("Fecha")
        ax.set_ylabel(titulo)
        fig.autofmt_xdate()
        canvas = Canvas(fig)
        layout.addWidget(canvas)

class ProyeccionIngresos(QWidget):
    def __init__(self, df):
        super().__init__()
        layout = QVBoxLayout(self)

        df_ordenado = df.sort_values("Fecha")
        df_ordenado["FechaNum"] = (df_ordenado["Fecha"] - df_ordenado["Fecha"].min()).dt.days
        X = df_ordenado["FechaNum"].values.reshape(-1, 1)
        y = df_ordenado["Ingresos"].values

        modelo = LinearRegression()
        modelo.fit(X, y)

        dias_futuros = [X[-1][0] + 7 * i for i in range(1, 5)]
        fechas_futuras = [df_ordenado["Fecha"].max() + pd.Timedelta(days=7 * i) for i in range(1, 5)]
        ingresos_futuros = modelo.predict(np.array(dias_futuros).reshape(-1, 1))

        fig, ax = plt.subplots()
        ax.plot(df_ordenado["Fecha"], y, label="Histórico", color="teal", marker="o")
        ax.plot(fechas_futuras, ingresos_futuros, label="Proyección", color="orange", linestyle="--", marker="x")

        ax.set_title("Proyección de Ingresos (4 semanas)")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Ingresos")
        ax.legend()
        fig.autofmt_xdate()

        canvas = Canvas(fig)
        layout.addWidget(canvas)

class EditorDatos(QWidget):
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.fecha_input = QLineEdit()
        self.ingresos_input = QLineEdit()
        self.crecimiento_input = QLineEdit()
        self.usuarios_input = QLineEdit()

        form.addRow("Fecha (YYYY-MM-DD)", self.fecha_input)
        form.addRow("Ingresos", self.ingresos_input)
        form.addRow("Crecimiento (%)", self.crecimiento_input)
        form.addRow("Usuarios Activos", self.usuarios_input)
        layout.addLayout(form)

        btn_agregar = QPushButton("Agregar Registro")
        btn_agregar.clicked.connect(self.agregar_datos)
        layout.addWidget(btn_agregar)

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Desde:"))
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDisplayFormat("yyyy-MM-dd")
        filtro_layout.addWidget(self.fecha_desde)

        filtro_layout.addWidget(QLabel("Hasta:"))
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDisplayFormat("yyyy-MM-dd")
        filtro_layout.addWidget(self.fecha_hasta)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.filtrar_tabla)
        filtro_layout.addWidget(btn_filtrar)
        layout.addLayout(filtro_layout)

        self.tabla = QTableWidget()
        layout.addWidget(self.tabla)
        self.actualizar_tabla()

        btn_excel = QPushButton("Exportar a Excel")
        btn_excel.clicked.connect(self.exportar_excel)
        layout.addWidget(btn_excel)

        btn_pdf = QPushButton("Exportar a PDF con Gráficos")
        btn_pdf.clicked.connect(self.exportar_pdf)
        layout.addWidget(btn_pdf)

        self.setLayout(layout)

    def actualizar_tabla(self):
        self.mostrar_tabla(self.dashboard.df.tail(10))

    def mostrar_tabla(self, datos):
        self.tabla.setRowCount(len(datos))
        self.tabla.setColumnCount(len(datos.columns))
        self.tabla.setHorizontalHeaderLabels(datos.columns)
        for i in range(len(datos)):
            for j in range(len(datos.columns)):
                self.tabla.setItem(i, j, QTableWidgetItem(str(datos.iloc[i, j])))

    def agregar_datos(self):
        try:
            nueva_fecha = pd.to_datetime(self.fecha_input.text())
            ingreso = float(self.ingresos_input.text())
            crecimiento = float(self.crecimiento_input.text())
            usuarios = int(self.usuarios_input.text())

            nuevo = pd.DataFrame([{
                "Fecha": nueva_fecha,
                "Ingresos": ingreso,
                "Crecimiento": crecimiento,
                "Usuarios Activos": usuarios
            }])

            self.dashboard.df = pd.concat([self.dashboard.df, nuevo], ignore_index=True)
            self.dashboard.actualizar_dashboard()
            self.actualizar_tabla()

            QMessageBox.information(self, "Éxito", "Registro agregado correctamente.")
            self.fecha_input.clear()
            self.ingresos_input.clear()
            self.crecimiento_input.clear()
            self.usuarios_input.clear()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Datos inválidos: {e}")

    def filtrar_tabla(self):
        desde = self.fecha_desde.date().toPyDate()
        hasta = self.fecha_hasta.date().toPyDate()
        df_filtrado = self.dashboard.df[
            (self.dashboard.df["Fecha"] >= pd.to_datetime(desde)) &
            (self.dashboard.df["Fecha"] <= pd.to_datetime(hasta))
        ]
        self.mostrar_tabla(df_filtrado)

    def exportar_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar como Excel", "", "Excel (*.xlsx)")
        if path:
            self.dashboard.df.to_excel(path, index=False)
            QMessageBox.information(self, "Éxito", f"Datos exportados:\n{path}")

    def exportar_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar como PDF", "", "PDF (*.pdf)")
        if not path:
            return

        c = pdf_canvas.Canvas(path, pagesize=letter)
        text = c.beginText(40, 750)
        text.setFont("Helvetica-Bold", 12)
        text.textLine("📊 Reporte Empresarial con Gráficos")
        text.setFont("Helvetica", 10)
        text.textLine(f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        text.textLine("")
        c.drawText(text)

        def guardar_grafico(columna, titulo):
            fig, ax = plt.subplots()
            ax.plot(self.dashboard.df["Fecha"], self.dashboard.df[columna], marker="o", linestyle="-", color="teal")
            ax.set_title(titulo)
            ax.set_xlabel("Fecha")
            ax.set_ylabel(titulo)
            fig.autofmt_xdate()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp.name, dpi=100, bbox_inches="tight")
            plt.close(fig)
            return tmp.name

        y_offset = 620
        for columna, titulo in [
            ("Ingresos", "Ingresos"),
            ("Crecimiento", "Crecimiento (%)"),
            ("Usuarios Activos", "Usuarios Activos")
        ]:
            img_path = guardar_grafico(columna, titulo)
            c.drawImage(img_path, 60, y_offset, width=460, height=130)
            y_offset -= 150
            os.unlink(img_path)

        y_offset -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y_offset, "Últimos 5 registros:")
        c.setFont("Helvetica", 9)
        y_offset -= 15
        for _, row in self.dashboard.df.tail(5).iterrows():
            linea = f"{row['Fecha'].date()} | Ingresos: ${row['Ingresos']:.2f} | Crecimiento: {row['Crecimiento']}% | Usuarios: {row['Usuarios Activos']}"
            c.drawString(40, y_offset, linea)
            y_offset -= 12

        c.save()
        QMessageBox.information(self, "Éxito", f"PDF creado con gráficos:\n{path}")

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Empresarial de Indicadores")
        self.setGeometry(100, 100, 1100, 650)
        self.df = df.copy()

        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)

        self.kpi_layout = QHBoxLayout()
        self.kpi_labels = {}
        for kpi, color in zip(["Ingresos", "Crecimiento", "Usuarios Activos"], ["green", "blue", "orange"]):
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"font-size: 20px; color: {color}")
            self.kpi_layout.addWidget(lbl)
            self.kpi_labels[kpi] = lbl
        layout.addLayout(self.kpi_layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.actualizar_dashboard()

        self.timer = QTimer()
        self.timer.timeout.connect(self.generar_reporte)
        self.timer.start(30000)

    def actualizar_dashboard(self):
        self.kpi_labels["Ingresos"].setText(f"Ingresos: ${self.df['Ingresos'].iloc[-1]:,.2f}")
        self.kpi_labels["Crecimiento"].setText(f"Crecimiento: {self.df['Crecimiento'].iloc[-1]:.2f}%")
        self.kpi_labels["Usuarios Activos"].setText(f"Usuarios: {self.df['Usuarios Activos'].iloc[-1]:,}")
        self.actualizar_graficos()

    def actualizar_graficos(self):
        self.tabs.clear()
        self.tab_ingresos = Grafico(self.df["Fecha"], self.df["Ingresos"], "Ingresos")
        self.tab_crecimiento = Grafico(self.df["Fecha"], self.df["Crecimiento"], "Crecimiento")
        self.tab_usuarios = Grafico(self.df["Fecha"], self.df["Usuarios Activos"], "Usuarios Activos")
        self.tab_proyeccion = ProyeccionIngresos(self.df)
        self.editor = EditorDatos(self)

        self.tabs.addTab(self.tab_ingresos, "Ingresos")
        self.tabs.addTab(self.tab_crecimiento, "Crecimiento")
        self.tabs.addTab(self.tab_usuarios, "Usuarios")
        self.tabs.addTab(self.tab_proyeccion, "Proyección")
        self.tabs.addTab(self.editor, "Editar / Exportar")

    def generar_reporte(self):
        try:
            print(f"Reporte automático generado - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(self.df.tail(1))
        except Exception as e:
            print(f"Error en reporte automático: {e}")

def excepthook(type, value, traceback):
    print("Error global:", value)
    QMessageBox.critical(None, "Error", f"Ocurrió un error: {value}")

sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Dashboard()
    ventana.show()
    sys.exit(app.exec_())