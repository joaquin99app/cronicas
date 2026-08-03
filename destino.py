        padding=15, border_radius=12, gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B"])
    )
    chat_view = ft.ListView(expand=True, spacing=10, height=360)
    
    def cargar_bloque(rol, modo, texto):
        if rol == "usuario":
            bg = "#0F172A" if modo == "Pensar" else "#022C22"
            lbl = "💭 Pensasíntesis: " if modo == "Pensar" else "🗣️ Voz Alta: "
            return ft.Container(content=ft.Text(f"{lbl}{texto}", color="#94A3B8" if modo == "Pensar" else "#34D399", italic=(modo=="Pensar")), padding=14, border_radius=10, bgcolor=bg)
        return ft.Container(content=ft.Text(f"🔮 Narrador: {texto}", color="#F3F4F6", font_family="Georgia"), padding=14, border_radius=10, bgcolor="#111827")

    def pintar_bienvenida():
        chat_view.controls.clear()
        chat_view.controls.append(cargar_bloque("ia", "Pensar", f"Detrás del ruidoso tráfico humano y los carteles de neón de la ciudad moderna, late un mundo oculto regido por la magia antigua, los estatutos del Velo Secreto y los decretos del Ministerio de Hechicería.\n\n📧 [SISTEMA DE GRIMORIO AUTOMÁTICO EN LA NUBE]:\nEscribe tu dirección de correo electrónico abajo en la barra de texto y dale a enviar para iniciar tu andadura o recuperar tu progreso guardado en el servidor:"))
    pintar_bienvenida()

    modo_radio = ft.RadioGroup(content=ft.Row([ft.Radio(value="Pensar", label="Narrar/Pensar"), ft.Radio(value="Hablar", label="Hablar")], alignment=ft.MainAxisAlignment.CENTER))
    modo_radio.value = "Pensar"
    input_texto = ft.TextField(hint_text="Introduce tu correo electrónico para empezar...", bgcolor="#111827", border_color="#1E293B", expand=True)

    def enviar_accion(e):
        nonlocal lore_partida_contenedor, stats, historial, inventario_contenedor
        if not input_texto.value: return
        txt = input_texto.value.strip()
        input_texto.value = ""
        
        if page.data["correo_usuario"] is None:
            if "@" in txt and "." in txt:
                page.data["correo_usuario"] = txt
                partida_cargada = leer_nube_remota(txt)
                if partida_cargada:
                    stats.clear(); stats.update(partida_cargada["stats"])
                    historial.clear(); historial.extend(partida_cargada["historial"])
                    inventario_contenedor = partida_cargada["inventario"]
                    lore_partida_contenedor = partida_cargada["lore"]
                    chat_view.controls.clear()
                    for msg in historial: chat_view.controls.append(cargar_bloque(msg.get("rol", "ia"), msg.get("modo", "Pensar"), msg.get("texto", "")))
                    chat_view.controls.append(cargar_bloque("ia", "Pensar", f"🔮 Vínculo establecido con {txt}. Tu historial de mensajes, monedas y mochila se han descargado desde la nube permanente con éxito. Continúa tu aventura."))
                else:
                    chat_view.controls.append(cargar_bloque("ia", "Pensar", f"✨ Correo [{txt}] registrado en la nube permanente por primera vez.\n\nTienes {stats['Dinero']}€ mágicos en tu monedero de cuero. Los callejones invisibles albergan mercados negros y boticarios oscuros. Todo tiene un precio.\n\nElige tu arquetipo místico escribiéndolo abajo para adentrarte en el mapa abierto: Mago Urbano, Detective, Cazador o Humano Despierto."))
                reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
                stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
                inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
                input_texto.hint_text = "¿Qué dirección toma tu voluntad?"
                btn_save.content.text = f"💾 Guardar: {txt[:4]}..."
                page.update()
                return
            else:
                chat_view.controls.append(cargar_bloque("ia", "Pensar", "❌ Formato incorrecto. Por favor, introduce un correo electrónico válido para identificarte (ejemplo: jugador@gmail.com):"))
                page.update()
                return

        mod = modo_radio.value
        chat_view.controls.append(cargar_bloque("usuario", mod, txt))
        historial.append({"rol": "usuario", "modo": mod, "texto": txt})
        page.update()

        prompt_sistema = f"Actúa como el Game Master de un RPG conversacional de Fantasía Urbana Contemporánea. Estilo denso y descriptivo.\n[SISTEMA ECONÓMICO REAL EN EUROS]\n- Despliega tiendas (armerías de varitas, boticarios, tabernas).\n- Si compra, descuenta dinero y añádelo a su mochila.\n[REGLA DE ASIGNACIÓN CRÍTICA VALORES FIJOS]\nEstadísticas actuales antes de tu turno: Vida={stats['Vida']}, Dinero={stats['Dinero']}, Mana={stats['Mana']}, EXP={stats['EXP']}, Dias={stats['Dias']}.\nMochila actual: '{inventario_contenedor}'.\nAL FINAL ABSOLUTO de tu mensaje, incluye estrictamente estos bloques:\n1. [ESTADÍSTICAS: Vida=VALOR, Dinero=VALOR, Mana=VALOR, EXP=VALOR, Dias=VALOR]\n2. [MOCHILA: Lista completa de objetos]\n3. [MEMORIA: Resumen corto de la trama]."
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": prompt_sistema}] + [{"role": "user" if m.get("rol") == "usuario" else "assistant", "content": m.get("texto", "")} for m in historial[-6:]])
        raw_res = str(completion.choices.message.content)
        res_narrador = raw_res
                if "[MEMORIA:" in raw_res:
            try:
                idx_ini = raw_res.index("[MEMORIA:")
                idx_fin = raw_res.index("]", idx_ini)
                lore_partida_contenedor = [raw_res[idx_ini + 9:idx_fin].replace('"', '').strip()]
                res_narrador = raw_res[:idx_ini].strip()
            except: pass

        if "[MOCHILA:" in raw_res:
            try:
                idx_ini = raw_res.index("[MOCHILA:")
                idx_fin = raw_res.index("]", idx_ini)
                inventario_contenedor = [raw_res[idx_ini + 9:idx_fin].strip()]
                if idx_ini < len(res_narrador): res_narrador = raw_res[:idx_ini].strip()
            except: pass

        if "[ESTADÍSTICAS:" in raw_res:
            try:
                idx_ini = raw_res.index("[ESTADÍSTICAS:")
                idx_fin = raw_res.index("]", idx_ini)
                cambios_str = raw_res[idx_ini + 14:idx_fin].strip()
                if idx_ini < len(res_narrador): res_narrador = raw_res[:idx_ini].strip()
                for cambio in cambios_str.split(","):
                    try:
                        clave, valor = cambio.split("=")
                        k = clave.strip(); v = int(valor.strip())
                        if k in stats:
                            if k == "Vida" and v > 100: v = 100
                            if k == "Mana" and v > 30: v = 30
                            stats[k] = v
                    except: pass
            except: pass

        chat_view.controls.append(cargar_bloque("ia", "Pensar", res_narrador.strip()))
        historial.append({"rol": "ia", "texto": res_narrador.strip()})
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        hora_label.value = f"⏰ Tiempo Real: {datetime.now().strftime('%H:%M')} | ☀️ BAJO EL VELO"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
        page.update()

    def abrir_menu_guardar(e):
        nonlocal lore_partida_contenedor, stats, historial, inventario_contenedor
        if page.data["correo_usuario"] is not None:
            datos = {"stats": stats, "historial": historial, "inventario": inventario_contenedor, "lore": lore_partida_contenedor}
            exito = escribir_nube_remota(page.data["correo_usuario"], datos)
            if exito:
                btn_save.content.text = "✅ Guardado Permanente"
                btn_save.bgcolor = "#10B981"
            else:
                btn_save.content.text = "❌ Error de Red"; btn_save.bgcolor = "#EF4444"
            page.update()
        else:
            chat_view.controls.append(cargar_bloque("ia", "Pensar", "❌ Primero debes introducir tu correo electrónico en la barra inferior para poder registrar tu Grimorio."))
            page.update()

    def reiniciar(e):
        nonlocal lore_partida_contenedor, inventario_contenedor
        if page.data["correo_usuario"] is not None: borrar_nube_remota(page.data["correo_usuario"])
        stats["Vida"], stats["Dinero"], stats["Mana"], stats["EXP"], stats["Dias"] = 100, 50, 30, 0, 30
        inventario_contenedor = ["Varita de Sauce, Toga Escolar"]
        historial.clear(); page.data["correo_usuario"] = None
        input_texto.hint_text = "Introduce tu correo electrónico para empezar..."
        nueva_semilla = random.choice(semillas_amenaza_final)
        lore_partida_contenedor = [f"Amenaza de extinción oculta elegida: {nueva_semilla}"]
        pintar_bienvenida()
        btn_save.content.text = "💾 Guardar Grimorio"; btn_save.bgcolor = "#059669"
        reloj_label.value = f"⏳ RELOJ DE LA CRISIS: Quedan {stats['Dias']} días para el fin del Velo"
        stats_text.value = f"❤️ {stats['Vida']}%  |  💰 {stats['Dinero']}€  |  🔮 {stats['Mana']}/30  |  ✨ {stats['EXP']}%"
        inventario_text.value = f"🎒 Mochila: {inventario_contenedor}"
        page.update()

    btn_enviar = ft.ElevatedButton(content=ft.Text("🚀 ALTERAR EL DESTINO", color="white", weight=ft.FontWeight.BOLD), bgcolor="#6D28D9", on_click=enviar_accion, height=50)
    btn_save = ft.ElevatedButton(content=ft.Text("💾 Guardar Grimorio", color="white", weight=ft.FontWeight.BOLD), bgcolor="#059669", on_click=abrir_menu_guardar)
    btn_reset = ft.TextButton(content=ft.Text("💀 Reiniciar", color="#EF4444", weight=ft.FontWeight.BOLD), on_click=reiniciar)
    page.add(ft.Column([ft.Row([ft.Text("🧙‍♂️ CRÓNICAS DEL VELO", size=14, weight=ft.FontWeight.BOLD, color="#9333EA"), ft.Row([btn_save, btn_reset], spacing=5)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), stat_container, ft.Divider(color="#1E293B"), chat_view, ft.Divider(color="#1E293B"), modo_radio, ft.Row([input_texto, btn_enviar])], expand=True))

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
                
