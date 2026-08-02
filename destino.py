import flet as ft
from groq import Groq
import os
import random
from datetime import datetime
import json

# BASE DE DATOS FÍSICA REAL EN EL SERVIDOR (Inmune a apagones y cierres de app)
ARCHIVO_BASE = "base_datos_grimorios.json"

def leer_disco_duro():
    if os.path.exists(ARCHIVO_BASE):
        try:
            with open(ARCHIVO_BASE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def escribir_disco_duro(datos):
    try:
        with open(ARCHIVO_BASE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except: pass

def main(page: ft.Page):
    # 1. Configuración de pantalla estilo App Móvil Premium
    page.title = "🚨 Crónicas del Velo Mágico"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Conexión segura con la IA de Groq en Render
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Variables de estado internas de la sesión actual
    stats = {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30}
    inventario_contenedor = ["Varita de Sauce, Toga Escolar"]
    historial = []
    
    semillas_amenaza_final = [
        "El motor de transmutación del Ministerio de Magia ha sido infectado por una maldición de óxido eterno que disuelve el maná de la ciudad.",
        "Una secta de licántropos y magos oscuros está preparando el despertar de un dragón mitológico sepultado bajo los cimientos urbanos.",
        "Un brote de 'estática mística' se está filtrando a través de la red eléctrica, borrando los recuerdos de los hechiceros y exponiendo el velo.",
        "El Reloj de Arena Ancestral que mantiene la barrera de invisibilidad frente a los humanos mundanos ha sido agrietado en un sabotaje interno.",
        "Un antiguo linaje de vampiros puros está comprando los nexos de sangre de las alcantarillas para desatar una plaga mística purificadora."
    ]
    semilla_inicial = random.choice(semillas_amenaza_final)
    lore_partida_contenedor = [f"Amenaza de extinción oculta elegida: {semilla_inicial}"]

    # Variables de control de correo electrónico fijadas en la página
    page.data = {"correo_usuario": None}

    # Obtener el ciclo horario de 24 horas reales
    hora_actual_real = datetime.now().strftime("%H:%M")
    es_de_noche = 20 <= datetime.now().hour or datetime.now().hour <= 6
    estado_dia_noche = "🌌 TOQUE DE QUEDA (El velo es frágil, criaturas en los callejones, patrols del Ministerio)" if es_de_noche else "☀️ BAJO EL VELO (La magia se esconde de los humanos, mercados mágicos abiertos, tabernas activas)"

    # 3. Componentes visuales superiores unificados (Añadido el Inventario Gráfico)
    reloj_label = ft.Text(f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo", color="#A78BFA", weight=ft.FontWeight.BOLD, size=14)
    hora_label = ft.Text(f"⏰ Tiempo Real: {hora_actual_real} | {estado_dia_noche}", color="#38BDF8", size=12, weight=ft.FontWeight.W_500)
    stats_text = ft.Text(f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%", color="#F3F4F6", weight=ft.FontWeight.BOLD, size=15)
    inventario_text = ft.Text(f"🎒 Mochila: {inventario_contenedor}", color="#94A3B8", size=12, italic=True)
    
    stat_container = ft.Container(
        content=ft.Column([reloj_label, hora_label, stats_text, ft.Divider(color="#1E293B", height=5), inventario_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), 
        padding=15, border_radius=12, gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"])
    )

    # 4. Historial del Chat Principal
    chat_view = ft.ListView(expand=True, spacing=10, height=360)
    
    def cargar_bloque(rol, modo, texto):
        if rol == "usuario":
            bg = "#0F172A" if modo == "Pensar" else "#022C22"
            lbl = "💭 Pensasíntesis: " if modo == "Pensar" else "🗣️ Voz Alta: "
            return ft.Container(
                content=ft.Text(f"{lbl}{texto}", color="#94A3B8" if modo == "Pensar" else "#34D399", italic=(modo=="Pensar")), 
                padding=14, border_radius=10, bgcolor=bg
            )
        return ft.Container(
            content=ft.Text(f"🔮 Narrador: {texto}", color="#F3F4F6", font_family="Georgia"), 
            padding=14, border_radius=10, bgcolor="#111827"
        )

    def pintar_bienvenida():
        chat_view.controls.clear()
        chat_view.controls.append(cargar_bloque("ia", "Pensar", f"Detrás del ruidoso tráfico humano y los carteles de neón de la ciudad moderna, late un mundo oculto regido por la magia antigua, los estatutos del Velo Secreto y los decretos del Ministerio de Hechicería.\n\n📧 [SISTEMA DE GRIMORIO POR CORREO]:\nEscribe tu dirección de correo electrónico abajo en la barra de texto y dale a enviar para iniciar tu andadura o recuperar tu progreso guardado en el servidor:"))
    
    pintar_bienvenida()
        # 5. Controles inferiores
    modo_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Pensar", label="Narrar/Pensar"), ft.Radio(value="Hablar", label="Hablar")], alignment=ft.MainAxisAlignment.CENTER))
    modo_radio.value = "Pensar"
    input_texto = ft.TextField(hint_text="Introduce tu correo electrónico para empezar...", bgcolor="#111827", border_color="#1E293B", expand=True)

    # 6. Lógica de ejecución de la IA al pulsar el botón
    def enviar_accion(e):
        nonlocal lore_partida_contenedor, stats, historial, inventario_contenedor
        if not input_texto.value: return
        txt = input_texto.value.strip()
        input_texto.value = ""
        
        # MECÁNICA DE CARGA AUTOMÁTICA DETECTANDO EL CORREO ELECTRÓNICO (Contiene arroba y punto)
        if page.data["correo_usuario"] is None:
            if "@" in txt and "." in txt:
                page.data["correo_usuario"] = txt
                db_disco = leer_disco_duro()
                
                if txt in db_disco:
                    partida_cargada = db_disco[txt]
                    stats.clear()
                    stats.update(partida_cargada["stats"])
                    historial.clear()
                    historial.extend(partida_cargada["historial"])
                    
                    if "inventario" in partida_cargada:
                        inventario_contenedor = [partida_cargada["inventario"]] if isinstance(partida_cargada["inventario"], str) else partida_cargada["inventario"]
                    else:
                        inventario_contenedor = ["Varita de Sauce, Toga Escolar"]
                        
                    lore_partida_contenedor = partida_cargada["lore"]
                    
                    chat_view.controls.clear()
                    for msg in historial:
                        chat_view.controls.append(cargar_bloque(msg.get("rol", "ia"), msg.get("modo", "Pensar"), msg.get("texto", "")))
                    
                    chat_view.controls.append(cargar_bloque("ia", "Pensar", f"🔮 Vínculo establecido con {txt}. Tu historial de mensajes, monedas y mochila se han restaurado con éxito. Continúa tu aventura."))
                else:
                    chat_view.controls.append(cargar_bloque("ia", "Pensar", f"✨ Correo {txt} registrado correctamente.\n\nTienes {stats['Dinero']}€ mágicos en tu monedero de cuero. Los callejones invisibles albergan mercados negros y boticarios oscuros. Todo tiene un precio.\n\nElige tu arquetipo místico escribiéndolo abajo para adentrarte en el mapa abierto: Mago Urbano, Detective, Cazador o Humano Despierto."))
                
                reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
                stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
                inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
                input_texto.hint_text = "¿Qué dirección toma tu voluntad?"
                btn_save.content.text = f"💾 Guardar: {txt[:4]}..."
                page.update()
                return
            else:
                chat_view.controls.append(cargar_bloque("ia", "Pensar", "❌ Formato incorrecto. Por favor, introduce un correo electrónico válido para identificarte (ejemplo: jugador@gmail.com):"))
                page.update()
                return

        # FLUJO DE JUEGO NORMAL CON LA IA (Solo se activa si el usuario ya se ha validado con su correo)
        mod = modo_radio.value
        chat_view.controls.append(cargar_bloque("usuario", mod, txt))
        historial.append({"rol": "usuario", "modo": mod, "texto": txt})
        page.update()

        prompt_sistema = f"""
        Actúa como el Game Master de un RPG conversacional de Fantasía Urbana Contemporánea. Tu estilo es denso, literario y profundamente descriptivo.
        [SISTEMA ECONÓMICO REAL Y COMERCIO PROFUNDO]
        - Gestionas una economía estricta. Todo tiene un precio real en Euros (€). No regales dinero ni objetos de valor porque sí.
        - Despliega un abanico inmenso de TIENDAS MÍSTICAS según donde vaya el jugador (armerías de varitas, boticarios, mercados negros, tabernas). 
        - Si el jugador compra un objeto en un comercio, des cuenta el precio de su dinero y mételo explícitamente dentro de su mochila.
        [RITMO DE APOCALIPSIS VARIABLE]
        La gran amenaza final que destruirá el Velo a los 30 días es: '{str(lore_partida_contenedor)}'. Decide si revelar este peligro inmediatamente o dejar caer pistas y rumores discretos de fondo.
        [REGLA DE ASIGNACIÓN CRÍTICA DE MARCADORES]
        Al final de tu respuesta, debes evaluar las estadísticas del jugador. REGLA: Los datos que pongas sustituirán por completo a los anteriores. NO son incrementos, son los NUEVOS VALORES FIJOS.
        Valores actuales del jugador antes de tu turno: Vida={stats['Vida']}, Dinero={stats['Dinero']}, Mana={stats['Mana']}, EXP={stats['EXP']}, Dias={stats['Dias']}.
        Contenido actual de la Mochila: '{inventario_contenedor}'.
        AL FINAL ABSOLUTO de tu mensaje, incluye estrictamente estos tres bloques en este formato exacto:
        1. [ESTADÍSTICAS: Vida=VALOR_FINAL, Dinero=VALOR_FINAL, Mana=VALOR_FINAL, EXP=VALOR_FINAL, Dias=VALOR_FINAL]
        2. [MOCHILA: Escribe aquí la lista completa de objetos actualizados de su inventario]
        3. [MEMORIA: "Resumen corto de la trama o situación actual"].
        """

        mensajes_api = [{"role": "system", "content": prompt_sistema}]
        for msg in historial[-6:]: 
            rol_api = "user" if msg.get("rol") == "usuario" else "assistant"
            mensajes_api.append({"role": rol_api, "content": msg.get("texto", "")})

        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes_api)
        raw_res = str(completion.choices[0].message.content)
        res_narrador = raw_res
                if "[MEMORIA:" in raw_res:
            try:
                idx_ini = raw_res.index("[MEMORIA:")
                idx_fin = raw_res.index("]", idx_ini)
                lore_partida_contenedor = [raw_res[idx_ini + 9:idx_fin].replace('"', '').strip()]
                res_narrador = raw_res[:idx_ini].strip()
            except: pass

        if "[MOCHILA:" in raw_res:
            try:
                idx_ini = raw_res.index("[MOCHILA:")
                idx_fin = raw_res.index("]", idx_ini)
                inventario_contenedor = [raw_res[idx_ini + 9:idx_fin].strip()]
                if idx_ini < len(res_narrador):
                    res_narrador = raw_res[:idx_ini].strip()
            except: pass

        if "[ESTADÍSTICAS:" in raw_res:
            try:
                idx_ini = raw_res.index("[ESTADÍSTICAS:")
                idx_fin = raw_res.index("]", idx_ini)
                cambios_str = raw_res[idx_ini + 14:idx_fin].strip()
                if idx_ini < len(res_narrador):
                    res_narrador = raw_res[:idx_ini].strip()
                
                for cambio in cambios_str.split(","):
                    try:
                        clave, valor = cambio.split("=")
                        k = clave.strip()
                        v = int(valor.strip())
                        if k in stats:
                            if k == "Vida" and v > 100: v = 100
                            if k == "Mana" and v > 30: v = 30
                            stats[k] = v
                    except: pass
            except: pass

        chat_view.controls.append(cargar_bloque("ia", "Pensar", res_narrador.strip()))
        historial.append({"rol": "ia", "texto": res_narrador.strip()})
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        hora_label.value = f"⏰ Tiempo Real: {datetime.now().strftime('%H:%M')} | {'🌌 TOQUE DE QUEDA' if (20 <= datetime.now().hour or datetime.now().hour <= 6) else '☀️ BAJO EL VELO'}"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
        page.update()

    def abrir_menu_guardar(e):
        nonlocal lore_partida_contenedor, stats, historial, inventario_contenedor
        if page.data["correo_usuario"] is not None:
            db_disco = leer_disco_duro()
            db_disco[page.data["correo_usuario"]] = {"stats": stats, "historial": historial, "inventario": inventario_contenedor, "lore": lore_partida_contenedor}
            escribir_disco_duro(db_disco)
            btn_save.content.text = "✅ Guardado Real"
            btn_save.bgcolor = "#10B981"
            page.update()
        else:
            chat_view.controls.append(cargar_bloque("ia", "Pensar", "❌ Primero debes introducir tu correo electrónico en la barra inferior para poder registrar tu Grimorio."))
            page.update()

    def reiniciar(e):
        nonlocal lore_partida_contenedor, inventario_contenedor
        if page.data["correo_usuario"] is not None:
            try:
                db_disco = leer_disco_duro()
                if page.data["correo_usuario"] in db_disco:
                    del db_disco[page.data["correo_usuario"]]
                    escribir_disco_duro(db_disco)
            except: pass
            
        stats["Vida"], stats["Dinero"], stats["Mana"], stats["EXP"], stats["Dias"] = 100, 50, 30, 0, 30
        inventario_contenedor = ["Varita de Sauce, Toga Escolar"]
        historial.clear()
        page.data["correo_usuario"] = None
        input_texto.hint_text = "Introduce tu correo electrónico para empezar..."
        nueva_semilla = random.choice(semillas_amenaza_final)
        lore_partida_contenedor = [f"Amenaza de extinción oculta elegida: {nueva_semilla}"]
        chat_view.controls.clear()
        pintar_bienvenida()
        btn_save.content.text = "💾 Guardar Grimorio"
        btn_save.bgcolor = "#059669"
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
        page.update()

    btn_enviar = ft.ElevatedButton(content=ft.Text("🚀 ALTERAR EL DESTINO", color="white", weight=ft.FontWeight.BOLD), bgcolor="#6D28D9", on_click=enviar_accion, height=50)
    btn_save = ft.ElevatedButton(content=ft.Text("💾 Guardar Grimorio", color="white", weight=ft.FontWeight.BOLD), bgcolor="#059669", on_click=abrir_menu_guardar)
    btn_reset = ft.TextButton(content=ft.Text("💀 Reiniciar", color="#EF4444", weight=ft.FontWeight.BOLD), on_click=reiniciar)

    page.add(ft.Column([ft.Row([ft.Text("🧙‍♂️ CRÓNICAS DEL VELO", size=14, weight=ft.FontWeight.BOLD, color="#9333EA"), ft.Row([btn_save, btn_reset], spacing=5)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), stat_container, ft.Divider(color="#1E293B"), chat_view, ft.Divider(color="#1E293B"), modo_radio, ft.Row([input_texto, btn_enviar])], expand=True))

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
