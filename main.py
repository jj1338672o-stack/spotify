import sqlite3
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# Permitir conexiones desde cualquier cliente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def inicializar_db():
  conn = sqlite3.connect("comunidad_ia.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS sugerencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cancion TEXT,
            artista TEXT,
            modo TEXT,
            usuario TEXT,
            votos INTEGER DEFAULT 1
        )
    """)
  conn.commit()
  conn.close()


inicializar_db()


@app.get("/", response_class=HTMLResponse)
def home():
  conn = sqlite3.connect("comunidad_ia.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, nombre_cancion, artista, modo, usuario, votos FROM sugerencias"
      " ORDER BY votos DESC"
  )
  filas = cursor.fetchall()
  conn.close()

  tabla_html = ""
  for row in filas:
    tabla_html += f"""
        <tr class="border-b border-slate-800 hover:bg-slate-900/40">
            <td class="py-3 px-4 text-slate-200">{row[1]}</td>
            <td class="py-3 px-4 text-slate-400">{row[2]}</td>
            <td class="py-3 px-4"><span class="bg-slate-800 text-emerald-400 px-2.5 py-1 rounded-lg text-xs font-bold uppercase">{row[3]}</span></td>
            <td class="py-3 px-4 text-slate-500">{row[4]}</td>
            <td class="py-3 px-4 text-center font-bold text-indigo-400">{row[5]}</td>
            <td class="py-3 px-4 text-right">
                <a href="/votar?id={row[0]}" class="bg-emerald-600/20 hover:bg-emerald-600 text-emerald-400 hover:text-slate-950 font-bold px-3 py-1.5 rounded-xl transition text-xs border border-emerald-500/30">👍 Votar</a>
            </td>
        </tr>
        """

  return f"""
    <html>
        <head>
            <title>GameMusicBot - Cloud Hub</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-950 text-slate-100 font-sans p-6 md:p-10">
            <div class="max-w-4xl mx-auto">
                <header class="mb-8 bg-slate-900/60 backdrop-blur-xl p-6 rounded-3xl border border-slate-800 shadow-2xl text-center">
                    <h1 class="text-2xl font-black text-white">🎮 GameMusicBot <span class="text-emerald-400">Cloud AI Hub</span></h1>
                    <p class="text-xs text-slate-400 mt-1">Plataforma global de entrenamiento musical y votaciones comunitarias 24/7</p>
                </header>

                <div class="bg-slate-900/60 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-2xl mb-8">
                    <h2 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">🧠 Entrenar la IA (Aportar Canción)</h2>
                    <form action="/sugerir" method="POST" class="grid grid-cols-1 md:grid-cols-4 gap-3">
                        <input type="text" name="nombre" placeholder="Canción" required class="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white">
                        <input type="text" name="artista" placeholder="Artista" required class="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white">
                        <select name="modo" class="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white">
                            <option value="lobby">Lobby (Chill)</option>
                            <option value="accion">Acción (Gaming)</option>
                            <option value="gym">Gym (Energía)</option>
                            <option value="estudio">Estudio (Enfoque)</option>
                        </select>
                        <button type="submit" class="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold py-2.5 rounded-xl transition text-xs shadow-lg">Enviar a la Nube</button>
                    </form>
                </div>

                <div class="bg-slate-900/60 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-2xl">
                    <h2 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">📊 Biblioteca Comunitaria Global</h2>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b border-slate-800 text-slate-500">
                                    <th class="py-3 px-4">Canción</th>
                                    <th class="py-3 px-4">Artista</th>
                                    <th class="py-3 px-4">Modo</th>
                                    <th class="py-3 px-4">Usuario</th>
                                    <th class="py-3 px-4 text-center">Votos</th>
                                    <th class="py-3 px-4 text-right">Acción</th>
                                </tr>
                            </thead>
                            <tbody>{tabla_html}</tbody>
                        </table>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """


@app.post("/sugerir")
def sugerir(
    nombre: str = Form(...), artista: str = Form(...), modo: str = Form(...)
):
  conn = sqlite3.connect("comunidad_ia.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO sugerencias (nombre_cancion, artista, modo, usuario, votos)"
      " VALUES (?, ?, ?, 'Comunidad', 1)",
      (nombre, artista, modo),
  )
  conn.commit()
  conn.close()
  return RedirectResponse(url="/", status_code=303)


@app.get("/votar")
def votar(id: int):
  conn = sqlite3.connect("comunidad_ia.db")
  cursor = conn.cursor()
  cursor.execute("UPDATE sugerencias SET votos = votos + 1 WHERE id = ?", (id,))
  conn.commit()
  conn.close()
  return RedirectResponse(url="/", status_code=303)


@app.get("/cancion_recomendada")
def cancion_recomendada(modo: str):
  conn = sqlite3.connect("comunidad_ia.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT nombre_cancion, artista FROM sugerencias WHERE modo = ? ORDER"
      " BY votos DESC LIMIT 5",
      (modo,),
  )
  resultados = cursor.fetchall()
  conn.close()
  if resultados:
    import random

    elegida = random.choice(resultados)
    return {"cancion": elegida[0], "artista": elegida[1]}
  return {"cancion": None, "artista": None}