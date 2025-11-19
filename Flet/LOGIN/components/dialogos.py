import flet as ft


class Dialogos:
    """Clase que contiene todos los diálogos de la aplicación"""
    
    def __init__(self, page, gestor_img):
        self.page = page
        self.gestor_img = gestor_img
    
    def dialogo_subida_nivel(self, nivel_nuevo):
        """Diálogo cuando el usuario sube de nivel"""
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CELEBRATION, color="gold", size=30),
                ft.Text("¡FELICIDADES!", size=24, weight="bold", color="gold"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column([
                    ft.Image(src=self.gestor_img.get("Imagen2"), width=120, height=120),
                    ft.Text(
                        f"¡Has subido al Nivel {nivel_nuevo}!",
                        size=18,
                        weight="bold",
                        color="black",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Sigue así y alcanzarás tus metas",
                        size=14,
                        color="black54",
                        text_align=ft.TextAlign.CENTER,
                        italic=True
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=20,
            ),
            actions=[
                ft.ElevatedButton(
                    "¡Continuar!",
                    bgcolor="gold",
                    color="white",
                    on_click=lambda e: self.page.close(dialogo)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.page.open(dialogo)
    
    def dialogo_reduccion_nivel(self, habitos_vencidos, callback_eliminar):
        """Diálogo cuando hay hábitos vencidos"""
        dialogo_contenido = ft.Column([
            ft.Icon(ft.Icons.WARNING_AMBER, color="red", size=50),
            ft.Text(
                "Hábitos Vencidos Detectados",
                size=18,
                weight="bold",
                color="red",
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                f"Tienes {len(habitos_vencidos)} hábito(s) sin completar que ya pasaron su fecha de vencimiento.",
                size=12,
                color="black54",
                text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(height=10, color="grey400"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        for hab_id, titulo, fecha in habitos_vencidos[:3]:
            dialogo_contenido.controls.append(
                ft.Text(f"• {titulo} (vencido: {fecha})", size=11, color="black")
            )
        
        if len(habitos_vencidos) > 3:
            dialogo_contenido.controls.append(
                ft.Text(f"... y {len(habitos_vencidos) - 3} más", size=11, color="black54", italic=True)
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Atención", size=20, weight="bold", color="red"),
            content=ft.Container(
                content=dialogo_contenido,
                padding=10,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self.page.close(dialogo),
                    style=ft.ButtonStyle(color="black54")
                ),
                ft.ElevatedButton(
                    "Eliminar y Aceptar Penalización",
                    bgcolor="red",
                    color="white",
                    on_click=lambda e: callback_eliminar(dialogo, habitos_vencidos)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.page.open(dialogo)
    
    def dialogo_nivel_reducido(self, nivel_actual):
        """Diálogo informando que el nivel fue reducido"""
        def cerrar_y_actualizar(e):
            self.page.close(dialogo)
            self.page.update()
        
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ARROW_DOWNWARD, color="red", size=30),
                ft.Text("Nivel Reducido", size=20, weight="bold", color="red"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column([
                    ft.Image(src=self.gestor_img.get("Imagen8"), width=120, height=120),
                    ft.Text(
                        f"Tu nivel ha bajado a Nivel {nivel_actual}",
                        size=16,
                        weight="bold",
                        color="black",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "No te desanimes. Completa tus hábitos a tiempo para recuperar tu nivel.",
                        size=12,
                        color="black54",
                        text_align=ft.TextAlign.CENTER
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=20,
            ),
            actions=[
                ft.ElevatedButton(
                    "Entendido",
                    bgcolor="black",
                    color="white",
                    on_click=cerrar_y_actualizar
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.page.open(dialogo)
    
    def dialogo_agregar_habito(self, validador, callback_agregar):
        """Diálogo para agregar un nuevo hábito"""
        titulo_field = ft.TextField(
            label="Título del hábito", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54"
        )
        
        fecha_field = ft.TextField(
            label="Fecha límite (ej: 25/12/2024, 2024-12-25)", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            helper_text="Formatos: dd/mm/yyyy, yyyy-mm-dd, ddmmyyyy",
            helper_style=ft.TextStyle(size=10, color="black54")
        )
        
        hora_field = ft.TextField(
            label="Hora de recordatorio (ej: 14:30, 1430, 9:00)", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            helper_text="Hora en que deseas recibir un recordatorio (formato 24h)",
            helper_style=ft.TextStyle(size=10, color="black54"),
            value="09:00"
        )
        
        prioridad_dropdown = ft.Dropdown(
            label="Prioridad del hábito",
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            options=[
                ft.dropdown.Option("1", "1 - Alta prioridad (Más importante)"),
                ft.dropdown.Option("2", "2 - Media prioridad"),
                ft.dropdown.Option("3", "3 - Baja prioridad (Menos importante)"),
            ],
            value="2",
        )
        
        mensaje = ft.Text("", color="red", size=12)

        def agregar_habito(e):
            if not titulo_field.value or not fecha_field.value or not hora_field.value:
                mensaje.value = "Por favor completa todos los campos"
                dialogo.update()
                return
            
            hora_normalizada = validador.normalizar_hora(hora_field.value)
            if not validador.validar_hora(hora_normalizada):
                mensaje.value = "Hora inválida. Usa formato HH:MM (0-23:0-59)"
                dialogo.update()
                return
            
            fecha_normalizada = validador.normalizar_fecha(fecha_field.value)
            prioridad = int(prioridad_dropdown.value)
            
            self.page.close(dialogo)
            callback_agregar(titulo_field.value, fecha_normalizada, hora_normalizada, prioridad)

        dialogo = ft.AlertDialog(
            title=ft.Text("Nuevo Hábito", color="black"),
            content=ft.Column([
                titulo_field,
                fecha_field,
                hora_field,
                prioridad_dropdown,
                mensaje,
            ], tight=True, height=380),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialogo), style=ft.ButtonStyle(color="black")),
                ft.ElevatedButton("Agregar", bgcolor="black", color="white", on_click=agregar_habito),
            ],
            bgcolor=ft.Colors.WHITE,
        )

        self.page.open(dialogo)
    
    def dialogo_editar_habito(self, habito_datos, validador, callback_guardar):
        """Diálogo para editar un hábito existente"""
        if not habito_datos:
            return
        
        if len(habito_datos) >= 5:
            habito_id, titulo_actual, fecha_actual, hora_actual, prioridad_actual = habito_datos
        else:
            habito_id, titulo_actual, fecha_actual, prioridad_actual = habito_datos
            hora_actual = "09:00"
        
        titulo_field = ft.TextField(
            label="Título del hábito", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            value=titulo_actual
        )
        
        fecha_field = ft.TextField(
            label="Fecha límite", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            helper_text="Formatos: dd/mm/yyyy, yyyy-mm-dd, ddmmyyyy",
            helper_style=ft.TextStyle(size=10, color="black54"),
            value=fecha_actual
        )
        
        hora_field = ft.TextField(
            label="Hora de recordatorio", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            helper_text="Hora en que deseas recibir un recordatorio (formato 24h)",
            helper_style=ft.TextStyle(size=10, color="black54"),
            value=hora_actual if hora_actual else "09:00"
        )
        
        prioridad_dropdown = ft.Dropdown(
            label="Prioridad del hábito",
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            options=[
                ft.dropdown.Option("1", "1 - Alta prioridad (Más importante)"),
                ft.dropdown.Option("2", "2 - Media prioridad"),
                ft.dropdown.Option("3", "3 - Baja prioridad (Menos importante)"),
            ],
            value=str(prioridad_actual),
        )
        
        mensaje = ft.Text("", color="red", size=12)

        def guardar_edicion(e):
            if not titulo_field.value or not fecha_field.value or not hora_field.value:
                mensaje.value = "Por favor completa todos los campos"
                dialogo.update()
                return
            
            hora_normalizada = validador.normalizar_hora(hora_field.value)
            if not validador.validar_hora(hora_normalizada):
                mensaje.value = "Hora inválida. Usa formato HH:MM (0-23:0-59)"
                dialogo.update()
                return
            
            fecha_normalizada = validador.normalizar_fecha(fecha_field.value)
            prioridad = int(prioridad_dropdown.value)
            
            self.page.close(dialogo)
            callback_guardar(habito_id, titulo_field.value, fecha_normalizada, hora_normalizada, prioridad)

        dialogo = ft.AlertDialog(
            title=ft.Text("Editar Hábito", color="black"),
            content=ft.Column([
                titulo_field,
                fecha_field,
                hora_field,
                prioridad_dropdown,
                mensaje,
            ], tight=True, height=380),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialogo), style=ft.ButtonStyle(color="black")),
                ft.ElevatedButton("Guardar Cambios", bgcolor="blue", color="white", on_click=guardar_edicion),
            ],
            bgcolor=ft.Colors.WHITE,
        )

        self.page.open(dialogo)