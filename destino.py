import flet as ft
from groq import Groq
import os, random, urllib.request, json
from datetime import datetime

URL_MOCK = "https://mockapi.io"

def leer_nube(correo):
    try:
        url = f"{URL_MOCK}/{correo.replace('@','_at_').replace('.','_dot_')}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as r:
            d = json.loads(r.read().decode('utf-8'))
            return {"stats": json.loads(d["stats"]), "historial": json.loads(d["historial"]), "inventario": json.loads(d["inventario"]), "lore": json.loads(d["lore_partida"])}
    except: return None

def escribir_nube(correo, datos):
    try:
        id_l = correo.replace("@", "_at_").replace(".", "_dot_")
        existe = True
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{URL_MOCK}/{id_l}", headers={'User-Agent': 'Mozilla/5.0'}), timeout=2) as r: pass
        except: existe = False
        payload = json.dumps({"id": id_l, "stats": json.dumps(datos["stats"]), "historial": json.dumps(datos["historial"]), "inventario": json.dumps(datos["inventario"]), "lore_partida": json.dumps(datos["lore"])}).encode('utf-8')
        req = urllib.request.Request(f"{URL_MOCK}/{id_l}" if existe else URL_MOCK, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method="PUT" if existe else "POST")
        with urllib.request.urlopen(req, timeout=4) as r: pass
        return True
    except: return False

def cargar_bloque(rol, modo, texto):
    bg = "#0F172A" if modo == "Pensar" else "#1E1B4B" if rol == "usuario" else "#111827"
    lbl = "💭 Travesura: " if modo == "Pensar" else "🗣️ Hablar: " if rol == "usuario" else "🏰 Director: "
    return ft.Container(content=ft.Text(f"{lbl}{texto}", color="#94A3B8" if modo == "Pensar" else "#A78BFA" if rol == "usuario" else "#F3F4F6", italic=(modo=="Pensar")), padding=12, border_radius=10, bgcolor=bg)

semillas = [
    "La criatura del pozo del ala norte despierta si no se respetan las patrullas nocturnas.",
    "El Gran Reloj Astronómico se ha retrasado, congelando estancias llenas de trampas rúnicas.",
    "Alguien está contrabandeando duendecillos de Cornualles en los dormitorios de primer año.",
    "Los cuadros de la tercera planta han huido de sus lienzos ocultando el pase a los sótanos."
]def main(page: ft.Page):
    page.title = "🏰 Academia Mágica"
    page.bgcolor = "#030712"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 15

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    page.data = {"stats": {"Vida": 100, "Dinero": 15, "Mana": 10, "EXP": 0, "Dias": 270}, "inventario": ["Túnica de Primer Año", "Varita de Fresno", "Mascota Pequeña"], "historial": [], "lore": [f"Misterio: {random.choice(semillas)}"], "correo_usuario": None}

    reloj_lbl = ft.Text(f"📅 CURSO: Quedan {page.data['stats']['Dias']} días para los Exámenes Finales", color="#A78BFA", weight=ft.FontWeight.BOLD, size=13)
    stats_lbl = ft.Text(f"❤️ Vitalidad: {page.data['stats']['Vida']}% | 🪙 {page.data['stats']['Dinero']} Galeones | 🔮 Maná: {page.data['stats']['Mana']}/10", color="#F3F4F6", size=12, weight=ft.FontWeight.BOLD)
    inv_lbl = ft.Text(f"🎒 Mochila: {page.data['inventario']}", color="#94A3B8", size=11, italic=True)
    
    stat_box = ft.Container(content=ft.Column([reloj_lbl, stats_lbl, inv_lbl], spacing=4), padding=12, border_radius=12, bgcolor="#111827")
    chat_box = ft.ListView(expand=True, spacing=10, height=340)

    modo_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Pensar", label="Ingeniar Travesura"), ft.Radio(value="Hablar", label="Hablar")], alignment=ft.MainAxisAlignment.CENTER))
    modo_radio.value = "Pensar"
    input_txt = ft.TextField(hint_text="Introduce tu correo electrónico de matrícula...", bgcolor="#111827", expand=True)

    btn_env = ft.ElevatedButton(content=ft.Text("🪄 CONJURAR", color="white"), bgcolor="#4C1D95", height=45)
    btn_sav = ft.ElevatedButton(content=ft.Text("💾 Guardar Notas", color="white"), bgcolor="#065F46")
    btn_res = ft.TextButton(content=ft.Text("💀 Expulsión", color="#EF4444"), on_click=lambda e: reiniciar())

    def la_bienvenida():
        chat_box.controls.clear()
        chat_box.controls.append(cargar_bloque("ia", "Pensar", "Frente a ti se alzan los muros del Colegio de Magia. Eres un niño pequeño dando tus primeros pasos. El uniforme te queda grande, el maná es limitado y hay zonas prohibidas vigiladas por gárgolas y prefectos severos donde requieres INGENIO PURO para colarte.\n\n📧 [MATRÍCULA]: Escribe tu correo abajo para cargar o iniciar curso:"))
    la_bienvenida()

    def enviar_accion(e):
        if not input_txt.value: return
        t = input_txt.value.strip()
        input_txt.value = ""
        
        if page.data["correo_usuario"] is None:
            if "@" in t and "." in t:
                page.data["correo_usuario"] = t
                p = leer_nube(t)
                if p:
                    page.data.update(p)
                    chat_box.controls.clear()
                    for m in page.data["historial"]: chat_box.controls.append(cargar_bloque(m.get("rol","ia"), m.get("modo","Pensar"), m.get("texto","")))
                    chat_box.controls.append(cargar_bloque("ia", "Pensar", f"🔮 Matrícula recuperada para {t}. Regresas a los pasillos del castillo."))
                else:
                    chat_box.controls.append(cargar_bloque("ia", "Pensar", f"✨ Registro completo para [{t}]. Tienes {page.data['stats']['Dinero']} galeones. El Sombrero Seleccionador espera abajo. Escribe tu primera acción como niño místico (ej. ¿Qué traes en tu baúl escolar?)."))
                reloj_lbl.value = f"📅 CURSO: Quedan {page.data['stats']['Dias']} días para los Exámenes Finales"
                stats_lbl.value = f"❤️ Vitalidad: {page.data['stats']['Vida']}% | 🪙 {page.data['stats']['Dinero']} Galeones | 🔮 Maná: {page.data['stats']['Mana']}/10"
                inv_lbl.value = f"🎒 Mochila: {page.data['inventario']}"
                input_txt.hint_text = "¿Qué travesura o conjuro intentas?"
                btn_sav.content.text = f"💾 Guardar: {t[:4]}..."
                page.update()
                return
            else:
                chat_box.controls.append(cargar_bloque("ia", "Pensar", "❌ Escribe un correo válido:"))
                page.update()
                return

        m = modo_radio.value
        chat_box.controls.append(cargar_bloque("usuario", m, t))
        page.data["historial"].append({"rol": "usuario", "modo": m, "texto": t})
        page.update()

        p_sys = f"Actúa como Game Master de un RPG en un Colegio de Magia escolar. El jugador es un NIÑO PEQUEÑO de primer año: bajo, físicamente débil y con maná máximo limitado (10). Las zonas prohibidas (Sección Restringida, Mazmorras Nocturnas) requieren INGENIO PURO (esconderse, conductos pequeños, distracciones). Moneda: Galeones. Quedan {page.data['stats']['Dias']} días de curso. Acciones descuentan maná, días o galeones. Valores actuales: Vida={page.data['stats']['Vida']}, Dinero={page.data['stats']['Dinero']}, Mana={page.data['stats']['Mana']}, EXP={page.data['stats']['EXP']}, Dias={page.data['stats']['Dias']}. Mochila: '{page.data['inventario']}'. AL FINAL ABSOLUTO de tu mensaje, incluye estrictamente estos bloques en este formato exacto:\n1. [ESTADÍSTICAS: Vida=VALOR, Dinero=VALOR, Mana=VALOR, EXP=VALOR, Dias=VALOR]\n2. [MOCHILA: Objetos escolares actualizados]\n3. [MEMORIA: Breve situación]."
        comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": p_sys}] + [{"role": "user" if msg.get("rol") == "usuario" else "assistant", "content": msg.get("texto", "")} for msg in page.data["historial"][-6:]])
        raw = str(comp.choices[0].message.content)
        res = raw

        if "[MEMORIA:" in raw:
            try: page.data["lore"] = [raw[raw.index("[MEMORIA:") + 9:raw.index("]", raw.index("[MEMORIA:"))].replace('"','').strip()]; res = raw[:raw.index("[MEMORIA:")].strip()
            except: pass
        if "[MOCHILA:" in raw:
            try: page.data["inventario"] = [raw[raw.index("[MOCHILA:") + 9:raw.index("]", raw.index("[MOCHILA:"))].strip()]; res = raw[:raw.index("[MOCHILA:")].strip()
            except: pass
        if "[ESTADÍSTICAS:" in raw:
            try:
                sub = raw[raw.index("[ESTADÍSTICAS:") + 14:raw.index("]", raw.index("[ESTADÍSTICAS:"))].strip()
                res = raw[:raw.index("[ESTADÍSTICAS:")].strip()
                for c in sub.split(","):
                    k, v = c.split("=")
                    k = k.strip(); v = int(v.strip())
                    if k in page.data["stats"]:
                        if k == "Vida" and v > 100: v = 100
                        if k == "Mana" and v > 10: v = 10
                        page.data["stats"][k] = v
            except: pass

        chat_box.controls.append(cargar_bloque("ia", "Pensar", res.strip()))
        page.data["historial"].append({"rol": "ia", "texto": res.strip()})
        reloj_lbl.value = f"📅 CURSO: Quedan {page.data['stats']['Dias']} días para los Exámenes Finales"
        stats_lbl.value = f"❤️ Vitalidad: {page.data['stats']['Vida']}% | 🪙 {page.data['stats']['Dinero']} Galeones | 🔮 Maná: {page.data['stats']['Mana']}/10"
        inv_lbl.value = f"🎒 Mochila: {page.data['inventario']}"
        page.update()

    def guardar():
        if page.data["correo_usuario"]:
            if escribir_nube(page.data["correo_usuario"], {"stats": page.data["stats"], "historial": page.data["historial"], "inventario": page.data["inventario"], "lore": page.data["lore"]}):
                btn_sav.content.text = "✅ Notas Guardadas"; btn_sav.bgcolor = "#10B981"
            else: btn_sav.content.text = "❌ Error Red"; btn_sav.bgcolor = "#EF4444"
            page.update()

    def reiniciar():
        if page.data["correo_usuario"]:
            try: urllib.request.urlopen(urllib.request.Request(f"{URL_MOCK}/{page.data['correo_usuario'].replace('@','_at_').replace('.','_dot_')}", method="DELETE", headers={'User-Agent': 'Mozilla/5.0'}), timeout=2)
            except: pass
        page.data.update({"stats": {"Vida": 100, "Dinero": 15, "Mana": 10, "EXP": 0, "Dias": 270}, "inventario": ["Túnica de Primer Año", "Varita de Fresno", "Mascota Pequeña"], "historial": [], "correo_usuario": None, "lore": [f"Misterio: {random.choice(semillas)}"]})
        la_bienvenida(); btn_sav.content.text = "💾 Guardar Notas"; btn_sav.bgcolor = "#065F46"
        reloj_lbl.value = f"📅 CURSO: Quedan {page.data['stats']['Dias']} días para los Exámenes Finales"
        stats_lbl.value = f"❤️ Vitalidad: {page.data['stats']['Vida']}% | 🪙 {page.data['stats']['Dinero']} Galeones | 🔮 Maná: {page.data['stats']['Mana']}/10"
        inv_lbl.value = f"🎒 Mochila: {page.data['inventario']}"; input_txt.hint_text = "Introduce tu correo electrónico de matrícula..."
        page.update()

    btn_env.on_click = enviar_accion
    btn_sav.on_click = lambda e: guardar()
    page.add(ft.Column([ft.Row([ft.Text("🧙‍♂️ ACADEMIA MÁGICA", size=12, weight=ft.FontWeight.BOLD, color="#A78BFA"), ft.Row([btn_sav, btn_res], spacing=5)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), stat_box, ft.Divider(color="#1E293B"), chat_box, ft.Divider(color="#1E293B"), modo_radio, ft.Row([input_txt, btn_env])], expand=True))

ft.app(target=main)
    
