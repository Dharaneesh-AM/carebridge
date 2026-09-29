from flask import Flask, jsonify, render_template_string, request
import sqlite3
import json
import os
from safety.alert_state import get_alert
from datetime import datetime
import urllib.request

app = Flask(__name__)

DB_FILE = "/home/dvm/CareBridge/data/carebridge.db"
EVENT_FILE = "/home/dvm/CareBridge/logs/events.json"

ESP32_API = "http://172.23.241.62:82"

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CareBridge | Caregiver Dashboard</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;
 font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
 background:#0b1220;
 color:#e8eef8;
}
.header{
 padding:22px 30px;
 background:#111b2e;
 border-bottom:1px solid #26344d;
 display:flex;
 justify-content:space-between;
 align-items:center;
}
.brand{font-size:25px;font-weight:800}
.subtitle{font-size:13px;color:#8fa2bf;margin-top:3px}
.status{
 padding:9px 14px;
 border-radius:20px;
 font-size:13px;
 font-weight:700;
 background:#12351f;
 color:#72e6a0;
}
.container{padding:24px;max-width:1500px;margin:auto}
.grid{
 display:grid;
 grid-template-columns:repeat(4,1fr);
 gap:16px;
}
.card{
 background:#111b2e;
 border:1px solid #26344d;
 border-radius:16px;
 padding:19px;
 box-shadow:0 8px 25px rgba(0,0,0,.15);
}
.label{
 color:#8fa2bf;
 font-size:12px;
 text-transform:uppercase;
 letter-spacing:.08em;
 font-weight:700;
}
.value{
 font-size:25px;
 font-weight:800;
 margin-top:8px;
}
.small{font-size:13px;color:#9eb0ca;margin-top:6px}
.section{
 margin-top:20px;
 display:grid;
 grid-template-columns:1.2fr .8fr;
 gap:20px;
}
h2{font-size:17px;margin:0 0 15px}
.row{
 display:flex;
 justify-content:space-between;
 align-items:center;
 padding:11px 0;
 border-bottom:1px solid #22304a;
}
.row:last-child{border-bottom:0}
.badge{
 padding:5px 9px;
 border-radius:8px;
 font-size:11px;
 font-weight:700;
 background:#1c2940;
 color:#b8c7dc;
}
.alert{
 border:1px solid #7d3030;
 background:#32191d;
 border-radius:14px;
 padding:16px;
 margin-bottom:12px;
}
.alert-title{font-weight:800;color:#ff9d9d}
.alert-time{font-size:11px;color:#bd9292;margin-top:4px}
.event{
 padding:12px 0;
 border-bottom:1px solid #22304a;
}
.event:last-child{border-bottom:0}
.event-type{font-weight:700}
.event-time{font-size:11px;color:#778aa6;margin-top:3px}
button{
 border:0;
 border-radius:9px;
 padding:9px 14px;
 font-weight:700;
 cursor:pointer;
 background:#263957;
 color:white;
 margin-right:7px;
}
button:hover{background:#365074}
button.on{background:#174f32;color:#8ff0b6}
button.off{background:#4d252b;color:#ffaaaa}
.footer{
 margin-top:20px;
 text-align:center;
 color:#687b98;
 font-size:11px;
}
@media(max-width:1000px){
 .grid{grid-template-columns:repeat(2,1fr)}
 .section{grid-template-columns:1fr}
}
@media(max-width:600px){
 .grid{grid-template-columns:1fr}
 .header{padding:18px}
 .container{padding:14px}
}
</style>
</head>

<body>
<div class="header">
 <div>
  <div class="brand">CareBridge</div>
  <div class="subtitle">Offline Caregiver Dashboard</div>
 </div>
 <div id="systemStatus" class="status">● LOCAL / OFFLINE</div>
</div>

<div class="container">

 <div class="grid">
  <div class="card">
   <div class="label">Patient</div>
   <div class="value" id="patient">—</div>
   <div class="small" id="patientStatus">Waiting for recognition</div>
  </div>

  <div class="card">
   <div class="label">Current Activity</div>
   <div class="value" id="activity">—</div>
   <div class="small" id="location">Location unknown</div>
  </div>

  <div class="card">
   <div class="label">Local Time</div>
   <div class="value" id="clock">—</div>
   <div class="small">Running locally on CareBridge</div>
  </div>

  <div class="card">
   <div class="label">CareBridge</div>
   <div class="value">ONLINE</div>
   <div class="small">Camera • Voice • LLM • TTS</div>
  </div>
 </div>

 <div class="section">

  <div>
   <div class="card">
    <h2>🚨 Caregiver Alerts</h2>
    <div id="alerts"><div class="small">No active alerts.</div></div>
    <div style="margin-top:13px">
      <button class="off" onclick="clearAlert()">Attend / Clear Alert</button>
    </div>
   </div>

   <div class="card" style="margin-top:20px">
    <h2>💬 Recent Interactions</h2>
    <div id="events"></div>
   </div>
  </div>

  <div>
   <div class="card">
    <h2>💊 Routines & Reminders</h2>
    <div id="routines"></div>
   </div>

   <div class="card" style="margin-top:20px">
    <h2>👨‍👩‍👧 Family</h2>
    <div id="family"></div>
   </div>

   <div class="card" style="margin-top:20px">
    <h2>💡 Home Control</h2>
    <div class="small" id="espStatus">Checking ESP32...</div>
    <div class="small" id="doorStatus" style="margin-top:8px">🚪 Door: Checking...</div>
    <div style="margin-top:13px">
      <button class="on" onclick="relay('on')">Light ON</button>
      <button class="off" onclick="relay('off')">Light OFF</button>
    </div>
   </div>
  </div>

 </div>

 <div class="footer">
  CareBridge • Local-first • No cloud services required
 </div>
</div>

<script>
function esc(x){
 return String(x ?? "").replace(/[&<>"']/g,
  c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
}

async function load(){
 try{
  const r=await fetch('/api/data');
  const d=await r.json();

  document.getElementById('patient').textContent=d.patient?.name || 'Unknown';
  document.getElementById('patientStatus').textContent=
    d.patient?.recognized ? 'Recognized patient' : 'Waiting for recognition';

  document.getElementById('activity').textContent=
    (d.activity || 'Monitoring').replaceAll('_',' ');

  document.getElementById('location').textContent=
    d.location || 'Location unknown';

  document.getElementById('clock').textContent=
    d.time || '—';

  const alerts=document.getElementById('alerts');
  if(!d.alert || !d.alert.active){
    alerts.innerHTML='<div class="small">No active caregiver alerts.</div>';
  }else{
    alerts.innerHTML='<div class="alert">'+
      '<div class="alert-title">⚠ ' + esc(d.alert.reason || "Caregiver alert") + '</div>' +
      '<div class="alert-time">' + esc(d.alert.timestamp || "") + '</div>' +
      '</div>';
  }

  document.getElementById('events').innerHTML=
   (d.events||[]).slice(0,10).map(e=>`
    <div class="event">
     <div class="event-type">${esc(e.event_type||'event')}</div>
     <div>${esc(e.description||'')}</div>
     <div class="event-time">${esc(e.timestamp||'')}</div>
    </div>`).join('') ||
   '<div class="small">No recent interactions.</div>';

  document.getElementById('routines').innerHTML=
   (d.routines||[]).map(r=>`
    <div class="row">
     <div>
      <b>${esc(r.name)}</b>
      <div class="small">${esc(r.description||'')}</div>
     </div>
     <span class="badge">${esc(r.time)}</span>
    </div>`).join('') ||
   '<div class="small">No routines configured.</div>';

  document.getElementById('family').innerHTML=
   (d.family||[]).map(p=>`
    <div class="row">
     <div><b>${esc(p.name)}</b></div>
     <span class="badge">${esc(p.relationship)}</span>
    </div>`).join('') ||
   '<div class="small">No family records.</div>';

  document.getElementById('espStatus').textContent=
   d.esp32_online ? 'ESP32 connected • relay control available'
                  : 'ESP32 offline • control unavailable';

  const door = d.esp32_status?.door;
  document.getElementById('doorStatus').textContent =
   door ? "🚪 Door: " + String(door).toUpperCase() : "🚪 Door: Unknown";

 }catch(e){
  document.getElementById('systemStatus').textContent='● DASHBOARD ERROR';
 }
}

async function clearAlert(){
 try{
  const r=await fetch("/api/alert/clear",{method:"POST"});
  const d=await r.json();
  await load();
 }catch(e){
  console.error("Alert clear error:",e);
 }
}

async function relay(state){
 try{
  const r=await fetch('/api/relay/'+state,{method:'POST'});
  const d=await r.json();
  document.getElementById('espStatus').textContent=d.message;
 }catch(e){
  document.getElementById('espStatus').textContent='ESP32 unavailable';
 }
}

load();
setInterval(load,2000);
</script>
</body>
</html>
"""

def db_rows(query, params=()):
    try:
        con = sqlite3.connect(DB_FILE)
        con.row_factory = sqlite3.Row
        rows = con.execute(query, params).fetchall()
        con.close()
        return [dict(r) for r in rows]
    except Exception:
        return []

def load_events():
    try:
        with open(EVENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def get_esp32_status():
    try:
        with urllib.request.urlopen(ESP32_API + "/status", timeout=1.5) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}

def esp32_online():
    return bool(get_esp32_status())

def dashboard_data():
    patients = db_rows("SELECT id,name FROM patients LIMIT 1")
    patient = patients[0] if patients else {"id":1,"name":"Demo Patient"}

    family = db_rows(
        "SELECT name,relationship FROM people WHERE patient_id=?",
        (patient["id"],)
    )

    locations = db_rows(
        "SELECT * FROM locations WHERE patient_id=?",
        (patient["id"],)
    )

    routines = db_rows(
        "SELECT * FROM routines WHERE patient_id=? ORDER BY time",
        (patient["id"],)
    )

    events = load_events()
    events = list(reversed(events[-20:]))

    activity = "monitoring"
    location = "Home"

    for e in events:
        et = str(e.get("event_type",""))
        if et in ("person_present","person_left"):
            activity = et
            break

    if locations:
        location = locations[0].get("location") or locations[0].get("name") or "Home"

    alerts = []
    for e in events:
        if str(e.get("event_type","")) in ("safety_alert","caregiver_alert"):
            alerts.append({
                "message": e.get("description") or "Caregiver attention required",
                "time": e.get("timestamp") or ""
            })

    shared_alert = get_alert()
    esp_status = get_esp32_status()

    return {
        "patient": {
            "name": patient["name"],
            "recognized": activity == "person_present"
        },
        "activity": activity,
        "location": location,
        "time": datetime.now().strftime("%I:%M:%S %p"),
        "family": family,
        "routines": routines,
        "events": events,
        "alerts": alerts[:5],
        "alert": shared_alert,
        "esp32_online": bool(esp_status),
        "esp32_status": esp_status
    }

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/data")
def api_data():
    return jsonify(dashboard_data())

@app.route("/api/alert/clear", methods=["POST"])
def clear_shared_alert():
    alert = get_alert()

    if not alert.get("active"):
        return jsonify({
            "message": "No active alert",
            "alert": alert
        })

    from safety.alert_state import clear_alert

    cleared = clear_alert()

    return jsonify({
        "message": "Alert attended and cleared",
        "alert": cleared
    })


@app.route("/api/relay/<state>", methods=["POST"])
def relay(state):
    if state not in ("on","off"):
        return jsonify({"message":"Invalid relay state"}),400

    try:
        url = ESP32_API + "/relay/" + state
        urllib.request.urlopen(url, timeout=2)
        return jsonify({"message":f"ESP32 relay switched {state.upper()}"})
    except Exception:
        return jsonify({"message":"ESP32 offline • relay command not sent"}),503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
