import flet as ft


class PantallaExito:
    """Pantalla 3: Registro exitoso"""
    
    def __init__(self, page, gestor_img, callback_regresar, callback_iniciar):
        self.page = page
        self.gestor_img = gestor_img
        self.callback_regresar = callback_regresar
        self.callback_iniciar = callback_iniciar
    
    def mostrar(self):
        """Muestra la pantalla de éxito"""
        contenido = ft.Column(
            [
                ft.Row(
                    [ft.TextButton("← Regresar", on_click=lambda e: self.callback_regresar(), 
                                  style=ft.ButtonStyle(color="black"))],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Text("Excelente", size=22, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text("Ya estás conectado conmigo, y juntos construiremos algo grande", color="black"),
                ft.Image(src=self.gestor_img.get("Imagen2"), width=120, height=120),
                ft.ElevatedButton("¡Iniciar!", bgcolor="black", color="white", on_click=lambda e: self.callback_iniciar()),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)