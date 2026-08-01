import flet as ft
from groq import Groq
import os
import random
from datetime import datetime

# BASE DE DATOS BLINDADA EN EL SERVIDOR (Almacena las partidas por usuario de forma limpia)
SERVIDOR_PARTIDAS = {}

def main(page: ft.Page):
    # 1. Configuración de pantalla estilo App Móvil Premium
    page.title = "🚨 Crónicas del Velo Mágico"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Conexión segura con la IA de Groq en Render
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Identificador único de red por pestaña
    if not hasattr(page, "_id_sesion_segura"):
        page._id_sesion_segura = str(random.randint(100000, 999999))
    
    id_id = page._id_sesion_segura

    # Catálogo de amenazas límite para los 30 días reales
    semillas_amenaza_final = [
        "El motor de transmutación del Ministerio de Magia ha sido infectado por una maldición de óxido eterno que disuelve el maná de la ciudad.",
        "Una secta de licántropos y magos oscuros está preparando el despertar de un dragón mitológico sepultado bajo los cimientos urbanos.",
        "Un brote de 'estática mística' se está filtrando a través de la red eléctrica, borrando los recuerdos de los hechiceros y exponiendo el velo.",
        "El Reloj de Arena Ancestral que mantiene la barrera de invisibilidad frente a los humanos mundanos ha sido agrietado en un sabotaje interno.",
        "Un antiguo linaje de vampiros puros está comprando los nexos de sangre de las alcantarillas para desatar una plaga mística purificadora."
    ]

    # Inicializar partida en la memoria de Python si el usuario es nuevo
    if id_id not in SERVIDOR_PARTIDAS:
        semilla_inicial = random.choice(semillas_amenaza_final)
        SERVIDOR_PARTIDAS[id_id] = {
            "stats": {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30},
            "historial": [],
            "lore": [f"Amenaza de extinción oculta elegida: {semilla_inicial}"]
        }

    stats = SERVIDOR_PARTIDAS[id_id]["stats"]
    historial = SERVIDOR_PARTIDAS[id_id]["historial"]
    lore_partida_contenedor = SERVIDOR_PARTIDAS[id_id]["lore"]

    # Obtener el ciclo horario de 24 horas reales
    hora_actual_real = datetime.now().strftime("%H:%M")
    es_de_noche = 20 <= datetime.now().hour or datetime.now().hour <= 6
    estado_dia_noche = "🌌 TOQUE DE QUEDA (El velo es frágil, criaturas en los callejones, patrullas del Ministerio)" if es_de_noche else "☀️ BAJO EL VELO (La magia se esconde de los humanos, mercados mágicos abiertos, tabernas activas)"

    # 3. Componentes visuales superiores unificados
    reloj_label = ft.Text(f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo", color="#A78BFA", weight=ft.FontWeight.BOLD, size=14)
    hora_label = ft.Text(f"⏰ Tiempo Real: {hora_actual_real} | {estado_dia_noche}", color="#38BDF8", size=12, weight=ft.FontWeight.W_500)
    stats_text = ft.Text(f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%", color="#F3F4F6", weight=ft.FontWeight.BOLD, size=15)
    
    stat_container = ft.Container(
        content=ft.Column([reloj_label, hora_label, stats_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), 
        padding=15, border_radius=12, gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"])
    )

    # 4. Historial del Chat Principal
    chat_view = ft.ListView(expand=True, spacing=10, height=380)
    
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

    # Mensaje de bienvenida inicial de Fantasía Urbana Comercial
    if not historial:
        chat_view.controls.append(cargar_bloque("ia", "Pensar", f"Detrás del ruidoso tráfico humano y los carteles de neón de la ciudad moderna, late un mundo oculto regido por la magia antigua, los estatutos del Velo Secreto y los decretos del Ministerio de Hechicería. Quedan 30 días reales antes de que la crisis actual rompa el equilibrio.\n\n[SITUACIÓN ECONÓMICA Y ENTORNO]\nHora actual: {hora_actual_real} ({estado_dia_noche}).\nTienes {stats['Dinero']}€ mágicos en tu monedero de cuero. Los callejones invisibles albergan mercados negros, armerías de varitas, boticarios de maná y tabernas oscuras llenas de secretos. Todo tiene un precio, y nadie regala nada.\n\nElige tu arquetipo místico escribiéndolo abajo para adentrarte en el mapa abierto: Mago Urbano, Detective, Cazador o Humano Despierto."))
    else:
        for msg in historial:
            chat_view.controls.append(cargar_bloque(msg["rol"], msg.get("modo", "Pensar"), msg["texto"]))
    # 5. Controles inferiores
    modo_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Pensar", label="Narrar/Pensar"), ft.Radio(value="Hablar", label="Hablar")], alignment=ft.MainAxisAlignment.CENTER))
    modo_radio.value = "Pensar"
    input_texto = ft.TextField(hint_text="¿Qué dirección toma tu voluntad?", bgcolor="#111827", border_color="#1E293B", expand=True)

    # 6. Lógica de ejecución de la IA al pulsar el botón
    def enviar_accion(e):
        nonlocal lore_partida_contenedor
        if not input_texto.value: return
        txt = input_texto.value
        mod = modo_radio.value
        input_texto.value = ""
        
        chat_view.controls.append(cargar_bloque("usuario", mod, txt))
        historial.append({"rol": "usuario", "modo": mod, "texto": txt})
        page.update()

        hora_envio = datetime.now().strftime("%H:%M")
        es_noche_envio = 20 <= datetime.now().hour or datetime.now().hour <= 6

        prompt_sistema = f"""
        Actúa como el Game Master de un RPG conversacional de Fantasía Urbana Contemporánea (estilo el mundo oculto de Harry Potter o Cazadores de Sombras, pero adulto, realista y cruel). Tu estilo es denso, literario y profundamente descriptivo.
        
        [SISTEMA ECONÓMICO REAL Y COMERCIO PROFUNDO]
        - Gestionas una economía estricta. Todo tiene un precio real en Euros (€). No regales estadísticas ni dinero porque sí; ganar dinero debe ser difícil (trabajos para el Ministerio, venta de reliquias saqueadas, apuestas de duelos).
        - Despliega un abanico inmenso de TIENDAS MÍSTICAS según donde vaya el jugador: Armerías de varitas/runas, boticarios clandestinos de pociones de maná/vida, mercados negros de reliquias, tabernas mágicas (donde comprar comida/bebida o pagar habitaciones para curarse), o casas de empeño de almas (dinero a cambio de bajar su Vida Máxima).
        - Si el jugador compra un objeto, ponle un precio lógico detallado en el diálogo (ej: una Poción de Maná cuesta 15€, una Varita Rúnica nueva cuesta 45€).
        
        [RITMO DE APOCALIPSIS VARIABLE]
        La gran amenaza final que destruirá el Velo a los 30 días es: '{lore_partida_contenedor}'. Decide libremente si destapar este peligro ahora o mantener la calma mística ordinaria dejando caer rumores discretos en las tiendas o tabernas.
        
        [MUNDO ABIERTO Y CICLO HORARIO]
        La hora real es exactamente las {hora_envio}. Si es de noche ({es_noche_envio}), los mercados negros abren y las criaturas de los callejones son letales. Si el jugador ignora una tienda o rechaza una misión, acéptalo de inmediato y narra cómo el mundo sigue girando sin él.
        
        [REGLA DE ASIGNACIÓN CRÍTICA DE MARCADORES]
        Al final de tu respuesta, debes evaluar las estadísticas del jugador. REGLA: Los números que pongas en [ESTADÍSTICAS] sustituirán por completo a los anteriores. NO son incrementos, son los NUEVOS VALORES FIJOS. No los subas sin sentido. Si compra algo, resta el dinero. Si sufre daño, baja la vida.
        Valores actuales del jugador antes de tu turno: Vida={stats['Vida']}, Dinero={stats['Dinero']}, Mana={stats['Mana']}, EXP={stats['EXP']}, Dias={stats['Dias']}.
        
        AL FINAL ABSOLUTO de tu mensaje, incluye estrictamente estos dos bloques en este formato exacto:
        1. [ESTADÍSTICAS: Vida=VALOR_FINAL, Dinero=VALOR_FINAL, Mana=VALOR_FINAL, EXP=VALOR_FINAL, Dias=VALOR_FINAL]
        2. [MEMORIA: "Resumen corto de la trama, inventario actual del jugador o situación"].
        """

        mensajes = [{"role": "system", "content": prompt_sistema}]
        for msg in historial[-6:]: 
            mensajes.append({"role": "user" if msg["rol"] == "usuario" else "assistant", "content": msg["texto"]})

        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes)
        res = completion.choices[0].message.content

        if "[MEMORIA:" in res:
            p_lore = res.split("[MEMORIA:")
            res = p_lore[0]
            lore_partida_contenedor = [p_lore[1].replace("]", "").replace('"', '').strip()]

        # PROCESADOR SEGURO DE ASIGNACIÓN FIJA DE MARCADORES ECONOMÍA
        if "[ESTADÍSTICAS:" in res:
            p_cambios = res.split("[ESTADÍSTICAS:")
            cambios_str = p_cambios[1].replace("]", "").strip()
            res = p_cambios[0]
            for cambio in cambios_str.split(","):
                try:
                    clave, valor = cambio.split("=")
                    k = clave.strip()
                    v = int(valor.strip())
                    # Limitadores lógicos para evitar desbordamientos
                    if k in stats:
                        if k == "Vida" and v > 100: v = 100
                        if k == "Mana" and v > 30: v = 30
                        stats[k] = v
                except: pass

        # Guardar estado actualizado en el diccionario seguro de Python
        SERVIDOR_PARTIDAS[id_id] = {
            "stats": stats,
            "historial": historial,
            "lore": lore_partida_contenedor
        }

        chat_view.controls.append(cargar_bloque("ia", "Pensar", res))
        historial.append({"rol": "ia", "texto": res})
        
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        hora_label.value = f"⏰ Tiempo Real: {datetime.now().strftime('%H('%M')} | {'🌌 TOQUE DE QUEDA' if (20 <= datetime.now().hour or datetime.now().hour <= 6) else '☀️ BAJO EL VELO'}"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        page.update()

    def reiniciar(e):
        nonlocal lore_partida_contenedor
        stats["Vida"] = 100
        stats["Dinero"] = 50
        stats["Mana"] = 30
        stats["EXP"] = 0
        stats["Dias"] = 30
        historial.clear()
        
        nueva_semilla = random.choice(semillas_amenaza_final)
        lore_partida_contenedor = [f"Amenaza de extinción oculta elegida: {nueva_semilla}"]
        
        SERVIDOR_PARTIDAS[id_id] = {
            "stats": stats,
            "historial": historial,
            "lore": lore_partida_contenedor
        }
        
        chat_view.controls.clear()
        chat_view.controls.append(cargar_bloque("ia", "Pensar", f"Detrás del ruidoso tráfico humano y los carteles de neón de la ciudad moderna, late un mundo oculto regido por la magia antigua, los estatutos del Velo Secreto y los decretos del Ministerio de Hechicería. Quedan 30 días reales de estabilidad existencial antes de que un desastre irreversible arrastre este mundo al olvido.\n\n[SITUACIÓN ECONÓMICA Y ENTORNO]\nHora actual: {datetime.now().strftime('%H:%M')} . Los callejones invisibles albergan mercados negros, armerías de varitas, boticarios de maná y tabernas oscuras llenas de secretos. Todo tiene un precio.\n\nElige tu arquetipo maldito escribiéndolo abajo: Mago Urbano, Detective, Cazador o Humano Despierto."))
        
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        page.update()

    btn_enviar = ft.ElevatedButton(
        content=ft.Text("🚀 ALTERAR EL DESTINO", color="white", weight=ft.FontWeight.BOLD),
        bgcolor="#6D28D9", on_click=enviar_accion, height=50
    )
    
    btn_reset = ft.TextButton(
        content=ft.Text("💀 Forzar Reinicio Absoluto", color="#EF4444", weight=ft.FontWeight.BOLD), on_click=reiniciar
    )

    page.add(
        ft.Column([
            ft.Row([ft.Text("🧙‍♂️ CRÓNICAS DEL VELO", size=15, weight=ft.FontWeight.BOLD, color="#9333EA"), btn_reset], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
            stat_container, ft.Divider(color="#1E293B"), chat_view, ft.Divider(color="#1E293B"), modo_radio, ft.Row([input_texto, btn_enviar])
        ], expand=True)
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
