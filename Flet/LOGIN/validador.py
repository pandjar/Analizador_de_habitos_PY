import re


class ValidadorFechaHora:
    """Clase para validar y normalizar fechas y horas"""
    
    @staticmethod
    def normalizar_fecha(fecha_texto):
        """Convierte diferentes formatos de fecha a dd/mm/yyyy"""
        fecha_texto = fecha_texto.strip()
        
        # Formato dd/mm/yyyy o dd-mm-yyyy
        if re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{4}$', fecha_texto):
            fecha_texto = fecha_texto.replace('-', '/')
            partes = fecha_texto.split('/')
            return f"{int(partes[0]):02d}/{int(partes[1]):02d}/{partes[2]}"
        
        # Formato yyyy/mm/dd o yyyy-mm-dd
        elif re.match(r'^\d{4}[/-]\d{1,2}[/-]\d{1,2}$', fecha_texto):
            fecha_texto = fecha_texto.replace('-', '/')
            partes = fecha_texto.split('/')
            return f"{int(partes[2]):02d}/{int(partes[1]):02d}/{partes[0]}"
        
        # Formato ddmmyyyy sin separadores
        elif re.match(r'^\d{8}$', fecha_texto):
            return f"{fecha_texto[:2]}/{fecha_texto[2:4]}/{fecha_texto[4:]}"
        
        return fecha_texto
    
    @staticmethod
    def normalizar_hora(hora_texto):
        """Convierte diferentes formatos de hora a HH:MM"""
        hora_texto = hora_texto.strip()
        
        # Formato HH:MM o H:MM
        if re.match(r'^\d{1,2}:\d{2}$', hora_texto):
            partes = hora_texto.split(':')
            return f"{int(partes[0]):02d}:{partes[1]}"
        
        # Formato HHMM sin separador
        elif re.match(r'^\d{4}$', hora_texto):
            return f"{hora_texto[:2]}:{hora_texto[2:]}"
        
        # Formato H:M (añadir cero)
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