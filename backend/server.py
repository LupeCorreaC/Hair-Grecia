"""HAIR GRECIA - API REST académica con Python estándar y SQLite.

Ejecución: python backend/server.py
No exponer este servidor de desarrollo a Internet.
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DB_FILE = Path(os.getenv('HAIR_DB_PATH', str(ROOT / 'backend' / 'hair_grecia.sqlite3')))
PORT = int(os.getenv('HAIR_API_PORT', '8000'))
CORS_ORIGIN = os.getenv('HAIR_CORS_ORIGIN', 'http://localhost:5173')

# Valores iniciales tomados de las páginas HTML entregadas. Son datos de demostración.
SERVICES = [
    ('Corte de cabello hombre', 45, 25000, 'corte_hombre.jpg'),
    ('Corte de cabello mujer', 60, 30000, 'corte_mujer.jpg'),
    ('Afeitado y barba', 30, 20000, 'afeitado.jpg'),
    ('Peinados y estilizado', 60, 35000, 'peinado.jpg'),
    ('Tratamientos capilares', 45, 40000, 'tratamiento.jpg'),
    ('Coloración', 60, 50000, 'color.jpg'),
]
BARBERS = [
    ('Andrés Gómez', 'Cortes modernos y degradados', 'barbero1.jpg', '09:00', '18:00', '09:00', '16:00'),
    ('Carlos Medina', 'Afeitados clásicos y diseño de barba', 'barbero2.jpg', '10:00', '19:00', '09:00', '15:00'),
    ('Hellen Ardila', 'Cortes artísticos y coloración', 'barbero3.jpg', '11:00', '20:00', '10:00', '17:00'),
    ('David Ruiz', 'Peinados para eventos', 'barbero4.jpg', '09:00', '17:00', '09:00', '14:00'),
]
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def connect(db_path=None):
    db = sqlite3.connect(str(db_path or DB_FILE), timeout=8, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=8000')
    return db


@contextmanager
def db_context(db_path=None):
    db = connect(db_path)
    try:
        with db:
            yield db
    finally:
        db.close()


def init_db(db_path=None):
    path = Path(db_path or DB_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with db_context(path) as db:
        db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, duration_min INTEGER NOT NULL,
                price_from INTEGER NOT NULL, image TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS barbers (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, specialty TEXT NOT NULL,
                image TEXT NOT NULL, week_from TEXT NOT NULL, week_to TEXT NOT NULL,
                sat_from TEXT NOT NULL, sat_to TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'client'
                CHECK(role IN ('client','admin')));
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
                barber_id INTEGER NOT NULL REFERENCES barbers(id),
                service_id INTEGER NOT NULL REFERENCES services(id),
                visit_date TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'reservada' CHECK(status IN ('reservada','cancelada')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE INDEX IF NOT EXISTS idx_booked ON appointments(barber_id, visit_date, status);
        ''')
        if db.execute('SELECT COUNT(*) FROM services').fetchone()[0] == 0:
            db.executemany('INSERT INTO services(name,duration_min,price_from,image) VALUES(?,?,?,?)', SERVICES)
        if db.execute('SELECT COUNT(*) FROM barbers').fetchone()[0] == 0:
            db.executemany('INSERT INTO barbers(name,specialty,image,week_from,week_to,sat_from,sat_to) VALUES(?,?,?,?,?,?,?)', BARBERS)
        email = os.getenv('HAIR_ADMIN_EMAIL', '').strip().lower()
        password = os.getenv('HAIR_ADMIN_PASSWORD', '')
        if email and len(password) >= 12 and EMAIL_RE.fullmatch(email):
            db.execute('INSERT OR IGNORE INTO users(name,email,password_hash,role) VALUES(?,?,?,?)',
                       ('Administración', email, hash_password(password), 'admin'))


def hash_password(password):
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 260000)
    return f'{salt.hex()}:{derived.hex()}'


def check_password(password, stored):
    try:
        salt, digest = stored.split(':', 1)
        match = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 260000)
        return hmac.compare_digest(match, bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False


def hm_to_min(text):
    if not isinstance(text, str) or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', text):
        raise ValueError('La hora debe tener el formato HH:MM.')
    hour, minute = map(int, text.split(':'))
    return hour * 60 + minute


def min_to_hm(value):
    return f'{value // 60:02}:{value % 60:02}'


def validate_day(text):
    if not isinstance(text, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        raise ValueError('La fecha debe tener el formato AAAA-MM-DD.')
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError('La fecha no es válida.') from exc


def schedule(barber, day):
    weekday = day.weekday()
    if weekday == 6:
        return None
    if weekday == 5:
        return (hm_to_min(barber['sat_from']), hm_to_min(barber['sat_to']))
    return (hm_to_min(barber['week_from']), hm_to_min(barber['week_to']))


def available_slots(db, barber_id, service_id, day):
    barber = db.execute('SELECT * FROM barbers WHERE id=?', (barber_id,)).fetchone()
    service = db.execute('SELECT * FROM services WHERE id=?', (service_id,)).fetchone()
    if not barber or not service:
        raise ValueError('Selecciona un servicio y un barbero válidos.')
    shift = schedule(barber, day)
    if not shift or day < date.today():
        return []
    occupied = db.execute('''SELECT start_time,end_time FROM appointments
        WHERE barber_id=? AND visit_date=? AND status='reservada' ''',
        (barber_id, day.isoformat())).fetchall()
    duration = service['duration_min']
    out = []
    for start in range(shift[0], shift[1] - duration + 1, 30):
        end = start + duration
        if not any(start < hm_to_min(b['end_time']) and end > hm_to_min(b['start_time']) for b in occupied):
            # No ofertar horas ya pasadas en el día actual según el reloj local del servidor.
            if day == date.today() and start <= datetime.now().hour * 60 + datetime.now().minute:
                continue
            out.append(min_to_hm(start))
    return out


def public_row(row):
    return dict(row)


def json_handler(db_path):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'HairGreciaDemo/1.0'

        def log_message(self, fmt, *args):
            return  # No registrar cuerpos ni credenciales en la consola.

        def respond(self, status, data):
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Access-Control-Allow-Origin', CORS_ORIGIN)
            self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            self.send_header('Access-Control-Allow-Methods', 'GET,POST,PATCH,OPTIONS')
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', CORS_ORIGIN)
            self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            self.send_header('Access-Control-Allow-Methods', 'GET,POST,PATCH,OPTIONS')
            self.end_headers()

        def read_body(self):
            try:
                length = int(self.headers.get('Content-Length','0'))
            except ValueError:
                raise ValueError('Solicitud incorrecta.')
            if length <= 0 or length > 16384:
                raise ValueError('El cuerpo de la solicitud está vacío o es demasiado grande.')
            try:
                data = json.loads(self.rfile.read(length).decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                raise ValueError('Se esperaba un JSON válido.')
            if not isinstance(data, dict):
                raise ValueError('Se esperaba un objeto JSON.')
            return data

        def current_user(self, db):
            header = self.headers.get('Authorization', '')
            if not header.startswith('Bearer '):
                return None
            token = header[7:].strip()
            if len(token) != 64 or not re.fullmatch('[a-f0-9]{64}',token):
                return None
            key = hashlib.sha256(token.encode()).hexdigest()
            return db.execute('''SELECT u.id,u.name,u.email,u.role FROM users u
                JOIN sessions s ON u.id=s.user_id
                WHERE s.token_hash=? AND s.expires_at>?''',
                (key,datetime.now(timezone.utc).isoformat())).fetchone()

        def with_error(self, action):
            try:
                with db_context(db_path) as db:
                    action(db)
            except ValueError as exc:
                self.respond(400, {'error':str(exc)})
            except sqlite3.IntegrityError:
                self.respond(409, {'error':'Ya existe una cuenta con ese correo.'})
            except Exception:
                self.respond(500, {'error':'Ocurrió un error interno. Revisa la consola del servidor.'})

        def route(self, method):
            url = urlsplit(self.path)
            path = url.path
            args = parse_qs(url.query)
            def action(db):
                if method == 'GET' and path == '/api/health':
                    return self.respond(200, {'status':'ok','name':'HAIR GRECIA API'})
                if method == 'GET' and path == '/api/services':
                    return self.respond(200, {'items':[public_row(r) for r in db.execute('SELECT * FROM services')]})
                if method == 'GET' and path == '/api/barbers':
                    return self.respond(200, {'items':[public_row(r) for r in db.execute('SELECT * FROM barbers')]})
                if method == 'GET' and path == '/api/availability':
                    day = validate_day(args.get('date',[''])[0])
                    try:
                        b_id,s_id = int(args.get('barber_id',['0'])[0]),int(args.get('service_id',['0'])[0])
                    except ValueError:
                        raise ValueError('Los identificadores deben ser números.')
                    return self.respond(200, {'date':day.isoformat(),'slots':available_slots(db,b_id,s_id,day)})
                if method == 'POST' and path == '/api/auth/register':
                    data = self.read_body()
                    name = str(data.get('name','')).strip()
                    email = str(data.get('email','')).strip().lower()
                    password = data.get('password','')
                    if not (2 <= len(name) <= 100 and EMAIL_RE.fullmatch(email) and isinstance(password,str) and 8 <= len(password) <= 128):
                        raise ValueError('Escribe nombre, correo válido y contraseña de al menos 8 caracteres.')
                    db.execute('INSERT INTO users(name,email,password_hash) VALUES (?,?,?)',
                               (name,email,hash_password(password)))
                    return self.respond(201, {'message':'Cuenta creada. Ya puedes ingresar.'})
                if method == 'POST' and path == '/api/auth/login':
                    data = self.read_body()
                    email = str(data.get('email','')).strip().lower()
                    password = data.get('password','')
                    user = db.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
                    if not isinstance(password,str) or not user or not check_password(password,user['password_hash']):
                        return self.respond(401, {'error':'Correo o contraseña incorrectos.'})
                    token = secrets.token_hex(32)
                    db.execute('INSERT INTO sessions(token_hash,user_id,expires_at) VALUES (?,?,?)',
                               (hashlib.sha256(token.encode()).hexdigest(),user['id'],
                                (datetime.now(timezone.utc)+timedelta(hours=8)).isoformat()))
                    return self.respond(200, {'token':token,'user':{k:user[k] for k in ('id','name','email','role')}})
                user = self.current_user(db)
                if path.startswith('/api/auth/') or path.startswith('/api/appointments') or path.startswith('/api/stats'):
                    if user is None:
                        return self.respond(401, {'error':'Debes iniciar sesión.'})
                if method == 'GET' and path == '/api/auth/me':
                    return self.respond(200, {'user':public_row(user)})
                if method == 'POST' and path == '/api/auth/logout':
                    token = self.headers.get('Authorization','')[7:].strip()
                    db.execute('DELETE FROM sessions WHERE token_hash=?',
                               (hashlib.sha256(token.encode()).hexdigest(),))
                    return self.respond(200,{'message':'Sesión cerrada.'})
                if method == 'GET' and path == '/api/appointments':
                    sql = '''SELECT a.*,s.name AS service_name,b.name AS barber_name,u.name AS client_name
                        FROM appointments a JOIN services s ON s.id=a.service_id
                        JOIN barbers b ON b.id=a.barber_id JOIN users u ON u.id=a.user_id'''
                    if user['role'] == 'admin':
                        rows=db.execute(sql+' ORDER BY a.visit_date DESC,a.start_time DESC').fetchall()
                    else:
                        rows=db.execute(sql+' WHERE a.user_id=? ORDER BY a.visit_date DESC,a.start_time DESC',
                                        (user['id'],)).fetchall()
                    return self.respond(200, {'items':[public_row(r) for r in rows]})
                if method == 'POST' and path == '/api/appointments':
                    data=self.read_body()
                    try:
                        b_id,s_id = int(data.get('barber_id')),int(data.get('service_id'))
                    except (ValueError,TypeError):
                        raise ValueError('Escoge un barbero y un servicio.')
                    day=validate_day(data.get('date'))
                    start=data.get('time')
                    hm_to_min(start)
                    # Reserva en transacción serializada. Impide citas que se solapan.
                    db.execute('BEGIN IMMEDIATE')
                    slots=available_slots(db,b_id,s_id,day)
                    if start not in slots:
                        db.rollback()
                        return self.respond(409, {'error':'Ese horario ya no está disponible. Elige otro.'})
                    service=db.execute('SELECT * FROM services WHERE id=?',(s_id,)).fetchone()
                    end=min_to_hm(hm_to_min(start)+service['duration_min'])
                    cur=db.execute('''INSERT INTO appointments
                        (user_id,barber_id,service_id,visit_date,start_time,end_time)
                        VALUES(?,?,?,?,?,?)''',(user['id'],b_id,s_id,day.isoformat(),start,end))
                    db.commit()
                    return self.respond(201, {'id':cur.lastrowid,'message':'Cita reservada correctamente.'})
                match=re.fullmatch(r'/api/appointments/(\d+)/cancel',path)
                if method == 'PATCH' and match:
                    appt=db.execute('SELECT * FROM appointments WHERE id=?',(int(match.group(1)),)).fetchone()
                    if not appt:
                        return self.respond(404, {'error':'No se encontró esa cita.'})
                    if user['role'] != 'admin' and appt['user_id'] != user['id']:
                        return self.respond(403, {'error':'No puedes modificar esa cita.'})
                    if appt['status'] == 'cancelada':
                        return self.respond(409, {'error':'La cita ya estaba cancelada.'})
                    db.execute('UPDATE appointments SET status=? WHERE id=?',('cancelada',appt['id']))
                    return self.respond(200, {'message':'Cita cancelada.'})
                if method == 'GET' and path == '/api/stats':
                    if user['role']!='admin':
                        return self.respond(403,{'error':'Solo disponible para administración.'})
                    return self.respond(200, {
                        'reservadas':db.execute("SELECT COUNT(*) FROM appointments WHERE status='reservada'").fetchone()[0],
                        'canceladas':db.execute("SELECT COUNT(*) FROM appointments WHERE status='cancelada'").fetchone()[0]})
                return self.respond(404, {'error':'Ruta no encontrada.'})
            self.with_error(action)

        def do_GET(self): self.route('GET')
        def do_POST(self): self.route('POST')
        def do_PATCH(self): self.route('PATCH')
    return Handler


def run():
    init_db()
    server=ThreadingHTTPServer(('127.0.0.1',PORT),json_handler(DB_FILE))
    print(f'HAIR GRECIA: http://localhost:{PORT}/api/health')
    print('Swagger/OpenAPI: abrir docs/openapi.yaml en https://editor.swagger.io/ (solo si puedes acceder a Internet).')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Servidor detenido')
    finally:
        server.server_close()


if __name__ == '__main__':
    run()
