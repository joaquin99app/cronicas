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

    # Variables de estado internas directas de la sesión actual
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

    # Variable para saber qué PIN numérico está usando este jugador actualmente
    page.data = {"pin_activo": None}

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

    # Mensaje de bienvenida inicial estándar
    def pintar_bienvenida():
        chat_view.controls.clear()
        chat_view.controls.append(cargar_bloque("ia", "Pensar", f"Detrás del ruidoso tráfico humano y los carteles de neón de la ciudad moderna, late un mundo oculto regido por la magia antigua, los estatutos del Velo Secreto y los decretos del Ministerio de Hechicería. Quedan 30 días reales antes de que la crisis actual rompa el equilibrio.\n\n[SITUACIÓN ECONÓMICA Y ENTORNO]\nHora actual: {hora_actual_real} ({estado_dia_noche}).\nTienes {stats['Dinero']}€ mágicos en tu monedero de cuero. Los callejones invisibles albergan mercados negros, armerías de varitas y boticarios clandestinos. Todo tiene un precio.\n\nSISTEMA DE RECUPERACIÓN: Si tenías una partida anterior, escribe tu PIN numérico de 3 cifras abajo en la barra y dale a enviar para recuperar tus mensajes e inventario. Si eres nuevo, escribe tu arquetipo para empezar: Mago Urbano, Detective, Cazador o Humano Despierto."))
    
    pintar_bienvenida()
        # 5. Controles inferiores
    modo_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Pensar", label="Narrar/Pensar"), ft.Radio(value="Hablar", label="Hablar")], alignment=ft.MainAxisAlignment.CENTER))
    modo_radio.value = "Pensar"
    input_texto = ft.TextField(hint_text="¿Qué dirección toma tu voluntad? (O pon tu PIN para cargar)", bgcolor="#111827", border_color="#1E293B", expand=True)

    # 6. Lógica de ejecución de la IA al pulsar el botón
    def enviar_accion(e):
        nonlocal lore_partida_contenedor, stats, historial, inventario_contenedor
        if not input_texto.value: return
        txt = input_texto.value.strip()
        mod = modo_radio.value
        input_texto.value = ""
        
        # MECÁNICA DE CARGA AUTOMÁTICA DETECTANDO CÓDIGO/PIN DE 3 NÚMEROS
        if txt.isdigit() and len(txt) == 3:
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
                page.data["pin_activo"] = txt
                
                # Reconstruir visualmente la pantalla con los mensajes viejos recuperados
                chat_view.controls.clear()
                for msg in historial:
                    chat_view.controls.append(cargar_bloque(msg.get("rol", "ia"), msg.get("modo", "Pensar"), msg.get("texto", "")))
                
                reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
                stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
                inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
                chat_view.controls.append(cargar_bloque("ia", "Pensar", f"🔮 Grimorio cargado con éxito desde el PIN [{txt}]. Tu mochila y tus mensajes históricos se han restaurado. Continúa tu andadura."))
                btn_save.content.text = f"💾 Guardar en PIN {txt}"
                page.update()
                return
            else:
                chat_view.controls.append(cargar_bloque("ia", "Pensar", f"❌ No existe ninguna partida grabada con el PIN [{txt}]. Escribe tu arquetipo para iniciar una nueva partida."))
                page.update()
                return

        # FLUJO DE JUEGO NORMAL CON LA IA
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
        Al final de tu respuesta, debes evaluar las estadísticas del jugador. REGLA: Los números que pongas en [ESTADÍSTICAS] sustituirán por completo a los anteriores. NO son incrementos, son los NUEVOS VALORES FIJOS.
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
            partes_lore = raw_res.split("[MEMORIA:")
            res_narrador = partes_lore[0]
            contenido_lore = partes_lore[1].replace("]", "").replace('"', '').strip()
            lore_partida_contenedor = [contenido_lore]

        if "[MOCHILA:" in raw_res:
            partes_inv = raw_res.split("[MOCHILA:")
            if "[MEMORIA:" not in partes_inv:
                res_narrador = partes_inv[0]
            contenido_inv = partes_inv[1].split("]")[0].strip()
            inventario_contenedor = [contenido_inv]

        if "[ESTADÍSTICAS:" in raw_res:
            partes_cambios = raw_res.split("[ESTADÍSTICAS:")
            if "[MOCHILA:" not in partes_cambios and "[MEMORIA:" not in partes_cambios:
                res_narrador = partes_cambios[0]
            
            cambios_str = partes_cambios[1].split("]")[0].strip()
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

        chat_view.controls.append(cargar_bloque("ia", "Pensar", res_narrador.strip()))
        historial.append({"rol": "ia", "texto": res_narrador.strip()})
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        hora_label.value = f"⏰ Tiempo Real: {datetime.now().strftime('%H:%M')} | {'🌌 TOQUE DE QUEDA' if (20 <= datetime.now().hour or datetime.now().hour <= 6) else '☀️ BAJO EL VELO'}"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
        page.update()

    def confirmar_pin_guardado(e):
        pin = input_pin.value.strip()
        if not pin.isdigit() or len(pin) != 3:
            input_pin.error_text = "Debe ser de 3 números"
            page.update()
            return
        db_disco = leer_disco_duro()
        db_disco[pin] = {"stats": stats, "historial": historial, "inventario": inventario_contenedor, "lore": lore_partida_contenedor}
        escribir_disco_duro(db_disco)
        page.data["pin_activo"] = pin
        page.dialog.open = False
        btn_save.content.text = f"✅ Guardado en PIN {pin}"
        btn_save.bgcolor = "#10B981"
        page.update()

    input_pin = ft.TextField(label="Inventa un PIN de 3 números (ej: 555)", password=True, max_length=3)
    dialogo_guardar = ft.AlertDialog(title=ft.Text("💾 Sellar Grimorio"), content=input_pin, actions=[ft.ElevatedButton("🔮 Grabar en Disco", on_click=confirmar_pin_guardado)])

    def abrir_menu_guardar(e):
        if page.data["pin_activo"] is not None:
            db_disco = leer_disco_duro()
            db_disco[page.data["pin_activo"]] = {"stats": stats, "historial": historial, "inventario": inventario_contenedor, "lore": lore_partida_contenedor}
            escribir_disco_duro(db_disco)
            btn_save.content.text = f"✅ Actualizado PIN {page.data['pin_activo']}"
            page.update()
        else:
            page.dialog = dialogo_guardar
            dialogo_guardar.open = True
            page.update()

    def reiniciar(e):
        nonlocal lore_partida_contenedor, inventario_contenedor
        stats["Vida"], stats["Dinero"], stats["Mana"], stats["EXP"], stats["Dias"] = 100, 50, 30, 0, 30
        inventario_contenedor = ["Varita de Sauce, Toga Escolar"]
        historial.clear()
        page.data["pin_activo"] = None
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
        
