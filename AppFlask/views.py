"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from AppFlask import app
from AppFlask.conexion import Conexion
from flask import request
from PIL import Image

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

@app.route('/cargar', methods=['POST'])
def cargar():
    respuesta = ''
    files = request.files
    if len(files) > 0:       
        file = files.get('file')
        if file.filename.endswith('.jpg'): 
            im = Image.open(file.stream)
            pix = im.load()
            print(im.size)  # Get the width and hight of the image for iterating over
            #for x in range(im.size[0]):
            #    for y in range(im.size[1]):
            #        pix[x,y] = 0.25 * pix[x,y][0]+ 0.5G+0.25B
            #        pass
            print(pix[400,600])  # Get the RGBA Value of the a pixel of an image
            gray = im.convert('L')            
            return Response(gray, mimetype="image/jpg", headers={"Content-disposition":"attachment; filename=converted.jpg"})
            im.close()
            #im.save('alive_parrot.png')
        else:
            respuesta='el tipo de archivo debe ser jpg'
    else:
        respuesta='no ha cargado ningun archivo'
  
    return render_template(
        'index.html',
        title='AFTER POST',
        year=datetime.now().year,
        lista = list(),
        respuesta=respuesta
    )
