import pandas as pd
from bs4 import BeautifulSoup as bs
#import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import time
from urllib.parse import quote
from googletrans import Translator
import sqlite3

def getImage(name):
	param = f'?term={quote(name)}'
	url = 'https://www.steamgriddb.com/search/grids/512x512,1024x1024/all/all'
	url = url + param
	driver = webdriver.Firefox()
	driver.get(url)
	#time.sleep(5)
	try:
		WebDriverWait(driver,5).until(
			EC.presence_of_element_located((By.XPATH,'//form[@class="search-filters"]'))
		)
	except TimeoutException as e:
		print(f'wait timed out for{name}')
	time.sleep(1)

	html = driver.page_source
	driver.close()
	soup = bs(html, 'lxml')
	img = soup.find('img', attrs={'class': 'lazy entered loaded'})
	if img is not None:
		return img['src']
	else:
		return None
def getUniques(col):
	uniques = []
	for c in col.dropna().unique():
		splits = c.split(',')
		for split in splits:
			if split not in uniques:
				uniques.append(split)
	return uniques
#generos
def getGenres(genres):
	uniques = getUniques(genres)
	mapa = {}
	ommit = ['Free to Play', 'RPG', 'Indie', 'Valve', 'HTC','Violent', 'Short']
	mapa['Violent'] = 'Violento'
	mapa['Short'] = 'Corto'

	translator = Translator()
	for i, genre in enumerate(uniques):
		if genre not in ommit:
			try:
				translated = translator.translate(genre,dest='es').text
				mapa[uniques[i]] = translated
			except Exception as e:
				print("error: " + genre)
				print(e)
	return mapa

#tag
def getTags(tags):
	uniques = getUniques(tags)
	translator = Translator()
	ommit = {	
				'FPS':'FPS','Great Soundtrack':'Gran banda sonora','PvP':'PvP','RPG':'RPG',
				'MMORPG':'MMORPG','PvE':'PvE','Hack and Slash':'Hack and Slash','RTS':'RTS',
				'Rogue-like':'Rogue-like','Board Game':'Juego de mesa',
				'Moddable':'Modeable','CRPG':'CRPG',
				'Beat \'em up':'Beat \'em up','Minigames':'Minijuegos',
				'Card Game':'Juego de Cartas','Choices Matter':'Las decisiones importan',
				'Mod':'Mod','2.5D':'2.5D','3D':'3D','Based On A Novel':'Basado en una novela',
				'Heist':'Golpe','VR':'VR','Fishing':'Pesca','Beautiful':'Bello',
				'Replay Value':'Para rejugar', 'Mini Golf':'Mini golf','1990\'s':'1990\'s',
				'Utilities':'Utilidades','Game Development':'Desarrollo de Juegos',
				'Procedural Generation':'Generación procedural','Perma Death':'Perma death',
				'Souls-like':'Souls-like','NSFW':'NSFW', '1980s':'1980s','Metroidvania':'Metroidvania',
				'Hacking':'Hacking','Jet':'Jet','Shoot \'Em Up':'Shoot \'Em Up','Sokoban':'Sokoban',
				'Villain Protagonist':'Protagonista villano','Trading':'Intercambios','Mars':'Mars',
				'MOBA':'MOBA','RPGMaker':'RPGMaker',
				'Music-Based Procedural Generation':'Generación procedural basado en música',
				'Match 3':'Match 3','Grid-Based Movement':'Movimiento en grilla','Benchmark':'Benchmark',
				'Video Production':'Producción de video','FMV':'FMV','Gambling':'Apuestas',
				'6DOF':'6DOF','ATV':'ATV','BMX':'BMX'
			}
	mapa = {}
	results = []
	for key in ommit:
		mapa[key] = ommit[key]
	for i, tag in enumerate(uniques):
		while True:
			try:
				translated = translator.translate(f'{tag} game',dest='es').text.lower()
			except:
				continue
			break
		if tag not in ommit:
			limpio = translated.replace(	'juego del',''
								).replace(	'juego de',	''
								).replace(	'juego en',	''
								).replace(	'juego',	''
								).replace(	'game',	''
								).replace('  ',' '
								).strip(
								).capitalize()
			if limpio not in results:
				results.append(limpio)
				mapa[tag] = limpio
			print(f'traducido {tag} -> {limpio}')
	return mapa
def getCal(review):
	try:
		s = review[review.find('- ')+2:review.rfind('%')]
		val = int(s)
		return (val/100)*5
	except:
		return None
def insertarJuegos(df):
	con = sqlite3.connect('appdb.db')
	cur = con.cursor()
	cur.execute('SELECT COUNT(*) FROM juego')
	cont = cur.fetchone()[0]
	cur.execute('SELECT titulo FROM juego order by id desc limit 1;')
	ultimo = cur.fetchone()[0]
	lastidx = df.index[df['name'] == ultimo].tolist()[0]+1
	for i, row in df.iloc[lastidx:,:].iterrows():
		id_j = 'juego_' + str(cont)
		titulo = row['name']
		caratula = getImage(titulo)
		if caratula is None:
			print(f'no hay carátula para {titulo}')
			continue
		translator = Translator()
		try:
			desc = translator.translate(row['game_description'],dest='es').text
		except:
			print(f'no se pudo traducir descripción de {titulo}')
			continue
		cal_usr = getCal(row['recent_reviews'])
		if cal_usr is None:
			print(f'no hay calificaciones para {titulo}')
			continue
		cal_exp = getCal(row['all_reviews'])
		if cal_exp is None:
			print(f'no hay calificaciones para {titulo}')
			continue
		precio = row['original_price']
		oferta = precio
		if not pd.isna(row['discount_price']):
			oferta = row['discount_price']
		print('---------------------------------------------------')
		print(f'id: {id_j}')
		print(f'titulo: {titulo}')
		print(f'caratula: {caratula}')
		print(f'descripción: {desc[:140]}...')
		print(f'calificación usuarios: {round(cal_usr,2)}')
		print(f'calificación expertos: {round(cal_exp,2)}')
		print(f'precio: {precio}')
		print(f'oferta: {oferta}')
		
		#insert values (id_j,titulo,caratula,desc,cal_usr,cal_exp,precio,oferta)
		cur.execute(	'INSERT INTO juego VALUES (?,?,?,?,?,?,?,?)',
					(id_j, titulo, caratula, desc,
				 	 round(cal_usr,2), round(cal_exp,2),
				 	 precio, oferta)
					)
		con.commit()
		cont = cont+1

	con.close()

def insertarGeneros(df):
	con = sqlite3.connect('appdb.db')
	cur = con.cursor()
	cur.execute('SELECT titulo,id FROM juego')
	tuplas = cur.fetchall()
	juegos = []
	ids = []
	for t in tuplas:
		juegos.append(t[0])
		ids.append(t[1])
	juegosdf = df[df['name'].isin(juegos)].copy()
	juegosdf['id_j'] = ids
	generos = getGenres(df['genre'])
	for genero in generos:
		print(f'insertando.. {generos[genero]}')
		cur.execute('INSERT INTO genero VALUES (?)',(generos[genero],))
		for i, row in juegosdf[juegosdf['genre'].str.contains(genero)].iterrows():
			cur.execute('INSERT INTO generojuego VALUES (?,?)',(row['id_j'],generos[genero]))
	con.commit()
	con.close()
def insertarTags(df):
	con = sqlite3.connect('appdb.db')
	cur = con.cursor()
	cur.execute('SELECT titulo,id FROM juego')
	tuplas = cur.fetchall()
	juegos = []
	ids = []
	for t in tuplas:
		juegos.append(t[0])
		ids.append(t[1])
	juegosdf = df[df['name'].isin(juegos)].copy()
	juegosdf['id_j'] = ids
	print('aislando...')
	tags = getTags(df['popular_tags'])
	for tag in tags:
		print(f'insertando... {tags[tag]}')
		cur.execute('INSERT INTO tag VALUES (?)',(tags[tag],))
		for i, row in juegosdf[juegosdf['popular_tags'].str.contains(tag)].iterrows():
			cur.execute('INSERT INTO tagjuego VALUES (?,?)',(row['id_j'],tags[tag]))
			#print(f'{row["name"]} | {generos[genero]}')
	con.commit()
	con.close()
def insertarDevs(df):
	con = sqlite3.connect('appdb.db')
	cur = con.cursor()
	cur.execute('SELECT titulo,id FROM juego')
	tuplas = cur.fetchall()
	juegos = []
	ids = []
	for t in tuplas:
		juegos.append(t[0])
		ids.append(t[1])
	juegosdf = df[df['name'].isin(juegos)].copy()
	juegosdf['id_j'] = ids
	devs = getUniques(df['developer'])
	for dev in devs:
		print(f'insertando.. {dev}')
		cur.execute('INSERT INTO desarrollador VALUES (?)',(dev,))
		for i, row in juegosdf[juegosdf[('developer')].str.contains(re.escape(dev))].iterrows():
			cur.execute('INSERT INTO desarrolladorjuego VALUES (?,?)',(row['id_j'],dev))
	con.commit()
	con.close()
def insertarPublis(df):
	con = sqlite3.connect('appdb.db')
	cur = con.cursor()
	cur.execute('SELECT titulo,id FROM juego')
	tuplas = cur.fetchall()
	juegos = []
	ids = []
	for t in tuplas:
		juegos.append(t[0])
		ids.append(t[1])
	juegosdf = df[df['name'].isin(juegos)].copy()
	juegosdf['id_j'] = ids
	publis = getUniques(df['publisher'])
	for pub in publis:
		print(f'insertando.. {pub}')
		cur.execute('INSERT INTO editor VALUES (?)',(pub,))
		for i, row in juegosdf[juegosdf[('publisher')].str.contains(re.escape(pub))].iterrows():
			cur.execute('INSERT INTO editorjuego VALUES (?,?)',(row['id_j'],pub))
	con.commit()
	con.close()
#['url' 'types' 'name' 'desc_snippet' 'recent_reviews' 'all_reviews'
# 'release_date' 'developer' 'publisher' 'popular_tags' 'game_details'
# 'languages' 'achievements' 'genre' 'game_description' 'mature_content'
# 'minimum_requirements' 'recommended_requirements' 'original_price'
# 'discount_price']

print('Leyendo...')
df = pd.read_csv('steam_games.csv')
print('Leido!')
print(df.columns.values)
#print(df['all_reviews'][1])
#insertarJuegos(df)
#insertarGeneros(df)
#insertarTags(df)
#insertarDevs(df)
insertarPublis(df)
#juego = df["name"][0]

#print(getGenres(df['genre']))
#print(getUniques(df['publisher']))
#print(getUniques(df['developer']))
#print(getTags(df['popular_tags']))