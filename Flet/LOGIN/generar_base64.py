import os
import base64


def generar_imagenes_base64():
    """Genera un archivo Python con todas las imágenes en base64"""
    
    # Ruta donde están tus imágenes
    carpeta_imagenes = "assets/images"
    
    # Nombres de las imágenes que tienes
    imagenes = ["Imagen1.png", "Imagen2.png", "Imagen3.png", 
                "Imagen4.png", "Imagen7.png", "Imagen8.png"]
    
    resultado = {}
    
    print("🔄 Convirtiendo imágenes a base64...")
    print("=" * 60)
    
    for img in imagenes:
        ruta_completa = os.path.join(carpeta_imagenes, img)
        
        if os.path.exists(ruta_completa):
            try:
                with open(ruta_completa, "rb") as f:
                    contenido = f.read()
                    base64_str = base64.b64encode(contenido).decode('utf-8')
                    
                    # Nombre sin extensión
                    nombre_base = img.replace(".png", "")
                    resultado[nombre_base] = base64_str
                    
                    tamaño_kb = len(contenido) / 1024
                    print(f"✅ {img:<20} → {tamaño_kb:.1f} KB")
            except Exception as e:
                print(f"❌ Error con {img}: {e}")
        else:
            print(f"⚠️  No encontrado: {ruta_completa}")
    
    print("=" * 60)
    
    # Generar archivo Python
    with open("imagenes_base64.py", "w", encoding="utf-8") as f:
        f.write('"""Imágenes embebidas en base64 para compatibilidad móvil"""\n\n')
        f.write("IMAGENES_BASE64 = {\n")
        
        for nombre, base64_str in resultado.items():
            # Escribir en bloques de 80 caracteres para legibilidad
            f.write(f'    "{nombre}": (\n')
            for i in range(0, len(base64_str), 80):
                chunk = base64_str[i:i+80]
                f.write(f'        "{chunk}"\n')
            f.write('    ),\n')
        
        f.write("}\n")
    
    print(f"\n✅ Archivo 'imagenes_base64.py' generado exitosamente")
    print(f"📊 Total de imágenes procesadas: {len(resultado)}")
    return len(resultado)


if __name__ == "__main__":
    generar_imagenes_base64()