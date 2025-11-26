import sqlite3
import os
from datetime import datetime
import json


class DatabaseManager:
    """Clase para manejar todas las operaciones de base de datos"""
    
    def __init__(self):
        self.user_db_path = os.path.join(os.path.dirname(__file__), "User.db")
        self.habitos_db_path = os.path.join(os.path.dirname(__file__), "habito.db")
        self.session_file = os.path.join(os.path.dirname(__file__), "session.json")
        self.inicializar_db()

    def inicializar_db(self):
        """Inicializa las bases de datos"""
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
                HoraLimite TEXT,
                Prioridad INTEGER DEFAULT 1,
                Completado INTEGER DEFAULT 0,
                FechaCreacion TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Base de datos de experiencia
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

    # MÉTODOS DE SESIÓN
    
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

    # MÉTODOS DE USUARIOS
    
    def registrar_usuario(self, nombre, apellido, usuarioid, correo, contrasena):
        """Registra un nuevo usuario"""
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
        """Valida las credenciales del usuario"""
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE UsuarioID=? AND Contraseña=?", (usuarioid, contrasena))
        user = cursor.fetchone()
        conn.close()
        return user is not None

    def obtener_usuario(self, usuarioid):
        """Obtiene el nombre del usuario"""
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Nombre FROM User WHERE UsuarioID=?", (usuarioid,))
        user = cursor.fetchone()
        conn.close()
        return user[0] if user else "Usuario"

    # MÉTODOS DE HÁBITOS
    
    def obtener_habitos(self, usuarioid):
        """Obtiene todos los hábitos del usuario"""
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
        """Agrega un nuevo hábito"""
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
        """Marca un hábito como completado o no completado"""
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE Habitos SET Completado=? WHERE ID=?", (completado, habito_id))
        conn.commit()
        conn.close()

    def eliminar_habito(self, habito_id):
        """Elimina un hábito"""
        conn = sqlite3.connect(self.habitos_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Habitos WHERE ID=?", (habito_id,))
        conn.commit()
        conn.close()

    def obtener_habitos_incompletos(self, usuarioid):
        """Obtiene los hábitos incompletos del usuario"""
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
        """Obtiene los hábitos completados del usuario"""
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

    # MÉTODOS DE EXPERIENCIA
    
    def obtener_experiencia(self, usuarioid):
        """Obtiene la experiencia del usuario"""
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
        """Inicializa la experiencia de un usuario nuevo"""
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Experiencia (UsuarioID, Nivel, ExperienciaActual, HabitosCompletados) VALUES (?, 1, 0, 0)", (usuarioid,))
        conn.commit()
        conn.close()

    def agregar_experiencia(self, usuarioid):
        """Agrega experiencia al completar un hábito"""
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