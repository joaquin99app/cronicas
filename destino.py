import flet as ft
from groq import Groq
import os

def main(page: ft.Page):
    page.title = "🚨 Crónicas del Colapso"
    page.bgcolor = "#05070B"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    client = Groq(api_key=os.environ.get("GROROQ_API_KEY") or os.environ.get("GROQ_API_KEY"))

    if "stats" not in page.session_state:
        page.session_state["stats"] = {"Vida": 100, "Dinero": 50, "Mana": 30, "EXP": 0, "Dias": 30}
    if "historial" not in page.session_state:
        page.session_state["historial"] = []
    if "lore_partida" not in page.session_state:
        page.session_state["lore_partida"] = "Pendiente de generación inicial"

    s = page.session_state["stats"]
    h_lista = page.session_state["historial"]

    reloj_label = ft.Text(f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {s['Dias']} días", color="#EF4444", weight=ft.FontWeight.BOLD, size=14)
    stats_text = ft.Text(f"❤️ {s['Vida']}%  |  💰 {s['Dinero']}€  |  🔮 {s['Mana']}/30  |  ✨ {s['EXP']}%", color="#F3F4F6", weight=ft.FontWeight.BOLD, size=15)
    stat_container = ft.Container(content=ft.Column([reloj_label, stats_text], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=15, border_radius=12, gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"]), border=ft.border.all(1, "#4C1D95"))

    chat_view = ft.ListView(expand=True, spacing=10, height=380)
    
    def cargar_bloque(rol, modo, texto):
        if rol == "usuario":
            bg = "#0F172A" if modo == "Pensar" else "#022C22"
            col = "#38BDF8" if modo == "Pensar" else "#10B981"
            lbl = "💭 Pensasíntesis: " if modo == "Pensar" else "🗣️ Voz Alta: "
            return ft.Container(content=ft.Text(f"{lbl}{texto}", color="#94A3B8" if modo == "Pensar" else "#34D399", italic=(modo=="Pensar")), padding=14, border_radius=10, bgcolor=bg, border=ft.border.only(left=ft.BorderSide(5, col)))
        return ft.Container(content=ft.Text(f"🔮 Narrador: {texto}", color="#F3F4F6", font_family="Georgia"), padding=14, border_radius=10, bgcolor="#111827", border=ft.border.only(left=ft.BorderSide(5, "#8B5CF6")))

    if not h_lista:
        chat_view.controls.append(cargar_bloque("ia", "Pensar", "El tejido de la realidad emite un zumbido agónico. La magia se pudre en el subsuelo. Quedan 30 días exactos para el desmoronamiento absoluto de la trama existencial.\n\nPeligros invisibles acechan en cada esquina. Tus actos ecoarán en el futuro. Existe una remota posibilidad de revertir la degradación y salvar el mundo, pero los métodos permanecen ocultos.\n\nEscoge tu arquetipo: Mago Urbano, Detective, Cazador o Humano Despierto."))
    else:
        for m in h_lista: chat_view.controls.append(cargar_bloque(m["rol"], m.get("modo","Pensar"), m["texto"]))

    modo_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Pensar", label="Narrar/Pensar"), ft.Radio(value="Hablar", label="Hablar")], alignment=ft.MainAxisAlignment.CENTER))
    modo_radio.value = "Pensar"
    input_texto = ft.TextField(hint_text="¿Qué dirección toma tu voluntad?", bgcolor="#111827", border_color="#1E293B", expand=True)

    def enviar_accion(e):
        if not input_texto.value: return
        txt = input_texto.value
        mod = modo_radio.value
        input_texto.value = ""
        
        chat_view.controls.append(cargar_bloque("usuario", mod, txt))
        h_lista.append({"rol": "usuario", "modo": mod, "texto": txt})
        page.update()

        prompt_sistema = f"Eres el Game Master de un RPG de terror místico. Estilo denso y largo. Mitología actual: {page.session_state['lore_partida']}. Si es el inicio, INVENTA una mitología de degradación única. Todo lo que hace tiene consecuencias. El mundo PUEDE SER SALVADO de los {s['Dias']} días restantes pero nunca lo expliques. Datos actuales: Vida={s['Vida']}, Dinero={s['Dinero']}, Mana={s['Mana']}. Modo='{mod}'. AL FINAL incluye estrictamente: 1. [CAMBIOS: Vida=X, Dinero=X, Mana=X, EXP=X, Dias=X] 2. [MEMORIA: 'Frase resumen de la mitología actual']."

        mensajes = [{"role": "system", "content": prompt_sistema}]
        for msg in h_lista[-6:]: mensajes.append({"role": "user" if msg["rol"] == "usuario" else "assistant", "content": msg["texto"]})

        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes).choices[0].message.content

        if "[MEMORIA:" in res:
            p = res.split("[MEMORIA:")
            res = p[0]
            page.session_state["lore_partida"] = p[1].replace("]", "").replace('"', '').strip()

        if "[CAMBIOS:" in res:
            p = res.split("[CAMBIOS:")
            res = p[0]
            for c in p[1].replace("]", "").strip().split(","):
                try:
                    k, v = c.split("=")
                    if k.strip() == "Dias": s["Dias"] += int(v.strip())
                    else: s[k.strip()] += int(v.strip())
                except: pass

        chat_view.controls.append(cargar_bloque("ia", "Pensar", res))
        h_lista.append({"rol": "ia", "texto": res})
        reloj_label.value = f"⏳ RELOJ DEL APOCALIPSIS MÁGICO: Quedan {s['Dias']} días"
        stats_text.value = f"❤️ {s['Vida']}%  |  💰 {s['Dinero']}€  |  🔮 {s['Mana']}/30  |  ✨ {s['EXP']}%"
        page.update()

    def reiniciar(e):
        page.session_state.clear()
        page.window_reload()

    btn_enviar = ft.ElevatedButton(text="🚀 ALTERAR EL DESTINO", bgcolor="#6D28D9", color="white", on_click=enviar_accion, height=50)
    btn_reset = ft.TextButton(text="💀 Reiniciar", icon=ft.icons.DELETE_FOREVER, icon_color="#EF4444", on_click=reiniciar)

    page.add(ft.Column([ft.Row([ft.Text("🧙‍♂️ CRÓNICAS DEL COLAPSO", size=18, weight=ft.FontWeight.BOLD, color="#9333EA"), btn_reset], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), stat_container, ft.Divider(color="#1E293B"), chat_view, ft.Divider(color="#1E293B"), modo_radio, ft.Row([input_texto, btn_enviar])], expand=True))

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
