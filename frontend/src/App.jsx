import { useEffect, useState } from 'react';
import { Link, NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import api, { messageFromError } from './api';
import { useAuth } from './AuthContext';
import { useBooking } from './BookingContext';

const pesos = (value) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value);
const labels = { reservada: 'Reservada', cancelada: 'Cancelada' };

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const links = [['/', 'Inicio'], ['/servicios', 'Servicios'], ['/barberos', 'Equipo'], ['/reservar', 'Reservar']];
  if (user) links.push(['/mis-citas', user.role === 'admin' ? 'Agenda general' : 'Mis citas']);
  if (user?.role === 'admin') links.push(['/administracion', 'Resumen']);
  return <>
    <header className="site-header">
      <div className="container header-inner">
        <Link to="/" className="brand" aria-label="HAIR GRECIA, ir al inicio"><span className="brand-mark">HG</span><span>HAIR <strong>GRECIA</strong><small>BARBER STUDIO</small></span></Link>
        <button type="button" className="mobile-menu" aria-label="Abrir menú" aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}>☰</button>
        <nav className={menuOpen ? 'nav open' : 'nav'} aria-label="Navegación principal">
          {links.map(([path, label]) => <NavLink key={path} to={path} end={path === '/'} onClick={() => setMenuOpen(false)}>{label}</NavLink>)}
          {user ? <button type="button" className="nav-button" onClick={async () => { await logout(); navigate('/'); }}>Salir ({user.name.split(' ')[0]})</button>
            : <NavLink to="/ingresar" className="nav-button" onClick={() => setMenuOpen(false)}>Ingresar</NavLink>}
        </nav>
      </div>
    </header>
    <main id="contenido">{children}</main>
    <footer className="footer"><div className="container"><strong>HAIR GRECIA</strong><span>Prototipo académico para la organización de citas. Servicios, equipo y precios de ejemplo.</span></div></footer>
  </>;
}

function Home() {
  return <>
    <section className="hero"><div className="hero-shade"><div className="container hero-content"><span className="eyebrow">BARBER STUDIO · TU TIEMPO IMPORTA</span><h1>Tu estilo, a tu hora.</h1><p>Conoce nuestros servicios, elige a tu barbero y separa tu próximo espacio en pocos pasos.</p><div className="hero-actions"><Link className="button" to="/reservar">Reservar una cita</Link><Link className="button ghost" to="/servicios">Ver servicios</Link></div></div></div></section>
    <section className="section container"><div className="section-title"><span className="eyebrow">MÁS FÁCIL PARA TODOS</span><h2>¿Cómo funciona?</h2><p>Una agenda sencilla para evitar enredos con los horarios.</p></div><div className="steps">
      {[['01', 'Escoge el servicio', 'Revisa las opciones y los precios desde.'], ['02', 'Elige quién te atiende', 'Consulta nuestro equipo y sus horarios.'], ['03', 'Confirma tu hora', 'La aplicación comprueba si el espacio sigue libre.']].map(([n,t,d]) => <article key={n} className="step"><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}
    </div></section>
    <section className="section light"><div className="container split"><img src="/img/corte_hombre.jpg" alt="Servicio de corte de cabello"/><div><span className="eyebrow">UN ESPACIO PARA TU ESTILO</span><h2>Todo empieza con una buena atención.</h2><p>La propuesta de HAIR GRECIA busca que cada cliente conozca los servicios y pueda revisar la disponibilidad sin tener que llamar o escribir varias veces.</p><Link to="/barberos" className="text-link">Conoce al equipo →</Link></div></div></section>
  </>;
}
function Services() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  useEffect(() => { api.get('/services').then(r => setItems(r.data.items)).catch(e => setError(messageFromError(e))); }, []);
  return <section className="section container"><div className="section-title"><span className="eyebrow">LO QUE HACEMOS</span><h1>Servicios</h1><p>Precios iniciales de referencia. El valor final puede variar según el servicio.</p></div>{error && <p role="alert" className="message error">{error}</p>}<div className="cards">{items.map(s => <article className="service-card" key={s.id}><img src={'/img/'+s.image} alt={s.name}/><div className="card-body"><h2>{s.name}</h2><p>{s.duration_min} minutos aprox.</p><strong>Desde {pesos(s.price_from)}</strong><Link className="text-link" to="/reservar">Reservar →</Link></div></article>)}</div></section>;
}
function Barbers() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState('');
  useEffect(() => { api.get('/barbers').then(r => setItems(r.data.items)).catch(e => setError(messageFromError(e))); }, []);
  return <section className="section container"><div className="section-title"><span className="eyebrow">NUESTRO EQUIPO</span><h1>Barberos y estilistas</h1><p>Consulta las especialidades y los horarios de referencia del equipo.</p></div>{error && <p className="message error" role="alert">{error}</p>}<div className="cards">{items.map(b => <article className="service-card" key={b.id}><img src={'/img/'+b.image} alt={'Fotografía de '+b.name}/><div className="card-body"><h2>{b.name}</h2><p>{b.specialty}</p><div className="hours">L–V: {b.week_from}–{b.week_to}<br/>Sáb: {b.sat_from}–{b.sat_to}</div><Link className="text-link" to="/reservar">Elegir hora →</Link></div></article>)}</div></section>;
}
function Login() {
  const [register, setRegister] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [working, setWorking] = useState(false);
  const { user, login } = useAuth();
  const navigate = useNavigate();
  if (user) return <Navigate to="/reservar" replace/>;
  const submit = async (e) => {
    e.preventDefault(); setWorking(true); setError(''); setSuccess('');
    try {
      if (register) {
        await api.post('/auth/register', form);
        setRegister(false); setSuccess('Cuenta creada. Ahora inicia sesión.'); setForm({ ...form, password: '' });
      } else { await login(form.email,form.password); navigate('/reservar'); }
    } catch (err) { setError(messageFromError(err)); }
    finally { setWorking(false); }
  };
  return <section className="section container"><div className="form-card narrow"><span className="eyebrow">TU CUENTA</span><h1>{register ? 'Crear cuenta' : 'Iniciar sesión'}</h1><p>{register ? 'Regístrate para separar tus citas.' : 'Entra para gestionar tus reservas.'}</p>
    <form onSubmit={submit} className="form-grid">{register && <label>Nombre completo<input required minLength="2" autoComplete="name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label>}
      <label>Correo electrónico<input required type="email" autoComplete="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label>
      <label>Contraseña<input required type="password" minLength="8" autoComplete={register?'new-password':'current-password'} value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label>
      {error && <p role="alert" className="message error">{error}</p>}{success && <p role="status" className="message success">{success}</p>}
      <button className="button" disabled={working}>{working ? 'Procesando…' : register ? 'Crear cuenta' : 'Ingresar'}</button>
    </form><button type="button" className="inline-button" onClick={()=>{setRegister(!register);setError('');setSuccess('');}}>{register?'Ya tengo cuenta':'¿Primera vez? Crear cuenta'}</button>
  </div></section>;
}
function Booking() {
  const { user } = useAuth();
  const { booking, dispatch } = useBooking();
  const [services,setServices] = useState([]);
  const [barbers,setBarbers] = useState([]);
  const [slots,setSlots] = useState([]);
  const [error,setError] = useState('');
  const [success,setSuccess] = useState('');
  const [working,setWorking] = useState(false);
  const [loadingSlots,setLoadingSlots] = useState(false);
  const today = new Date();
  const localToday = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
  useEffect(() => { Promise.all([api.get('/services'),api.get('/barbers')]).then(([a,b])=>{setServices(a.data.items);setBarbers(b.data.items);}).catch(e=>setError(messageFromError(e))); }, []);
  useEffect(() => {
    if (!booking.service_id || !booking.barber_id || !booking.date) { setSlots([]); return; }
    let active = true;
    setLoadingSlots(true);setSlots([]);
    api.get('/availability',{params:{service_id:booking.service_id,barber_id:booking.barber_id,date:booking.date}})
      .then(({data}) => { if(active) setSlots(data.slots); })
      .catch(e=>{ if(active)setError(messageFromError(e)); })
      .finally(()=>{ if(active)setLoadingSlots(false); });
    return () => {active=false;};
  }, [booking.service_id,booking.barber_id,booking.date]);
  const submit = async (e) => {
    e.preventDefault();setError('');setSuccess('');setWorking(true);
    try {
      await api.post('/appointments', {service_id:Number(booking.service_id),barber_id:Number(booking.barber_id),date:booking.date,time:booking.time});
      setSuccess('¡Listo! Tu reserva quedó registrada. Puedes revisarla en Mis citas.');
      dispatch({type:'RESET'});setSlots([]);
    } catch (err) {
      setError(messageFromError(err));
      if (err.response?.status === 409) {
        dispatch({type:'SET_TIME',value:''});
        api.get('/availability', {params:{service_id:booking.service_id,barber_id:booking.barber_id,date:booking.date}})
          .then(({data}) => setSlots(data.slots)).catch(() => setSlots([]));
      }
    } finally {setWorking(false);}
  };
  return <section className="section container"><div className="section-title"><span className="eyebrow">TU PRÓXIMA VISITA</span><h1>Reserva tu cita</h1><p>Escoge el servicio, el barbero, el día y una hora que esté libre.</p></div>
    <div className="booking-layout"><div className="form-card"><h2>Elige tu espacio</h2>
      {!user && <p className="message info">Necesitas <Link to="/ingresar">iniciar sesión o crear una cuenta</Link> para confirmar la reserva. Puedes consultar los horarios antes de ingresar.</p>}
      <form onSubmit={submit} className="form-grid"><label>1. Servicio<select required value={booking.service_id} onChange={e=>dispatch({type:'SET_SERVICE',value:e.target.value})}><option value="">Selecciona el servicio</option>{services.map(s=><option key={s.id} value={s.id}>{s.name} · {s.duration_min} min</option>)}</select></label>
      <label>2. Profesional<select required value={booking.barber_id} onChange={e=>dispatch({type:'SET_BARBER',value:e.target.value})}><option value="">Selecciona el barbero</option>{barbers.map(b=><option key={b.id} value={b.id}>{b.name}</option>)}</select></label>
      <label>3. Fecha<input required min={localToday} type="date" value={booking.date} onChange={e=>dispatch({type:'SET_DATE',value:e.target.value})}/></label>
      <label>4. Hora disponible<select required disabled={!slots.length} value={booking.time} onChange={e=>dispatch({type:'SET_TIME',value:e.target.value})}><option value="">Selecciona una hora</option>{slots.map(h=><option key={h} value={h}>{h}</option>)}</select></label>
      {loadingSlots && <p className="hint" role="status">Consultando disponibilidad…</p>}{booking.date && booking.barber_id && booking.service_id && !loadingSlots && !slots.length && <p className="hint">No aparecen espacios para esa combinación. Intenta otra fecha o profesional.</p>}
      {error && <p className="message error" role="alert">{error}</p>}{success && <p className="message success" role="status">{success}</p>}
      <button className="button" disabled={!user||!booking.time||working}>{working?'Confirmando…':'Confirmar reserva'}</button></form></div>
      <aside className="side-panel"><span className="eyebrow">ANTES DE CONFIRMAR</span><h2>Ten en cuenta</h2><p>La aplicación solo ofrece horarios dentro de la jornada de cada profesional. Tampoco permite ocupar una franja que ya tiene otra reserva.</p><p>Si necesitas cancelar, podrás hacerlo desde <strong>Mis citas</strong>.</p><p className="hint">Los horarios y precios usados en este prototipo son de ejemplo y deben validarse con el negocio.</p></aside></div>
  </section>;
}
function Appointments() {
  const [items,setItems]=useState([]),[error,setError]=useState(''),[message,setMessage]=useState('');
  const { user } = useAuth();
  const refresh = () => api.get('/appointments').then(({data})=>setItems(data.items)).catch(e=>setError(messageFromError(e)));
  useEffect(()=>{refresh();},[]);
  const cancel = async (id) => {
    if (!window.confirm('¿Cancelar esta cita?')) return;
    try {await api.patch(`/appointments/${id}/cancel`);setMessage('Se canceló la cita.'); await refresh();}
    catch(e){setError(messageFromError(e));}
  };
  return <section className="section container"><div className="section-title"><span className="eyebrow">AGENDA</span><h1>{user?.role==='admin'?'Reservas registradas':'Mis citas'}</h1><p>Consulta el estado de las reservas y cancela las que no vas a utilizar.</p></div>
    {error && <p className="message error" role="alert">{error}</p>}{message && <p className="message success" role="status">{message}</p>}
    {!items.length ? <div className="empty">Aún no hay citas para mostrar. <Link to="/reservar">Reservar una cita</Link></div>
      : <div className="table-wrap"><table><thead><tr>{user?.role==='admin'&&<th>Cliente</th>}<th>Fecha</th><th>Hora</th><th>Servicio</th><th>Profesional</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{items.map(a=><tr key={a.id}>{user?.role==='admin'&&<td>{a.client_name}</td>}<td>{a.visit_date}</td><td>{a.start_time}–{a.end_time}</td><td>{a.service_name}</td><td>{a.barber_name}</td><td><span className={'status '+a.status}>{labels[a.status]}</span></td><td>{a.status==='reservada'&&<button className="small-button" onClick={()=>cancel(a.id)}>Cancelar</button>}</td></tr>)}</tbody></table></div>}
  </section>;
}
function Administration() {
  const [stats,setStats]=useState(null),[error,setError]=useState('');
  useEffect(()=>{api.get('/stats').then(r=>setStats(r.data)).catch(e=>setError(messageFromError(e)));},[]);
  return <section className="section container"><div className="section-title"><span className="eyebrow">VISTA ADMINISTRATIVA</span><h1>Resumen de la agenda</h1><p>Indicadores básicos de este prototipo.</p></div>{error&&<p className="message error">{error}</p>}{stats&&<div className="steps"><article className="step"><span>01</span><h3>{stats.reservadas}</h3><p>Reservas vigentes</p></article><article className="step"><span>02</span><h3>{stats.canceladas}</h3><p>Citas canceladas</p></article><article className="step"><span>03</span><h3><Link to="/mis-citas">Ver todas</Link></h3><p>Consulta la agenda completa.</p></article></div>}</section>;
}
function Protected({ children, adminOnly = false }) {
  const { user,loading }=useAuth();
  if (loading) return <section className="section container">Revisando sesión…</section>;
  if (!user) return <Navigate to="/ingresar" replace/>;
  if (adminOnly && user.role!=='admin') return <Navigate to="/" replace/>;
  return children;
}
export default function App() {
  return <Layout><Routes>
    <Route path="/" element={<Home/>}/><Route path="/servicios" element={<Services/>}/>
    <Route path="/barberos" element={<Barbers/>}/><Route path="/reservar" element={<Booking/>}/>
    <Route path="/ingresar" element={<Login/>}/>
    <Route path="/mis-citas" element={<Protected><Appointments/></Protected>}/>
    <Route path="/administracion" element={<Protected adminOnly><Administration/></Protected>}/>
    <Route path="*" element={<section className="section container"><h1>Página no encontrada</h1><Link to="/">Volver al inicio</Link></section>}/>
  </Routes></Layout>;
}
