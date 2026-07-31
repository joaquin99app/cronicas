import flet as ft
from groq import Groq
import os
import random

def main(page: ft.Page):
    # 1. Configuración de pantalla estilo App Móvil Premium
    page.title = "🚨 Crónicas del Colapso"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Conexión segura con la IA de Groq en Render
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # 2. Variables de estado directas de la partida (Reiniciables)
    stats = {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30}
    historial = []
    
    # Generador de una semilla mística única en cada reinicio para forzar a la IA a variar el lore
    semillas_apocalipsis = [
        "Las sombras de los antepasados devoran los reflejos en el agua bendita.",
        "El Wi-Fi místico transmite el llanto de dioses de piedra sepultados.",
        "Las constelaciones se están apagando y la magia de sangre se corrompe.",
        "Los espejos de la ciudad retienen las almas de los que mueren en las calles.",
        "Las raíces de un árbol milenario maldito están quebrando el asfalto y envenenando el maná."
    ]
    semilla_actual = random.choice(semillas_apocalipsis)
    lore_partida_contenedor = [f"Semilla mística inicial: {semilla_actual}"]

    # 3. Componentes visuales superiores
    reloj_label = ft.Text(f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {stats['Dias']} días", color="#EF4444", weight=ft.FontWeight.BOLD, size=14)
    stats_text = ft.Text(f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%", color="#F3F4F6", weight=ft.FontWeight.BOLD, size=15)
    
    stat_container = ft.Container(
        content=ft.Column([reloj_label, stats_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), 
        padding=15, 
        border_radius=12, 
        gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"])
    )

    # 4. Historial del Chat Principal
    chat_view = ft.ListView(expand=True, spacing=10, height=380)
    
    def cargar_bloque(rol, modo, texto):
        if rol == "usuario":
            bg = "#0F172A" if modo == "Pensar" else "#022C22"
            lbl = "💭 Pensasíntesis: " if modo == "Pensar" else "🗣️ Voz Alta: "
            return ft.Container(
                content=ft.Text(f"{lbl}{texto}", color="#94A3B8" if modo == "Pensar" else "#34D399", italic=(modo=="Pensar")), 
                padding=14, 
                border_radius=10, 
                bgcolor=bg
            )
        return ft.Container(
            content=ft.Text(f"🔮 Narrador: {texto}", color="#F3F4F6", font_family="Georgia"), 
            padding=14, 
            border_radius=10, 
            bgcolor="#111827"
        )

    # Mensaje de bienvenida inicial
    chat_view.controls.append(cargar_bloque("ia", "Pensar", "El tejido de la realidad emite un zumbido agónico. La magia se pudre en las entrañas del mundo y el velo místico está a punto de colapsar. Quedan 30 días exactos para el desmoronamiento de la existencia.\n\nEste es un mundo abierto, fantástico y cruel. Peligros invisibles acechan en cada esquina. Tus decisiones dictarán tu destino, pero el mundo no se detendrá a esperarte si decides ignorar su llamada.\n\nManifiesta tu presencia escogiendo tu arquetipo maldito escribiéndolo abajo: Mago Urbano, Detective, Cazador o Humano Despierto."))

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
        Eres el Game Master de un RPG conversacional de terror místico, horror cósmico y alta fantasía oscura urbana. Tu estilo debe ser denso, literario, maduro, perturbador y profundamente detallado. Escribe respuestas largas.
        
        [REGLAS DE LORE Y PELIGROS CONSTANTES]
        - Todo el lore debe girar exclusivamente en torno al MUNDO MÁGICO OCULTO, sus leyes prohibidas, pactos de sangre y criaturas de pesadilla. 
        - Hay PELIGROS INMINENTES acechando constantemente. El entorno es hostil y reactivo.
        
        [REGLA DE MUNDO ABIERTO Y LIBERTAD ABSOLUTA (EFECTO VIDA REAL)]
        - El jugador tiene libre albedrío total. Actúa como la vida real: si el jugador rechaza un camino, ignora a un NPC moribundo, huye de una misión o decide dedicarse a sus propios asuntos egoístas o vicios, NO LE INSISTAS NI LE OBLIGUES a retomar la trama principal. 
        - Acepta su decisión de inmediato y narra de forma lógica cómo el mundo sigue su curso: las misiones ignoradas fracasan de fondo, los NPCs mueren o se vuelven enemigos, y el apocalipsis avanza implacable mientras el jugador hace otra cosa.
        
        [SISTEMA PROCEDURAL]
        Mitología base inyectada para esta partida única: {lore_partida_contenedor[0]}. Usa este concepto para expandir un lore exclusivo, tétrico y original que nunca se repita con otras partidas.
        
        Datos actuales del jugador: Vida={stats['Vida']}, Dinero={stats['Dinero']}, Mana={stats['Mana']}. Días restantes: {stats['Dias']}.
        Modo actual: '{mod}'. Reacciona diferente si piensa o habla en voz alta.
        
        AL FINAL ABSOLUTO de tu mensaje, incluye estrictamente estos dos bloques en este formato exacto:
        1. [CAMBIOS: Vida=X, Dinero=X, Mana=X, EXP=X, Dias=X] (O [CAMBIOS: Ninguno]).
        2. [MEMORIA: "Resumen corto de la mitología o situación actual"].
        """

        mensajes = [{"role": "system", "content": prompt_sistema}]
        for msg in historial[-6:]: 
            mensajes.append({"role": "user" if msg["rol"] == "usuario" else "assistant", "content": msg["texto"]})

        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes)
        res = completion.choices[0].message.content

        # Procesar memoria oculta de la partida de forma segura dentro de la lista
        if "[MEMORIA:" in res:
            p_lore = res.split("[MEMORIA:")
            res = p_lore[0]
            lore_partida_contenedor[0] = p_lore[1].replace("]", "").replace('"', '').strip()

        # Procesar cambios automáticos en los marcadores
        if "[CAMBIOS:" in res:
            p_cambios = res.split("[CAMBIOS:")
            cambios_str = p_cambios[1].replace("]", "").strip()
            res = p_cambios[0]
            if "Ninguno" not in cambios_str:
                for cambio in cambios_str.split(","):
                    try:
                        clave, valor = cambio.split("=")
                        k = clave.strip()
                        v = int(valor.strip())
                        if k == "Dias": stats["Dias"] += v
                        else: stats[k] = stats.get(k, 100) + v
                    except: pass

        # Mostrar respuesta del Narrador y actualizar la pantalla
        chat_view.controls.append(cargar_bloque("ia", "Pensar", res))
        historial.append({"rol": "ia", "texto": res})
        
        reloj_label.value = f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {stats['Dias']} días"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        page.update()

    # Función que limpia el historial del servidor y fuerza una nueva semilla aleatoria
    def reiniciar(e):
        stats["Vida"] = 100
        stats["Dinero"] = 50
        stats["Mana"] = 30
        stats["EXP"] = 0
        stats["Dias"] = 30
        historial.clear()
        lore_partida_contenedor[0] = f"Semilla mística inicial: {random.choice(semillas_apocalipsis)}"
        page.window_reload()

    # Botones estilizados con compatibilidad total
    btn_enviar = ft.ElevatedButton(
        content=ft.Text("🚀 ALTERAR EL DESTINO", color="white", weight=ft.FontWeight.BOLD),
        bgcolor="#6D28D9", 
        on_click=enviar_accion, 
        height=50
    )
    
    btn_reset = ft.TextButton(
        content=ft.Text("💀 Forzar Reinicio Absoluto", color="#EF4444", weight=ft.FontWeight.BOLD), 
        on_click=reiniciar
    )

    # 7. Construcción visual de la pantalla
    page.add(
        ft.Column([
            ft.Row([
                ft.Text("🧙‍♂️ CRÓNICAS DEL COLAPSO", size=16, weight=ft.FontWeight.BOLD, color="#9333EA"), 
                btn_reset
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
            stat_container, 
            ft.Divider(color="#1E293B"), 
            chat_view, 
            ft.Divider(color="#1E293B"), 
            modo_radio, 
            ft.Row([input_texto, btn_enviar])
        ], expand=True)
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
