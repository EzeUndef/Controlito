"""Settings and preferences view for Controlito with Backup, Restore and Cloud Sync."""
import os
import shutil
import subprocess
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
from ui.theme import (
    ThemeManager, THEMES, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_DANGER, BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from database.db_manager import DatabaseManager
from utils.category_normalizer import normalize_database_categories


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db, on_theme_change=None, on_import_excel=None, on_reset_onboarding=None, on_database_changed=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_theme_change = on_theme_change
        self.on_import_excel = on_import_excel
        self.on_reset_onboarding = on_reset_onboarding
        self.on_database_changed = on_database_changed

        self.build_ui()

    def build_ui(self):
        curr = ThemeManager.get_current_theme()

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 15))

        lbl_title = ctk.CTkLabel(
            header,
            text="⚙️ Configuración y Preferencias",
            font=FONT_TITLE,
            text_color=curr["text_main"]
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header,
            text="Personaliza la apariencia corporativa, copias de seguridad, sincronización en la nube y administración de datos.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_sub.pack(anchor="w")

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # =========================================================================
        # SECCIÓN 1: 💾 COPIAS DE SEGURIDAD Y RESTAURACIÓN (1 CLIC)
        # =========================================================================
        sec_backup = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_backup.pack(fill="x", pady=(0, 15), padx=5)

        lbl_b_title = ctk.CTkLabel(sec_backup, text="💾 Copias de Seguridad y Respaldo (1 Clic)", font=FONT_HEADER, text_color=curr["text_main"])
        lbl_b_title.pack(anchor="w", padx=20, pady=(15, 4))

        lbl_b_desc = ctk.CTkLabel(
            sec_backup,
            text="Crea un archivo de respaldo con todos tus movimientos, servicios y cuentas para moverlo a otra PC, o restaura un backup previo.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_b_desc.pack(anchor="w", padx=20, pady=(0, 12))

        b_btn_row = ctk.CTkFrame(sec_backup, fg_color="transparent")
        b_btn_row.pack(fill="x", padx=20, pady=(0, 15))

        btn_create_backup = ctk.CTkButton(
            b_btn_row,
            text="💾 Crear Copia de Seguridad",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color=curr["primary"],
            hover_color=curr["primary_hover"],
            command=self._create_backup
        )
        btn_create_backup.pack(side="left", padx=(0, 10))

        btn_restore_backup = ctk.CTkButton(
            b_btn_row,
            text="📥 Restaurar Copia de Seguridad",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color=curr.get("secondary", "#475569"),
            hover_color=curr["border"],
            command=self._restore_backup
        )
        btn_restore_backup.pack(side="left", padx=(0, 10))

        # =========================================================================
        # SECCIÓN 2: ☁️ SINCRONIZACIÓN EN LA NUBE (GOOGLE DRIVE / ONEDRIVE / DROPBOX)
        # =========================================================================
        sec_cloud = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_cloud.pack(fill="x", pady=(0, 15), padx=5)

        lbl_c_title = ctk.CTkLabel(sec_cloud, text="☁️ Sincronización en la Nube y Multi-Dispositivo", font=FONT_HEADER, text_color=curr["text_main"])
        lbl_c_title.pack(anchor="w", padx=20, pady=(15, 4))

        lbl_c_desc = ctk.CTkLabel(
            sec_cloud,
            text="Conecta tu base de datos a una carpeta de Google Drive, OneDrive o Dropbox. Lo que cargues en una máquina se sincronizará automáticamente en las demás.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_c_desc.pack(anchor="w", padx=20, pady=(0, 12))

        # Active path card
        is_custom = DatabaseManager.is_using_custom_path()
        status_text = "☁️ Base Sincronizada en Carpeta Personalizada / Nube" if is_custom else "🟢 Base Local Predeterminada"
        status_color = curr["primary"] if is_custom else curr.get("success", "#059669")

        path_box = ctk.CTkFrame(sec_cloud, fg_color=curr["bg_input"], corner_radius=8, border_width=1, border_color=curr["border"])
        path_box.pack(fill="x", padx=20, pady=(0, 12))

        badge_row = ctk.CTkFrame(path_box, fg_color="transparent")
        badge_row.pack(fill="x", padx=12, pady=(10, 4))

        lbl_status = ctk.CTkLabel(badge_row, text=status_text, font=FONT_BODY_BOLD, text_color=status_color)
        lbl_status.pack(side="left")

        lbl_path = ctk.CTkLabel(
            path_box,
            text=f"📁 Ruta activa: {self.db.db_path}",
            font=FONT_SMALL,
            text_color=curr["text_main"],
            anchor="w"
        )
        lbl_path.pack(fill="x", padx=12, pady=(0, 10))

        c_btn_row = ctk.CTkFrame(sec_cloud, fg_color="transparent")
        c_btn_row.pack(fill="x", padx=20, pady=(0, 15))

        btn_cloud_move = ctk.CTkButton(
            c_btn_row,
            text="☁️ Mudar / Conectar a Carpeta en la Nube",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color=curr["primary"],
            hover_color=curr["primary_hover"],
            command=self._choose_cloud_folder
        )
        btn_cloud_move.pack(side="left", padx=(0, 10))

        if is_custom:
            btn_reset_default = ctk.CTkButton(
                c_btn_row,
                text="🔄 Volver a Local Predeterminado",
                font=FONT_BODY_BOLD,
                height=36,
                fg_color="transparent",
                border_width=1,
                border_color=curr["border"],
                text_color=curr["text_main"],
                hover_color=curr["bg_main"],
                command=self._reset_to_default_db
            )
            btn_reset_default.pack(side="left", padx=(0, 10))

        btn_open_folder = ctk.CTkButton(
            c_btn_row,
            text="📁 Abrir Carpeta Activa",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=curr["border"],
            text_color=curr["text_main"],
            hover_color=curr["bg_main"],
            command=self._open_data_folder
        )
        btn_open_folder.pack(side="left", padx=(0, 10))

        # =========================================================================
        # SECCIÓN 3: 🎨 TEMAS Y ESTÉTICA EMPRESARIAL
        # =========================================================================
        sec_theme = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_theme.pack(fill="x", pady=(0, 15), padx=5)

        lbl_t_title = ctk.CTkLabel(sec_theme, text="🎨 Temas y Estética Empresarial", font=FONT_HEADER, text_color=curr["text_main"])
        lbl_t_title.pack(anchor="w", padx=20, pady=(15, 4))

        lbl_t_desc = ctk.CTkLabel(
            sec_theme,
            text="Elige el estilo visual corporativo. La tipografía estándar empresarial es Segoe UI / Segoe UI Semibold.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_t_desc.pack(anchor="w", padx=20, pady=(0, 12))

        current_theme_name = self.db.get_setting("theme", ThemeManager._current_theme_name) if self.db else ThemeManager._current_theme_name

        themes_grid = ctk.CTkFrame(sec_theme, fg_color="transparent")
        themes_grid.pack(fill="x", padx=15, pady=(0, 15))
        themes_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for idx, (theme_name, t_data) in enumerate(THEMES.items()):
            row = idx // 4
            col = idx % 4
            is_active = (theme_name == current_theme_name)

            card = ctk.CTkFrame(
                themes_grid,
                fg_color=t_data["bg_main"],
                border_width=2 if is_active else 1,
                border_color=curr["primary"] if is_active else t_data["border"],
                corner_radius=8
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            btn = ctk.CTkButton(
                card,
                text=f"{'✓ ' if is_active else ''}{theme_name}",
                font=FONT_BODY_BOLD,
                height=38,
                fg_color="transparent",
                hover_color=t_data["bg_card"],
                text_color=t_data["text_main"],
                command=lambda name=theme_name: self._apply_theme(name)
            )
            btn.pack(fill="both", expand=True, padx=4, pady=4)

        # =========================================================================
        # SECCIÓN 4: 💵 COTIZACIÓN DÓLAR PREFERIDA
        # =========================================================================
        sec_dolar = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_dolar.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(sec_dolar, text="💵 Cotización Dólar Preferida para Ahorros", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=20, pady=(15, 4))
        ctk.CTkLabel(
            sec_dolar,
            text="Selecciona qué cotización en tiempo real se usará para convertir y calcular tus saldos en dólares a pesos:",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        ).pack(anchor="w", padx=20, pady=(0, 10))

        dolar_options = [
            ("blue", "Dólar Blue (Mercado Paralelo)"),
            ("bolsa", "Dólar MEP / Bolsa (Mercado de Capitales)"),
            ("oficial", "Dólar Oficial BNA (Banco de la Nación Argentina)"),
            ("tarjeta", "Dólar Tarjeta / Turista"),
            ("cripto", "Dólar Cripto (USDT / USDC)"),
            ("contadoconliqui", "Contado con Liquidación (CCL)")
        ]

        current_dolar = self.db.get_setting("dolar_rate_type", "blue") if self.db else "blue"
        self.dolar_var = ctk.StringVar(value=current_dolar)

        dolar_grid = ctk.CTkFrame(sec_dolar, fg_color="transparent")
        dolar_grid.pack(fill="x", padx=15, pady=(0, 15))
        dolar_grid.grid_columnconfigure((0, 1), weight=1)

        for idx, (key, label) in enumerate(dolar_options):
            row = idx // 2
            col = idx % 2
            rb = ctk.CTkRadioButton(
                dolar_grid,
                text=label,
                variable=self.dolar_var,
                value=key,
                font=FONT_BODY,
                text_color=curr["text_main"],
                command=lambda k=key: self._on_dolar_change(k)
            )
            rb.grid(row=row, column=col, padx=10, pady=6, sticky="w")

        # =========================================================================
        # SECCIÓN 5: 📂 HERRAMIENTAS DE DATOS ADICIONALES
        # =========================================================================
        sec_data = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_data.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(sec_data, text="📂 Herramientas de Datos y Mantenimiento", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=20, pady=(15, 4))
        ctk.CTkLabel(
            sec_data,
            text="Operaciones de importación masiva desde Excel, unificación automática de sinónimos y reinicio del asistente.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        ).pack(anchor="w", padx=20, pady=(0, 12))

        btn_row = ctk.CTkFrame(sec_data, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 15))

        if self.on_import_excel:
            btn_imp = ctk.CTkButton(
                btn_row,
                text="📂 Importar Nuevo Excel",
                font=FONT_BODY_BOLD,
                height=36,
                fg_color=curr["primary"],
                hover_color=curr["primary_hover"],
                command=self.on_import_excel
            )
            btn_imp.pack(side="left", padx=(0, 10))

        btn_norm = ctk.CTkButton(
            btn_row,
            text="🪄 Unificar Sinónimos",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color=curr.get("secondary", "#475569"),
            hover_color=curr["border"],
            command=self._normalize_categories
        )
        btn_norm.pack(side="left", padx=(0, 10))

        if self.on_reset_onboarding:
            btn_reset = ctk.CTkButton(
                btn_row,
                text="⚠️ Reiniciar a Pantalla Inicial",
                font=FONT_BODY_BOLD,
                height=36,
                fg_color=curr["danger"],
                hover_color="#b91c1c",
                command=self.on_reset_onboarding
            )
            btn_reset.pack(side="right")

        # =========================================================================
        # SECCIÓN 6: 🛡️ INFORMACIÓN DEL SISTEMA
        # =========================================================================
        sec_info = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_info.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(sec_info, text="🛡️ Información del Sistema y Licencia", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=20, pady=(15, 4))

        info_text = (
            "• Versión: Controlito v1.2.0 Empresarial\n"
            "• Privacidad: 100% Local y Privado. Sin servidores externos ni telemetría.\n"
            "• Base de Datos: SQLite 3 con modo WAL de alta velocidad y atomic backups.\n"
            "• Sincronización: Compatible con carpetas compartidas de Google Drive, OneDrive y Dropbox.\n"
            "• Tipografía: Segoe UI / Segoe UI Semibold (Windows Fluent Enterprise Typography).\n"
            "• Licencia: Código Abierto (MIT License). Gratuito y auditable.\n"
            "• Repositorio Oficial: https://github.com/EzeUndef/Controlito"
        )
        lbl_info = ctk.CTkLabel(
            sec_info,
            text=info_text,
            font=FONT_BODY,
            text_color=curr["text_muted"],
            justify="left"
        )
        lbl_info.pack(anchor="w", padx=20, pady=(0, 12))

        info_btn_row = ctk.CTkFrame(sec_info, fg_color="transparent")
        info_btn_row.pack(fill="x", padx=20, pady=(0, 15))

        btn_check_updates = ctk.CTkButton(
            info_btn_row,
            text="🔍 Buscar Actualizaciones Ahora",
            font=FONT_BODY_BOLD,
            height=34,
            fg_color=curr["primary"],
            hover_color=curr["primary_hover"],
            command=self._check_updates_manually
        )
        btn_check_updates.pack(side="left")

    # --- HANDLERS ---
    def _check_updates_manually(self):
        """Manually triggers update check and notifies the user."""
        import threading
        from utils.updater import check_for_updates

        def _worker():
            try:
                info = check_for_updates(timeout=5)
                if info and info.get("has_update"):
                    from ui.update_dialog import UpdateDialog
                    self.after(0, lambda: UpdateDialog(self.winfo_toplevel(), info))
                elif info:
                    self.after(0, lambda: messagebox.showinfo(
                        "Controlito Actualizado",
                        f"¡Tienes la versión más reciente ({info.get('current_version')})!\nNo hay actualizaciones pendientes disponibles."
                    ))
                else:
                    self.after(0, lambda: messagebox.showwarning(
                        "Sin Conexión",
                        "No se pudo conectar con el servidor de actualizaciones en GitHub.\nRevisa tu conexión a internet e inténtalo nuevamente."
                    ))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error al verificar actualizaciones:\n{e}"))

        threading.Thread(target=_worker, daemon=True).start()
    def _create_backup(self):
        """Creates a timestamped backup in the user's chosen location."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        default_filename = f"Controlito_Backup_{timestamp}.db"

        file_path = filedialog.asksaveasfilename(
            title="Guardar Copia de Seguridad",
            defaultextension=".db",
            initialfile=default_filename,
            filetypes=[("Base de Datos SQLite", "*.db"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            self.db.backup_database(file_path)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            messagebox.showinfo(
                "Copia de Seguridad Creada",
                f"La copia de seguridad se generó exitosamente:\n\n{file_path}\n\nTamaño: {file_size_mb:.2f} MB\n"
                "Puedes guardar este archivo en un pendrive o en tu correo para restaurarlo en cualquier computadora."
            )
        except Exception as e:
            messagebox.showerror("Error al Crear Backup", f"No se pudo crear la copia de seguridad:\n{str(e)}")

    def _restore_backup(self):
        """Restores a backup file into the active database."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Copia de Seguridad a Restaurar",
            filetypes=[("Base de Datos SQLite", "*.db *.sqlite"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        confirm = messagebox.askyesno(
            "Confirmar Restauración de Copia de Seguridad",
            f"¿Estás seguro de que deseas restaurar la base de datos desde este archivo?\n\n{file_path}\n\n"
            "ADVERTENCIA: Los datos actuales se reemplazarán con la información del backup seleccionado."
        )
        if not confirm:
            return

        try:
            self.db.restore_database(file_path)
            messagebox.showinfo(
                "Restauración Exitosa",
                "Los datos se restauraron correctamente.\nLa interfaz se actualizará con tu información respaldada."
            )
            if self.on_database_changed:
                self.on_database_changed(self.db.db_path)
        except Exception as e:
            messagebox.showerror("Error al Restaurar", f"No se pudo restaurar la copia de seguridad:\n{str(e)}")

    def _choose_cloud_folder(self):
        """Connects or moves the database to a cloud/synced directory (e.g. Google Drive, OneDrive)."""
        folder = filedialog.askdirectory(
            title="Seleccionar Carpeta Sincronizada (Google Drive, OneDrive, etc.)"
        )
        if not folder:
            return

        target_db_path = os.path.normpath(os.path.join(folder, "controlito.db"))

        if os.path.exists(target_db_path):
            # Existing database found in chosen cloud folder
            use_existing = messagebox.askyesno(
                "Base Existente Detectada",
                f"Se encontró un archivo 'controlito.db' en la carpeta seleccionada:\n{target_db_path}\n\n"
                "¿Deseas conectar y usar esta base de datos existente (por ejemplo, proveniente de otra PC)?\n\n"
                "• Sí: Conectar a la base existente.\n"
                "• No: Cancelar para no sobreescribir tus datos."
            )
            if not use_existing:
                return
        else:
            # Copy current database to the new location
            try:
                self.db.backup_database(target_db_path)
            except Exception as e:
                messagebox.showerror("Error al copiar base", f"No se pudo copiar la base a la carpeta elegida:\n{str(e)}")
                return

        # Save preference in config.json
        try:
            DatabaseManager.set_custom_db_path(target_db_path)
            messagebox.showinfo(
                "Sincronización en la Nube Configurada",
                f"¡Base de datos vinculada con éxito!\n\nUbicación activa:\n{target_db_path}\n\n"
                "Cualquier cambio que realices se guardará en esta carpeta sincronizada para estar disponible en tus otras computadoras."
            )
            if self.on_database_changed:
                self.on_database_changed(target_db_path)
        except Exception as e:
            messagebox.showerror("Error al Configurar Nube", f"Ocurrió un error al actualizar la configuración:\n{str(e)}")

    def _reset_to_default_db(self):
        """Switches back to the default local path (~/.controlito/controlito.db)."""
        confirm = messagebox.askyesno(
            "Volver a Almacenamiento Local Predeterminado",
            "¿Deseas volver a utilizar la ubicación local predeterminada de Controlito en tu computadora?\n\n"
            f"Ubicación: {DatabaseManager.DEFAULT_DB_FILE}"
        )
        if not confirm:
            return

        default_path = DatabaseManager.reset_to_default_db()
        messagebox.showinfo(
            "Ubicación Restablecida",
            f"Se restableció la ubicación a la base local predeterminada:\n{default_path}"
        )
        if self.on_database_changed:
            self.on_database_changed(default_path)

    def _open_data_folder(self):
        try:
            folder = os.path.dirname(self.db.db_path)
            os.makedirs(folder, exist_ok=True)
            subprocess.run(f'explorer "{folder}"', shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta de datos:\n{str(e)}")

    def _apply_theme(self, name):
        ThemeManager.set_theme(name)
        if self.db:
            self.db.set_setting("theme", name)
        if self.on_theme_change:
            self.on_theme_change(name)

    def _on_dolar_change(self, val):
        if self.db:
            self.db.set_setting("dolar_rate_type", val)

    def _normalize_categories(self):
        if not self.db:
            return
        updated_count = normalize_database_categories(self.db)
        messagebox.showinfo(
            "Normalización de Categorías",
            f"Proceso completado con éxito.\nSe actualizaron {updated_count} movimientos a categorías canónicas sinónimas."
        )
