import flet as ft


class PantallaPrincipal:
    """Pantalla 5: Pantalla principal con hábitos"""
    
    def __init__(self, page, gestor_img, db, usuario_actual, tarjetas, dialogos, validador,
                 callback_home, callback_notificaciones, callback_perfil):
        self.page = page
        self.gestor_img = gestor_img
        self.db = db
        self.usuario_actual = usuario_actual
        self.tarjetas = tarjetas
        self.dialogos = dialogos
        self.validador = validador
        self.callback_home = callback_home
        self.callback_notificaciones = callback_notificaciones
        self.callback_perfil = callback_perfil
        self.lista_habitos = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def mostrar(self, verificar_vencidos=True):
        """Muestra la pantalla principal"""
        nombre_usuario = self.db.obtener_usuario(self.usuario_actual)
        
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.gestor_img.crear_imagen("Imagen3", width=40, height=40),
                    ft.Column([
                        ft.Text(f"Bienvenido a HabitTracker", size=14, weight="bold", color="black"),
                        ft.Text(nombre_usuario, size=12, color="black54"),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=self.gestor_img.crear_imagen("Imagen1", width=200, height=150, fit=ft.ImageFit.CONTAIN),
                    alignment=ft.alignment.center,
                ),
            ]),
            padding=15,
            bgcolor=ft.Colors.WHITE,
        )

        btn_agregar = ft.Container(
            content=ft.ElevatedButton(
                "Añadir Hábitos",
                bgcolor="black",
                color="white",
                width=300,
                on_click=lambda e: self.mostrar_dialogo_agregar()
            ),
            padding=ft.padding.symmetric(vertical=10),
            alignment=ft.alignment.center,
        )

        self.actualizar_lista_habitos()

        actividades_titulo = ft.Container(
            content=ft.Text("Tus actividades por realizar son:", size=14, weight="bold", color="black"),
            padding=ft.padding.only(left=15, top=10, bottom=5),
        )

        habitos_pendientes = len(self.db.obtener_habitos_incompletos(self.usuario_actual))
        
        bottom_nav = self.crear_bottom_nav(habitos_pendientes)

        contenido = ft.Column(
            [
                header,
                btn_agregar,
                actividades_titulo,
                ft.Container(
                    content=self.lista_habitos,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=15),
                ),
                bottom_nav,
            ],
            spacing=0,
            expand=True,
        )

        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.add(contenido)
        self.page.update()
        
        if verificar_vencidos:
            habitos_vencidos = self.db.obtener_habitos_vencidos(self.usuario_actual)
            if habitos_vencidos:
                self.dialogos.dialogo_reduccion_nivel(habitos_vencidos, self.eliminar_y_penalizar)
    
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
    
    def actualizar_lista_habitos(self):
        """Actualiza la lista de hábitos"""
        self.lista_habitos.controls.clear()
        habitos = self.db.obtener_habitos(self.usuario_actual)
        
        if not habitos:
            self.lista_habitos.controls.append(
                ft.Text("No tienes hábitos agregados aún", size=12, color="black54", italic=True)
            )
        else:
            for habito in habitos:
                if len(habito) >= 6:
                    habito_id, titulo, fecha_limite, hora_limite, prioridad, completado = habito
                else:
                    habito_id, titulo, fecha_limite, prioridad, completado = habito
                    hora_limite = None
                
                self.lista_habitos.controls.append(
                    self.tarjetas.crear_tarjeta_habito(
                        habito_id, titulo, fecha_limite, hora_limite, prioridad, 
                        bool(completado), self.toggle_habito, self.mostrar_dialogo_editar
                    )
                )
        
        self.page.update()
    
    def toggle_habito(self, habito_id, completado):
        """Marca un hábito como completado o no"""
        self.db.actualizar_habito_completado(habito_id, int(completado))
        
        if completado:
            nivel, exp_actual, exp_necesaria, subio_nivel = self.db.agregar_experiencia(self.usuario_actual)
            
            if subio_nivel:
                self.dialogos.dialogo_subida_nivel(nivel)
        
        self.actualizar_lista_habitos()
    
    def mostrar_dialogo_agregar(self):
        """Muestra el diálogo para agregar un hábito"""
        def callback_agregar(titulo, fecha, hora, prioridad):
            self.db.agregar_habito(self.usuario_actual, titulo, fecha, hora, prioridad)
            self.actualizar_lista_habitos()
        
        self.dialogos.dialogo_agregar_habito(self.validador, callback_agregar)
    
    def mostrar_dialogo_editar(self, habito_id):
        """Muestra el diálogo para editar un hábito"""
        habito_datos = self.db.obtener_habito_por_id(habito_id)
        
        def callback_guardar(hab_id, titulo, fecha, hora, prioridad):
            self.db.editar_habito(hab_id, titulo, fecha, hora, prioridad)
            self.actualizar_lista_habitos()
        
        self.dialogos.dialogo_editar_habito(habito_datos, self.validador, callback_guardar)
    
    def eliminar_y_penalizar(self, dialogo, habitos_vencidos):
        """Elimina hábitos vencidos y reduce nivel"""
        for hab_id, _, _ in habitos_vencidos:
            self.db.eliminar_habito(hab_id)
        
        bajo_nivel, nivel_actual = self.db.reducir_nivel(self.usuario_actual)
        
        self.page.close(dialogo)
        
        self.mostrar(verificar_vencidos=False)
        
        if bajo_nivel:
            self.dialogos.dialogo_nivel_reducido(nivel_actual)