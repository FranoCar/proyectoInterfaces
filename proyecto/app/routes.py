from app import app, render_template, request,  redirect, url_for, sqlite3

@app.route("/")
def root():
	return redirect(url_for('recomendaciones'))

@app.route("/recomendaciones")
def recomendaciones():
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('SELECT id,titulo,caratula,precio,oferta FROM juego WHERE substring(precio,2,1) > substring(oferta,2,1) ORDER BY precio LIMIT 3')
	ofertas = cur.fetchall()
	cur.execute('SELECT id,titulo,caratula,precio,oferta FROM juego LIMIT 3')
	novs = cur.fetchall()
	cur.execute('SELECT id,titulo,caratula,precio,oferta,gj.juego FROM juego, generojuego as gj WHERE gj.juego = id AND gj.genero="Acción" ORDER BY id DESC LIMIT 3')
	jugados = cur.fetchall()
	con.close()
	return render_template('recomendaciones.html', ofertas=ofertas, novs=novs, jugados=jugados)

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
	cur.execute('SELECT id,titulo,caratula FROM juego limit 5')
	juegos = cur.fetchall()
	con.close()
	return render_template('biblioteca.html',juegos=juegos)

@app.route("/carrito", methods = ['GET','POST'])
def carrito():
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	if request.method == 'POST':
		if 'borrar' in request.form:
			cur.execute('DELETE FROM carrito WHERE juego==?',(request.form['borrar'],))
			con.commit()
	cur.execute('SELECT * FROM carrito')
	ids = cur.fetchall()
	juegos = []
	for id_j in ids:
		cur.execute('SELECT * FROM juego WHERE id==?',(id_j[0],))
		juegos.append(cur.fetchone())
	return render_template('carrito.html',juegos=juegos)

#----------------    La idea es solo usar 1 html para estos     ----------------
#---------------- elementos y cambiar su contenido usando un id ----------------
@app.route("/juego", methods = ['GET','POST'])
def juego():
	# La idea es llamar a esta url tipo url_for("juego",id=[idJuego]), 
	# para que aparezca como argumento en la url (ej: /juego?id=2198379).
	idJuego = request.args.get('id') 
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('SELECT * FROM carrito WHERE juego == ?',(idJuego,))
	existente = cur.fetchone()	
	encarrito=True
	
	if request.method == 'POST': #Agregar a carrito
		if existente is None:
			cur.execute('INSERT INTO carrito VALUES (?)',(idJuego,))
			con.commit()
	else:
		if existente is None:
			encarrito= False
	cur.execute('SELECT * FROM juego WHERE id == ?',(idJuego,))
	juego = cur.fetchone()
	precio = 0
	oferta = 0
	if '$' in juego[6]:
		precio = int(float(juego[6].strip('$'))*1000)
		oferta = int(float(juego[7].strip('$'))*1000)

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
										precio=precio,
										oferta=oferta,
										editores=editores,
										desarrolladores=desarrolladores,
										tags=tags,
										generos=generos,
										encarrito=encarrito)

@app.route("/noticia")
def noticia():
	# La idea es llamar a esta url tipo url_for("noticia",id=[idNoticia]), 
	# para que aparezca como argumento en la url (ej: /noticia?id=asdfha).
	idNoticia = request.args.get('id')
	return render_template('noticia.html',noticia=idNoticia)
