import flet as ft
from groq import Groq
import os

def main(page: ft.Page):
    # 1. Configuración de pantalla estilo App Móvil
    page.title = "🚨 Crónicas del Colapso"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Conexión segura con la IA de Groq en Render
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # 2. Variables de estado directas de la partida
    stats = {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30}
    historial = []
    lore_partida = ["Pendiente de generación inicial"]

    # 3. Componentes visuales superiores
    reloj_label = ft.Text(f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {stats['Dias']} días", color="#EF4444", weight=ft.FontWeight.BOLD, size=14)
    stats_text = ft.Text(f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%", color="#F3F4F6", weight=ft.FontWeight.BOLD, size=15)
    stat_container = ft.Container(content=ft.Column([reloj_label, stats_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=15, border_radius=12, gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"]), border=ft.border.all(1, "#4C1D95"))

    # 4. Historial del Chat Principal
    chat_view = ft.ListView(expand=True, spacing=10, height=380)
    
    def cargar_bloque(rol, modo, texto):
        if rol == "usuario":
            bg = "#0F172A" if modo == "Pensar" else "#022C22"
            col = "#38BDF8" if modo == "Pensar" else "#10B981"
            lbl = "💭 Pensasíntesis: " if modo == "Pensar" else "🗣️ Voz Alta: "
            return ft.Container(content=ft.Text(f"{lbl}{texto}", color="#94A3B8" if modo == "Pensar" else "#34D399", italic=(modo=="Pensar")), padding=14, border_radius=10, bgcolor=bg, border=ft.border.only(left=ft.BorderSide(5, col)))
        return ft.Container(content=ft.Text(f"🔮 Narrador: {texto}", color="#F3F4F6", font_family="Georgia"), padding=14, border_radius=10, bgcolor="#111827", border=ft.border.only(left=ft.BorderSide(5, "#8B5CF6")))

    # Mensaje de bienvenida inicial
    chat_view.controls.append(cargar_bloque("ia", "Pensar", "El tejido de la realidad emite un zumbido agónico. La magia se pudre en el subsuelo de la ciudad y el velo místico está a punto de desgarrarse de forma irreversible. Quedan 30 días exactos para el desmoronamiento absoluto de la trama existencial.\n\nPeligros invisibles acechan en cada esquina. Tus actos ecoarán en el futuro. Existe una remota posibilidad de revertir la degradación y salvar el mundo, pero los métodos permanecen ocultos en el misterio absoluto.\n\nManifiesta tu presencia escogiendo tu arquetipo maldito escribiéndolo abajo: Mago Urbano, Detective, Cazador o Humano Despierto."))

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

        prompt_sistema = f"""
        Eres el Game Master de un RPG conversacional de terror místico y magia urbana oculta. Tu estilo debe ser denso, literario, perturbador y profundamente detallado. Escribe respuestas largas.
        Todo el lore debe girar en torno al MUNDO MÁGICO OCULTO. Hay peligros acechando constantemente. Genera eventos imprevistos que el jugador puede abordar o ignorar libremente. Todo lo que hace tiene consecuencias futuras.
        El mundo PUEDE SER SALVADO de los {stats['Dias']} días restantes si el jugador hace cosas extraordinariamente complejas, pero nunca se lo expliques.
        Mitología actual de esta sesión: {lore_partida[0]}. Si es el inicio, INVENTA una mitología única de degradación.
        Datos actuales del jugador: Vida={stats['Vida']}, Dinero={stats['Dinero']}, Mana={stats['Mana']}. Días restantes: {stats['Dias']}.
        Modo actual: '{mod}'. Reacciona diferente si piensa o habla en voz alta.
        AL FINAL ABSOLUTO de tu mensaje, incluye estrictamente estos dos bloques en este formato exacto:
        1. [CAMBIOS: Vida=X, Dinero=X, Mana=X, EXP=X, Dias=X] (O [CAMBIOS: Ninguno]).
        2. [MEMORIA: "Resumen corto de la mitología o situación actual"].
        """

        mensajes = [{"role": "system", "content": prompt_sistema}]
        for msg in historial[-6:]: 
            mensajes.append({"role": "user" if msg["rol"] == "usuario" else "assistant", "content": msg["texto"]})

        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes).choices[0].message.content

        # Procesar memoria oculta de la partida
        if "[MEMORIA:" in res:
            p_lore = res.split("[MEMORIA:")
            res = p_lore[0]
            lore_partida[0] = p_lore[1].replace("]", "").replace('"', '').strip()

        # Procesar cambios automáticos en los marcadores
        if "[CAMBIOS:" in res:
            p_cambios = res.split("[CAMBIOS:")
            res = p_cambios[0]
            cambios_str = p_cambios[1].replace("]", "").strip()
            if "Ninguno" not in cambios_str:
                for cambio in cambios_str.split(","):
                    try:
                        clave, valor = cambio.split("=")
                        k = clave.strip()
                        v = int(valor.strip())
                        if k == "Dias": stats["Dias"] += v
                        else: stats[k] += v
                    except: pass

        # Mostrar respuesta del Narrador y actualizar la pantalla
        chat_view.controls.append(cargar_bloque("ia", "Pensar", res))
        historial.append({"rol": "ia", "texto": res})
        
        reloj_label.value = f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {stats['Dias']} días"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        page.update()

    def reiniciar(e):
        page.window_reload()

    btn_enviar = ft.ElevatedButton(text="🚀 ALTERAR EL DESTINO", bgcolor="#6D28D9", color="white", on_click=enviar_accion, height=50)
    btn_reset = ft.TextButton(text="💀 Reiniciar", icon=ft.icons.DELETE_FOREVER, icon_color="#EF4444", on_click=reiniciar)

    # 7. Construcción visual de la pantalla
    page.add(ft.Column([ft.Row([ft.Text("🧙‍♂️ CRÓNICAS DEL COLAPSO", size=18, weight=ft.FontWeight.BOLD, color="#9333EA"), btn_reset], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), stat_container, ft.Divider(color="#1E293B"), chat_view, ft.Divider(color="#1E293B"), modo_radio, ft.Row([input_texto, btn_enviar])], expand=True))

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
