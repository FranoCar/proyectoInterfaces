from app import app, render_template, request,  redirect, url_for, sqlite3, getCarrito

@app.route("/")
def root():
	return redirect(url_for('recomendaciones'))

@app.route("/recomendaciones")
def recomendaciones():
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('SELECT id,titulo,caratula,precio,oferta FROM juego WHERE precio > oferta ORDER BY precio LIMIT 3')
	ofertas = cur.fetchall()
	cur.execute('SELECT id,titulo,caratula,precio,oferta FROM juego LIMIT 3')
	novs = cur.fetchall()
	cur.execute('SELECT id,titulo,caratula,precio,oferta,gj.juego FROM juego, generojuego as gj WHERE gj.juego = id AND gj.genero="Acción" ORDER BY id DESC LIMIT 3')
	jugados = cur.fetchall()
	carrito = getCarrito()
	con.close()
	return render_template('recomendaciones.html', ofertas=ofertas, novs=novs, jugados=jugados, carrito=carrito)

@app.route("/catalogo")
def catalogo():
	carrito = getCarrito()
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('SELECT id,titulo,caratula,cal_usr,cal_exp,precio,oferta FROM juego')
	juegos = cur.fetchall()

	con.close()
	return render_template('catalogo.html',juegos=juegos,carrito=carrito)

@app.route("/noticias", methods = ['GET','POST'])
def noticias():
	carrito = getCarrito()
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	if request.method == 'POST':
		if len(request.form["nombre"]) > 0:
			cur.execute(f'''SELECT * FROM noticia
							WHERE titulo LIKE "%{request.form["nombre"]}%" 
							ORDER BY fecha DESC''')
		else:
			cur.execute('select * from noticia order by fecha DESC')
	else:
		cur.execute('select * from noticia order by fecha DESC')
	noticias = cur.fetchall()

	con.close()
	return render_template('noticias.html',carrito=carrito,noticias=noticias)

@app.route("/biblioteca", methods = ['GET','POST'])
def biblioteca():
	carrito = getCarrito()
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute("select * from biblioteca order by ultima desc limit 4")
	biblioteca = cur.fetchall()
	juegosjugados = []
	for b in biblioteca:
		cur.execute('SELECT id,titulo,caratula FROM juego where id=?',(b[0],))
		juegosjugados.append(cur.fetchone())
	cur.execute("select * from biblioteca order by instalado desc, esta_instalado")
	biblioteca = cur.fetchall()
	if request.method == 'POST':
		if 'filtro' in request.form:
			if request.form['filtro'] == 'alfabetico':
				cur.execute("select * from biblioteca order by esta_instalado desc,juego asc")
			elif request.form['filtro'] == 'instalado':
				cur.execute("select * from biblioteca order by esta_instalado desc,instalado desc")
			else:
				cur.execute("select * from biblioteca order by esta_instalado desc,ultima desc")
			biblioteca = cur.fetchall()
		elif len(request.form["nombre"]) > 0:
			print(request.form["nombre"])
			cur.execute(f'''SELECT * from biblioteca as B, (SELECT id FROM juego
							WHERE titulo LIKE "%{request.form["nombre"]}%") as J
							WHERE B.juego = J.id''')
			biblioteca = cur.fetchall()
	juegosinstalados = []
	instalado = []
	for b in biblioteca:
		cur.execute('SELECT id,titulo,caratula FROM juego where id=?',(b[0],))
		juegosinstalados.append(cur.fetchone())
		instalado.append(b[3])
		
	con.close()
	return render_template('biblioteca.html',	juegos_j=juegosjugados,
												carrito=carrito,
												juegos_i=juegosinstalados,
												instalado=instalado)

@app.route("/carrito", methods = ['GET','POST'])
def carrito():
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	if request.method == 'POST':
		if 'borrar' in request.form:
			cur.execute('DELETE FROM carrito WHERE juego==?',(request.form['borrar'],))
			con.commit()
		elif 'pagar' in request.form:
			cur.execute('SELECT * FROM carrito')
			ids = cur.fetchall()
			for id_j in ids:
				cur.execute('INSERT INTO biblioteca VALUES (?,?,?,?)',
								(id_j[0],'2000-01-01','2000-01-01',0))
				cur.execute('DELETE FROM carrito WHERE juego=?',(id_j[0],))
			con.commit()
	cur.execute('SELECT * FROM carrito')
	ids = cur.fetchall()
	juegos = []
	precios = []
	total = 0
	for id_j in ids:
		cur.execute('SELECT * FROM juego WHERE id==?',(id_j[0],))
		juego = cur.fetchone()
		if juego[6] == juego[7]:
			precios.append(juego[6])
			total = total + juego[6]
		else:
			precios.append(juego[7])
			total = total + juego[7]
		juegos.append(juego)
	return render_template('carrito.html',juegos=juegos,precios=precios,total=total)

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
	cur.execute('SELECT * FROM biblioteca WHERE juego == ?',(idJuego,))
	comprado = cur.fetchone()	
	encarrito=True
	enbiblioteca=True
	if request.method == 'POST': #Agregar a carrito
		if existente is None and comprado is None:
			cur.execute('INSERT INTO carrito VALUES (?)',(idJuego,))
			con.commit()
		if request.form['comprar'] == 'catalogo':
			return redirect(url_for('catalogo'))
		else:
			return redirect(url_for('carrito'))
	else:
		if existente is None:
			encarrito= False
		if comprado is None:
			enbiblioteca = False

	cur.execute('SELECT * FROM juego WHERE id == ?',(idJuego,))
	juego = cur.fetchone()
	precio = juego[6]
	oferta = juego[7]
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
	carrito = getCarrito()
	return render_template('juego.html',juego=juego,
										precio=precio,
										oferta=oferta,
										editores=editores,
										desarrolladores=desarrolladores,
										tags=tags,
										generos=generos,
										encarrito=encarrito,
										enbiblioteca=enbiblioteca,
										carrito=carrito)

@app.route("/noticia")
def noticia():
	# La idea es llamar a esta url tipo url_for("noticia",id=[idNoticia]), 
	# para que aparezca como argumento en la url (ej: /noticia?id=asdfha).
	idNoticia = request.args.get('id')
	return render_template('noticia.html',noticia=idNoticia)
