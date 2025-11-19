import flet as ft
from datetime import datetime


class TarjetasHabitos:
    """Clase que contiene las tarjetas de hábitos"""
    
    def __init__(self, gestor_img):
        self.gestor_img = gestor_img
    
    def crear_tarjeta_habito(self, habito_id, titulo, fecha_limite, hora_limite, prioridad, completado, 
                            callback_toggle, callback_editar):
        """Crea una tarjeta de hábito para la pantalla principal"""
        checkbox = ft.Checkbox(
            value=completado,
            on_change=lambda e: callback_toggle(habito_id, e.control.value)
        )
        
        colores_prioridad = {
            1: ft.Colors.RED_100,
            2: ft.Colors.YELLOW_100,
            3: ft.Colors.GREEN_100,
        }
        
        etiquetas_prioridad = {
            1: " Alta",
            2: " Media",
            3: " Baja",
        }
        
        color_fondo = ft.Colors.GREY_300 if completado else colores_prioridad.get(prioridad, ft.Colors.GREY_100)
        
        fecha_hora_texto = f"{fecha_limite}"
        if hora_limite:
            fecha_hora_texto = f"Vence: {fecha_limite} |  {hora_limite}"
        
        btn_editar = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color="blue",
            icon_size=20,
            tooltip="Editar hábito",
            on_click=lambda e: callback_editar(habito_id)
        )
        
        return ft.Container(
            content=ft.Row([
                checkbox,
                ft.Column([
                    ft.Text(titulo, size=14, weight="bold", color="black"),
                    ft.Row([
                        ft.Text(fecha_hora_texto, size=11, color="black54"),
                    ], spacing=5),
                    ft.Text(f"Prioridad: {etiquetas_prioridad.get(prioridad, ' Media')}", size=11, color="black54"),
                ], spacing=2, expand=True),
                btn_editar,
            ]),
            bgcolor=color_fondo,
            border_radius=10,
            padding=10,
        )
    
    def crear_tarjeta_notificacion(self, habito_id, titulo, fecha_limite, hora_limite, prioridad, 
                                   es_completado, callback_eliminar=None):
        """Crea una tarjeta de notificación"""
        try:
            fecha_obj = datetime.strptime(fecha_limite, "%d/%m/%Y")
            hoy = datetime.now()
            dias_restantes = (fecha_obj - hoy).days
            
            if hora_limite:
                fecha_hora_str = f"{fecha_limite} {hora_limite}"
                fecha_hora_recordatorio = datetime.strptime(fecha_hora_str, "%d/%m/%Y %H:%M")
                
                if dias_restantes < 0:
                    texto_tiempo = f"{abs(dias_restantes)} día(s) vencido"
                    estado_texto = "Estado: Vencido"
                    estado_color = "red"
                elif dias_restantes == 0 and fecha_hora_recordatorio < hoy:
                    tiempo_pasado = hoy - fecha_hora_recordatorio
                    horas_pasadas = int(tiempo_pasado.total_seconds() / 3600)
                    if horas_pasadas < 1:
                        texto_tiempo = f"hace {int(tiempo_pasado.total_seconds() / 60)} min"
                    elif horas_pasadas < 24:
                        texto_tiempo = f"hace {horas_pasadas}h"
                    else:
                        texto_tiempo = "hoy"
                    estado_texto = f"Recordatorio: {hora_limite}"
                    estado_color = "orange"
                elif dias_restantes == 0:
                    texto_tiempo = f"hoy a las {hora_limite}"
                    estado_texto = "Recordatorio programado"
                    estado_color = "blue"
                elif dias_restantes == 1:
                    texto_tiempo = f"mañana a las {hora_limite}"
                    estado_texto = "Recordatorio programado"
                    estado_color = "black54"
                else:
                    texto_tiempo = f"{dias_restantes} días"
                    estado_texto = f"Recordatorio: {hora_limite}"
                    estado_color = "black54"
            else:
                if dias_restantes < 0:
                    texto_tiempo = f"{abs(dias_restantes)} día(s) vencido"
                    estado_texto = "Estado: Vencido"
                    estado_color = "red"
                elif dias_restantes == 0:
                    texto_tiempo = "Hoy"
                    estado_texto = "Vence hoy"
                    estado_color = "orange"
                elif dias_restantes == 1:
                    texto_tiempo = "Mañana"
                    estado_texto = "Vence mañana"
                    estado_color = "black54"
                else:
                    texto_tiempo = f"{dias_restantes} días"
                    estado_texto = "Pendiente"
                    estado_color = "black54"
        except:
            texto_tiempo = f"{fecha_limite}"
            if hora_limite:
                texto_tiempo += f" |  {hora_limite}"
            estado_texto = "Pendiente"
            estado_color = "black54"

        if es_completado:
            estado_final = "✓ Completado"
            estado_color = "green"
            texto_tiempo = "Completado"
        elif prioridad == 1:
            estado_final = f" Alta prioridad - {estado_texto}"
        elif prioridad == 2:
            estado_final = estado_texto
        else:
            estado_final = estado_texto

        eliminar_btn = None
        if es_completado and callback_eliminar:
            eliminar_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color="red",
                icon_size=20,
                on_click=lambda e: callback_eliminar(habito_id)
            )

        fila_contenido = ft.Row([
            self.gestor_img.crear_imagen("Imagen7", width=30, height=30),
            ft.Column([
                ft.Text(f"{titulo}", size=13, weight="bold", color="black"),
                ft.Text(f" {texto_tiempo}", size=11, color="black54"),
                ft.Text(estado_final, size=11, color=estado_color, weight="bold"),
            ], spacing=2, expand=True),
        ])
        
        if eliminar_btn:
            fila_contenido.controls.append(eliminar_btn)

        return ft.Container(
            content=ft.Column([
                fila_contenido,
                ft.Divider(height=1, color="grey300"),
            ], spacing=5),
            padding=10,
        )