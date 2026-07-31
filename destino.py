import flet as ft
from groq import Groq

def main(page: ft.Page):
    # 1. Configuración de pantalla estilo App Móvil Natiiva
    page.title = "🚨 Crónicas del Colapso"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # CONEXIÓN CON EL CEREBRO DE LA IA - ¡PON TU CLAVE DE GROQ AQUÍ ABAJO!
    client = Groq(api_key="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")

    # 2. Variables de estado del juego (Mecánicas adictivas)
    if "stats" not in page.session_state:
        page.session_state["stats"] = {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30}
    if "historial" not in page.session_state:
        page.session_state["historial"] = []

    s = page.session_state["stats"]
    h_lista = page.session_state["historial"]

    # 3. Componentes visuales (Marcadores superiores premium)
    reloj_label = ft.Text(f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {s['Dias']} días", color="#EF4444", weight=ft.FontWeight.BOLD, size=14)
    stats_text = ft.Text(f"❤️ {s['Vida']}%  |  💰 {s['Dinero']}€  |  🔮 {s['Mana']}/30  |  ✨ {s['EXP']}%", color="#F3F4F6", weight=ft.FontWeight.BOLD, size=15)
    
    stat_container = ft.Container(
        content=ft.Column([reloj_label, stats_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        border_radius=12,
        gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"]),
        border=ft.border.all(1, "#4C1D95")
    )

    # 4. Historial del Chat Principal (Contenedor de la historia)
    chat_view = ft.ListView(expand=True, spacing=10, height=380)
    
    # Mensaje de bienvenida inicial si el chat está vacío
    if not h_lista:
        chat_view.controls.append(ft.Container(
            content=ft.Text("🔮 Narrador: El tejido de la realidad emite un zumbido agónico. La magia se pudre en el subsuelo de la ciudad y el velo místico está a punto de desgarrarse de forma irreversible. Quedan 30 días exactos para el desmoronamiento absoluto de la trama existencial.\n\nPeligros invisibles acechan en cada esquina. Tus actos ecoarán en el futuro. Existe una remota posibilidad de revertir la degradación y salvar el mundo, pero los métodos permanecen ocultos en el misterio absoluto.\n\nManifiesta tu presencia escogiendo tu arquetipo maldito escribiéndolo abajo: Mago Urbano, Detective, Cazador o Humano Despierto.", color="#F3F4F6", size=14, font_family="Georgia"),
            padding=14, border_radius=10, bgcolor="#111827", border=ft.border.only(left=ft.BorderSide(5, "#8B5CF6"))
        ))

    # 5. Controles inferiores (Selector de modo y caja de escritura simétrica)
    modo_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Pensar", label="Narrar/Pensar"),
            ft.Radio(value="Hablar", label="Hablar")
        ], alignment=ft.MainAxisAlignment.CENTER)
    )
    modo_radio.value = "Pensar"

    input_texto = ft.TextField(hint_text="¿Qué dirección toma tu voluntad?", bgcolor="#111827", border_color="#1E293B", expand=True)

    # 6. Lógica de ejecución de la IA al pulsar el botón móvil
    def enviar_accion(e):
        if not input_texto.value:
            return
        
        texto_usuario = input_texto.value
        modo_actual = modo_radio.value
        input_texto.value = ""
        
        # Mostrar mensaje del usuario en el chat aplicando los colores de tu diseño
        if modo_actual == "Pensar":
            chat_view.controls.append(ft.Container(
                content=ft.Text(f"💭 Pensasíntesis: {texto_usuario}", color="#94A3B8", italic=True),
                padding=14, border_radius=10, bgcolor="#0F172A", border=ft.border.only(left=ft.BorderSide(5, "#38BDF8"))
            ))
        else:
            chat_view.controls.append(ft.Container(
                content=ft.Text(f"🗣️ Voz Alta: \"{texto_usuario}\"", color="#34D399", weight=ft.FontWeight.W_500),
                padding=14, border_radius=10, bgcolor="#022C22", border=ft.border.only(left=ft.BorderSide(5, "#10B981"))
            ))
        
        h_lista.append({"rol": "usuario", "texto": f"Modo: {modo_actual}. Acción: {texto_usuario}"})
        page.update()

        # Configurar prompt con las reglas de Lore Oscuro y Consecuencias futuras
        prompt_sistema = f"""
        Eres el Game Master de un RPG conversacional de terror místico y magia urbana oculta. Tu estilo debe ser denso, literario, perturbador y profundamente detallado. Escribe respuestas largas (mínimo 3 o 4 párrafos extensos).
        
        [REGLAS DE LORE Y PELIGROS CONSTANTES]
        - Todo el lore debe girar exclusivamente en torno al MUNDO MÁGICO OCULTO, sus leyes prohibidas, linajes antiguos corruptos, sectas y criaturas que se filtran en la ciudad moderna.
        - Hay PELIGROS INMINENTES acechando constantemente. En cada turno, introduce amenazas mágicas, emboscadas de entidades del velo, maldiciones latentes o NPCs traicioneros. El entorno es hostil.
        - Cada partida DEBE poseer una mitología, una causa y un síntoma de degradación mística completamente distintos creados sobre la marcha para que sea 100% procedural.
        
        [SISTEMA DE EVENTOS Y LIBERTAD TOTAL]
        - Genera constantemente eventos imprevistos de todo tipo (rituales callejeros clandestinos, mercados negros espirituales, anomalías temporales). El jugador puede abordar estos eventos como desee o ignorarlos libremente.
        
        [MECÁNICA OCULTA: SALVAR EL MUNDO Y CONSECUENCIAS]
        - Absolutamente TODO lo que el jugador hace tiene consecuencias a largo plazo. Recuerda las decisiones del historial para cobrárselas o recompensarle en el futuro de forma lógica y retorcida.
        - El mundo PUEDE SER SALVADO de los {s['Dias']} días restantes. Sin embargo, el juego NUNCA debe explicarle cómo hacerlo. Solo si el jugador realiza acciones extraordinariamente complejas, descifra misterios prohibidos o estabiliza nexos mágicos, la situación mejorará.
        
        Datos actuales del jugador: Vida={s['Vida']}, Dinero={s['Dinero']}, Mana={s['Mana']}. Días restantes: {s['Dias']}.
        Modo actual: '{modo_actual}'. Reacciona de forma diferente si el jugador está pensando o hablando en voz alta.
        
        AL FINAL ABSOLUTO de tu mensaje, incluye esta estructura exacta para modificar los números y el tiempo del juego:
        [CAMBIOS: Vida=X, Dinero=X, Mana=X, EXP=X, Dias=X]. Si no hay variaciones, escribe obligatoriamente [CAMBIOS: Ninguno].
        """

        mensajes_api = [{"role": "system", "content": prompt_sistema}]
        for msg in h_lista[-6:]:
            mensajes_api.append({"role": "user" if msg["rol"] == "usuario" else "assistant", "content": msg["texto"]})

        # Llamada a Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api
        )
        respuesta_ia = completion.choices[0].message.content

        # Procesamiento seguro de estadísticas y días del apocalipsis
        if "[CAMBIOS:" in respuesta_ia:
            partes = respuesta_ia.split("[CAMBIOS:")
            texto_limpio = partes[0]
            cambios_str = partes[1].replace("]", "").strip()
            
            if "Ninguno" not in cambios_str:
                for cambio in cambios_str.split(","):
                    try:
                        clave, valor = cambio.split("=")
                        k = clave.strip()
                        v = int(valor.strip())
                        if k == "Dias":
                            s["Dias"] += v
                        else:
                            s[k] += v
                    except:
                        pass
            respuesta_ia = texto_limpio

        # Actualizar textos de los marcadores móviles superiores
        reloj_label.value = f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {s['Dias']} días"
        stats_text.value = f"❤️ {s['Vida']}%  |  💰 {s['Dinero']}€  |  🔮 {s['Mana']}/30  |  ✨ {s['EXP']}%"

        # Mostrar respuesta del Narrador en el chat móvil
        chat_view.controls.append(ft.Container(
            content=ft.Text(f"🔮 Narrador: {respuesta_ia}", color="#F3F4F6", font_family="Georgia"),
            padding=14, border_radius=10, bgcolor="#111827", border=ft.border.only(left=ft.BorderSide(5, "#8B5CF6"))
        ))
        
        h_lista.append({"rol": "ia", "texto": respuesta_ia})
        page.update()

    btn_enviar = ft.ElevatedButton(
        text="🚀 ALTERAR EL DESTINO",
        bgcolor="#6D28D9",
        color="white",
        on_click=enviar_accion,
        height=50
    )

    # Añadir todos los componentes a la vista de la App Móvil
    page.add(
        ft.Column([
            ft.Text("🧙‍♂️ CRÓNICAS DEL COLAPSO", size=22, weight=ft.FontWeight.BOLD, color="#9333EA", text_align=ft.TextAlign.CENTER),
            stat_container,
            ft.Divider(color="#1E293B"),
            chat_view,
            ft.Divider(color="#1E293B"),
            modo_radio,
            ft.Row([input_texto, btn_enviar])
        ], expand=True)
    )

# Lanzar en formato Web adaptado a pantallas móviles automáticamente
# Forzar la ruta raíz para servidores de internet
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)


