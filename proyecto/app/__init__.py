from flask import Flask,render_template, redirect, url_for, request
import sqlite3

def getCarrito():
	con = sqlite3.connect('app/appdb.db')
	cur = con.cursor()
	cur.execute('select count(juego) from carrito')
	n = cur.fetchone()[0]
	return n
#----------------- Aquí hacer todos los imports y funciones y variables globales!!! -----------------
# Luego se importan los paquetes en routes.py de forma: "from app import [paquete,función o variable en __init__.py]"

app = Flask(__name__)
from app import routes