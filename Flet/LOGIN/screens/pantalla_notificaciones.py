import flet as ft


class PantallaNotificaciones:
    """Pantalla 6: Notificaciones de hábitos"""
    
    def __init__(self, page, gestor_img, db, usuario_actual, tarjetas,
                 callback_home, callback_notificaciones, callback_perfil):
        self.page = page
        self.gestor_img = gestor_img
        self.db = db
        self.usuario_actual = usuario_actual
        self.tarjetas = tarjetas
        self.callback_home = callback_home
        self.callback_notificaciones = callback_notificaciones
        self.callback_perfil = callback_perfil
        self.lista_notificaciones = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def mostrar(self):
        """Muestra la pantalla de notificaciones"""
        header = ft.Container(
            content=ft.Row([
                self.gestor_img.crear_imagen("Imagen7", width=40, height=40),
                ft.Text("Notificaciones", size=18, weight="bold", color="black"),
            ], alignment=ft.MainAxisAlignment.START),
            padding=15,
            bgcolor=ft.Colors.WHITE,
        )

        self.actualizar_lista_notificaciones()

        habitos_pendientes = len(self.db.obtener_habitos_incompletos(self.usuario_actual))
        
        bottom_nav = self.crear_bottom_nav(habitos_pendientes)

        contenido = ft.Column(
            [
                header,
                ft.Container(
                    content=self.lista_notificaciones,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
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
                        ft.IconButton(icon=ft.Icons.NOTIFICATIONS, icon_color="blue", icon_size=28, on_click=lambda e: None),
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
    
    def actualizar_lista_notificaciones(self):
        """Actualiza la lista de notificaciones"""
        self.lista_notificaciones.controls.clear()
        habitos_pendientes = self.db.obtener_habitos_incompletos(self.usuario_actual)
        habitos_completados = self.db.obtener_habitos_completados(self.usuario_actual)
        
        if habitos_pendientes:
            self.lista_notificaciones.controls.append(
                ft.Text("Pendientes", size=16, weight="bold", color="black")
            )
            for habito in habitos_pendientes:
                if len(habito) >= 6:
                    habito_id, titulo, fecha_limite, hora_limite, prioridad, completado = habito
                else:
                    habito_id, titulo, fecha_limite, prioridad, completado = habito
                    hora_limite = None
                
                self.lista_notificaciones.controls.append(
                    self.tarjetas.crear_tarjeta_notificacion(
                        habito_id, titulo, fecha_limite, hora_limite, prioridad, False
                    )
                )
        else:
            self.lista_notificaciones.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("¡Excelente trabajo!", size=16, weight="bold", color="green", text_align=ft.TextAlign.CENTER),
                        ft.Text("No tienes hábitos pendientes", size=12, color="black54", text_align=ft.TextAlign.CENTER, italic=True),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                )
            )
        
        if habitos_completados:
            self.lista_notificaciones.controls.append(
                ft.Divider(height=20, color="grey400")
            )
            self.lista_notificaciones.controls.append(
                ft.Row([
                    ft.Text("Completados", size=16, weight="bold", color="green"),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "Borrar todos",
                        on_click=lambda e: self.borrar_completados(),
                        style=ft.ButtonStyle(color="red")
                    ),
                ])
            )
            for habito in habitos_completados:
                if len(habito) >= 6:
                    habito_id, titulo, fecha_limite, hora_limite, prioridad, completado = habito
                else:
                    habito_id, titulo, fecha_limite, prioridad, completado = habito
                    hora_limite = None
                
                self.lista_notificaciones.controls.append(
                    self.tarjetas.crear_tarjeta_notificacion(
                        habito_id, titulo, fecha_limite, hora_limite, prioridad, True, 
                        self.eliminar_habito
                    )
                )
        
        self.page.update()
    
    def eliminar_habito(self, habito_id):
        """Elimina un hábito específico"""
        self.db.eliminar_habito(habito_id)
        self.actualizar_lista_notificaciones()
    
    def borrar_completados(self):
        """Elimina todos los hábitos completados"""
        habitos_completados = self.db.obtener_habitos_completados(self.usuario_actual)
        for habito in habitos_completados:
            habito_id = habito[0]
            self.db.eliminar_habito(habito_id)
        self.actualizar_lista_notificaciones()