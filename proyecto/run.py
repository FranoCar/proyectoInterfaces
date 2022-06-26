from app import app

# Script para correr la aplicación solamente!!, nada de funciones ni paquetes ni nada aquí
# Para correr la aplicación usar "python run.py" en lugar de flask run, o no se ejecuta el "if __name__ ..."

if __name__=="__main__":
        app.run(debug=True)