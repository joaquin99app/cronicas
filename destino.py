import flet as ft
from groq import Groq
import os
import random
from datetime import datetime

def main(page: ft.Page):
    # 1. Configuración de pantalla estilo App Móvil Premium
    page.title = "🚨 Crónicas del Velo Mágico"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Conexión segura con la IA de Groq en Render
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # 2. Variables de estado directas de la partida (Reiniciables de forma segura)
    stats = {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30}
    historial = []
    
    # Semillas de amenazas que significan el fin de la comunidad mágica a los 30 días
    semillas_amenaza_final = [
        "El motor de transmutación del Ministerio de Magia ha sido infectado por una maldición de óxido eterno que disuelve el maná de la ciudad.",
        "Una secta de licántropos y magos oscuros está preparando el despertar de un dragón mitológico sepultado bajo los cimientos urbanos.",
        "Un brote de 'estática mística' se está filtrando a través de la red eléctrica, borrando los recuerdos de los hechiceros y exponiendo el velo.",
        "El Reloj de Arena Ancestral que mantiene la barrera de invisibilidad frente a los humanos mundanos ha sido agrietado en un sabotaje interno.",
        "Un antiguo linaje de vampiros puros está comprando los nexos de sangre de las alcantarillas para desatar una plaga mística purificadora."
    ]
    semilla_actual = [random.choice(semillas_amenaza_final)]
    lore_partida_contenedor = [f"Amenaza de extinción oculta elegida: {semilla_actual}"]

    # OBTENER LA HORA REAL DE LA PARTIDA (Ciclo 24 horas reales)
    hora_actual_real = datetime.now().strftime("%H:%M")
    es_de_noche = 20 <= datetime.now().hour or datetime.now().hour <= 6
    estado_dia_noche = "🌌 TOQUE DE QUEDA (El velo es frágil, criaturas en los callejones, patrullas del Ministerio)" if es_de_noche else "☀️ BAJO EL VELO (La magia se esconde de los humanos, mercados mágicos abiertos, tabernas activas)"

    # 3. Componentes visuales superiores
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

    # Mensaje de bienvenida inicial
    chat_view.controls.append(cargar_bloque("ia", "Pensar", f"Detrás del ruidoso tráfico humano y los carteles de neón de la ciudad moderna, late un mundo oculto regido por la magia antigua, los estatutos del Velo Secreto y los decretos del Ministerio de Hechicería. Quedan 30 días reales de estabilidad existencial antes de que un desastre irreversible arrastre este mundo al olvido.\n\n[ENTORNO REAL DEL VELO]\nHora actual del dispositivo: {hora_actual_real}.\nEstado del entorno: {estado_dia_noche}.\n\nEste es un mundo abierto repleto de misterios, reliquias, tabernas mágicas escondidas y peligros. Si rechazas un camino, la historia avanzará por su cuenta sin esperarte. Elige tu arquetipo maldito: Mago Urbano, Detective, Cazador o Humano Despierto."))
    # 5. Controles inferiores
    modo_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Pensar", label="Narrar/Pensar"), ft.Radio(value="Hablar", label="Hablar")], alignment=ft.MainAxisAlignment.CENTER))
    modo_radio.value = "Pensar"
    input_texto = ft.TextField(hint_text="¿Qué dirección toma tu voluntad?", bgcolor="#111827", border_color="#1E293B", expand=True)

    # 6. Lógica de ejecución de la IA al pulsar el botón
    def enviar_accion(e):
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
        Actúa como el Game Master de un RPG conversacional de Fantasía Urbana Contemporánea (estilo el mundo oculto tras la sociedad de Harry Potter, Percy Jackson o Cazadores de Sombras, pero con una identidad totalmente original, madura y detallada). Tu estilo debe ser denso, literario, inmersivo, descriptivo y centrado en la magia.
        [REGLAS DEL MUNDO MÁGICO OCULTO]
        - Todo el lore debe centrarse exclusivamente en la magia: hechizos, pociones, varitas, tiendas ocultas tras fachadas humanas, ministerios mágicos burocráticos y linajes antiguos. 
        - Hay peligros constantes (fugas de criaturas, maldiciones antiguas, magos renegados corruptos, patrullas del ministerio). El entorno es reactivo.
        [MECÁNICA ADICTIVA: RITMO DE APOCALIPSIS VARIABLE]
        - El peligro cataclísmico inminente que destruirá el mundo al llegar el día 0 es exactamente este: '{lore_partida_contenedor}'.
        - REGLA DE RITMO EN ESTA PARTIDA: Decide de forma invisible mediante la IA si revelar este peligro inmediatamente o no. 
        - OPCIÓN 1: Muéstralo abiertamente desde el principio en tu respuesta si el jugador toma una acción relevante.
        - OPCIÓN 2: Mantén la ciudad en una aparente 'normalidad mágica ordinaria'. Comienza a formar el problema poco a poco de fondo. Deja caer pistas sutiles en los primeros turnos (rumores lejanos, noticias raras en los diarios mágicos, nerviosismo en las tiendas de varitas). Tras 3 o 4 mensajes del jugador, empieza a informarle formalmente de la magnitud de la amenaza que se le viene encima.
        [TIEMPO REAL DE 24 HORAS Y UBICACIÓN]
        - La hora real en el mundo del jugador es exactamente las {hora_envio}. 
        - Si es de NOCHE ({es_noche_envio}), los peligros se vuelven más físicos y agresivos en las calles. Si es de DÍA, la comunidad mágica actúa con extrema cautela para no ser descubierta por los humanos ordinarios (muggles/mundanos).
        - El peligro y las misiones secundarias cambian drásticamente según la UBICACIÓN. Introduce constantemente tanto peligros de la trama principal como amenazas o encuentros SECUNDARIOS COMPLETAMENTE ALEATORIOS (comerciantes excéntricos, duendes ladrones, duelos de varitas callejeros).
        [REGLA DE MUNDO ABIERTO REAL]
        El jugador tiene libre albedrío total. Si decide ignorar la amenaza, rechazar misiones o irse a una taberna mística a pasar de todo, ACEPTA su decisión de inmediato. No le insistas ni le obligues a volver. Describe cómo la conspiración apocalíptica oculta avanza por su cuenta de fondo, restando o sumando días en el marcador según el caos generado.
        Datos actuales del jugador: Vida={stats['Vida']}, Dinero={stats['Dinero']}, Mana={stats['Mana']}. Días restantes: {stats['Dias']}.
        Modo actual: '{mod}'. Reacciona diferente si piensa o habla en voz alta.
        AL FINAL ABSOLUTO de tu mensaje, incluye estrictamente estos dos bloques en este formato exacto:
        1. [CAMBIOS: Vida=X, Dinero=X, Mana=X, EXP=X, Dias=X] (O [CAMBIOS: Ninguno]).
        2. [MEMORIA: "Resumen corto de la trama, sospechosos descubiertos o situación actual"].
        """

        mensajes = [{"role": "system", "content": prompt_sistema}]
        for msg in historial[-6:]: 
            mensajes.append({"role": "user" if msg["rol"] == "usuario" else "assistant", "content": msg["texto"]})

        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes)
        res = completion.choices.message.content

        if "[MEMORIA:" in res:
            p_lore = res.split("[MEMORIA:")
            res = p_lore
            lore_partida_contenedor = [p_lore.replace("]", "").replace('"', '').strip()]

        if "[CAMBIOS:" in res:
            p_cambios = res.split("[CAMBIOS:")
            cambios_str = p_cambios.replace("]", "").strip()
            res = p_cambios
            if "Ninguno" not in cambios_str:
                for cambio in cambios_str.split(","):
                    try:
                        clave, valor = cambio.split("=")
                        k = clave.strip()
                        v = int(valor.strip())
                        if k == "Dias": stats["Dias"] += v
                        else: stats[k] = stats.get(k, 100) + v
                    except: pass

        chat_view.controls.append(cargar_bloque("ia", "Pensar", res))
        historial.append({"rol": "ia", "texto": res})
        
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        hora_label.value = f"⏰ Tiempo Real: {datetime.now().strftime('%H:%M')} | {'🌌 TOQUE DE QUEDA' if (20 <= datetime.now().hour or datetime.now().hour <= 6) else '☀️ BAJO EL VELO'}"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        page.update()

    def reiniciar(e):
        stats["Vida"] = 100
        stats["Dinero"] = 50
        stats["Mana"] = 30
        stats["EXP"] = 0
        stats["Dias"] = 30
        historial.clear()
        nueva_semilla = random.choice(semillas_amenaza_final)
        lore_partida_contenedor = [f"Amenaza de extinción oculta elegida: {nueva_semilla}"]
        
        chat_view.controls.clear()
        chat_view.controls.append(cargar_bloque("ia", "Pensar", f"Detrás del ruidoso tráfico humano y los carteles de neón de la ciudad moderna, late un mundo oculto regido por la magia antigua, los estatutos del Velo Secreto y los decretos del Ministerio de Hechicería. Quedan 30 días reales de estabilidad existencial antes de que un desastre irreversible arrastre este mundo al olvido.\n\n[ENTORNO REAL DEL VELO]\nHora actual del dispositivo: {datetime.now().strftime('%H:%M')}.\nEstado del entorno: {'🌌 TOQUE DE QUEDA' if (20 <= datetime.now().hour or datetime.now().hour <= 6) else '☀️ BAJO EL VELO'}.\n\nEste es un mundo abierto repleto de misterios, reliquias, tabernas mágicas escondidas y peligros. Si rechazas un camino, la historia avanzará por su cuenta sin esperarte. Elige tu arquetipo maldito: Mago Urbano, Detective, Cazador o Humano Despierto."))
        
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
