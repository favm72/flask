from flask import render_template
from AppFlask import app
from datetime import datetime

@app.route('/home')
def home():
	#c = Conexion()
	#lista = c.consultar("select * from Federation")   
	return render_template(
		'index.html',
		title='TEST INICIO',
		year=datetime.now().year,
		lista = []
	)