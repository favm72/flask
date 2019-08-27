from datetime import datetime
import flask as fl
from AppFlask import app

@app.route('/')
@app.route('/login', methods=['GET'])
def get_login():	
	return fl.render_template(
		'login.html'
	)

@app.route('/login', methods=['POST'])
def post_login():
	txt_user = fl.request.form["user"]
	txt_pass = fl.request.form["pass"]
	if (txt_user == "fabio" and txt_pass == "123"):	    
		#return fl.redirect(fl.url_for("/home"), code=307)
		return fl.render_template(
			'index.html',
			title='TEST INICIO',
			year=datetime.now().year,
			lista = [])
	else:
		return fl.render_template(
			'login.html',
			mensaje="invalid credentials"
		)