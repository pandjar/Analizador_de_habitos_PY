class Database:
    def __init__(self, db_name="usuarios.db"):
        import sqlite3
        self.conn = sqlite3.connect(db_name)
        self.crear_tabla()

    def crear_tabla(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Apellido TEXT NOT NULL,
                UsuarioID TEXT UNIQUE NOT NULL,
                Correo TEXT,
                Contraseña TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def registrar_usuario(self, nombre, apellido, usuarioid, correo, contrasena):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO User (Nombre, Apellido, UsuarioID, Correo, Contraseña) VALUES (?, ?, ?, ?, ?)",
                (nombre, apellido, usuarioid, correo, contrasena)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print("Error al registrar usuario:", e)
            return False

    def validar_usuario(self, usuarioid, contrasena):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM User WHERE UsuarioID=? AND Contraseña=?", (usuarioid, contrasena))
        return cursor.fetchone() is not None
