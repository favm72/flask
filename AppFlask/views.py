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
import time
from imutils.object_detection  import non_max_suppression
import pytesseract
from AppFlask.Controller import login_controller
from AppFlask.Controller import home_controller

def read_file(request, process):
    files = request.files
    if len(files) > 0:       
        file = files.get('file')
        if file.filename.endswith('.jpg'):            
            return (True, process(file))
        else:
            return (False,'el tipo de archivo debe ser jpg')
    else:
        return 'no ha cargado ningun archivo'

def exportar(img):
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

def decode_predictions(scores, geometry):
	# grab the number of rows and columns from the scores volume, then
	# initialize our set of bounding box rectangles and corresponding
	# confidence scores

	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []

	# loop over the number of rows
	for y in range(0, numRows):
		# extract the scores (probabilities), followed by the geometrical
		# data used to derive potential bounding box coordinates that
		# surround text
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]

		# loop over the number of columns
		for x in range(0, numCols):
			# if our score does not have sufficient probability, ignore it
			if scoresData[x] < 0.5:
				continue
			# compute the offset factor as our resulting feature maps will
			# be 4x smaller than the input image
			(offsetX, offsetY) = (x * 4.0, y * 4.0)
			# extract the rotation angle for the prediction and then
			# compute the sin and cosine
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)
			# use the geometry volume to derive the width and height of
			# the bounding box
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]

			# compute both the starting and ending (x, y)-coordinates for
			# the text prediction bounding box
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)

			# add the bounding box coordinates and probability score to
			# our respective lists
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])
	# return a tuple of the bounding boxes and associated confidences
	return (rects, confidences)

@app.route('/contact')
def contact():   
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/readnet', methods=['POST'])
def readnet():
	def process(file):		
		# load the input image and grab the image dimensions
		img = Image.open(file.stream)		
		# load the input image and grab the image dimensions
		#image = cv2.imread(args["image"])
		image = np.array(img)
		width = int(img.size[0]/float(32))*32
		height = int(img.size[1]/float(32))*32
		image = cv2.resize(image, (width, height))
		orig = image.copy()
		(H, W) = image.shape[:2]
		# set the new width and height and then determine the ratio in change
		# for both the width and height
		(newW, newH) = (width, height)
		rW = W / float(newW)
		rH = H / float(newH)
		# resize the image and grab the new image dimensions
		image = cv2.resize(image, (newW, newH))		
		# resize the image and grab the new image dimensions
		
		print("[INFO] loading EAST text detector...")
		net = cv2.dnn.readNet('frozen_east_text_detection.pb')
		# construct a blob from the image and then perform a forward pass of
		# the model to obtain the two output layer sets
		blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
		layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
		start = time.time()
		net.setInput(blob)
		(scores, geometry) = net.forward(layerNames)
		end = time.time()       
		print("[INFO] text detection took {:.6f} seconds".format(end - start))

		# grab the number of rows and columns from the scores volume, then
		# initialize our set of bounding box rectangles and corresponding
		# confidence scores
		#print(type(scores))
		#for k in scores:
		#	print(k)

		(numRows, numCols) = scores.shape[2:4]
		rects = []
		confidences = []

		# loop over the number of rows
		for y in range(0, numRows):
			# extract the scores (probabilities), followed by the geometrical
			# data used to derive potential bounding box coordinates that
			# surround text
			scoresData = scores[0, 0, y]
			xData0 = geometry[0, 0, y]
			xData1 = geometry[0, 1, y]
			xData2 = geometry[0, 2, y]
			xData3 = geometry[0, 3, y]
			anglesData = geometry[0, 4, y]

			# loop over the number of columns
			for x in range(0, numCols):
				# if our score does not have sufficient probability, ignore it
				if scoresData[x] < 0.5:
					continue
				# compute the offset factor as our resulting feature maps will
				# be 4x smaller than the input image
				(offsetX, offsetY) = (x * 4.0, y * 4.0)
				# extract the rotation angle for the prediction and then
				# compute the sin and cosine
				angle = anglesData[x]
				cos = np.cos(angle)
				sin = np.sin(angle)
				# use the geometry volume to derive the width and height of
				# the bounding box
				h = xData0[x] + xData2[x]
				w = xData1[x] + xData3[x]

				# compute both the starting and ending (x, y)-coordinates for
				# the text prediction bounding box
				endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
				endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
				startX = int(endX - w)
				startY = int(endY - h)

				# add the bounding box coordinates and probability score to
				# our respective lists
				rects.append((startX, startY, endX, endY))
				confidences.append(scoresData[x])
		# apply non-maxima suppression to suppress weak, overlapping bounding
		# boxes
		boxes = non_max_suppression(np.array(rects), probs=confidences)

		# loop over the bounding boxes
		print("cantidad de boxes ", len(boxes))
		for (startX, startY, endX, endY) in boxes:
			# scale the bounding box coordinates based on the respective
			# ratios
			startX = int(startX * rW)
			startY = int(startY * rH)
			endX = int(endX * rW)
			endY = int(endY * rH)

			# draw the bounding box on the image
			cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)

		# show the output image
		#cv2.imshow("Text Detection", orig)
		cv2.waitKey(0)
		return Image.fromarray(orig)

	status = read_file(request, process)
	if status[0]:
		return exportar(status[1])
	return render_template(
		'index.html',
		title='NETWORK',
		year=datetime.now().year,
		lista = list(),
		respuesta=status[1]
	)

@app.route('/readnet2', methods=['POST'])
def readnet2():
	def process(file):		
		# load the input image and grab the image dimensions
		img = Image.open(file.stream)		
		# load the input image and grab the image dimensions
		#image = cv2.imread(args["image"])
		image = np.array(img)
		width = int(img.size[0]/float(32))*32
		height = int(img.size[1]/float(32))*32
		image = cv2.resize(image, (width, height))
		orig = image.copy()
		(H, W) = image.shape[:2]
		# set the new width and height and then determine the ratio in change
		# for both the width and height
		(newW, newH) = (width, height)
		rW = W / float(newW)
		rH = H / float(newH)
		# resize the image and grab the new image dimensions
		image = cv2.resize(image, (newW, newH))		
		# resize the image and grab the new image dimensions
		
		print("[INFO] loading EAST text detector...")
		net = cv2.dnn.readNet('frozen_east_text_detection.pb')
		# construct a blob from the image and then perform a forward pass of
		# the model to obtain the two output layer sets
		blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
		layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
		start = time.time()
		net.setInput(blob)
		(scores, geometry) = net.forward(layerNames)
		end = time.time()       
		print("[INFO] text detection took {:.6f} seconds".format(end - start))

		(rects, confidences) = decode_predictions(scores, geometry)
		# apply non-maxima suppression to suppress weak, overlapping bounding
		# boxes
		boxes = non_max_suppression(np.array(rects), probs=confidences)
		# initialize the list of results
		results = []
		# loop over the bounding boxes
		print("cantidad de boxes ", len(boxes))
		for (startX, startY, endX, endY) in boxes:
			# scale the bounding box coordinates based on the respective
			# ratios
			startX = int(startX * rW)
			startY = int(startY * rH)
			endX = int(endX * rW)
			endY = int(endY * rH)

			# in order to obtain a better OCR of the text we can potentially
			# apply a bit of padding surrounding the bounding box -- here we
			# are computing the deltas in both the x and y directions
			dX = int((endX - startX) * 0.05)
			dY = int((endY - startY) * 0.05)
 
			# apply padding to each side of the bounding box, respectively
			startX = max(0, startX - dX)
			startY = max(0, startY - dY)
			endX = min(W, endX + (dX * 2))
			endY = min(H, endY + (dY * 2))

			# extract the actual padded ROI
			roi = orig[startY:endY, startX:endX]

			# in order to apply Tesseract v4 to OCR text we must supply
			# (1) a language, (2) an OEM flag of 4, indicating that the we
			# wish to use the LSTM neural net model for OCR, and finally
			# (3) an OEM value, in this case, 7 which implies that we are
			# treating the ROI as a single line of text
			config = ("-l spa --oem 1 --psm 7")
			pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
			text = pytesseract.image_to_string(roi, config=config)

			# add the bounding box coordinates and OCR'd text to the list
			# of results
			results.append(((startX, startY, endX, endY), text))

			# draw the bounding box on the image
			#cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)

		# sort the results bounding box coordinates from top to bottom
		results = sorted(results, key=lambda r:r[0][1])
 
		# loop over the results
		for ((startX, startY, endX, endY), text) in results:
			# display the text OCR'd by Tesseract
			print("OCR TEXT")
			print("========")
			print("{}\n".format(text))
 
			# strip out non-ASCII text so we can draw the text on the image
			# using OpenCV, then draw the text and a bounding box surrounding
			# the text region of the input image
			text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
			#output = orig.copy()
			cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)
			cv2.putText(orig, text, (startX, startY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
 
			# show the output image
			#cv2.imshow("Text Detection", output)
			#cv2.waitKey(0)

		# show the output image
		#cv2.imshow("Text Detection", orig)
		cv2.waitKey(0)
		return Image.fromarray(orig)

	status = read_file(request, process)
	if status[0]:
		return exportar(status[1])
	return render_template(
		'index.html',
		title='NETWORK',
		year=datetime.now().year,
		lista = list(),
		respuesta=status[1]
	)


@app.route('/about')
def about():   
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

def resize32(image):
	(height, width) = image.shape[:2]
	return cv2.resize(image, (32*int(width/32), 32*int(height/32)))

#TEST
@app.route('/test', methods=['POST'])
def test():    
	def process(file):
		img = Image.open(file.stream)
		image = np.array(img)		
		return resize32(image)
	status = read_file(request, process)
	#if status[0]:
		#return exportar(status[1])
	return render_template(
		'index.html',
		title='AFTER POST',
		year=datetime.now().year,
		lista = list(),
		respuesta=status[1]
	)


#USANDO PILLOW
@app.route('/cargar_pillow', methods=['POST'])
def cargar():    
	def process(file):
		img = Image.open(file.stream)
		pix = img.load()
		print(img.size)
		print(pix[400,600])  # Get the RGBA Value of the a pixel of an image
		#gray = im.convert('L')
		converted = img.filter(ImageFilter.FIND_EDGES)       
		return img
	status = read_file(request, process)
	if status[0]:
		return exportar(status[1])
	return render_template(
		'index.html',
		title='AFTER POST',
		year=datetime.now().year,
		lista = list(),
		respuesta=status[1]
	)

#USANDO OPEN-CV
@app.route('/cargar_opencv', methods=['POST'])
def cargaropen():
	def process(file):
		img = Image.open(file.stream)
		#pix = img.load()
		npa = np.array(img)            
		npa = cv2.resize(npa, (int(img.size[0]/2), int(img.size[1]/2)))
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
		#print("Number of Contours found = " + str(len(contours))) 
		#print(contours)
		# Draw all contours 
		# -1 signifies drawing all contours 
		cv2.drawContours(edged, contours, -1, (0, 255, 0), 3) 
		return Image.fromarray(edged)
	status = read_file(request, process)
	if status[0]:
		return exportar(status[1])       

	return render_template(
		'index.html',
		title='AFTER POST',
		year=datetime.now().year,
		lista = list(),
		respuesta=respuesta
	)