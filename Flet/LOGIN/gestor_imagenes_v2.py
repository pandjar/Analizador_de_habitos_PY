import json
import os

# Intentar importar las imágenes base64 generadas
try:
    from imagenes_base64 import IMAGENES_BASE64
    print("✅ Imágenes base64 importadas correctamente")
except ImportError:
    print("⚠️ No se encontró imagenes_base64.py - ejecuta generar_base64.py primero")
    IMAGENES_BASE64 = {}


class GestorImagenes:
    """Gestiona la carga de imágenes priorizando base64 embebido"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "imagenes_config.json")
        self.imagenes = {}
        self.imagenes_base64 = IMAGENES_BASE64.copy()
        self.cargar_configuracion()
        print(f"📊 Gestor inicializado con {len(self.imagenes_base64)} imágenes base64")
    
    def cargar_configuracion(self):
        """Carga rutas de respaldo desde JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.imagenes = config.get("imagenes", {})
        except:
            self._cargar_rutas_por_defecto()
    
    def _cargar_rutas_por_defecto(self):
        """Rutas por defecto"""
        self.imagenes = {
            "Imagen1": "images/Imagen1.png",
            "Imagen2": "images/Imagen2.png",
            "Imagen3": "images/Imagen3.png",
            "Imagen4": "images/Imagen4.png",
            "Imagen7": "images/Imagen7.png",
            "Imagen8": "images/Imagen8.png",
        }
    
    def get(self, nombre_imagen):
        """Obtiene la imagen (prioriza base64)"""
        nombre_base = nombre_imagen.replace(".png", "").replace(".jpg", "")
        
        # Prioridad absoluta: base64 embebido
        if nombre_base in self.imagenes_base64:
            return self.imagenes_base64[nombre_base]
        
        # Fallback: ruta relativa
        ruta = self.imagenes.get(nombre_base, "")
        if ruta.startswith("/"):
            ruta = ruta[1:]
        
        return ruta if ruta else f"images/{nombre_base}.png"
    
    def get_with_extension(self, nombre_con_extension):
        """Obtiene con extensión"""
        nombre_base = nombre_con_extension.rsplit(".", 1)[0]
        return self.get(nombre_base)
    
    def listar_imagenes(self):
        """Lista imágenes disponibles"""
        return list(set(list(self.imagenes_base64.keys()) + list(self.imagenes.keys())))