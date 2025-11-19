import flet as ft
import os

# Importar gestor de imágenes
from gestor_imagenes import GestorImagenes

# Importar clases de gestión
from database_manager import DatabaseManager
from validador import ValidadorFechaHora

# Importar componentes
from components.dialogos import Dialogos
from components.tarjetas import TarjetasHabitos

# Importar pantallas
from screens.pantalla_inicio import PantallaInicio
from screens.pantalla_registro import PantallaRegistro
from screens.pantalla_exito import PantallaExito
from screens.pantalla_login import PantallaLogin
from screens.pantalla_principal import PantallaPrincipal
from screens.pantalla_notificaciones import PantallaNotificaciones
from screens.pantalla_perfil import PantallaPerfil


class HabitApp:
    """Clase principal que coordina toda la aplicación"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Habit Tracker"
        self.page.bgcolor = ft.Colors.WHITE
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Configuración de ventana
        self.page.window_width = 400
        self.page.window_height = 800
        self.page.window_resizable = False
        
        # Gestor de imágenes con JSON
        self.gestor_img = GestorImagenes()
        
        self.db = DatabaseManager()
        self.validador = ValidadorFechaHora()
        self.usuario_actual = None
        
        # Componentes reutilizables
        self.dialogos = Dialogos(self.page, self.gestor_img)
        self.tarjetas = TarjetasHabitos(self.gestor_img)
        
        # Verificar sesión y mostrar pantalla correspondiente
        self.iniciar_aplicacion()
    
    def iniciar_aplicacion(self):
        """Inicia la aplicación verificando si hay sesión guardada"""
        sesion_guardada = self.db.cargar_sesion()
        if sesion_guardada:
            self.usuario_actual = sesion_guardada
            self.ir_a_pantalla_principal(verificar_vencidos=True)
        else:
            self.ir_a_pantalla_inicio()
    
    # ========== NAVEGACIÓN ENTRE PANTALLAS ==========
    
    def ir_a_pantalla_inicio(self):
        """Navega a la pantalla de inicio"""
        pantalla = PantallaInicio(
            self.page, 
            self.gestor_img,
            callback_registro=self.ir_a_pantalla_registro,
            callback_login=self.ir_a_pantalla_login
        )
        pantalla.mostrar()
    
    def ir_a_pantalla_registro(self):
        """Navega a la pantalla de registro"""
        pantalla = PantallaRegistro(
            self.page,
            self.gestor_img,
            self.db,
            callback_regresar=self.ir_a_pantalla_inicio,
            callback_exito=self.ir_a_pantalla_exito
        )
        pantalla.mostrar()
    
    def ir_a_pantalla_exito(self):
        """Navega a la pantalla de éxito"""
        pantalla = PantallaExito(
            self.page,
            self.gestor_img,
            callback_regresar=self.ir_a_pantalla_registro,
            callback_iniciar=self.ir_a_pantalla_login
        )
        pantalla.mostrar()
    
    def ir_a_pantalla_login(self):
        """Navega a la pantalla de login"""
        pantalla = PantallaLogin(
            self.page,
            self.gestor_img,
            self.db,
            callback_regresar=self.ir_a_pantalla_inicio,
            callback_login_exitoso=self.login_exitoso
        )
        pantalla.mostrar()
    
    def login_exitoso(self, usuarioid):
        """Callback cuando el login es exitoso"""
        self.usuario_actual = usuarioid
        self.ir_a_pantalla_principal(verificar_vencidos=True)
    
    def ir_a_pantalla_principal(self, verificar_vencidos=True):
        """Navega a la pantalla principal"""
        pantalla = PantallaPrincipal(
            self.page,
            self.gestor_img,
            self.db,
            self.usuario_actual,
            self.tarjetas,
            self.dialogos,
            self.validador,
            callback_home=lambda: self.ir_a_pantalla_principal(verificar_vencidos=False),
            callback_notificaciones=self.ir_a_pantalla_notificaciones,
            callback_perfil=self.ir_a_pantalla_perfil
        )
        pantalla.mostrar(verificar_vencidos=verificar_vencidos)
    
    def ir_a_pantalla_notificaciones(self):
        """Navega a la pantalla de notificaciones"""
        pantalla = PantallaNotificaciones(
            self.page,
            self.gestor_img,
            self.db,
            self.usuario_actual,
            self.tarjetas,
            callback_home=lambda: self.ir_a_pantalla_principal(verificar_vencidos=False),
            callback_notificaciones=self.ir_a_pantalla_notificaciones,
            callback_perfil=self.ir_a_pantalla_perfil
        )
        pantalla.mostrar()
    
    def ir_a_pantalla_perfil(self):
        """Navega a la pantalla de perfil"""
        pantalla = PantallaPerfil(
            self.page,
            self.gestor_img,
            self.db,
            self.usuario_actual,
            callback_home=lambda: self.ir_a_pantalla_principal(verificar_vencidos=False),
            callback_notificaciones=self.ir_a_pantalla_notificaciones,
            callback_perfil=self.ir_a_pantalla_perfil,
            callback_cerrar_sesion=self.cerrar_sesion
        )
        pantalla.mostrar()
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        self.db.cerrar_sesion()
        self.usuario_actual = None
        self.ir_a_pantalla_inicio()


def main(page: ft.Page):
    """Función principal que inicia la aplicación"""
    HabitApp(page)


# Punto de entrada de la aplicación
if __name__ == "__main__":
    # Especificar la carpeta de assets
    import os
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    print(f" Assets directory: {assets_dir}")
    ft.app(target=main, assets_dir=assets_dir)