import flet as ft


class PantallaLogin:
    """Pantalla 4: Login con credenciales"""
    
    def __init__(self, page, gestor_img, db, callback_regresar, callback_login_exitoso):
        self.page = page
        self.gestor_img = gestor_img
        self.db = db
        self.callback_regresar = callback_regresar
        self.callback_login_exitoso = callback_login_exitoso
    
    def mostrar(self):
        """Muestra la pantalla de login"""
        usuarioid = ft.TextField(label="Usuario ID", width=300, color="black")
        contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, color="black")
        mensaje = ft.Text("", color="red")

        def login_click(e):
            if self.db.validar_usuario(usuarioid.value, contrasena.value):
                self.db.guardar_sesion(usuarioid.value)
                self.callback_login_exitoso(usuarioid.value)
            else:
                mensaje.value = "Usuario o contraseña incorrectos."
                mensaje.color = "red"
                self.page.update()

        contenido = ft.Column(
            [
                ft.Row(
                    [ft.TextButton("← Regresar", on_click=lambda e: self.callback_regresar(), 
                                  style=ft.ButtonStyle(color="black"))],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Image(src=self.gestor_img.get("Imagen4"), width=150, height=150),
                ft.Text("INICIO DE SESIÓN", color="black", size=20, weight="bold"),
                usuarioid,
                contrasena,
                mensaje,
                ft.ElevatedButton("Continuar", bgcolor="black", color="white", on_click=login_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)