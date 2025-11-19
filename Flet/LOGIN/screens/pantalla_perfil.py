import flet as ft


class PantallaPerfil:
    """Pantalla 7: Perfil del usuario"""
    
    def __init__(self, page, gestor_img, db, usuario_actual, 
                 callback_home, callback_notificaciones, callback_perfil, callback_cerrar_sesion):
        self.page = page
        self.gestor_img = gestor_img
        self.db = db
        self.usuario_actual = usuario_actual
        self.callback_home = callback_home
        self.callback_notificaciones = callback_notificaciones
        self.callback_perfil = callback_perfil
        self.callback_cerrar_sesion = callback_cerrar_sesion
    
    def mostrar(self):
        """Muestra la pantalla de perfil"""
        nombre_usuario = self.db.obtener_usuario(self.usuario_actual)
        nivel, exp_actual, habitos_completados = self.db.obtener_experiencia(self.usuario_actual)
        
        exp_necesaria = min(nivel * 3, 30)
        
        header = ft.Container(
            content=ft.Row([
                self.gestor_img.crear_imagen("Imagen7", width=40, height=40),
                ft.Column([
                    ft.Text(f"Bienvenido a HabitTracker", size=14, weight="bold", color="black"),
                    ft.Text(nombre_usuario, size=12, color="black54"),
                ], spacing=0),
            ], alignment=ft.MainAxisAlignment.START),
            padding=15,
            bgcolor=ft.Colors.WHITE,
        )

        nombre_field = ft.TextField(
            label="Nombre del Usuario",
            value=nombre_usuario,
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            read_only=True,
            border_color="black54"
        )
        
        id_field = ft.TextField(
            label="Id del Usuario",
            value=self.usuario_actual,
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            read_only=True,
            border_color="black54"
        )
        
        nivel_field = ft.TextField(
            label="Nivel del Usuario",
            value=f"Nivel {nivel}",
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            read_only=True,
            border_color="black54"
        )

        def crear_cuadro_exp(lleno):
            return ft.Container(
                width=8,
                height=30,
                bgcolor=ft.Colors.BLUE if lleno else ft.Colors.GREY_300,
                border_radius=2,
            )
        
        cuadros_exp = [crear_cuadro_exp(i < exp_actual) for i in range(exp_necesaria)]
        
        barra_experiencia = ft.Container(
            content=ft.Column([
                ft.Text("Experiencia", size=14, weight="bold", color="black", text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=ft.Row(
                        cuadros_exp,
                        spacing=3,
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True,
                    ),
                    width=300,
                    padding=10,
                    border=ft.border.all(1, "black54"),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.Text(
                    f"{exp_actual}/{exp_necesaria} - {habitos_completados} hábitos completados",
                    size=11,
                    color="black54",
                    text_align=ft.TextAlign.CENTER
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            alignment=ft.alignment.center,
        )

        btn_cerrar_sesion = ft.ElevatedButton(
            "Cerrar Sesión",
            bgcolor="black",
            color="white",
            width=300,
            on_click=lambda e: self.callback_cerrar_sesion()
        )

        habitos_pendientes = len(self.db.obtener_habitos_incompletos(self.usuario_actual))
        
        bottom_nav = self.crear_bottom_nav(habitos_pendientes)

        contenido = ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Column([
                        nombre_field,
                        id_field,
                        nivel_field,
                        barra_experiencia,
                        ft.Container(height=20),
                        btn_cerrar_sesion,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=15, vertical=20),
                    alignment=ft.alignment.center,
                ),
                bottom_nav,
            ],
            spacing=0,
            expand=True,
        )

        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.add(contenido)
    
    def crear_bottom_nav(self, habitos_pendientes):
        """Crea la barra de navegación inferior"""
        return ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.HOME, icon_color="black", on_click=lambda e: self.callback_home()),
                ft.Container(
                    content=ft.Stack([
                        ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color="black", icon_size=28, 
                                    on_click=lambda e: self.callback_notificaciones()),
                        ft.Container(
                            content=ft.Text(str(habitos_pendientes), 
                                          size=10, color="white", weight="bold"),
                            bgcolor="red",
                            width=18,
                            height=18,
                            border_radius=9,
                            alignment=ft.alignment.center,
                            right=8,
                            top=8,
                            visible=habitos_pendientes > 0,
                        ),
                    ]),
                    width=48,
                    height=48,
                ),
                ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color="teal", on_click=lambda e: self.callback_perfil()),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border=ft.border.only(top=ft.BorderSide(1, "grey300")),
        )