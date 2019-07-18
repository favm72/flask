import pyodbc

class Conexion:
    """description of class"""
    def __init__(self):
        self.con = pyodbc.connect(
            driver='{SQL Server}',
            host='.\SQLExpress',
            database='CGTP',
            trusted_connection='yes')

    def consultar(self, query):
        cursor = self.con.cursor()
        cursor.execute(query)
        lista = []
        for row in cursor:
            lista.append(row)
        return lista

