import flet as ft
import sqlite3
import os
from datetime import datetime
import re
import json

# Clase para manejar la base de datos
class DatabaseManager:
    def __init__(self):
        self.user_db_path = os.path.join(os.path.dirname(__file__), "User.db")
        self.habitos_db_path = os.path.join(os.path.dirname(__file__), "habito.db")
        self.session_file = os.path.join(os.path.dirname(__file__), "session.json")
        self.inicializar_db()

    def inicializar_db(self):
        # Base de datos de usuarios
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS User (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT,
                Apellido TEXT,
                UsuarioID TEXT UNIQUE,
                Correo TEXT,
                Contraseña TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Base de datos de hábitos - MODIFICADA para incluir HoraLimite
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Habitos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                UsuarioID TEXT,
                Titulo TEXT,
                FechaLimite TEXT,
                HoraLimite TEXT,
                Prioridad INTEGER DEFAULT 1,
                Completado INTEGER DEFAULT 0,
                FechaCreacion TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Base de datos de experiencia de usuarios
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Experiencia (
                UsuarioID TEXT PRIMARY KEY,
                Nivel INTEGER DEFAULT 1,
                ExperienciaActual INTEGER DEFAULT 0,
                HabitosCompletados INTEGER DEFAULT 0,
                FOREIGN KEY (UsuarioID) REFERENCES User(UsuarioID)
            )
        """)
        conn.commit()
        conn.close()

    def guardar_sesion(self, usuarioid):
        """Guarda la sesión del usuario"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump({"usuario": usuarioid, "timestamp": datetime.now().isoformat()}, f)
        except:
            pass

    def cargar_sesion(self):
        """Carga la sesión guardada"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    return data.get("usuario")
        except:
            pass
        return None

    def cerrar_sesion(self):
        """Elimina el archivo de sesión"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except:
            pass

    def registrar_usuario(self, nombre, apellido, usuarioid, correo, contrasena):
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE UsuarioID=? OR Correo=?", (usuarioid, correo))
        if cursor.fetchone():
            conn.close()
            return False
        cursor.execute(
            "INSERT INTO User (Nombre, Apellido, UsuarioID, Correo, Contraseña) VALUES (?, ?, ?, ?, ?)",
            (nombre, apellido, usuarioid, correo, contrasena)
        )
        conn.commit()
        conn.close()
        return True

    def validar_usuario(self, usuarioid, contrasena):
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE UsuarioID=? AND Contraseña=?", (usuarioid, contrasena))
        user = cursor.fetchone()
        conn.close()
        return user is not None

    def obtener_usuario(self, usuarioid):
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Nombre FROM User WHERE UsuarioID=?", (usuarioid,))
        user = cursor.fetchone()
        conn.close()
        return user[0] if user else "Usuario"

    def obtener_habitos(self, usuarioid):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if "HoraLimite" in columnas:
            cursor.execute("SELECT ID, Titulo, FechaLimite, HoraLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? ORDER BY Completado ASC, Prioridad ASC", (usuarioid,))
        else:
            cursor.execute("SELECT ID, Titulo, FechaLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? ORDER BY Completado ASC, Prioridad ASC", (usuarioid,))
        
        habitos = cursor.fetchall()
        conn.close()
        return habitos

    def obtener_habito_por_id(self, habito_id):
        """Obtiene un hábito específico por su ID"""
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if "HoraLimite" in columnas:
            cursor.execute("SELECT ID, Titulo, FechaLimite, HoraLimite, Prioridad FROM Habitos WHERE ID=?", (habito_id,))
        else:
            cursor.execute("SELECT ID, Titulo, FechaLimite, Prioridad FROM Habitos WHERE ID=?", (habito_id,))
        
        habito = cursor.fetchone()
        conn.close()
        return habito

    def agregar_habito(self, usuarioid, titulo, fecha_limite, hora_limite, prioridad):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        fecha_creacion = datetime.now().strftime("%d/%m/%Y")
        
        if "HoraLimite" in columnas and "FechaCreacion" in columnas:
            cursor.execute(
                "INSERT INTO Habitos (UsuarioID, Titulo, FechaLimite, HoraLimite, Prioridad, FechaCreacion) VALUES (?, ?, ?, ?, ?, ?)",
                (usuarioid, titulo, fecha_limite, hora_limite, prioridad, fecha_creacion)
            )
        elif "FechaCreacion" in columnas:
            cursor.execute(
                "INSERT INTO Habitos (UsuarioID, Titulo, FechaLimite, Prioridad, FechaCreacion) VALUES (?, ?, ?, ?, ?)",
                (usuarioid, titulo, fecha_limite, prioridad, fecha_creacion)
            )
        else:
            cursor.execute(
                "INSERT INTO Habitos (UsuarioID, Titulo, FechaLimite, Prioridad) VALUES (?, ?, ?, ?)",
                (usuarioid, titulo, fecha_limite, prioridad)
            )
        conn.commit()
        conn.close()

    def editar_habito(self, habito_id, titulo, fecha_limite, hora_limite, prioridad):
        """Edita un hábito existente"""
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if "HoraLimite" in columnas:
            cursor.execute(
                "UPDATE Habitos SET Titulo=?, FechaLimite=?, HoraLimite=?, Prioridad=? WHERE ID=?",
                (titulo, fecha_limite, hora_limite, prioridad, habito_id)
            )
        else:
            cursor.execute(
                "UPDATE Habitos SET Titulo=?, FechaLimite=?, Prioridad=? WHERE ID=?",
                (titulo, fecha_limite, prioridad, habito_id)
            )
        
        conn.commit()
        conn.close()

    def actualizar_habito_completado(self, habito_id, completado):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE Habitos SET Completado=? WHERE ID=?", (completado, habito_id))
        conn.commit()
        conn.close()

    def eliminar_habito(self, habito_id):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Habitos WHERE ID=?", (habito_id,))
        conn.commit()
        conn.close()

    def obtener_habitos_incompletos(self, usuarioid):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if "HoraLimite" in columnas:
            cursor.execute("SELECT ID, Titulo, FechaLimite, HoraLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? AND Completado=0 ORDER BY Prioridad ASC", (usuarioid,))
        else:
            cursor.execute("SELECT ID, Titulo, FechaLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? AND Completado=0 ORDER BY Prioridad ASC", (usuarioid,))
        
        habitos = cursor.fetchall()
        conn.close()
        return habitos

    def obtener_habitos_completados(self, usuarioid):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if "HoraLimite" in columnas:
            cursor.execute("SELECT ID, Titulo, FechaLimite, HoraLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? AND Completado=1 ORDER BY Prioridad ASC", (usuarioid,))
        else:
            cursor.execute("SELECT ID, Titulo, FechaLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? AND Completado=1 ORDER BY Prioridad ASC", (usuarioid,))
        
        habitos = cursor.fetchall()
        conn.close()
        return habitos

    def obtener_habitos_vencidos(self, usuarioid):
        """Obtiene hábitos incompletos que ya pasaron su fecha y hora límite"""
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if "HoraLimite" in columnas:
            cursor.execute(
                "SELECT ID, Titulo, FechaLimite, HoraLimite FROM Habitos WHERE UsuarioID=? AND Completado=0",
                (usuarioid,)
            )
        else:
            cursor.execute(
                "SELECT ID, Titulo, FechaLimite FROM Habitos WHERE UsuarioID=? AND Completado=0",
                (usuarioid,)
            )
        
        habitos = cursor.fetchall()
        conn.close()
        
        ahora = datetime.now()
        vencidos = []
        
        for habito in habitos:
            try:
                if "HoraLimite" in columnas and len(habito) >= 4:
                    hab_id, titulo, fecha_limite, hora_limite = habito[:4]
                    if hora_limite:
                        fecha_hora_str = f"{fecha_limite} {hora_limite}"
                        fecha_hora_obj = datetime.strptime(fecha_hora_str, "%d/%m/%Y %H:%M")
                        
                        if fecha_hora_obj < ahora:
                            vencidos.append((hab_id, titulo, f"{fecha_limite} {hora_limite}"))
                    else:
                        fecha_obj = datetime.strptime(fecha_limite, "%d/%m/%Y")
                        if fecha_obj.date() < ahora.date():
                            vencidos.append((hab_id, titulo, fecha_limite))
                else:
                    hab_id, titulo, fecha_limite = habito[:3]
                    fecha_obj = datetime.strptime(fecha_limite, "%d/%m/%Y")
                    if fecha_obj.date() < ahora.date():
                        vencidos.append((hab_id, titulo, fecha_limite))
            except:
                pass
        
        return vencidos

    def obtener_experiencia(self, usuarioid):
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Nivel, ExperienciaActual, HabitosCompletados FROM Experiencia WHERE UsuarioID=?", (usuarioid,))
        exp = cursor.fetchone()
        conn.close()
        if exp:
            return exp
        else:
            self.inicializar_experiencia(usuarioid)
            return (1, 0, 0)

    def inicializar_experiencia(self, usuarioid):
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Experiencia (UsuarioID, Nivel, ExperienciaActual, HabitosCompletados) VALUES (?, 1, 0, 0)", (usuarioid,))
        conn.commit()
        conn.close()

    def agregar_experiencia(self, usuarioid):
        nivel, exp_actual, habitos_completados = self.obtener_experiencia(usuarioid)
        exp_actual += 1
        habitos_completados += 1
        
        exp_necesaria = min(nivel * 3, 30)
        subio_nivel = False
        
        if exp_actual >= exp_necesaria:
            nivel += 1
            exp_actual = 0
            subio_nivel = True
        
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE Experiencia SET Nivel=?, ExperienciaActual=?, HabitosCompletados=? WHERE UsuarioID=?", 
                      (nivel, exp_actual, habitos_completados, usuarioid))
        conn.commit()
        conn.close()
        
        return nivel, exp_actual, exp_necesaria, subio_nivel

    def reducir_nivel(self, usuarioid):
        """Reduce el nivel del usuario por fallar en completar un hábito"""
        nivel, exp_actual, habitos_completados = self.obtener_experiencia(usuarioid)
        
        if nivel > 1:
            nivel -= 1
            exp_necesaria = min(nivel * 3, 30)
            exp_actual = 0
            
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE Experiencia SET Nivel=?, ExperienciaActual=? WHERE UsuarioID=?", 
                          (nivel, exp_actual, usuarioid))
            conn.commit()
            conn.close()
            
            return True, nivel
        return False, nivel


# Clase: Validador de Fecha y Hora
class ValidadorFechaHora:
    """Clase para validar y normalizar fechas y horas"""
    
    @staticmethod
    def normalizar_fecha(fecha_texto):
        """Convierte diferentes formatos de fecha a dd/mm/yyyy"""
        fecha_texto = fecha_texto.strip()
        
        if re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{4}$', fecha_texto):
            fecha_texto = fecha_texto.replace('-', '/')
            partes = fecha_texto.split('/')
            return f"{int(partes[0]):02d}/{int(partes[1]):02d}/{partes[2]}"
        
        elif re.match(r'^\d{4}[/-]\d{1,2}[/-]\d{1,2}$', fecha_texto):
            fecha_texto = fecha_texto.replace('-', '/')
            partes = fecha_texto.split('/')
            return f"{int(partes[2]):02d}/{int(partes[1]):02d}/{partes[0]}"
        
        elif re.match(r'^\d{8}$', fecha_texto):
            return f"{fecha_texto[:2]}/{fecha_texto[2:4]}/{fecha_texto[4:]}"
        
        return fecha_texto
    
    @staticmethod
    def normalizar_hora(hora_texto):
        """Convierte diferentes formatos de hora a HH:MM"""
        hora_texto = hora_texto.strip()
        
        if re.match(r'^\d{1,2}:\d{2}$', hora_texto):
            partes = hora_texto.split(':')
            return f"{int(partes[0]):02d}:{partes[1]}"
        
        elif re.match(r'^\d{4}$', hora_texto):
            return f"{hora_texto[:2]}:{hora_texto[2:]}"
        
        elif re.match(r'^\d{1,2}:\d{1}$', hora_texto):
            partes = hora_texto.split(':')
            return f"{int(partes[0]):02d}:{int(partes[1]):02d}"
        
        return hora_texto
    
    @staticmethod
    def validar_hora(hora_texto):
        """Valida que la hora sea correcta (0-23:0-59)"""
        try:
            partes = hora_texto.split(':')
            if len(partes) != 2:
                return False
            
            hora = int(partes[0])
            minuto = int(partes[1])
            
            return 0 <= hora <= 23 and 0 <= minuto <= 59
        except:
            return False


# Clase principal de la app
class HabitApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Habit Tracker"
        self.page.bgcolor = ft.Colors.WHITE
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.page.window_width = 400
        self.page.window_height = 800
        self.page.window_resizable = False

        self.img_path = os.path.join(os.path.dirname(__file__), "Imagenes")
        self.db = DatabaseManager()
        self.validador = ValidadorFechaHora()
        self.usuario_actual = None
        self.mostrar_mensaje_nivel = None
        self.verificar_habitos_al_cargar = False  # Flag para verificar después

        # Verificar si hay sesión guardada
        sesion_guardada = self.db.cargar_sesion()
        if sesion_guardada:
            self.usuario_actual = sesion_guardada
            self.verificar_habitos_al_cargar = True  # Activar flag
            self.cargar_pantalla_principal_sin_verificacion()  # Cargar sin verificar
        else:
            self.pantalla_inicio()

    def mostrar_dialogo_subida_nivel(self, nivel_nuevo):
        "Muestra un diálogo cuando el usuario sube de nivel"
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CELEBRATION, color="gold", size=30),
                ft.Text("¡FELICIDADES!", size=24, weight="bold", color="gold"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column([
                    ft.Image(src=os.path.join(self.img_path, "Imagen2.png"), width=120, height=120),
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

    def mostrar_dialogo_reduccion_nivel(self, habitos_vencidos):
        "Muestra un diálogo cuando hay hábitos vencidos y se reduce el nivel"
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
                f"Tienes {len(habitos_vencidos)} hábito(s) sin completar que ya pasaron su fecha límite.",
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
                    on_click=lambda e: self.eliminar_y_penalizar_habitos(dialogo, habitos_vencidos)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.page.open(dialogo)

    def eliminar_y_penalizar_habitos(self, dialogo, habitos_vencidos):
        "Función separada para manejar la eliminación y penalización"
        for hab_id, _, _ in habitos_vencidos:
            self.db.eliminar_habito(hab_id)
        
        bajo_nivel, nivel_actual = self.db.reducir_nivel(self.usuario_actual)
        
        self.page.close(dialogo)
        
        self.mostrar_mensaje_nivel = (bajo_nivel, nivel_actual) if bajo_nivel else None
        
        self.cargar_pantalla_principal_sin_verificacion()

    def mostrar_dialogo_nivel_reducido(self, nivel_actual):
        "Muestra diálogo informando que el nivel fue reducido - CON IMAGEN8"
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
                    # IMAGEN8 AGREGADA AQUÍ
                    ft.Image(src=os.path.join(self.img_path, "Imagen8.png"), width=120, height=120),
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

    def verificar_habitos_vencidos(self):
        "Verifica si hay hábitos vencidos al entrar a la pantalla principal"
        habitos_vencidos = self.db.obtener_habitos_vencidos(self.usuario_actual)
        if habitos_vencidos:
            self.mostrar_dialogo_reduccion_nivel(habitos_vencidos)

    def cargar_pantalla_principal_sin_verificacion(self):
        "Carga la pantalla principal sin verificar hábitos vencidos"
        nombre_usuario = self.db.obtener_usuario(self.usuario_actual)
        
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Image(src=os.path.join(self.img_path, "Imagen3.png"), width=40, height=40),
                    ft.Column([
                        ft.Text(f"Bienvenido a HabitTracker", size=14, weight="bold", color="black"),
                        ft.Text(nombre_usuario, size=12, color="black54"),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.Image(src=os.path.join(self.img_path, "Imagen1.png"), width=200, height=150, fit=ft.ImageFit.CONTAIN),
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
                on_click=lambda e: self.mostrar_dialogo_agregar_habito()
            ),
            padding=ft.padding.symmetric(vertical=10),
            alignment=ft.alignment.center,
        )

        self.lista_habitos = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.actualizar_lista_habitos()

        actividades_titulo = ft.Container(
            content=ft.Text("Tus actividades por realizar son:", size=14, weight="bold", color="black"),
            padding=ft.padding.only(left=15, top=10, bottom=5),
        )

        habitos_pendientes = len(self.db.obtener_habitos_incompletos(self.usuario_actual))
        
        bottom_nav = ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.HOME, icon_color="black", on_click=lambda e: self.mostrar_pantalla_principal()),
                ft.Container(
                    content=ft.Stack([
                        ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color="black", icon_size=28, 
                                    on_click=lambda e: self.mostrar_notificaciones()),
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
                ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color="teal", on_click=lambda e: self.mostrar_perfil()),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border=ft.border.only(top=ft.BorderSide(1, "grey300")),
        )

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
        self.page.update()  # Asegurar que la página se actualice
        
        # Verificar hábitos vencidos DESPUÉS de que la página esté lista
        if self.verificar_habitos_al_cargar:
            self.verificar_habitos_al_cargar = False
            habitos_vencidos = self.db.obtener_habitos_vencidos(self.usuario_actual)
            if habitos_vencidos:
                self.mostrar_dialogo_reduccion_nivel(habitos_vencidos)
        
        # Mostrar mensaje de nivel reducido si existe
        if self.mostrar_mensaje_nivel:
            bajo_nivel, nivel_actual = self.mostrar_mensaje_nivel
            self.mostrar_mensaje_nivel = None
            if bajo_nivel:
                self.mostrar_dialogo_nivel_reducido(nivel_actual)

    def pantalla_inicio(self):
        correo = ft.TextField(label="correo@electrónico.com", width=300, color="black")
        btn_continuar = ft.ElevatedButton(
            "Continuar", bgcolor="black", color="white", on_click=lambda e: self.mostrar_login_contra()
        )
        registrar_link = ft.TextButton(
            "¿No tienes una cuenta? Regístrate",
            on_click=lambda e: self.mostrar_registro(),
            style=ft.ButtonStyle(color="blue"),
        )

        contenido = ft.Column(
            [
                ft.Image(src=os.path.join(self.img_path, "Imagen3.png"), width=150, height=150),
                ft.Text("INICIO DE SESIÓN", size=20, weight=ft.FontWeight.BOLD, color="black"),
                correo,
                btn_continuar,
                registrar_link,
                ft.Text("Términos de servicio y Política de privacidad", size=10, color="black54"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)

    def mostrar_registro(self):
        def regresar_click(e):
            self.pantalla_inicio()

        nombre = ft.TextField(label="Nombre(s)", width=300, color="black")
        apellido = ft.TextField(label="Apellidos", width=300, color="black")
        usuarioid = ft.TextField(label="Nombre de usuario (id)", width=300, color="black")
        correo = ft.TextField(label="Correo", width=300, color="black")
        contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, color="black")
        confirmar = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True, width=300, color="black")
        mensaje = ft.Text("", color="red")

        def registrar_click(e):
            if not all([nombre.value, apellido.value, usuarioid.value, correo.value, contrasena.value, confirmar.value]):
                mensaje.value = "Por favor completa todos los campos."
                self.page.update()
                return
            if contrasena.value != confirmar.value:
                mensaje.value = "Las contraseñas no coinciden."
                self.page.update()
                return
            if self.db.registrar_usuario(nombre.value, apellido.value, usuarioid.value, correo.value, contrasena.value):
                self.mostrar_exito()
            else:
                mensaje.value = "El usuario o correo ya existe."
                self.page.update()

        contenido = ft.Column(
            [
                ft.Row(
                    [ft.TextButton("← Regresar", on_click=regresar_click, style=ft.ButtonStyle(color="black"))],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Text("Hola Soy Habit", size=20, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text("¿Listo para programar tus hábitos y optimizar tu día?", color="black"),
                ft.Image(src=os.path.join(self.img_path, "Imagen1.png"), width=100, height=100),
                nombre,
                apellido,
                usuarioid,
                correo,
                contrasena,
                confirmar,
                ft.Text(
                    "Al hacer clic en registrarse, aceptas usar la aplicación HabitTracker",
                    size=10,
                    text_align=ft.TextAlign.CENTER,
                    color="black"
                ),
                mensaje,
                ft.ElevatedButton("Registrarse", bgcolor="black", color="white", on_click=registrar_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)

    def mostrar_exito(self):
        def regresar_click(e):
            self.mostrar_registro()

        contenido = ft.Column(
            [
                ft.Row(
                    [ft.TextButton("← Regresar", on_click=regresar_click, style=ft.ButtonStyle(color="black"))],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Text("Excelente", size=22, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text("Ya estás conectado conmigo, y juntos construiremos algo grande", color="black"),
                ft.Image(src=os.path.join(self.img_path, "Imagen2.png"), width=120, height=120),
                ft.ElevatedButton("¡Iniciar!", bgcolor="black", color="white", on_click=lambda e: self.mostrar_login_contra()),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)

    def mostrar_login_contra(self):
        def regresar_click(e):
            self.pantalla_inicio()

        usuarioid = ft.TextField(label="Usuario ID", width=300, color="black")
        contrasena = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, color="black")
        mensaje = ft.Text("", color="red")

        def login_click(e):
            if self.db.validar_usuario(usuarioid.value, contrasena.value):
                self.usuario_actual = usuarioid.value
                self.db.guardar_sesion(usuarioid.value)  # GUARDAR SESIÓN
                self.mostrar_pantalla_principal()
            else:
                mensaje.value = "Usuario o contraseña incorrectos."
                mensaje.color = "red"
                self.page.update()

        contenido = ft.Column(
            [
                ft.Row(
                    [ft.TextButton("← Regresar", on_click=regresar_click, style=ft.ButtonStyle(color="black"))],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Image(src=os.path.join(self.img_path, "Imagen4.png"), width=150, height=150),
                ft.Text("INICIO DE SESIÓN", color="black", size=20, weight="bold"),
                usuarioid,
                contrasena,
                mensaje,
                ft.ElevatedButton("Continuar", bgcolor="black", color="white", on_click=login_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.clean()
        self.page.add(contenido)

    def mostrar_pantalla_principal(self):
        self.verificar_habitos_vencidos()
        
        nombre_usuario = self.db.obtener_usuario(self.usuario_actual)
        
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Image(src=os.path.join(self.img_path, "Imagen3.png"), width=40, height=40),
                    ft.Column([
                        ft.Text(f"Bienvenido a HabitTracker", size=14, weight="bold", color="black"),
                        ft.Text(nombre_usuario, size=12, color="black54"),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.Image(src=os.path.join(self.img_path, "Imagen1.png"), width=200, height=150, fit=ft.ImageFit.CONTAIN),
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
                on_click=lambda e: self.mostrar_dialogo_agregar_habito()
            ),
            padding=ft.padding.symmetric(vertical=10),
            alignment=ft.alignment.center,
        )

        self.lista_habitos = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.actualizar_lista_habitos()

        actividades_titulo = ft.Container(
            content=ft.Text("Tus actividades por realizar son:", size=14, weight="bold", color="black"),
            padding=ft.padding.only(left=15, top=10, bottom=5),
        )

        habitos_pendientes = len(self.db.obtener_habitos_incompletos(self.usuario_actual))
        
        bottom_nav = ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.HOME, icon_color="black", on_click=lambda e: self.mostrar_pantalla_principal()),
                ft.Container(
                    content=ft.Stack([
                        ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color="black", icon_size=28, 
                                    on_click=lambda e: self.mostrar_notificaciones()),
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
                ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color="teal", on_click=lambda e: self.mostrar_perfil()),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border=ft.border.only(top=ft.BorderSide(1, "grey300")),
        )

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

    def actualizar_lista_habitos(self):
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
                    self.crear_tarjeta_habito(habito_id, titulo, fecha_limite, hora_limite, prioridad, bool(completado))
                )
        
        self.page.update()

    def crear_tarjeta_habito(self, habito_id, titulo, fecha_limite, hora_limite, prioridad, completado):
        checkbox = ft.Checkbox(
            value=completado,
            on_change=lambda e: self.toggle_habito(habito_id, e.control.value)
        )
        
        colores_prioridad = {
            1: ft.Colors.RED_100,
            2: ft.Colors.YELLOW_100,
            3: ft.Colors.GREEN_100,
        }
        
        etiquetas_prioridad = {
            1: "🔴 Alta",
            2: "🟡 Media",
            3: "🟢 Baja",
        }
        
        color_fondo = ft.Colors.GREY_300 if completado else colores_prioridad.get(prioridad, ft.Colors.GREY_100)
        
        fecha_hora_texto = f"{fecha_limite}"
        if hora_limite:
            fecha_hora_texto += f" a las {hora_limite}"
        
        # BOTÓN DE EDICIÓN AGREGADO
        btn_editar = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color="blue",
            icon_size=20,
            tooltip="Editar hábito",
            on_click=lambda e: self.mostrar_dialogo_editar_habito(habito_id)
        )
        
        return ft.Container(
            content=ft.Row([
                checkbox,
                ft.Column([
                    ft.Text(titulo, size=14, weight="bold", color="black"),
                    ft.Row([
                        ft.Text(f"Límite: {fecha_hora_texto}", size=11, color="black54"),
                    ], spacing=5),
                    ft.Text(f"Prioridad: {etiquetas_prioridad.get(prioridad, '🟡 Media')}", size=11, color="black54"),
                ], spacing=2, expand=True),
                btn_editar,  # BOTÓN AGREGADO AQUÍ
            ]),
            bgcolor=color_fondo,
            border_radius=10,
            padding=10,
        )

    def toggle_habito(self, habito_id, completado):
        self.db.actualizar_habito_completado(habito_id, int(completado))
        
        if completado:
            nivel, exp_actual, exp_necesaria, subio_nivel = self.db.agregar_experiencia(self.usuario_actual)
            
            if subio_nivel:
                self.mostrar_dialogo_subida_nivel(nivel)
        
        self.actualizar_lista_habitos()

    def mostrar_dialogo_agregar_habito(self):
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
            label="Hora límite (ej: 14:30, 1430, 9:00)", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            helper_text="Formatos: HH:MM, HHMM (formato 24h)",
            helper_style=ft.TextStyle(size=10, color="black54"),
            value="23:59"
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
            
            hora_normalizada = self.validador.normalizar_hora(hora_field.value)
            if not self.validador.validar_hora(hora_normalizada):
                mensaje.value = "Hora inválida. Usa formato HH:MM (0-23:0-59)"
                dialogo.update()
                return
            
            fecha_normalizada = self.validador.normalizar_fecha(fecha_field.value)
            prioridad = int(prioridad_dropdown.value)
            
            self.db.agregar_habito(
                self.usuario_actual, 
                titulo_field.value, 
                fecha_normalizada, 
                hora_normalizada,
                prioridad
            )
            
            self.page.close(dialogo)
            self.actualizar_lista_habitos()

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

    def mostrar_dialogo_editar_habito(self, habito_id):
        """NUEVA FUNCIÓN: Diálogo para editar un hábito existente"""
        habito_datos = self.db.obtener_habito_por_id(habito_id)
        
        if not habito_datos:
            return
        
        # Extraer datos del hábito
        if len(habito_datos) >= 5:
            _, titulo_actual, fecha_actual, hora_actual, prioridad_actual = habito_datos
        else:
            _, titulo_actual, fecha_actual, prioridad_actual = habito_datos
            hora_actual = "23:59"
        
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
            label="Hora límite", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            helper_text="Formatos: HH:MM, HHMM (formato 24h)",
            helper_style=ft.TextStyle(size=10, color="black54"),
            value=hora_actual if hora_actual else "23:59"
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
            
            hora_normalizada = self.validador.normalizar_hora(hora_field.value)
            if not self.validador.validar_hora(hora_normalizada):
                mensaje.value = "Hora inválida. Usa formato HH:MM (0-23:0-59)"
                dialogo.update()
                return
            
            fecha_normalizada = self.validador.normalizar_fecha(fecha_field.value)
            prioridad = int(prioridad_dropdown.value)
            
            self.db.editar_habito(
                habito_id,
                titulo_field.value, 
                fecha_normalizada, 
                hora_normalizada,
                prioridad
            )
            
            self.page.close(dialogo)
            self.actualizar_lista_habitos()

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

    def mostrar_notificaciones(self):
        header = ft.Container(
            content=ft.Row([
                ft.Image(src=os.path.join(self.img_path, "Imagen7.png"), width=40, height=40),
                ft.Text("Notificaciones", size=18, weight="bold", color="black"),
            ], alignment=ft.MainAxisAlignment.START),
            padding=15,
            bgcolor=ft.Colors.WHITE,
        )

        self.lista_notificaciones = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.actualizar_lista_notificaciones()

        habitos_pendientes = len(self.db.obtener_habitos_incompletos(self.usuario_actual))
        
        bottom_nav = ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.HOME, icon_color="black", on_click=lambda e: self.mostrar_pantalla_principal()),
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
                ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color="teal", on_click=lambda e: self.mostrar_perfil()),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border=ft.border.only(top=ft.BorderSide(1, "grey300")),
        )

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

    def mostrar_perfil(self):
        nombre_usuario = self.db.obtener_usuario(self.usuario_actual)
        nivel, exp_actual, habitos_completados = self.db.obtener_experiencia(self.usuario_actual)
        
        exp_necesaria = min(nivel * 3, 30)
        
        header = ft.Container(
            content=ft.Row([
                ft.Image(src=os.path.join(self.img_path, "Imagen7.png"), width=40, height=40),
                ft.Column([
                    ft.Text(f"Bienvenido a HabitTracker", size=14, weight="bold", color="black"),
                    ft.Text(nombre_usuario, size=12, color="black54"),
                ], spacing=0),
            ], alignment=ft.MainAxisAlignment.START),
            padding=15,
            bgcolor=ft.Colors.WHITE,
        )

        nombre_field = ft.TextField(
            label="Nombre del Usuario",
            value=nombre_usuario,
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            read_only=True,
            border_color="black54"
        )
        
        id_field = ft.TextField(
            label="Id del Usuario",
            value=self.usuario_actual,
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            read_only=True,
            border_color="black54"
        )
        
        nivel_field = ft.TextField(
            label="Nivel del Usuario",
            value=f"Nivel {nivel}",
            width=300,
            color="black",
            bgcolor=ft.Colors.WHITE,
            read_only=True,
            border_color="black54"
        )

        def crear_cuadro_exp(lleno):
            return ft.Container(
                width=8,
                height=30,
                bgcolor=ft.Colors.BLUE if lleno else ft.Colors.GREY_300,
                border_radius=2,
            )
        
        cuadros_exp = [crear_cuadro_exp(i < exp_actual) for i in range(exp_necesaria)]
        
        barra_experiencia = ft.Container(
            content=ft.Column([
                ft.Text("Experiencia", size=14, weight="bold", color="black", text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=ft.Row(
                        cuadros_exp,
                        spacing=3,
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True,
                    ),
                    width=300,
                    padding=10,
                    border=ft.border.all(1, "black54"),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.Text(
                    f"{exp_actual}/{exp_necesaria} - {habitos_completados} hábitos completados",
                    size=11,
                    color="black54",
                    text_align=ft.TextAlign.CENTER
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            alignment=ft.alignment.center,
        )

        btn_cerrar_sesion = ft.ElevatedButton(
            "Cerrar Sesión",
            bgcolor="black",
            color="white",
            width=300,
            on_click=lambda e: self.cerrar_sesion()
        )

        habitos_pendientes = len(self.db.obtener_habitos_incompletos(self.usuario_actual))
        
        bottom_nav = ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.Icons.HOME, icon_color="black", on_click=lambda e: self.mostrar_pantalla_principal()),
                ft.Container(
                    content=ft.Stack([
                        ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color="black", icon_size=28, 
                                    on_click=lambda e: self.mostrar_notificaciones()),
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
                ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color="teal", on_click=lambda e: self.mostrar_perfil()),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border=ft.border.only(top=ft.BorderSide(1, "grey300")),
        )

        contenido = ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Column([
                        nombre_field,
                        id_field,
                        nivel_field,
                        barra_experiencia,
                        ft.Container(height=20),
                        btn_cerrar_sesion,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=15, vertical=20),
                    alignment=ft.alignment.center,
                ),
                bottom_nav,
            ],
            spacing=0,
            expand=True,
        )

        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.add(contenido)

    def cerrar_sesion(self):
        """ACTUALIZADO: Cerrar sesión y eliminar archivo de sesión"""
        self.db.cerrar_sesion()  # Eliminar sesión guardada
        self.usuario_actual = None
        self.pantalla_inicio()

    def actualizar_lista_notificaciones(self):
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
                    self.crear_tarjeta_notificacion(habito_id, titulo, fecha_limite, hora_limite, prioridad, False)
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
                    self.crear_tarjeta_notificacion(habito_id, titulo, fecha_limite, hora_limite, prioridad, True)
                )
        
        self.page.update()

    def crear_tarjeta_notificacion(self, habito_id, titulo, fecha_limite, hora_limite, prioridad, es_completado):
        try:
            if hora_limite:
                fecha_hora_str = f"{fecha_limite} {hora_limite}"
                fecha_hora_obj = datetime.strptime(fecha_hora_str, "%d/%m/%Y %H:%M")
                ahora = datetime.now()
                diferencia = fecha_hora_obj - ahora
                
                if diferencia.total_seconds() < 0:
                    horas_pasadas = int(abs(diferencia.total_seconds()) / 3600)
                    if horas_pasadas < 24:
                        texto_tiempo = f"{horas_pasadas}h"
                    else:
                        texto_tiempo = f"{int(horas_pasadas/24)} días"
                    estado_texto = "Estado: Vencido"
                    estado_color = "red"
                elif diferencia.total_seconds() < 3600:
                    texto_tiempo = f"{int(diferencia.total_seconds()/60)}min"
                    estado_texto = "Estado: ¡Urgente!"
                    estado_color = "red"
                elif diferencia.days == 0:
                    texto_tiempo = f"{int(diferencia.total_seconds()/3600)}h"
                    estado_texto = "Estado: Hoy"
                    estado_color = "orange"
                else:
                    texto_tiempo = f"{diferencia.days} días"
                    estado_texto = "Estado: Pendiente"
                    estado_color = "black54"
            else:
                fecha_obj = datetime.strptime(fecha_limite, "%d/%m/%Y")
                hoy = datetime.now()
                dias_restantes = (fecha_obj - hoy).days
                
                if dias_restantes < 0:
                    texto_tiempo = f"{abs(dias_restantes)} días"
                    estado_texto = "Estado: Vencido"
                    estado_color = "red"
                elif dias_restantes == 0:
                    texto_tiempo = "Hoy"
                    estado_texto = "Estado: Vence hoy"
                    estado_color = "orange"
                elif dias_restantes == 1:
                    texto_tiempo = "1 día"
                    estado_texto = "Estado: Pendiente"
                    estado_color = "black54"
                else:
                    texto_tiempo = f"{dias_restantes} días"
                    estado_texto = "Estado: Pendiente"
                    estado_color = "black54"
        except:
            texto_tiempo = f"{fecha_limite}"
            if hora_limite:
                texto_tiempo += f" {hora_limite}"
            estado_texto = "Estado: Pendiente"
            estado_color = "black54"

        if es_completado:
            estado_final = "Estado: Completado ✓"
            estado_color = "green"
        elif prioridad == 1:
            estado_final = "Estado: Pendiente"
        elif prioridad == 2:
            estado_final = estado_texto
        else:
            estado_final = "Estado: Incompleto"

        eliminar_btn = None
        if es_completado:
            eliminar_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color="red",
                icon_size=20,
                on_click=lambda e: self.eliminar_habito_notificacion(habito_id)
            )

        fila_contenido = ft.Row([
            ft.Image(src=os.path.join(self.img_path, "Imagen7.png"), width=30, height=30),
            ft.Column([
                ft.Text(f"Actividad de {texto_tiempo}", size=13, weight="bold", color="black"),
                ft.Text(estado_final, size=11, color=estado_color),
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

    def eliminar_habito_notificacion(self, habito_id):
        self.db.eliminar_habito(habito_id)
        self.actualizar_lista_notificaciones()

    def borrar_completados(self):
        habitos_completados = self.db.obtener_habitos_completados(self.usuario_actual)
        for habito in habitos_completados:
            habito_id = habito[0]
            self.db.eliminar_habito(habito_id)
        self.actualizar_lista_notificaciones()


def main(page: ft.Page):
    HabitApp(page)

ft.app(target=main)