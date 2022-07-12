from app import app, render_template, request,  redirect, url_for, sqlite3

@app.route("/")
def root():
	return redirect(url_for('recomendaciones'))

@app.route("/recomendaciones")
def recomendaciones():
	return render_template('recomendaciones.html')

@app.route("/catalogo")
def catalogo():
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('SELECT id,titulo,caratula,cal_usr,cal_exp,precio,oferta FROM juego')
	juegos = cur.fetchall()
	con.close()
	return render_template('catalogo.html',juegos=juegos)

@app.route("/noticias")
def noticias():
	return render_template('noticias.html')

@app.route("/biblioteca")
def biblioteca():
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('SELECT id,titulo,caratula FROM juego')
	juegos = cur.fetchall()
	con.close()
	return render_template('biblioteca.html',juegos=juegos)

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
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('SELECT * FROM juego WHERE id == ?',(idJuego,))
	juego = cur.fetchone()
	cur.execute('SELECT editor FROM editorjuego WHERE juego == ?',(idJuego,))
	editores = cur.fetchall()
	cur.execute('SELECT desarrollador FROM desarrolladorjuego WHERE juego == ?',(idJuego,))
	desarrolladores = cur.fetchall()
	cur.execute('SELECT tag FROM tagjuego WHERE juego == ?',(idJuego,))
	tags = cur.fetchall()
	cur.execute('SELECT genero FROM generojuego WHERE juego == ?',(idJuego,))
	aux = cur.fetchall()
	generos = ""
	for g in aux:
		generos = generos + ', ' + g[0]
	generos = generos[2:]

	con.close()
	return render_template('juego.html',juego=juego,
										editores=editores,
										desarrolladores=desarrolladores,
										tags=tags,
										generos=generos)

@app.route("/noticia")
def noticia():
	# La idea es llamar a esta url tipo url_for("noticia",id=[idNoticia]), 
	# para que aparezca como argumento en la url (ej: /noticia?id=asdfha).
	idNoticia = request.args.get('id')
	return render_template('noticia.html',noticia=idNoticia)
