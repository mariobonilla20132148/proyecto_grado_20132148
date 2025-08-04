Guía de Instalación y Puesta en Marcha
Esta guía detalla los pasos necesarios para configurar y ejecutar el "Sistema de Asistencias Clock In y Clock Out" en un entorno de desarrollo local. El proceso ha sido validado en Ubuntu 20.04 LTS.
1. Prerrequisitos de Software
Asegúrese de que los siguientes paquetes estén instalados en su sistema:
    • Python (versión 3.8 o superior): sudo apt-get install python3 python3-pip python3-venv
    • Node.js (versión 16 o superior): sudo apt-get install nodejs npm
    • Servidor de Base de Datos MySQL: sudo apt-get install mysql-server
2. Configuración de la Base de Datos (MySQL)
    1. Iniciar y Configurar MySQL por Primera Vez:
        ◦ Después de la instalación, el servidor MySQL debería iniciarse automáticamente. Puede verificar su estado con: sudo systemctl status mysql.
        ◦ A continuación, ejecute el script de configuración de seguridad para establecer la contraseña del usuario root y asegurar la instalación:
sudo mysql_secure_installation
        ◦ El asistente le guiará para configurar el componente VALIDATE PASSWORD, establecer una contraseña para el usuario root, eliminar usuarios anónimos y restringir el acceso remoto. Se recomienda seguir las instrucciones y anotar la contraseña que establezca para root.
    2. Crear la Base de Datos:
        ◦ Acceda a la consola de MySQL con el usuario root:
sudo mysql -u root -p
        ◦ Una vez dentro, ejecute la siguiente sentencia SQL para crear la base de datos:
CREATE DATABASE sistema_registros;
        ◦ Salga de la consola con el comando exit.
    3. Configurar la Conexión en la Aplicación:
        ◦ Abra el archivo app.py del backend.
        ◦ Localice la línea app.config['SQLALCHEMY_DATABASE_URI'] y modifíquela con su usuario (root), la contraseña que estableció y el nombre de la base de datos.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:SU_CONTRASEÑA@localhost/sistema_registros'

3. Instalación del Backend (Servidor Flask)
    1. Navegar a la Carpeta: Abra una terminal y navegue hasta la carpeta del backend.
    2. Crear y Activar Entorno Virtual:
        ◦ python3 -m venv venv
        ◦ source venv/bin/activate
    3. Instalar Dependencias:
pip install Flask Flask-Cors Flask-SQLAlchemy Flask-JWT-Extended Werkzeug PyMySQL openpyxl
    4. Iniciar el Servidor:
python app.py
El servidor se ejecutará en http://localhost:5000.
Descripción de Dependencias (Backend)
    • Flask: Es el microframework web sobre el que se construye toda la API.
    • Flask-Cors: Gestiona los permisos CORS para que el frontend pueda comunicarse con el backend.
    • Flask-SQLAlchemy: Integra el ORM SQLAlchemy con Flask para facilitar la interacción con la base de datos.
    • Flask-JWT-Extended: Proporciona toda la funcionalidad para la autenticación segura mediante JSON Web Tokens.
    • Werkzeug: Una librería fundamental de la que depende Flask para manejar peticiones y respuestas. Provee las funciones de hash para las contraseñas.
    • PyMySQL: Es el conector que permite a SQLAlchemy comunicarse específicamente con la base de datos MySQL.
    • openpyxl: Librería utilizada para crear los archivos de reporte en formato Excel (.xlsx).
4. Instalación del Frontend (Cliente Vue.js)
    1. Navegar a la Carpeta: Abra una nueva terminal y navegue hasta la carpeta del frontend.
    2. Instalar Dependencias: El archivo package.json del proyecto define todas las librerías necesarias. Ejecute el siguiente comando para instalarlas:
npm install
    3. Iniciar el Servidor de Desarrollo:
npm run serve
La aplicación será accesible desde https://localhost:8080.
Descripción de Dependencias Principales (Frontend)
El comando npm install instalará, entre otras, las siguientes librerías clave definidas en el archivo package.json:
    • vue: El framework principal de JavaScript para construir la interfaz de usuario.
    • vue-router: Gestiona la navegación y las rutas de la Aplicación de Página Única (SPA).
    • axios: Es el cliente HTTP utilizado para realizar todas las peticiones a la API del backend.
    • html5-qrcode: La librería que permite acceder a la cámara del dispositivo para escanear los códigos de barras en tiempo real.
    • chart.js y vue-chartjs: Librerías utilizadas para renderizar los gráficos y diagramas en el dashboard administrativo.
5. Acceso al Sistema
    • Usuario Administrador por Defecto:
        ◦ DNI: admin
        ◦ Contraseña: admin123
