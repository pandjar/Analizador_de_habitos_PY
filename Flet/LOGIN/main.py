import flet as ft
import sqlite3
import os
from datetime import datetime
import re

# Clase para manejar la base de datos
class DatabaseManager:
    def __init__(self):
        self.user_db_path = os.path.join(os.path.dirname(__file__), "User.db")
        self.habitos_db_path = os.path.join(os.path.dirname(__file__), "habito.db")
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
        
        # Base de datos de hábitos
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Habitos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                UsuarioID TEXT,
                Titulo TEXT,
                FechaLimite TEXT,
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
        cursor.execute("SELECT ID, Titulo, FechaLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? ORDER BY Completado ASC, Prioridad ASC", (usuarioid,))
        habitos = cursor.fetchall()
        conn.close()
        return habitos

    def agregar_habito(self, usuarioid, titulo, fecha_limite, prioridad):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        # Verificar si la columna FechaCreacion existe
        cursor.execute("PRAGMA table_info(Habitos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if "FechaCreacion" in columnas:
            fecha_creacion = datetime.now().strftime("%d/%m/%Y")
            cursor.execute(
                "INSERT INTO Habitos (UsuarioID, Titulo, FechaLimite, Prioridad, FechaCreacion) VALUES (?, ?, ?, ?, ?)",
                (usuarioid, titulo, fecha_limite, prioridad, fecha_creacion)
            )
        else:
            # Si no existe la columna, insertar sin ella
            cursor.execute(
                "INSERT INTO Habitos (UsuarioID, Titulo, FechaLimite, Prioridad) VALUES (?, ?, ?, ?)",
                (usuarioid, titulo, fecha_limite, prioridad)
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
        cursor.execute("SELECT ID, Titulo, FechaLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? AND Completado=0 ORDER BY Prioridad ASC", (usuarioid,))
        habitos = cursor.fetchall()
        conn.close()
        return habitos

    def obtener_habitos_completados(self, usuarioid):
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Titulo, FechaLimite, Prioridad, Completado FROM Habitos WHERE UsuarioID=? AND Completado=1 ORDER BY Prioridad ASC", (usuarioid,))
        habitos = cursor.fetchall()
        conn.close()
        return habitos

    def obtener_habitos_vencidos(self, usuarioid):
        "Obtiene hábitos incompletos que ya pasaron su fecha límite"
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, Titulo, FechaLimite FROM Habitos WHERE UsuarioID=? AND Completado=0",
            (usuarioid,)
        )
        habitos = cursor.fetchall()
        conn.close()
        
        hoy = datetime.now()
        vencidos = []
        for hab_id, titulo, fecha_limite in habitos:
            try:
                fecha_obj = datetime.strptime(fecha_limite, "%d/%m/%Y")
                if fecha_obj.date() < hoy.date():
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
            exp_actual = 0  # Resetear experiencia al bajar de nivel
            
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE Experiencia SET Nivel=?, ExperienciaActual=? WHERE UsuarioID=?", 
                          (nivel, exp_actual, usuarioid))
            conn.commit()
            conn.close()
            
            return True, nivel
        return False, nivel


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
        self.usuario_actual = None
        self.mostrar_mensaje_nivel = None  # Para guardar mensaje de nivel reducido

        self.pantalla_inicio()

    def normalizar_fecha(self, fecha_texto):
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
        
        # Mostrar lista de hábitos vencidos
        for hab_id, titulo, fecha in habitos_vencidos[:3]:  # Mostrar máximo 3
            dialogo_contenido.controls.append(
                ft.Text(f"• {titulo} (vencido: {fecha})", size=11, color="black")
            )
        
        if len(habitos_vencidos) > 3:
            dialogo_contenido.controls.append(
                ft.Text(f"... y {len(habitos_vencidos) - 3} más", size=11, color="black54", italic=True)
            )

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(" Atención", size=20, weight="bold", color="red"),
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
        # Eliminar hábitos vencidos
        for hab_id, _, _ in habitos_vencidos:
            self.db.eliminar_habito(hab_id)
        
        # Reducir nivel
        bajo_nivel, nivel_actual = self.db.reducir_nivel(self.usuario_actual)
        
        # Cerrar el diálogo
        self.page.close(dialogo)
        
        # Guardar si bajó de nivel para mostrarlo después
        self.mostrar_mensaje_nivel = (bajo_nivel, nivel_actual) if bajo_nivel else None
        
        # Recargar la pantalla 5 completamente
        self.cargar_pantalla_principal_sin_verificacion()

    def mostrar_dialogo_nivel_reducido(self, nivel_actual):
        "Muestra diálogo informando que el nivel fue reducido"
        def cerrar_y_actualizar(e):
            self.page.close(dialogo)
            # Actualizar la pantalla para reflejar los cambios
            self.page.update()
        
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ARROW_DOWNWARD, color="red", size=30),
                ft.Text("Nivel Reducido", size=20, weight="bold", color="red"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column([
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
        
        # Mostrar mensaje de nivel reducido si existe
        if self.mostrar_mensaje_nivel:
            bajo_nivel, nivel_actual = self.mostrar_mensaje_nivel
            self.mostrar_mensaje_nivel = None  # Limpiar después de mostrar
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
        # Verificar hábitos vencidos al entrar
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
            for habito_id, titulo, fecha_limite, prioridad, completado in habitos:
                self.lista_habitos.controls.append(
                    self.crear_tarjeta_habito(habito_id, titulo, fecha_limite, prioridad, bool(completado))
                )
        
        self.page.update()

    def crear_tarjeta_habito(self, habito_id, titulo, fecha_limite, prioridad, completado):
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
        
        return ft.Container(
            content=ft.Row([
                checkbox,
                ft.Column([
                    ft.Text(titulo, size=14, weight="bold", color="black"),
                    ft.Row([
                        ft.Text(f"Fecha: {fecha_limite}", size=11, color="black54"),
                        ft.Text("|", size=11, color="black54"),
                        ft.Text(f"Prioridad: {etiquetas_prioridad.get(prioridad, '🟡 Media')}", size=11, color="black54"),
                    ], spacing=5),
                ], spacing=2, expand=True),
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
            label="Fecha límite (ej: 25/12/2024, 2024-12-25, 25122024)", 
            width=300, 
            color="black",
            bgcolor=ft.Colors.WHITE,
            border_color="black54",
            helper_text="Formatos: dd/mm/yyyy, yyyy-mm-dd, dd-mm-yyyy, ddmmyyyy",
            helper_style=ft.TextStyle(size=10, color="black54")
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
            if not titulo_field.value or not fecha_field.value:
                mensaje.value = "Por favor completa todos los campos"
                dialogo.update()
                return
            
            fecha_normalizada = self.normalizar_fecha(fecha_field.value)
            prioridad = int(prioridad_dropdown.value)
            self.db.agregar_habito(self.usuario_actual, titulo_field.value, fecha_normalizada, prioridad)
            self.page.close(dialogo)
            self.actualizar_lista_habitos()

        dialogo = ft.AlertDialog(
            title=ft.Text("Nuevo Hábito", color="black"),
            content=ft.Column([
                titulo_field,
                fecha_field,
                prioridad_dropdown,
                mensaje,
            ], tight=True, height=280),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialogo), style=ft.ButtonStyle(color="black")),
                ft.ElevatedButton("Agregar", bgcolor="black", color="white", on_click=agregar_habito),
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
            for habito_id, titulo, fecha_limite, prioridad, completado in habitos_pendientes:
                self.lista_notificaciones.controls.append(
                    self.crear_tarjeta_notificacion(habito_id, titulo, fecha_limite, prioridad, False)
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
            for habito_id, titulo, fecha_limite, prioridad, completado in habitos_completados:
                self.lista_notificaciones.controls.append(
                    self.crear_tarjeta_notificacion(habito_id, titulo, fecha_limite, prioridad, True)
                )
        
        self.page.update()

    def crear_tarjeta_notificacion(self, habito_id, titulo, fecha_limite, prioridad, es_completado):
        try:
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
            texto_tiempo = fecha_limite
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
        for habito_id, _, _, _, _ in habitos_completados:
            self.db.eliminar_habito(habito_id)
        self.actualizar_lista_notificaciones()


def main(page: ft.Page):
    HabitApp(page)

ft.app(target=main)