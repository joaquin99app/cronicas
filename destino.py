import urllib.request
import json
import os
import flet as ft
from groq import Groq

# =====================================================================
# CONFIGURACIÓN DE CLIENTES Y VARIABLES DE ENTORNO
# =====================================================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "tu_api_key_aqui")
client = Groq(api_key=GROQ_API_KEY)

# URL base para MockAPI de persistencia infinita
MOCKAPI_BASE_URL = "https://mockapi.io"

# =====================================================================
# 3. FUNCIONES DE LA NUBE PERMANENTE (ESTRUCTURA PLANA)
# =====================================================================
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
            # CORREGIDO: Sintaxis válida de pertenencia para estados HTTP exitosos
            if response.status in [200, 201]:
                return True
    except Exception as e:
        print(f"Error al escribir en la nube: {e}")
        return False
    return False

# =====================================================================
# 1. & 4. FUNCIÓN PRINCIPAL DE INTERFAZ (FLET)
# =====================================================================
def main(page: ft.Page):
    # Configuración de ventana móvil para simulación/web
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
        "historial_lore": "Acabas de cruzar las grandes puertas del castillo. Eres un niño pequeño de primer año, tus ojos brillan de asombro y tu varita se siente pesada en tu túnica."
    }

    # PROMPT DEL SISTEMA - NARRADOR
    PROMPT_SISTEMA = (
        "Actúa como el Director y Narrador omnisciente de un prestigioso Colegio de Magia (estilo Harry Potter). "
        "El jugador es un niño muy pequeño de primer año. Adapta el entorno a su baja estatura, su inocencia e ingenio limitado. "
        "Haz énfasis en las normas escolares: zonas prohibidas, prefectos celosos patrullando, el toque de queda nocturno y los castigos por romper reglas. "
        "Sé descriptivo, mágico y mantén el tono de novela fantástica juvenil.\n\n"
        "REQUISITO INQUEBRANTABLE: Al final de absolutamente cada respuesta, debes añadir estrictamente las siguientes tres líneas con el formato exacto para actualización del sistema:\n"
        "1. [ESTADÍSTICAS: Vida=X, Dinero=X, Mana=X/10, EXP=X%, Dias=X]\n"
        "2. [MOCHILA: Item1, Item2, ...]\n"
        "3. [MEMORIA: Evento crucial resumido en una frase]"
    )

    # -----------------------------------------------------------------
    # COMPONENTES VISUALES INTERNOS (Inicializados ANTES de vincular eventos)
    # -----------------------------------------------------------------
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
    panel_inventario = ft.Container(
        content=lbl_mochila, padding=10, bgcolor=ft.colors.BACKGROUND, 
        border=ft.border.all(1, ft.colors.OUTLINE), border_radius=8, margin=ft.margin.only(bottom=15)
    )

    txt_narracion = ft.Text(page.data["historial_lore"], size=16, selectable=True)
    scroll_narracion = ft.Column([txt_narracion], scroll=ft.ScrollMode.ALWAYS, height=320)

    txt_accion = ft.TextField(
        label="¿Qué quieres hacer, pequeño aprendiz?", 
        hint_text="Ej: Investigar los pasillos oscuros / Ir a la clase de Encantamientos",
        expand=True, disabled=True
    )
    btn_enviar = ft.Button("Acción", icon=ft.icons.SEND, disabled=True)

    txt_correo = ft.TextField(label="Introduce tu Correo para Cargar/Registrar", expand=True, hint_text="ejemplo@magia.com")
    btn_conectar = ft.ElevatedButton("Entrar al Colegio")
        # -----------------------------------------------------------------
    # FUNCIONES DE LÓGICA DE INTERFAZ Y PROCESAMIENTO
    # -----------------------------------------------------------------
    def actualizar_interfaz_visual():
        """Refleja los datos de 'page.data' en los widgets de la pantalla."""
        lbl_vida.value = f"❤️ Vida: {page.data['vida']}"
        lbl_dinero.value = f"💰 Galeones: {page.data['dinero']}"
        lbl_mana.value = f"✨ Maná: {page.data['mana_actual']}/{page.data['mana_max']}"
        lbl_exp.value = f"🎓 EXP: {page.data['exp']}%"
        lbl_dias.value = f"⏳ Curso: {page.data['dias']} días"
        lbl_mochila.value = f"🎒 Mochila: {', '.join(page.data['mochila'])}"
        txt_narracion.value = page.data["historial_lore"]
        page.update()

    def procesar_bloques_ia(texto_ia: str):
        """Busca y recorta los bloques imperativos de estadísticas mediante .index()."""
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
                if "vida" in key:
                    page.data["vida"] = int(val)
                elif "dinero" in key or "galeones" in key:
                    page.data["dinero"] = int(val)
                elif "mana" in key:
                    cur_m, max_m = val.split("/")
                    page.data["mana_actual"] = int(cur_m)
                    page.data["mana_max"] = int(max_m)
                elif "exp" in key:
                    page.data["exp"] = int(val.replace("%", ""))
                elif "dias" in key:
                    page.data["dias"] = int(val)

            str_mochila = texto_ia[idx_mochila:idx_memoria].replace("[MOCHILA:", "").replace("]", "").strip()
            if str_mochila and str_mochila.lower() != "ninguno":
                page.data["mochila"] = [item.strip() for item in str_mochila.split(",")]
            else:
                page.data["mochila"] = []
        except Exception as e:
            page.data["historial_lore"] = texto_ia
            print(f"Error recortando bloques de la IA: {e}")

    # -----------------------------------------------------------------
    # MANEJADORES DE EVENTOS
    # -----------------------------------------------------------------
    def al_conectar_click(e):
        correo = txt_correo.value.strip()
        if not correo or "@" not in correo:
            txt_correo.error_text = "Por favor, introduce un correo electrónico válido"
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
            txt_narracion.value = f"¡Bienvenido de vuelta, alumno! Reanudando tu partida en el Colegio...\n\n{page.data['historial_lore']}"
        else:
            escribir_nube_remota(correo, {
                "vida": page.data["vida"], "dinero": page.data["dinero"],
                "mana_actual": page.data["mana_actual"], "mana_max": page.data["mana_max"],
                "exp": page.data["exp"], "dias": page.data["dias"],
                "mochila": page.data["mochila"], "historial_lore": page.data["historial_lore"]
            })
            txt_narracion.value = f"¡Expediente de inscripción mágico creado con éxito!\n\n{page.data['historial_lore']}"

        txt_accion.disabled = False
        btn_enviar.disabled = False
        actualizar_interfaz_visual()

    def al_enviar_accion_click(e):
        accion_usuario = txt_accion.value.strip()
        if not accion_usuario:
            return

        txt_accion.disabled = True
        btn_enviar.disabled = True
        txt_narracion.value = "Pensando tu siguiente evento mágico..."
        page.update()

        contexto_rol = (
            f"El alumno (Correo ID: {page.data['correo']}) intenta realizar la acción: '{accion_usuario}'. "
            f"Estado actual: Vida={page.data['vida']}, Dinero={page.data['dinero']} Galeones, "
            f"Maná={page.data['mana_actual']}/{page.data['mana_max']}, EXP={page.data['exp']}%, Días de curso restantes={page.data['dias']}. "
            f"Lleva en su mochila: {', '.join(page.data['mochila'])}. "
            f"Contexto previo: {page.data['historial_lore']}"
        )

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": contexto_rol}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            # Sintaxis reglamentaria estricta de Groq con el índice del mensaje
            raw_res = str(completion.choices[0].message.content)
            procesar_bloques_ia(raw_res)

            escribir_nube_remota(page.data["correo"], {
                "vida": page.data["vida"], "dinero": page.data["dinero"],
                "mana_actual": page.data["mana_actual"], "mana_max": page.data["mana_max"],
                "exp": page.data["exp"], "dias": page.data["dias"],
                "mochila": page.data["mochila"], "historial_lore": page.data["historial_lore"]
            })

        except Exception as err:
            page.data["historial_lore"] = f"Hubo un problema de conexión con las corrientes de maná del servidor (Error de API). Inténtalo de nuevo.\nDetalle: {err}"

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
            content=ft.Column(
                [
                    ft.Text("🏰 ACADEMIA DE JÓVENES MAGOS", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_600, alignment=ft.alignment.center),
                    ft.Divider(),
                    panel_stats,
                    panel_inventario,
                    ft.Text("NARRACIÓN DEL DIRECTOR:", size=11, weight=ft.FontWeight.W_300, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Container(scroll_narracion, border=ft.border.all(1, ft.colors.SURFACE_CONTAINER_HIGHEST), padding=12, border_radius=6, bgcolor=ft.colors.SURFACE_CONTAINER),
                    ft.Row([txt_accion, btn_enviar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Row([txt_correo, btn_conectar])
                ],
                tight=True,
                spacing=10
            ),
            padding=15
        ),
        margin=10
    )

    page.add(interfaz_juego)

# =====================================================================
# 5. ARRANQUE DE PRODUCCIÓN ADAPTATIVO PARA PORT DE RENDER
# =====================================================================
if __name__ == "__main__":
    # Render inyecta la variable de entorno PORT dinámicamente para enlazar servicios web
    puerto_render = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=puerto_render, view=None)
    
