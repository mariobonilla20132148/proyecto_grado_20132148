import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta, timezone
from sqlalchemy import func, select
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from functools import wraps
import services

print("--- Running app.py version: FINAL_WITH_ALL_FIXES_V3 ---")

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mamimo04@localhost/sistema_registros'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "una-clave-super-secreta-que-debes-cambiar"
jwt = JWTManager(app)
db = SQLAlchemy(app)

# --- DECORADOR DE SEGURIDAD PARA ADMINISTRADORES ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_dni = get_jwt_identity()
            user = db.session.get(Usuario, current_user_dni)
            if user and user.rol == 'admin':
                return fn(*args, **kwargs)
            else:
                return jsonify(message="Acceso denegado: se requieren permisos de administrador."), 403
        return decorator
    return wrapper

# --- MODELOS DE DATOS ---
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    dni = db.Column(db.String(20), db.ForeignKey('empleados.id_empleado'), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='empleado')
    is_first_login = db.Column(db.Boolean, default=True)

class Departamento(db.Model):
    __tablename__ = 'departamentos'
    id_departamento = db.Column(db.Integer, primary_key=True)
    nombre_departamento = db.Column(db.String(100), unique=True, nullable=False)
    def to_dict(self): return {"id": self.id_departamento, "nombre": self.nombre_departamento}

class Cargo(db.Model):
    __tablename__ = 'cargos'
    id_cargo = db.Column(db.Integer, primary_key=True)
    nombre_cargo = db.Column(db.String(100), nullable=False)
    id_departamento = db.Column(db.Integer, db.ForeignKey('departamentos.id_departamento'), nullable=False)
    departamento = db.relationship("Departamento")
    def to_dict(self):
        return {"id": self.id_cargo, "nombre": self.nombre_cargo, "id_departamento": self.id_departamento, "departamento_nombre": self.departamento.nombre_departamento if self.departamento else "N/A"}

class Horario(db.Model):
    __tablename__ = 'horarios'
    id_horario = db.Column(db.Integer, primary_key=True)
    nombre_horario = db.Column(db.String(100), nullable=False)
    hora_entrada_esperada = db.Column(db.Time, nullable=False)
    hora_salida_esperada = db.Column(db.Time, nullable=False)
    def to_dict(self):
        return { "id": self.id_horario, "nombre": self.nombre_horario, "hora_entrada_esperada": str(self.hora_entrada_esperada), "hora_salida_esperada": str(self.hora_salida_esperada) }

class Empleado(db.Model):
    __tablename__ = 'empleados'
    id_empleado = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    correo_electronico = db.Column(db.String(120), unique=True, nullable=True)
    genero = db.Column(db.String(50), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    fecha_contratacion = db.Column(db.Date, nullable=False, default=date.today)
    activo = db.Column(db.Boolean, default=True)
    id_departamento = db.Column(db.Integer, db.ForeignKey('departamentos.id_departamento'), nullable=True)
    id_cargo = db.Column(db.Integer, db.ForeignKey('cargos.id_cargo'), nullable=True)
    id_horario = db.Column(db.Integer, db.ForeignKey('horarios.id_horario'), nullable=True)
    usuario = db.relationship("Usuario", backref="empleado", uselist=False, cascade="all, delete-orphan")
    departamento = db.relationship("Departamento")
    cargo = db.relationship("Cargo")
    horario = db.relationship("Horario")
    def to_dict(self):
        return {
            "id_empleado": self.id_empleado, "nombre": self.nombre, "apellido": self.apellido, "telefono": self.telefono, "correo_electronico": self.correo_electronico,
            "genero": self.genero, "fecha_nacimiento": self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            "fecha_contratacion": self.fecha_contratacion.isoformat() if self.fecha_contratacion else None,
            "activo": self.activo, "id_departamento": self.id_departamento, "id_cargo": self.id_cargo, "id_horario": self.id_horario,
            "departamento_nombre": self.departamento.nombre_departamento if self.departamento else None,
            "cargo_nombre": self.cargo.nombre_cargo if self.cargo else None,
            "horario_nombre": self.horario.nombre_horario if self.horario else None,
            "horario_entrada_esperada": str(self.horario.hora_entrada_esperada) if self.horario else None,
            "horario_salida_esperada": str(self.horario.hora_salida_esperada) if self.horario else None,
            "rol": self.usuario.rol if self.usuario else None
        }

class RegistroAsistencia(db.Model):
    __tablename__ = 'registros_asistencia'
    id_registro = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.String(20), db.ForeignKey('empleados.id_empleado'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    tipo = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.String(255), nullable=True)
    def to_dict(self):
        ts = self.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = ts.astimezone(timezone.utc)
        return { 
            "id_registro": self.id_registro, 
            "id_empleado": self.id_empleado, 
            "timestamp": ts.isoformat().replace('+00:00', 'Z'), 
            "tipo": self.tipo, 
            "observaciones": self.observaciones 
        }

def get_local_offset():
    return datetime.now().astimezone().utcoffset()

# --- RUTAS DE LA API ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    dni = data.get('dni')
    password = data.get('password')
    usuario = db.session.get(Usuario, dni)
    if not usuario or not check_password_hash(usuario.password, password):
        return jsonify({"message": "Credenciales inválidas."}), 401
    access_token = create_access_token(identity=usuario.dni)
    return jsonify({
        "success": True, "access_token": access_token, "user_dni": usuario.dni, 
        "user_role": usuario.rol, "is_first_login": usuario.is_first_login
    }), 200

@app.route('/api/change_password/<string:dni>', methods=['POST'])
@jwt_required()
def change_password(dni):
    current_user_dni = get_jwt_identity()
    user_making_request = db.session.get(Usuario, current_user_dni)
    if user_making_request.rol != 'admin' and current_user_dni != dni:
        return jsonify(message="No autorizado."), 403
    usuario = db.session.get(Usuario, dni)
    if not usuario: return jsonify({"message": "Usuario no encontrado."}), 404
    data = request.get_json()
    new_password = data.get('new_password')
    if not new_password or len(new_password) < 6:
        return jsonify({"message": "La contraseña debe tener al menos 6 caracteres."}), 400
    usuario.password = generate_password_hash(new_password)
    usuario.is_first_login = False
    db.session.commit()
    return jsonify({"success": True, "message": "Contraseña actualizada con éxito."}), 200

@app.route('/api/fichar', methods=['POST'])
def fichar():
    data = request.get_json()
    dni = data.get('dni')
    if not dni: return jsonify({"message": "DNI es requerido."}), 400
    empleado = db.session.get(Empleado, dni)
    if not empleado or not empleado.activo:
        return jsonify({"message": "Empleado no encontrado o inactivo."}), 404
    
    current_utc_time = datetime.now(timezone.utc)
    local_offset = get_local_offset()
    today_local = (current_utc_time + local_offset).date()
    
    start_of_today_local = datetime.combine(today_local, time.min)
    end_of_today_local = datetime.combine(today_local, time.max)
    
    local_tz = datetime.now().astimezone().tzinfo
    start_of_today_utc = start_of_today_local.replace(tzinfo=local_tz).astimezone(timezone.utc)
    end_of_today_utc = end_of_today_local.replace(tzinfo=local_tz).astimezone(timezone.utc)
    
    stmt = select(RegistroAsistencia).filter_by(id_empleado=dni).filter(RegistroAsistencia.timestamp.between(start_of_today_utc, end_of_today_utc)).order_by(RegistroAsistencia.timestamp.desc())
    last_record = db.session.scalars(stmt).first()
    
    tipo_fichaje = 'salida' if last_record and last_record.tipo == 'entrada' else 'entrada'
    nuevo_registro = RegistroAsistencia(id_empleado=dni, tipo=tipo_fichaje, timestamp=current_utc_time)
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify({
        "success": True, "message": f"Fichaje de {tipo_fichaje} registrado para {empleado.nombre}.",
        "tipo": tipo_fichaje, "nombre_empleado": f"{empleado.nombre} {empleado.apellido}",
        "genero": empleado.genero
    }), 200

@app.route('/api/empleados', methods=['GET', 'POST'])
@admin_required()
def handle_empleados():
    if request.method == 'POST':
        data = request.get_json()
        if not all(k in data for k in ['id_empleado', 'nombre', 'apellido', 'password', 'rol']):
            return jsonify({"message": "Faltan campos requeridos."}), 400
        if db.session.get(Empleado, data['id_empleado']):
            return jsonify({"message": "Un empleado con este DNI ya existe."}), 409
        nuevo_empleado = Empleado(
            id_empleado=data['id_empleado'], nombre=data['nombre'], apellido=data['apellido'],
            telefono=data.get('telefono'), correo_electronico=data.get('correo_electronico'),
            genero=data.get('genero'), fecha_nacimiento=date.fromisoformat(data['fecha_nacimiento']) if data.get('fecha_nacimiento') else None,
            fecha_contratacion=date.fromisoformat(data['fecha_contratacion']) if data.get('fecha_contratacion') else date.today(),
            activo=data.get('activo', True), id_departamento=data.get('id_departamento'), id_cargo=data.get('id_cargo'),
            id_horario=data.get('id_horario')
        )
        nuevo_usuario = Usuario(
            dni=data['id_empleado'], rol=data['rol'],
            password=generate_password_hash(data['password']), is_first_login=True
        )
        db.session.add(nuevo_empleado)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify(nuevo_empleado.to_dict()), 201
    empleados = db.session.execute(select(Empleado)).scalars().all()
    return jsonify([e.to_dict() for e in empleados]), 200

@app.route('/api/empleados/<string:dni>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_single_empleado(dni):
    current_user_dni = get_jwt_identity()
    current_user = db.session.get(Usuario, current_user_dni)
    if request.method == 'GET':
        if current_user.rol != 'admin' and current_user.dni != dni:
            return jsonify(message="No autorizado para ver datos de otros empleados."), 403
        empleado = db.session.get(Empleado, dni)
        if not empleado: return jsonify({"message": "Empleado no encontrado."}), 404
        return jsonify(empleado.to_dict()), 200
    if current_user.rol != 'admin':
        return jsonify(message="Se requieren permisos de administrador para esta acción."), 403
    empleado = db.session.get(Empleado, dni)
    if not empleado: return jsonify({"message": "Empleado no encontrado."}), 404
    if request.method == 'PUT':
        data = request.get_json()
        empleado.nombre = data.get('nombre', empleado.nombre)
        empleado.apellido = data.get('apellido', empleado.apellido)
        empleado.telefono = data.get('telefono', empleado.telefono)
        empleado.correo_electronico = data.get('correo_electronico', empleado.correo_electronico)
        empleado.genero = data.get('genero', empleado.genero)
        empleado.fecha_nacimiento = date.fromisoformat(data['fecha_nacimiento']) if data.get('fecha_nacimiento') else None
        empleado.fecha_contratacion = date.fromisoformat(data['fecha_contratacion']) if data.get('fecha_contratacion') else empleado.fecha_contratacion
        empleado.activo = data.get('activo', empleado.activo)
        empleado.id_departamento = data.get('id_departamento', empleado.id_departamento)
        empleado.id_cargo = data.get('id_cargo', empleado.id_cargo)
        empleado.id_horario = data.get('id_horario', empleado.id_horario)
        if 'rol' in data and empleado.usuario:
            empleado.usuario.rol = data['rol']
        if 'password' in data and data['password']:
            if not empleado.usuario:
                nuevo_usuario = Usuario(dni=dni, rol=data.get('rol', 'empleado'), password=generate_password_hash(data['password']), is_first_login=True)
                db.session.add(nuevo_usuario)
            else:
                empleado.usuario.password = generate_password_hash(data['password'])
                empleado.usuario.is_first_login = True
        db.session.commit()
        return jsonify(empleado.to_dict()), 200
    elif request.method == 'DELETE':
        db.session.delete(empleado)
        db.session.commit()
        return jsonify({"success": True}), 200

@app.route('/api/registros', methods=['GET', 'POST'])
@jwt_required()
def handle_registros():
    if request.method == 'GET':
        empleado_dni = request.args.get('empleado_dni')
        if not empleado_dni: return jsonify({"message": "DNI del empleado es requerido."}), 400
        current_user_dni = get_jwt_identity()
        user = db.session.get(Usuario, current_user_dni)
        if user.rol != 'admin' and user.dni != empleado_dni:
            return jsonify(message="No autorizado para ver registros de otros empleados."), 403
        registros = db.session.execute(select(RegistroAsistencia).filter_by(id_empleado=empleado_dni).order_by(RegistroAsistencia.timestamp.asc())).scalars().all()
        return jsonify([r.to_dict() for r in registros]), 200
    elif request.method == 'POST':
        current_user_dni = get_jwt_identity()
        user = db.session.get(Usuario, current_user_dni)
        if user.rol != 'admin':
            return jsonify(message="No autorizado para crear registros manualmente."), 403
        data = request.get_json()
        id_empleado, tipo, timestamp_str, observaciones = data.get('id_empleado'), data.get('tipo'), data.get('timestamp'), data.get('observaciones')
        if not all([id_empleado, tipo, timestamp_str]):
            return jsonify({"message": "id_empleado, tipo y timestamp son requeridos."}), 400
        if not db.session.get(Empleado, id_empleado): return jsonify({"message": "Empleado no encontrado."}), 404
        try:
            local_dt_naive = datetime.fromisoformat(timestamp_str)
            local_offset = get_local_offset()
            local_dt_aware = local_dt_naive.replace(tzinfo=timezone(local_offset))
            utc_dt = local_dt_aware.astimezone(timezone.utc)
        except ValueError:
            return jsonify({"message": "Formato de fecha/hora inválido."}), 400
        nuevo_registro = RegistroAsistencia(id_empleado=id_empleado, tipo=tipo, timestamp=utc_dt, observaciones=observaciones)
        db.session.add(nuevo_registro)
        db.session.commit()
        return jsonify({"success": True, "message": "Registro añadido con éxito.", "registro": nuevo_registro.to_dict()}), 201

@app.route('/api/registros/<int:id_registro>', methods=['PUT', 'DELETE'])
@admin_required()
def handle_single_registro(id_registro):
    registro = db.session.get(RegistroAsistencia, id_registro)
    if not registro: return jsonify({"message": "Registro no encontrado."}), 404
    if request.method == 'PUT':
        data = request.get_json()
        timestamp_str, tipo, observaciones = data.get('timestamp'), data.get('tipo'), data.get('observaciones')
        if not all([timestamp_str, tipo]): return jsonify({"message": "Timestamp y tipo son requeridos."}), 400
        try:
            local_dt_naive = datetime.fromisoformat(timestamp_str)
            local_offset = get_local_offset()
            local_dt_aware = local_dt_naive.replace(tzinfo=timezone(local_offset))
            utc_dt = local_dt_aware.astimezone(timezone.utc)
        except ValueError:
            return jsonify({"message": "Formato de fecha/hora inválido."}), 400
        registro.timestamp = utc_dt
        registro.tipo = tipo
        registro.observaciones = observaciones
        db.session.commit()
        return jsonify({"success": True, "message": "Registro actualizado con éxito.", "registro": registro.to_dict()}), 200
    elif request.method == 'DELETE':
        db.session.delete(registro)
        db.session.commit()
        return jsonify({"success": True}), 200

@app.route('/api/data_for_forms', methods=['GET'])
@admin_required()
def get_data_for_forms():
    departments = db.session.execute(select(Departamento)).scalars().all()
    cargos = db.session.execute(select(Cargo)).scalars().all()
    horarios = db.session.execute(select(Horario)).scalars().all()
    return jsonify({
        "departments": [d.to_dict() for d in departments],
        "cargos": [c.to_dict() for c in cargos],
        "horarios": [h.to_dict() for h in horarios]
    }), 200

@app.route('/api/departments', methods=['GET', 'POST'])
@admin_required()
def handle_departments():
    if request.method == 'POST':
        data = request.get_json()
        new_dept = Departamento(nombre_departamento=data['nombre_departamento'])
        db.session.add(new_dept)
        db.session.commit()
        return jsonify(new_dept.to_dict()), 201
    departments = db.session.execute(select(Departamento)).scalars().all()
    return jsonify([d.to_dict() for d in departments]), 200

@app.route('/api/departments/<int:id>', methods=['DELETE'])
@admin_required()
def delete_department(id):
    if db.session.execute(select(Cargo).filter_by(id_departamento=id)).first() or db.session.execute(select(Empleado).filter_by(id_departamento=id)).first():
        return jsonify({"message": "No se puede borrar: reasigne cargos y empleados primero."}), 409
    dept = db.session.get(Departamento, id)
    if not dept: return jsonify({"message": "Departamento no encontrado."}), 404
    db.session.delete(dept)
    db.session.commit()
    return jsonify({"success": True}), 200

@app.route('/api/cargos', methods=['GET', 'POST'])
@admin_required()
def handle_cargos():
    if request.method == 'POST':
        data = request.get_json()
        new_cargo = Cargo(nombre_cargo=data['nombre_cargo'], id_departamento=data['id_departamento'])
        db.session.add(new_cargo)
        db.session.commit()
        return jsonify(new_cargo.to_dict()), 201
    cargos = db.session.execute(select(Cargo)).scalars().all()
    return jsonify([c.to_dict() for c in cargos]), 200

@app.route('/api/cargos/<int:id>', methods=['DELETE'])
@admin_required()
def delete_cargo(id):
    if db.session.execute(select(Empleado).filter_by(id_cargo=id)).first():
        return jsonify({"message": "No se puede borrar: reasigne empleados con este cargo."}), 409
    cargo = db.session.get(Cargo, id)
    if not cargo: return jsonify({"message": "Cargo no encontrado."}), 404
    db.session.delete(cargo)
    db.session.commit()
    return jsonify({"success": True}), 200

@app.route('/api/horarios', methods=['GET', 'POST'])
@admin_required()
def handle_horarios():
    if request.method == 'POST':
        data = request.get_json()
        new_horario = Horario(
            nombre_horario=data['nombre_horario'],
            hora_entrada_esperada=datetime.strptime(data['hora_entrada_esperada'], '%H:%M').time(),
            hora_salida_esperada=datetime.strptime(data['hora_salida_esperada'], '%H:%M').time()
        )
        db.session.add(new_horario)
        db.session.commit()
        return jsonify(new_horario.to_dict()), 201
    horarios = db.session.execute(select(Horario)).scalars().all()
    return jsonify([h.to_dict() for h in horarios]), 200

@app.route('/api/horarios/<int:id>', methods=['DELETE'])
@admin_required()
def delete_horario(id):
    if db.session.execute(select(Empleado).filter_by(id_horario=id)).first():
        return jsonify({"message": "No se puede borrar: reasigne empleados con este horario."}), 409
    horario = db.session.get(Horario, id)
    if not horario: return jsonify({"message": "Horario no encontrado."}), 404
    db.session.delete(horario)
    db.session.commit()
    return jsonify({"success": True}), 200

@app.route('/api/reports/attendance_summary', methods=['GET'])
@admin_required()
def get_attendance_summary_report():
    try:
        employee_dni = request.args.get('employee_dni')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        timezone_offset_minutes = request.args.get('timezone_offset_minutes', type=int)

        if not all([employee_dni, month, year, timezone_offset_minutes is not None]):
            return jsonify({"message": "Argumentos incompletos para el reporte."}), 400
            
        user_tz = timezone(timedelta(minutes=-timezone_offset_minutes))

        file_stream, filename = services.generate_attendance_report_excel(
            db_session=db.session,
            employee_dni=employee_dni,
            year=year,
            month=month,
            user_tz=user_tz
        )
        
        return send_file(
            file_stream, 
            download_name=filename, 
            as_attachment=True, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        print(f"Error inesperado al generar el reporte: {e}")
        return jsonify({"message": "Ocurrió un error inesperado al generar el reporte."}), 500

@app.route('/api/dashboard_summary', methods=['GET'])
@admin_required()
def get_dashboard_summary():
    try:
        data = services.get_dashboard_summary_data(db.session)
        return jsonify(data)
    except Exception as e:
        print(f"Error generando resumen del dashboard: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500

@app.route('/api/test_db')
def test_db():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify(message="Conexión a la base de datos exitosa."), 200
    except Exception as e:
        return jsonify(message=f"Error de conexión a la base de datos: {str(e)}"), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not db.session.get(Usuario, 'admin'):
            if not db.session.get(Empleado, 'admin'):
                admin_emp = Empleado(id_empleado='admin', nombre='Admin', apellido='User', fecha_contratacion=date.today())
                db.session.add(admin_emp)
            admin_user = Usuario(dni='admin', password=generate_password_hash("admin123"), rol='admin', is_first_login=False)
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5000)
