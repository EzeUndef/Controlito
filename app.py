"""Main Application Window for Controlito."""
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

from database.db_manager import DatabaseManager
from utils.excel_importer import import_excel
from ui.theme import BG_MAIN, BG_CARD
from ui.sidebar import Sidebar
from ui.dashboard import DashboardView
from ui.transactions import TransactionsView
from ui.services import ServicesView
from ui.bank_accounts import BankAccountsView
from ui.budget import BudgetView
from ui.advisor import AdvisorView
from ui.categories import CategoriesView
from ui.simple_chat import SimpleChatView
from ui.onboarding import OnboardingView
from ui.settings_view import SettingsView


class ControlitoApp(ctk.CTk):
    def __init__(self, db_path=None):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Apply 'clam' ttk theme once at startup (prevents freeze on each navigation)
        try:
            from tkinter import ttk as _ttk
            _ttk.Style().theme_use("clam")
        except Exception:
            pass

        self.title("Controlito - Software de Finanzas y Control de Gastos")
        self.geometry("1180x750")
        self.minsize(980, 620)

        # Database initialization
        self.db = DatabaseManager(db_path)

        # Load saved theme preference
        from ui.theme import ThemeManager, BG_MAIN, BG_SIDEBAR
        saved_theme = self.db.get_setting("theme", "💼 Corporate Slate")
        ThemeManager.set_theme(saved_theme)

        # Layout: Sidebar on left, Content on right
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.current_mode = "data"  # "data" or "simple"

        self.sidebar = Sidebar(
            self,
            on_navigate=self.navigate_to,
            on_import_excel=self.import_excel_dialog,
            on_toggle_mode=self.toggle_mode,
            on_theme_change=self.handle_theme_changed,
            initial_theme=saved_theme,
            on_reset_onboarding=self.confirm_reset_onboarding,
            db=self.db
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_area = ctk.CTkFrame(self, fg_color=ThemeManager.get_current_theme()["bg_main"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Views dictionary
        self.views = {}
        self.current_view_key = None

        # Ensure clean application termination (never leaves background processes)
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

        # Check onboarding status
        is_onboarded = self.db.get_setting("onboarding_completed") == "1"
        if not is_onboarded:
            self.show_onboarding()
        else:
            self.navigate_to("dashboard")

    def on_app_close(self):
        """Cleanly terminates the application, closes DB connections and exits without background residency."""
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
        import sys
        sys.exit(0)

    def show_onboarding(self):
        for child in self.content_area.winfo_children():
            child.destroy()
        self.sidebar.grid_remove()
        view = OnboardingView(self.content_area, self.db, on_complete=self.finish_onboarding)
        view.pack(fill="both", expand=True)

    def finish_onboarding(self):
        self.sidebar.grid()
        self.current_view_key = None
        self.navigate_to("dashboard")

    def confirm_reset_onboarding(self):
        if messagebox.askyesno(
            "Reiniciar Base de Datos",
            "¿Deseas volver a la pantalla de bienvenida inicial?\nPodrás cargar otro archivo Excel o arrancar de 0 con una base limpia."
        ):
            self.show_onboarding()

    def handle_theme_changed(self, theme_name):
        from ui.theme import ThemeManager, configure_treeview_style
        self.db.set_setting("theme", theme_name)
        curr = ThemeManager.get_current_theme()
        configure_treeview_style(curr)
        self.sidebar.configure(fg_color=curr["bg_sidebar"])
        self.content_area.configure(fg_color=curr["bg_main"])
        # Update sidebar buttons colors
        for k, btn in self.sidebar.buttons.items():
            if k == self.sidebar.active_tab:
                btn.configure(fg_color=curr["primary"], text_color=curr["text_main"], hover_color=curr["primary_hover"])
            else:
                btn.configure(fg_color="transparent", text_color=curr["text_muted"], hover_color=curr["primary_hover"])
        # Reload current view with the new theme colors
        active_key = self.current_view_key
        self.current_view_key = None
        self.navigate_to(active_key or "dashboard")

    def toggle_mode(self, mode):
        self.current_mode = mode
        if mode == "simple":
            # Hide sidebar for pure minimalist chat experience
            self.sidebar.grid_remove()
            self.current_view_key = None
            self.navigate_to("chat")
        else:
            # Restore sidebar for full data experience
            self.sidebar.grid()
            self.sidebar.mode_seg.set("📊 Data")
            self.current_view_key = None
            self.navigate_to("dashboard")

    def navigate_to(self, key):
        if self.current_view_key == key:
            return

        # Destroy old view or hide
        for child in self.content_area.winfo_children():
            child.destroy()

        if key == "chat":
            view = SimpleChatView(
                self.content_area,
                self.db,
                on_switch_to_data=lambda: self.toggle_mode("data"),
                on_theme_change=self.handle_theme_changed
            )
        elif key == "dashboard":
            view = DashboardView(self.content_area, self.db, on_navigate=self.navigate_to)
        elif key == "transactions":
            view = TransactionsView(self.content_area, self.db, on_data_changed=self.on_data_updated)
        elif key == "categories":
            view = CategoriesView(self.content_area, self.db, on_data_changed=self.on_data_updated)
        elif key == "services":
            view = ServicesView(self.content_area, self.db, on_data_changed=self.on_data_updated)
        elif key == "bank_accounts":
            view = BankAccountsView(self.content_area, self.db, on_data_changed=self.on_data_updated)
        elif key == "budget":
            view = BudgetView(self.content_area, self.db, on_data_changed=self.on_data_updated)
        elif key == "advisor":
            view = AdvisorView(self.content_area, self.db)
        elif key == "settings":
            view = SettingsView(
                self.content_area,
                self.db,
                on_theme_change=self.handle_theme_changed,
                on_import_excel=self.import_excel_dialog,
                on_reset_onboarding=self.confirm_reset_onboarding
            )
        else:
            view = DashboardView(self.content_area, self.db, on_navigate=self.navigate_to)

        view.grid(row=0, column=0, sticky="nsew")
        self.current_view_key = key

    def on_data_updated(self):
        # Refresh current view if needed
        pass

    def import_excel_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel de Controlito",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        # Create modal progress dialog
        progress_dlg = ctk.CTkToplevel(self)
        progress_dlg.title("Importando Datos...")
        progress_dlg.geometry("420x160")
        progress_dlg.resizable(False, False)
        progress_dlg.transient(self)
        progress_dlg.grab_set()
        progress_dlg.protocol("WM_DELETE_WINDOW", lambda v=progress_dlg: [v.grab_release(), v.destroy()])

        lbl_status = ctk.CTkLabel(progress_dlg, text="Iniciando importación...", font=("Segoe UI", 12))
        lbl_status.pack(pady=(25, 10))

        bar = ctk.CTkProgressBar(progress_dlg, width=320)
        bar.pack(pady=5)
        bar.set(0)

        self.update_idletasks()

        def progress_cb(pct, msg):
            bar.set(pct)
            lbl_status.configure(text=msg)
            progress_dlg.update()

        try:
            results = import_excel(self.db, file_path, progress_callback=progress_cb)
            progress_dlg.destroy()

            total_imported = sum(v for k, v in results.items() if isinstance(v, int))
            messagebox.showinfo(
                "Importación Exitosa",
                f"Se importaron exitosamente {total_imported} registros desde:\n{os.path.basename(file_path)}"
            )
            # Reload active view
            active = self.current_view_key
            self.current_view_key = None
            self.navigate_to(active or "dashboard")
        except Exception as e:
            progress_dlg.destroy()
            messagebox.showerror("Error al importar", f"Ocurrió un error al procesar el archivo:\n{str(e)}")


def run():
    app = ControlitoApp()
    app.mainloop()


if __name__ == "__main__":
    run()
