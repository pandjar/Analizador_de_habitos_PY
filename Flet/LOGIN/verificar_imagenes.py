import os
import sys


def verificar_estructura():
    """Verifica toda la estructura de archivos e imágenes"""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE ESTRUCTURA DE IMÁGENES")
    print("=" * 60)
    
    # 1. Ubicación actual
    print(f"\n📍 Directorio actual: {os.getcwd()}")
    print(f"📍 Directorio del script: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 2. Verificar carpetas
    carpetas_verificar = [
        "assets",
        "assets/images",
        "images",
        "assets/img",
        "img",
    ]
    
    print("\n📁 CARPETAS ENCONTRADAS:")
    carpetas_existentes = []
    for carpeta in carpetas_verificar:
        existe = os.path.exists(carpeta)
        simbolo = "✅" if existe else "❌"
        print(f"{simbolo} {carpeta}")
        if existe:
            carpetas_existentes.append(carpeta)
    
    # 3. Buscar archivos de imagen
    print("\n🖼️  IMÁGENES ENCONTRADAS:")
    total_imagenes = 0
    extensiones_imagen = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    
    for carpeta in carpetas_existentes:
        try:
            archivos = os.listdir(carpeta)
            imagenes = [f for f in archivos if f.lower().endswith(extensiones_imagen)]
            
            if imagenes:
                print(f"\n  📂 {carpeta}/ ({len(imagenes)} imágenes)")
                for img in sorted(imagenes):
                    ruta_completa = os.path.join(carpeta, img)
                    tamaño = os.path.getsize(ruta_completa)
                    tamaño_kb = tamaño / 1024
                    print(f"    • {img} ({tamaño_kb:.1f} KB)")
                    total_imagenes += 1
        except Exception as e:
            print(f"  ⚠️ Error al leer {carpeta}: {e}")
    
    # 4. Verificar archivos de configuración
    print("\n⚙️  ARCHIVOS DE CONFIGURACIÓN:")
    archivos_config = [
        "imagenes_config.json",
        "imagenes_base64.py",
        "gestor_imagenes.py",
    ]
    
    for archivo in archivos_config:
        existe = os.path.exists(archivo)
        simbolo = "✅" if existe else "❌"
        print(f"{simbolo} {archivo}")
    
    # 5. Leer JSON si existe
    if os.path.exists("imagenes_config.json"):
        print("\n📄 CONTENIDO DE imagenes_config.json:")
        try:
            import json
            with open("imagenes_config.json", "r") as f:
                config = json.load(f)
                for key, value in config.get("imagenes", {}).items():
                    existe_archivo = os.path.exists(value) or os.path.exists(value.lstrip("/"))
                    simbolo = "✅" if existe_archivo else "❌"
                    print(f"  {simbolo} {key}: {value}")
        except Exception as e:
            print(f"  ⚠️ Error al leer JSON: {e}")
    
    # 6. Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"  • Total de imágenes encontradas: {total_imagenes}")
    print(f"  • Carpetas con imágenes: {len(carpetas_existentes)}")
    
    if total_imagenes == 0:
        print("\n⚠️  NO SE ENCONTRARON IMÁGENES")
        print("📋 SOLUCIONES:")
        print("  1. Verifica que las imágenes estén en: assets/images/")
        print("  2. O cópialas a: images/")
        print("  3. Ejecuta: python generar_base64.py")
    else:
        print("\n✅ Imágenes encontradas correctamente")
        print("📋 SIGUIENTE PASO:")
        print("  Ejecuta: python generar_base64.py")
    
    print("=" * 60)


if __name__ == "__main__":
    verificar_estructura()