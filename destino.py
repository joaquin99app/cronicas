import flet as ft
from groq import Groq
import json

def main(page: ft.Page):
    # 1. Configuración de pantalla estilo App Móvil
    page.title = "🚨 Crónicas del Colapso"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Conexión con la IA usando la variable segura de Render
    import os
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # 2. SISTEMA DE GUARDADO PERSISTENTE Y PROCEDURAL
    stats = {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30}
    historial = []
    lore_procedural = {"mitologia_partida": "Pendiente de generación inicial por la IA"}

    saved_stats = page.client_storage.get("rpg_stats")
    saved_history = page.client_storage.get("rpg_historial")
    saved_lore = page.client_storage.get("rpg_lore_procedural")

    if saved_stats:
        try: stats = json.loads(saved_stats)
        except: pass
    if saved_history:
        try: historial = json.loads(saved_history)
        except: pass
    if saved_lore:
        try: lore_procedural = json.loads(saved_lore)
        except: pass

    # 3. Componentes visuales (Marcadores superiores premium)
    reloj_label = ft.Text(f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {stats['Dias']} días", color="#EF4444", weight=ft.FontWeight.BOLD, size=14)
    stats_text = ft.Text(f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%", color="#F3F4F6", weight=ft.FontWeight.BOLD, size=15)
    
    stat_container = ft.Container(
        content=ft.Column([reloj_label, stats_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15, border_radius=12, gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"]), border=ft.border.all(1, "#4C1D95")
    )

    # 4. Historial del Chat Principal
    chat_view = ft.ListView(expand=True, spacing=10, height=360)
    
    def cargar_bloque_chat(rol, modo, texto):
        if rol == "usuario":
            if modo == "Pensar":
                return ft.Container(
                    content=ft.Text(f"💭 Pensasíntesis: {texto}", color="#94A3B8", italic=True),
                    padding=14, border_radius=10, bgcolor="#0F172A", border=ft.border.only(left=ft.BorderSide(5, "#38BDF8"))
                )
            else:
                return ft.Container(
                    content=ft.Text(f"🗣️ Voz Alta: \"{texto}\"", color="#34D399", weight=ft.FontWeight.W_500),
                    padding=14, border_radius=10, bgcolor="#022C22", border=ft.border.only(left=ft.BorderSide(5, "#10B981"))
                )
        else:
            return ft.Container(
                content=ft.Text(f"🔮 Narrador: {texto}", color="#F3F4F6", font_family="Georgia"),
                padding=14, border_radius=10, bgcolor="#111827", border=ft.border.only(left=ft.BorderSide(5, "#8B5CF6"))
            )

    if not historial:
        chat_view.controls.append(ft.Container(
            content=ft.Text("🔮 Narrador: El tejido de la realidad emite un zumbido agónico. La magia se pudre en el subsuelo de la ciudad y el velo místico está a punto de desgarrarse de forma irreversible. Quedan 30 días exactos para el desmoronamiento absoluto de la trama existencial.\n\nPeligros invisibles acechan en cada esquina. Tus actos ecoarán en el futuro. Existe una remota posibilidad de revertir la degradación y salvar el mundo, pero los métodos permanecen ocultos en el misterio absoluto.\n\nManifiesta tu presencia escogiendo tu arquetipo maldito escribiéndolo abajo: Mago Urbano, Detective, Cazador o Humano Despierto.", color="#F3F4F6", size=14, font_family="Georgia"),
            padding=14, border_radius=10, bgcolor="#111827", border=ft.border.only(left=ft.BorderSide(5, "#8B5CF6"))
        ))
    else:
        for msg in historial:
            chat_view.controls.append(cargar_bloque_chat(msg["rol"], msg.get("modo", "Pensar"), msg["texto"]))
    # 5. Controles inferiores (Selector de modo y caja de escritura)
    modo_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Pensar", label="Narrar/Pensar"),
            ft.Radio(value="Hablar", label="Hablar")
        ], alignment=ft.MainAxisAlignment.CENTER)
    )
    modo_radio.value = "Pensar"

    input_texto = ft.TextField(hint_text="¿Qué dirección toma tu voluntad?", bgcolor="#111827", border_color="#1E293B", expand=True)

    # 6. Lógica de ejecución de la IA y guardado
    def enviar_accion(e):
        if not input_texto.value:
            return
        
        texto_usuario = input_texto.value
        modo_actual = modo_radio.value
        input_texto.value = ""
        
        chat_view.controls.append(cargar_bloque_chat("usuario", modo_actual, texto_usuario))
        historial.append({"rol": "usuario", "modo": modo_actual, "texto": texto_usuario})
        page.update()

        prompt_sistema = f"""
        Eres el Game Master de un RPG conversacional de terror místico y magia urbana oculta. Tu estilo debe ser denso, literario, perturbador y profundamenteax detallado. Escribe respuestas largas.
        [MEMORIA PROCEDURAL DE ESTA PARTIDA CONCRETA]
        Debes ceñirte estrictamente a la mitología y eventos establecidos de esta sesión:
        {json.dumps(lore_procedural)}
        Si esta es la primera acción, INVENTA una mitología, una causa y un síntoma de degradación mística único para esta partida y descrébela.
        [REGLAS]
        Todo el lore gira en torno al MUNDO MÁGICO OCULTO. Hay peligros acechando constantemente. Genera eventos imprevistos que el jugador puede abordar o ignorar libremente. Todo lo que hace tiene consecuencias a largo plazo.
        El mundo PUEDE SER SALVADO de los {stats['Dias']} días restantes si el jugador hace cosas extraordinariamente complejas, pero nunca se lo expliques.
        Datos actuales: Vida={stats['Vida']}, Dinero={stats['Dinero']}, Mana={stats['Mana']}. Días restantes: {stats['Dias']}.
        Modo actual: '{modo_actual}'. Reacciona diferente si piensa o habla en voz alta.
        AL FINAL ABSOLUTO, incluye obligatoriamente:
        1. [CAMBIOS: Vida=X, Dinero=X, Mana=X, EXP=X, Dias=X] (O [CAMBIOS: Ninguno]).
        2. [MEMORIA: "Resumen corto en una frase de la mitología o situación actual"].
        """

        mensajes_api = [{"role": "system", "content": prompt_sistema}]
        for msg in historial[-6:]:
            mensajes_api.append({"role": "user" if msg["rol"] == "usuario" else "assistant", "content": msg["texto"]})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_api
        )
        respuesta_ia = completion.choices.message.content

        if "[MEMORIA:" in respuesta_ia:
            partes_lore = respuesta_ia.split("[MEMORIA:")
            texto_sin_lore = partes_lore
            contenido_lore = partes_lore.replace("]", "").replace('"', '').strip()
            lore_procedural["mitologia_partida"] = contenido_lore
            respuesta_ia = texto_sin_lore

        if "[CAMBIOS:" in respuesta_ia:
            partes = respuesta_ia.split("[CAMBIOS:")
            texto_limpio = partes
            cambios_str = partes.replace("]", "").strip()
            if "Ninguno" not in cambios_str:
                for cambio in cambios_str.split(","):
                    try:
                        clave, valor = cambio.split("=")
                        k = clave.strip()
                        v = int(valor.strip())
                        if k == "Dias": stats["Dias"] += v
                        else: stats[k] += v
                    except: pass
            respuesta_ia = texto_limpio

        chat_view.controls.append(cargar_bloque_chat("ia", "Pensar", respuesta_ia))
        historial.append({"rol": "ia", "texto": respuesta_ia})

        page.client_storage.set("rpg_stats", json.dumps(stats))
        page.client_storage.set("rpg_historial", json.dumps(historial))
        page.client_storage.set("rpg_lore_procedural", json.dumps(lore_procedural))

        reloj_label.value = f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {stats['Dias']} días"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        page.update()

    def reiniciar_partida(e):
        page.client_storage.remove("rpg_stats")
        page.client_storage.remove("rpg_historial")
        page.client_storage.remove("rpg_lore_procedural")
        page.window_reload()

    btn_enviar = ft.ElevatedButton(text="🚀 ALTERAR EL DESTINO", bgcolor="#6D28D9", color="white", on_click=enviar_accion, height=50)
    btn_reset = ft.TextButton(text="💀 Reiniciar", icon=ft.icons.DELETE_FOREVER, icon_color="#EF4444", style=ft.ButtonStyle(color="#EF4444"), on_click=reiniciar_partida)

    page.add(
        ft.Column([
            ft.Row([ft.Text("🧙‍♂️ CRÓNICAS DEL COLAPSO", size=18, weight=ft.FontWeight.BOLD, color="#9333EA"), btn_reset], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            stat_container, ft.Divider(color="#1E293B"), chat_view, ft.Divider(color="#1E293B"), modo_radio, ft.Row([input_texto, btn_enviar])
        ], expand=True)
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)


