"""Pruebas de integración de HAIR GRECIA API; no requieren paquetes externos."""
import json
from concurrent.futures import ThreadPoolExecutor
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import server  # noqa: E402


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        db = Path(cls.tmp.name) / 'test.sqlite3'
        server.init_db(db)
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.json_handler(db))
        cls.base = f'http://127.0.0.1:{cls.httpd.server_port}/api'
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown(); cls.httpd.server_close(); cls.thread.join(timeout=3)
        cls.tmp.cleanup()

    @classmethod
    def req(cls, path, method='GET', payload=None, token=None):
        headers = {}
        if payload is not None: headers['Content-Type'] = 'application/json'
        if token: headers['Authorization'] = 'Bearer ' + token
        data = json.dumps(payload).encode('utf-8') if payload is not None else None
        request = Request(cls.base + path, headers=headers, method=method, data=data)
        try:
            with urlopen(request, timeout=8) as response:
                return response.status, json.load(response)
        except HTTPError as exc:
            return exc.code, json.load(exc)

    @classmethod
    def auth(cls, label):
        email = f'{label}@example.com'
        result, _ = cls.req('/auth/register', 'POST', {'name': label,'email':email,'password':'ClavePrueba2026'})
        assert result == 201, result
        status, data = cls.req('/auth/login', 'POST', {'email':email,'password':'ClavePrueba2026'})
        assert status == 200
        return data['token']

    def test_01_services_and_barbers(self):
        status, data = self.req('/services'); self.assertEqual(status, 200); self.assertEqual(len(data['items']), 6)
        status, data = self.req('/barbers'); self.assertEqual(status, 200); self.assertEqual(len(data['items']), 4)

    def test_02_public_availability_and_closed_sunday(self):
        status, data = self.req('/availability?date=2030-11-25&barber_id=1&service_id=1')
        self.assertEqual(status,200);self.assertIn('09:00', data['slots'])
        status, data = self.req('/availability?date=2030-11-24&barber_id=1&service_id=1')
        self.assertEqual(status,200);self.assertEqual(data['slots'],[])

    def test_03_reservation_overlaps_and_cancellation(self):
        token = self.auth('reserva')
        body = {'barber_id':1,'service_id':1,'date':'2030-11-25','time':'09:00'}
        status, data = self.req('/appointments','POST',body,token)
        self.assertEqual(status,201);appt_id=data['id']
        status, _ = self.req('/appointments','POST',body,token)
        self.assertEqual(status,409)
        # 09:30 se solapa con 09:00-09:45.
        status, data = self.req('/appointments','POST',{**body,'time':'09:30'},token)
        self.assertEqual(status,409)
        status, items = self.req('/appointments',token=token)
        self.assertEqual(status,200);self.assertEqual(len(items['items']),1)
        status, data = self.req(f'/appointments/{appt_id}/cancel','PATCH',token=token)
        self.assertEqual(status,200)
        status, data = self.req('/appointments','POST',body,token)
        self.assertEqual(status,201)
        # Dos solicitudes simultáneas para una franja libre: solo una puede entrar.
        race = {'barber_id':3, 'service_id':2, 'date':'2030-11-26', 'time':'11:00'}
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.req('/appointments','POST',race,token)[0],range(2)))
        self.assertEqual(sorted(results),[201,409])

    def test_04_unauthorized_actions_and_invalid_input(self):
        status, _ = self.req('/appointments');self.assertEqual(status,401)
        status, _ = self.req('/auth/register','POST',{'name':'A','email':'invalido','password':'123'})
        self.assertEqual(status,400)
        status, _ = self.req('/availability?date=2030-02-31&barber_id=1&service_id=1')
        self.assertEqual(status,400)

    def test_05_user_cannot_access_other_user_reservation(self):
        first = self.auth('propietario')
        second = self.auth('otra')
        status, payload = self.req('/appointments','POST',{'barber_id':2,'service_id':3,'date':'2030-11-25','time':'10:00'},first)
        self.assertEqual(status,201)
        status, _ = self.req(f"/appointments/{payload['id']}/cancel",'PATCH',token=second)
        self.assertEqual(status,403)
        status, data = self.req('/appointments', token=second)
        self.assertEqual(status,200);self.assertEqual(data['items'],[])
        status, _ = self.req('/stats',token=second)
        self.assertEqual(status,403)

    def test_06_logout(self):
        token = self.auth('logout')
        status, _ = self.req('/auth/me',token=token);self.assertEqual(status,200)
        status, _ = self.req('/auth/logout','POST',token=token);self.assertEqual(status,200)
        status, _ = self.req('/auth/me',token=token);self.assertEqual(status,401)


if __name__ == '__main__': unittest.main()
