import flet as ft


class PantallaRegistro:
    """Pantalla 2: Registro de usuario"""
    
    def __init__(self, page, gestor_img, db, callback_regresar, callback_exito):
        self.page = page
        self.gestor_img = gestor_img
        self.db = db
        self.callback_regresar = callback_regresar
        self.callback_exito = callback_exito
    
    def mostrar(self):
        """Muestra la pantalla de registro"""
        nombre = ft.TextField(label="Nombre(s)", width=300, color="black")
        apellido = ft.TextField(label="Apellidos", width=300, color="black")
        usuarioid = ft.TextField(label="Nombre de usuario (id)", width=300, color="black")
        correo = ft.TextField(label="Correo", width=300, color="black")
        contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, color="black")
        confirmar = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True, width=300, color="black")
        mensaje = ft.Text("", color="red")

        def registrar_click(e):
            if not all([nombre.value, apellido.value, usuarioid.value, correo.value, contrasena.value, confirmar.value]):
                mensaje.value = "Por favor completa todos los campos."
                self.page.update()
                return
            if contrasena.value != confirmar.value:
                mensaje.value = "Las contraseñas no coinciden."
                self.page.update()
                return
            if self.db.registrar_usuario(nombre.value, apellido.value, usuarioid.value, correo.value, contrasena.value):
                self.callback_exito()
            else:
                mensaje.value = "El usuario o correo ya existe."
                self.page.update()

        contenido = ft.Column(
            [
                ft.Row(
                    [ft.TextButton("← Regresar", on_click=lambda e: self.callback_regresar(), 
                                  style=ft.ButtonStyle(color="black"))],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Text("Hola Soy Habit", size=20, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text("¿Listo para programar tus hábitos y optimizar tu día?", color="black"),
                ft.Image(src=self.gestor_img.get("Imagen1"), width=100, height=100),
                nombre,
                apellido,
                usuarioid,
                correo,
                contrasena,
                confirmar,
                ft.Text(
                    "Al hacer clic en registrarse, aceptas usar la aplicación HabitTracker",
                    size=10,
                    text_align=ft.TextAlign.CENTER,
                    color="black"
                ),
                mensaje,
                ft.ElevatedButton("Registrarse", bgcolor="black", color="white", on_click=registrar_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)