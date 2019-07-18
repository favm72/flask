"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from AppFlask import app
from AppFlask.conexion import Conexion

@app.route('/')
@app.route('/home')
def home():
    c = Conexion()
    lista = c.consultar("select * from Federation")   
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        lista = lista
    )

@app.route('/contact')
def contact():   
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():   
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
