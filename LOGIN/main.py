import flet as ft
import sqlite3
import os

# === CONFIGURACIÓN DE BASE DE DATOS ===
DB_PATH = os.path.join(os.path.dirname(__file__), "User.db")

def inicializar_bd():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT,
            Apellido TEXT,
            UsuarioID TEXT,
            Correo TEXT UNIQUE,
            Contrasena TEXT
        )
        """)
        conn.commit()

def registrar_usuario(nombre, apellido, usuarioid, correo, contrasena):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE UsuarioID=? OR Correo=?", (usuarioid, correo))
        if cursor.fetchone():
            return False
        cursor.execute(
            "INSERT INTO User (Nombre, Apellido, UsuarioID, Correo, Contrasena) VALUES (?, ?, ?, ?, ?)",
            (nombre, apellido, usuarioid, correo, contrasena)
        )
        conn.commit()
        return True


# === CLASE PRINCIPAL ===
class HabitApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Habit App"
        self.page.bgcolor = ft.colors.WHITE
        self.page.window_width = 390
        self.page.window_height = 844
        self.page.window_resizable = False
        self.page.scroll = ft.ScrollMode.AUTO

        inicializar_bd()
        self.mostrar_inicio_sesion()

    # === PANTALLA 1: INICIO DE SESIÓN ===
    def mostrar_inicio_sesion(self):
        self.page.clean()

        imagen_path = os.path.join(os.path.dirname(__file__), "Imagenes", "Imagen3.png")

        correo = ft.TextField(
            label="correo@electrónico@dominio.com",
            width=300,
            color="black"
        )

        btn_continuar = ft.ElevatedButton(
            "Continuar",
            bgcolor="black",
            color="white",
            width=300,
            on_click=lambda e: self.mostrar_registro()
        )

        link_olvidar = ft.TextButton(
            "¿Olvidaste tu contraseña?",
            style=ft.ButtonStyle(color=ft.colors.BLUE),
            on_click=lambda e: self.mostrar_olvidar_contrasena()
        )

        link_registro = ft.TextButton(
            "¿No tienes una cuenta? Regístrate",
            style=ft.ButtonStyle(color=ft.colors.BLUE),
            on_click=lambda e: self.mostrar_registro()
        )

        terminos = ft.Text(
            "Términos de servicio y Política de privacidad",
            size=10,
            color=ft.colors.BLACK54,
            text_align=ft.TextAlign.CENTER
        )

        contenido = ft.Column(
            [
                ft.Container(
                    ft.Image(src=imagen_path, width=150, height=150),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=40, bottom=20)
                ),
                ft.Text("Crea una cuenta", size=20, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text("Ingresa tu correo electrónico para registrarte en esta aplicación", color="black"),
                correo,
                btn_continuar,
                link_olvidar,
                link_registro,
                terminos
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.page.add(contenido)
        self.page.update()

    # === PANTALLA 2: REGISTRO ===
    def mostrar_registro(self):
        self.page.clean()

        nombre = ft.TextField(label="Nombre", width=300)
        apellido = ft.TextField(label="Apellido", width=300)
        usuarioid = ft.TextField(label="Usuario ID", width=300)
        correo = ft.TextField(label="Correo", width=300)
        contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)

        def registrar_click(e):
            if registrar_usuario(nombre.value, apellido.value, usuarioid.value, correo.value, contrasena.value):
                self.mostrar_confirmacion()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Usuario o correo ya existe"), bgcolor=ft.colors.RED)
                self.page.snack_bar.open = True
                self.page.update()

        def regresar_click(e):
            self.mostrar_inicio_sesion()

        imagen_path = os.path.join(os.path.dirname(__file__), "Imagenes", "Imagen1.png")

        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [ft.IconButton(icon=ft.icons.ARROW_BACK, icon_color="black", on_click=regresar_click)],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(ft.Image(src=imagen_path, width=200, height=200), alignment=ft.alignment.center),
                    ft.Text("Regístrate en esta aplicación", size=18, color=ft.colors.BLACK),
                    nombre,
                    apellido,
                    usuarioid,
                    correo,
                    contrasena,
                    ft.ElevatedButton("Continuar", on_click=registrar_click, bgcolor=ft.colors.BLACK, color=ft.colors.WHITE),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            )
        )
        self.page.update()

    # === PANTALLA 3: CONFIRMACIÓN ===
    def mostrar_confirmacion(self):
        self.page.clean()

        def regresar_click(e):
            self.mostrar_registro()

        imagen_path = os.path.join(os.path.dirname(__file__), "Imagenes", "Imagen3.png")

        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [ft.IconButton(icon=ft.icons.ARROW_BACK, icon_color="black", on_click=regresar_click)],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(ft.Image(src=imagen_path, width=200, height=200), alignment=ft.alignment.center),
                    ft.Text("Excelente", size=22, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Text("Ya estás conectado conmigo, y juntos construiremos algo grande", color="black"),
                    ft.ElevatedButton("Continuar", on_click=lambda e: self.mostrar_final(), bgcolor="black", color="white"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )
        self.page.update()

    # === PANTALLA 4: FINAL ===
    def mostrar_final(self):
        self.page.clean()

        imagen_path = os.path.join(os.path.dirname(__file__), "Imagenes", "Imagen4.png")

        self.page.add(
            ft.Column(
                [
                    ft.Container(ft.Image(src=imagen_path, width=200, height=200), alignment=ft.alignment.center),
                    ft.Text("En construcción...", size=18, color=ft.colors.BLACK),
                    ft.ElevatedButton("Volver al inicio", on_click=lambda e: self.mostrar_inicio_sesion(), bgcolor="black", color="white"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )
        self.page.update()

    # === PANTALLA: OLVIDÉ CONTRASEÑA ===
    def mostrar_olvidar_contrasena(self):
        self.page.clean()

        imagen_path = os.path.join(os.path.dirname(__file__), "Imagenes", "Imagen5.png")

        correo = ft.TextField(label="correo@electrónico@dominio.com", width=300)
        btn_enviar = ft.ElevatedButton("Enviar", bgcolor="black", color="white", width=300, on_click=lambda e: self.mostrar_reset_contrasena())
        btn_volver = ft.ElevatedButton("Volver", bgcolor="white", color="black", width=300, on_click=lambda e: self.mostrar_inicio_sesion())

        contenido = ft.Column(
            [
                ft.Image(src=imagen_path, width=150, height=150),
                ft.Text("¿Olvidaste tu contraseña?", size=20, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text("Ingresa tu correo electrónico, te enviaremos un enlace para restablecerla.", color="black"),
                correo,
                btn_enviar,
                btn_volver,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        self.page.add(contenido)
        self.page.update()

    # === PANTALLA: RESTABLECER CONTRASEÑA ===
    def mostrar_reset_contrasena(self):
        self.page.clean()

        imagen_path = os.path.join(os.path.dirname(__file__), "Imagenes", "Imagen6.png")

        nueva = ft.TextField(label="Nueva contraseña", password=True, can_reveal_password=True, width=300)
        confirmar = ft.TextField(label="Confirmar contraseña", password=True, can_reveal_password=True, width=300)

        def enviar_click(e):
            if nueva.value and confirmar.value and nueva.value == confirmar.value:
                self.page.snack_bar = ft.SnackBar(ft.Text("Contraseña cambiada exitosamente"), bgcolor=ft.colors.GREEN)
                self.page.snack_bar.open = True
                self.page.update()
                self.mostrar_confirmacion()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Las contraseñas no coinciden"), bgcolor=ft.colors.RED)
                self.page.snack_bar.open = True
                self.page.update()

        contenido = ft.Column(
            [
                ft.Image(src=imagen_path, width=150, height=150),
                ft.Text("Ingresa tu nueva contraseña", size=18, weight=ft.FontWeight.BOLD, color="black"),
                nueva,
                confirmar,
                ft.ElevatedButton("Enviar", bgcolor="black", color="white", on_click=enviar_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.page.add(contenido)
        self.page.update()


# === INICIO DE LA APP ===
def main(page: ft.Page):
    HabitApp(page)

ft.app(target=main)
