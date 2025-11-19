import flet as ft


class PantallaInicio:
    """Pantalla 1: Inicio de sesión"""
    
    def __init__(self, page, gestor_img, callback_registro, callback_login):
        self.page = page
        self.gestor_img = gestor_img
        self.callback_registro = callback_registro
        self.callback_login = callback_login
    
    def mostrar(self):
        """Muestra la pantalla de inicio"""
        correo = ft.TextField(label="correo@electrónico.com", width=300, color="black")
        
        btn_continuar = ft.ElevatedButton(
            "Continuar", 
            bgcolor="black", 
            color="white", 
            on_click=lambda e: self.callback_login()
        )
        
        registrar_link = ft.TextButton(
            "¿No tienes una cuenta? Regístrate",
            on_click=lambda e: self.callback_registro(),
            style=ft.ButtonStyle(color="blue"),
        )

        contenido = ft.Column(
            [
                self.gestor_img.crear_imagen("Imagen3", width=150, height=150),
                ft.Text("INICIO DE SESIÓN", size=20, weight=ft.FontWeight.BOLD, color="black"),
                correo,
                btn_continuar,
                registrar_link,
                ft.Text("Términos de servicio y Política de privacidad", size=10, color="black54"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)