import json
import os
import flet as ft

# Intentar importar las imágenes base64 generadas
try:
    from imagenes_base64 import IMAGENES_BASE64
    print("✅ Imágenes base64 cargadas correctamente")
    USAR_BASE64 = True
except ImportError:
    print("⚠️ No se encontró imagenes_base64.py, usando rutas de archivos")
    IMAGENES_BASE64 = {}
    USAR_BASE64 = False


class GestorImagenes:
    """Gestiona la carga de imágenes desde base64 o archivos"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "imagenes_config.json")
        self.imagenes_base64_raw = {}
        self.imagenes_rutas = {}
        self.usar_base64 = USAR_BASE64
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Carga la configuración de imágenes"""
        if self.usar_base64:
            # Procesar imágenes base64
            for nombre, base64_str in IMAGENES_BASE64.items():
                # Concatenar todas las líneas si es tupla
                if isinstance(base64_str, tuple):
                    base64_str = ''.join(base64_str)
                # Guardar raw sin prefijo
                self.imagenes_base64_raw[nombre] = base64_str
            print(f"✅ Gestor: {len(self.imagenes_base64_raw)} imágenes en base64")
        else:
            # Usar rutas de archivos
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    rutas = config.get("imagenes", {})
                    for nombre, ruta in rutas.items():
                        if ruta.startswith("/images/"):
                            ruta = "assets" + ruta
                        elif ruta.startswith("images/"):
                            ruta = "assets/" + ruta
                        self.imagenes_rutas[nombre] = ruta
                    print(f"✅ Gestor: {len(self.imagenes_rutas)} rutas cargadas desde JSON")
            except FileNotFoundError:
                print(f"⚠️ No se encontró {self.config_file}")
                self._cargar_rutas_por_defecto()
            except json.JSONDecodeError as e:
                print(f"❌ Error al leer JSON: {e}")
                self._cargar_rutas_por_defecto()
    
    def _cargar_rutas_por_defecto(self):
        """Rutas por defecto si falla la carga"""
        self.imagenes_rutas = {
            "Imagen1": "assets/images/Imagen1.png",
            "Imagen2": "assets/images/Imagen2.png",
            "Imagen3": "assets/images/Imagen3.png",
            "Imagen4": "assets/images/Imagen4.png",
            "Imagen7": "assets/images/Imagen7.png",
            "Imagen8": "assets/images/Imagen8.png",
        }
        print(f"✅ Rutas por defecto cargadas: {len(self.imagenes_rutas)} imágenes")
    
    def get(self, nombre_imagen):
        """
        OBSOLETO: Mantener por compatibilidad
        Ahora usa crear_imagen() en su lugar
        """
        nombre_base = nombre_imagen.replace(".png", "").replace(".jpg", "")
        
        if self.usar_base64:
            # Devolver ruta vacía, las imágenes deben usar src_base64
            return ""
        else:
            ruta = self.imagenes_rutas.get(nombre_base, "")
            if ruta.startswith("/"):
                ruta = ruta[1:]
            return ruta
    
    def crear_imagen(self, nombre_imagen, **kwargs):
        """
        Crea un ft.Image con la configuración correcta
        
        Args:
            nombre_imagen: Nombre sin extensión (ej: "Imagen1")
            **kwargs: Argumentos adicionales para ft.Image (width, height, fit, etc.)
        
        Returns:
            ft.Image configurado
        """
        nombre_base = nombre_imagen.replace(".png", "").replace(".jpg", "")
        
        if self.usar_base64:
            # Usar base64
            base64_data = self.imagenes_base64_raw.get(nombre_base, "")
            return ft.Image(src_base64=base64_data, **kwargs)
        else:
            # Usar ruta de archivo
            ruta = self.imagenes_rutas.get(nombre_base, "")
            if ruta.startswith("/"):
                ruta = ruta[1:]
            return ft.Image(src=ruta, **kwargs)
    
    def get_with_extension(self, nombre_con_extension):
        """
        OBSOLETO: Mantener por compatibilidad
        """
        nombre_base = nombre_con_extension.rsplit(".", 1)[0]
        return self.get(nombre_base)
    
    def listar_imagenes(self):
        """Lista todas las imágenes disponibles"""
        if self.usar_base64:
            return list(self.imagenes_base64_raw.keys())
        else:
            return list(self.imagenes_rutas.keys())
    
    def esta_usando_base64(self):
        """Verifica si está usando base64"""
        return self.usar_base64