"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from AppFlask import app
from AppFlask.conexion import Conexion
from flask import request
from PIL import Image
from PIL import ImageFilter
from io import BytesIO
from flask import send_file
import numpy as np
import cv2

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

#USANDO PILLOW
@app.route('/cargar_pillow', methods=['POST'])
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
            #gray = im.convert('L')
            converted = im.filter(ImageFilter.FIND_EDGES)           
            img_io = BytesIO()
            converted.save(img_io, 'JPEG', quality=70)
            img_io.seek(0)
            im.close()
            return send_file(img_io, mimetype='image/jpeg')
            #return Response(gray.iter_content(chunk_size=10*1024), mimetype="image/jpg", headers={"Content-disposition":"attachment; filename=converted.jpg"})
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

#USANDO OPEN-CV
@app.route('/cargar_opencv', methods=['POST'])
def cargaropen():
    respuesta = ''
    files = request.files
    if len(files) > 0:       
        file = files.get('file')
        if file.filename.endswith('.jpg'):             
            img = Image.open(file.stream)
            pix = img.load()
            npa = np.array(img)
            npa = cv2.resize(npa, (int(img.size[0]/2), int(img.size[1]/2)))

            # Grayscale 
            gray = cv2.cvtColor(npa, cv2.COLOR_BGR2GRAY) 
  
            # Find Canny edges 
            edged = cv2.Canny(gray, 30, 200) 
            cv2.waitKey(0) 
  
            # Finding Contours 
            # Use a copy of the image e.g. edged.copy() 
            # since findContours alters the image 
            contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
  
            #cv2.imshow('Canny Edges After Contouring', edged) 
            cv2.waitKey(0) 
  
            print("Number of Contours found = " + str(len(contours))) 
            print(contours)
            # Draw all contours 
            # -1 signifies drawing all contours 
            cv2.drawContours(edged, contours, -1, (0, 255, 0), 3) 


            img2 = Image.fromarray(edged)
            img_io = BytesIO()
            img2.save(img_io, 'JPEG', quality=70)
            img_io.seek(0)
            img.close()
            return send_file(img_io, mimetype='image/jpeg')           
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

