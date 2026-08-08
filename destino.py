import urllib.request
import json
import os
import flet as ft
from groq import Groq

# Configuración del cliente de Groq (Variable de entorno en Render)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "tu_api_key_aqui")
client = Groq(api_key=GROQ_API_KEY)

# URL base para MockAPI de persistencia infinita
MOCKAPI_BASE_URL = "https://mockapi.io"

def limpiar_correo_id(correo: str) -> str:
    """Limpia el correo de arrobas y puntos para crear un ID compatible."""
    return correo.replace("@", "_").replace(".", "_").strip().lower()

def leer_nube_remota(correo: str) -> dict:
    """Lee el progreso del alumno desde la nube remota usando urllib."""
    user_id = limpiar_correo_id(correo)
    url = f"{MOCKAPI_BASE_URL}/{user_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("progreso", None)
    except Exception:
        return None
    return None

def escribir_nube_remota(correo: str, datos: dict) -> bool:
    """Escribe o actualiza el progreso del alumno en la nube remota."""
    user_id = limpiar_correo_id(correo)
    existe = leer_nube_remota(correo)
    
    payload = {
        "id": user_id,
        "correo_original": correo,
        "progreso": datos
    }
    data_bytes = json.dumps(payload).encode('utf-8')
    
    if existe is not None:
        url = f"{MOCKAPI_BASE_URL}/{user_id}"
        method = "PUT"
    else:
        url = MOCKAPI_BASE_URL
        method = "POST"
        
    try:
        req = urllib.request.Request(
            url, 
            data=data_bytes, 
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            method=method
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in:
                return True
    except Exception as e:
        print(f"Error al escribir en la nube: {e}")
        return False
    return False
    def main(page: ft.Page):
    # Configuración de ventana móvil
    page.title = "Colegio de Magia - Escuela de Aprendices"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Inicialización de Datos por Defecto en page.data
    page.data = {
        "correo": "",
        "vida": 100,
        "dinero": 15,
        "mana_actual": 10,
        "mana_max": 10,
        "exp": 0,
        "dias": 270,
        "mochila": ["Túnica de Primer Año", "Varita de Fresno", "Mascota Pequeña"],
        "historial_lore": "Acabas de cruzar las grandes puertas del castillo. Eres un niño pequeño de primer año, tus ojos brillan de asombro."
    }

    # PROMPT DEL SISTEMA - NARRADOR
    PROMPT_SISTEMA = (
        "Actúa como el Director y Narrador omnisciente de un prestigioso Colegio de Magia. "
        "El jugador es un niño muy pequeño de primer año. Adapta el entorno a su baja estatura e inocencia. "
        "Haz énfasis en las normas escolares: zonas prohibidas, prefectos celosos y toque de queda.\n\n"
        "REQUISITO INQUEBRANTABLE: Al final de absolutamente cada respuesta, debes añadir estrictamente:\n"
        "1. [ESTADÍSTICAS: Vida=X, Dinero=X, Mana=X/10, EXP=X%, Dias=X]\n"
        "2. [MOCHILA: Item1, Item2, ...]\n"
        "3. [MEMORIA: Evento resumido]"
    )

    # Indicadores de Estado Táctiles
    lbl_vida = ft.Text("❤️ Vida: 100", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.RED_400)
    lbl_dinero = ft.Text("💰 Galeones: 15", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400)
    lbl_mana = ft.Text("✨ Maná: 10/10", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
    lbl_exp = ft.Text("🎓 EXP: 0%", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400)
    lbl_dias = ft.Text("⏳ Curso: 270 días", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE_400)
    
    panel_stats = ft.Container(
        content=ft.Row([lbl_vida, lbl_dinero, lbl_mana, lbl_exp, lbl_dias], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True),
        padding=10, bgcolor=ft.colors.SURFACE_CONTAINER_HIGHEST, border_radius=10, margin=ft.margin.only(bottom=10)
    )

    lbl_mochila = ft.Text("🎒 Mochila: Túnica de Primer Año, Varita de Fresno, Mascota Pequeña", size=12, italic=True)
    panel_inventario = ft.Container(content=lbl_mochila, padding=10, bgcolor=ft.colors.BACKGROUND, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=8, margin=ft.margin.only(bottom=15))

    txt_narracion = ft.Text(page.data["historial_lore"], size=16, selectable=True)
    scroll_narracion = ft.Column([txt_narracion], scroll=ft.ScrollMode.ALWAYS, height=320)

    txt_accion = ft.TextField(label="¿Qué quieres hacer, pequeño aprendiz?", hint_text="Ej: Ir a la clase de Encantamientos", expand=True, disabled=True)
    btn_enviar = ft.Button("Acción", icon=ft.icons.SEND, disabled=True)

    txt_correo = ft.TextField(label="Introduce tu Correo para Cargar/Registrar", expand=True, hint_text="ejemplo@magia.com")
    btn_conectar = ft.ElevatedButton("Entrar al Colegio")
        def actualizar_interfaz_visual():
        lbl_vida.value = f"❤️ Vida: {page.data['vida']}"
        lbl_dinero.value = f"💰 Galeones: {page.data['dinero']}"
        lbl_mana.value = f"✨ Maná: {page.data['mana_actual']}/{page.data['mana_max']}"
        lbl_exp.value = f"🎓 EXP: {page.data['exp']}%"
        lbl_dias.value = f"⏳ Curso: {page.data['dias']} días"
        lbl_mochila.value = f"🎒 Mochila: {', '.join(page.data['mochila'])}"
        txt_narracion.value = page.data["historial_lore"]
        page.update()

    def procesar_bloques_ia(texto_ia: str):
        try:
            idx_stats = texto_ia.index("[ESTADÍSTICAS:")
            idx_mochila = texto_ia.index("[MOCHILA:")
            idx_memoria = texto_ia.index("[MEMORIA:")

            narrativa_limpia = texto_ia[:idx_stats].strip()
            page.data["historial_lore"] = narrativa_limpia

            str_stats = texto_ia[idx_stats:idx_mochila].replace("[ESTADÍSTICAS:", "").replace("]", "").strip()
            partes_stats = str_stats.split(",")
            for p in partes_stats:
                key, val = p.split("=")
                key = key.strip().lower()
                val = val.strip()
                if "vida" in key: page.data["vida"] = int(val)
                elif "dinero" in key or "galeones" in key: page.data["dinero"] = int(val)
                elif "mana" in key:
                    cur_m, max_m = val.split("/")
                    page.data["mana_actual"] = int(cur_m)
                    page.data["mana_max"] = int(max_m)
                elif "exp" in key: page.data["exp"] = int(val.replace("%", ""))
                elif "dias" in key: page.data["dias"] = int(val)

            str_mochila = texto_ia[idx_mochila:idx_memoria].replace("[MOCHILA:", "").replace("]", "").strip()
            if str_mochila and str_mochila.lower() != "ninguno":
                page.data["mochila"] = [item.strip() for item in str_mochila.split(",")]
            else:
                page.data["mochila"] = []
        except Exception as e:
            page.data["historial_lore"] = texto_ia
            print(f"Error recortando bloques: {e}")

    def al_conectar_click(e):
        correo = txt_correo.value.strip()
        if not correo or "@" not in correo:
            txt_correo.error_text = "Introduce un correo válido"
            page.update()
            return
        
        txt_correo.error_text = None
        btn_conectar.disabled = True
        txt_correo.disabled = True
        page.update()

        progreso_guardado = leer_nube_remota(correo)
        page.data["correo"] = correo

        if progreso_guardado:
            page.data.update(progreso_guardado)
            txt_narracion.value = f"¡Bienvenido de vuelta!\n\n{page.data['historial_lore']}"
        else:
            escribir_nube_remota(correo, {
                "vida": page.data["vida"], "dinero": page.data["dinero"],
                "mana_actual": page.data["mana_actual"], "mana_max": page.data["mana_max"],
                "exp": page.data["exp"], "dias": page.data["dias"],
                "mochila": page.data["mochila"], "historial_lore": page.data["historial_lore"]
            })
            txt_narracion.value = f"¡Inscripción mágica creada!\n\n{page.data['historial_lore']}"

        txt_accion.disabled = False
        btn_enviar.disabled = False
        actualizar_interfaz_visual()

    def al_enviar_accion_click(e):
        accion_usuario = txt_accion.value.strip()
        if not accion_usuario: return

        txt_accion.disabled = True
        btn_enviar.disabled = True
        txt_narracion.value = "Pensando tu siguiente evento mágico..."
        page.update()

        contexto_rol = (
            f"El alumno intenta: '{accion_usuario}'. Estado: Vida={page.data['vida']}, Dinero={page.data['dinero']},"
            f"Maná={page.data['mana_actual']}/{page.data['mana_max']}, EXP={page.data['exp']}%, Días={page.data['dias']}. "
            f"Mochila: {', '.join(page.data['mochila'])}. Contexto: {page.data['historial_lore']}"
        )

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": contexto_rol}
                ],
                temperature=0.7, max_tokens=1024
            )
            # SINTAXIS REGLAMENTARIA EXACTA CON ÍNDICE [0]
            raw_res = str(completion.choices[0].message.content)
            procesar_bloques_ia(raw_res)

            escribir_nube_remota(page.data["correo"], {
                "vida": page.data["vida"], "dinero": page.data["dinero"],
                "mana_actual": page.data["mana_actual"], "mana_max": page.data["mana_max"],
                "exp": page.data["exp"], "dias": page.data["dias"],
                "mochila": page.data["mochila"], "historial_lore": page.data["historial_lore"]
            })
        except Exception as err:
            page.data["historial_lore"] = f"Error de conexión con el maná del servidor: {err}"

        txt_accion.value = ""
        txt_accion.disabled = False
        btn_enviar.disabled = False
        actualizar_interfaz_visual()
            # Vincular referencias de click a las funciones planas
    btn_conectar.on_click = al_conectar_click
    btn_enviar.on_click = al_enviar_accion_click

    # Confección del Layout Visual Móvil
    interfaz_juego = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("🏰 ACADEMIA DE JÓVENES MAGOS", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_600),
                ft.Divider(),
                panel_stats,
                panel_inventario,
                ft.Text("NARRACIÓN DEL DIRECTOR:", size=11, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Container(scroll_narracion, border=ft.border.all(1, ft.colors.SURFACE_CONTAINER_HIGHEST), padding=12, border_radius=6, bgcolor=ft.colors.SURFACE_CONTAINER),
                ft.Row([txt_accion, btn_enviar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([txt_correo, btn_conectar])
            ], tight=True, spacing=10),
            padding=15
        ), margin=10
    )

    page.add(interfaz_juego)

# Arranque limpio imperativo para Render sin forzar navegadores locales
ft.app(target=main)
