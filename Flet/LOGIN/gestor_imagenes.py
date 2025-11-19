import json
import os


class GestorImagenes:
    """Gestiona la carga de imágenes desde configuración JSON"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "imagenes_config.json")
        self.imagenes = {}
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Carga la configuración de imágenes desde JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.imagenes = config.get("imagenes", {})
                print(f"✅ Gestor de imágenes: {len(self.imagenes)} imágenes cargadas desde JSON")
        except FileNotFoundError:
            print(f"⚠️ No se encontró {self.config_file}, usando rutas por defecto")
            self._cargar_rutas_por_defecto()
        except json.JSONDecodeError as e:
            print(f"❌ Error al leer JSON: {e}")
            self._cargar_rutas_por_defecto()
    
    def _cargar_rutas_por_defecto(self):
        """Rutas por defecto si falla la carga del JSON"""
        self.imagenes = {
            "Imagen1": "/images/Imagen1.png",
            "Imagen2": "/images/Imagen2.png",
            "Imagen3": "/images/Imagen3.png",
            "Imagen4": "/images/Imagen4.png",
            "Imagen7": "/images/Imagen7.png",
            "Imagen8": "/images/Imagen8.png",
        }
    
    def get(self, nombre_imagen):
        """
        Obtiene la ruta de una imagen
        
        Args:
            nombre_imagen: Nombre sin extensión (ej: "Imagen1")
        
        Returns:
            Ruta de la imagen (ej: "/images/Imagen1.png")
        """
        # Quitar extensión si la tiene
        nombre_base = nombre_imagen.replace(".png", "").replace(".jpg", "")
        return self.imagenes.get(nombre_base, "")
    
    def get_with_extension(self, nombre_con_extension):
        """
        Obtiene la ruta usando el nombre con extensión
        
        Args:
            nombre_con_extension: Nombre con extensión (ej: "Imagen1.png")
        
        Returns:
            Ruta de la imagen
        """
        nombre_base = nombre_con_extension.rsplit(".", 1)[0]
        return self.imagenes.get(nombre_base, "")
    
    def listar_imagenes(self):
        """Lista todas las imágenes disponibles"""
        return list(self.imagenes.keys())