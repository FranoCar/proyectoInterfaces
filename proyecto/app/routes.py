from app import app, render_template, request,  redirect, url_for

@app.route("/")
def root():
	return redirect(url_for('recomendaciones'))

@app.route("/recomendaciones")
def recomendaciones():
	return render_template('recomendaciones.html')

@app.route("/catalogo")
def catalogo():
	return render_template('catalogo.html')

@app.route("/noticias")
def noticias():
	return render_template('noticias.html')

@app.route("/biblioteca")
def biblioteca():
	return render_template('biblioteca.html')

@app.route("/carrito")
def carrito():
	return render_template('carrito.html')

#----------------    La idea es solo usar 1 html para estos     ----------------
#---------------- elementos y cambiar su contenido usando un id ----------------
@app.route("/juego")
def juego():
	# La idea es llamar a esta url tipo url_for("juego",id=[idJuego]), 
	# para que aparezca como argumento en la url (ej: /juego?id=2198379).
	idJuego = request.args.get('id') 
	return render_template('juego.html',juego=idJuego)

@app.route("/noticia")
def noticia():
	# La idea es llamar a esta url tipo url_for("noticia",id=[idNoticia]), 
	# para que aparezca como argumento en la url (ej: /noticia?id=asdfha).
	idNoticia = request.args.get('id')
	return render_template('noticia.html',noticia=idNoticia)
