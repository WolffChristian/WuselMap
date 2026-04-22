import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import pandas as pd
import database_manager as db

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EditDialog(ctk.CTkToplevel):
    """Das Kommando-Fenster zum Bearbeiten von Einträgen"""
    def __init__(self, parent, title, data, save_callback):
        super().__init__(parent)
        self.title(title)
        self.geometry("550x750")
        self.save_callback = save_callback
        self.entries = {}
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="Eintrag bearbeiten", font=("Arial", 22, "bold")).pack(pady=20)

        # Scrollbarer Bereich für viele Spalten
        scroll = ctk.CTkScrollableFrame(self, width=500, height=550)
        scroll.pack(padx=20, pady=10, fill="both", expand=True)

        for key, value in data.items():
            if key == "id": continue
            frame = ctk.CTkFrame(scroll, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(frame, text=key.capitalize(), width=130, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.insert(0, str(value) if value is not None else "")
            entry.pack(side="right", expand=True, fill="x")
            self.entries[key] = entry

        ctk.CTkButton(self, text="💾 Änderungen speichern", fg_color="#1e8449", height=45,
                      font=("Arial", 16, "bold"), command=self.save).pack(pady=25)

    def save(self):
        neue_daten = {k: v.get() for k, v in self.entries.items()}
        self.save_callback(neue_daten)
        self.destroy()

class WuselMasterConsole(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WuselMap - Master Control Center 1.0")
        self.geometry("1400x850")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="Wusel-Zentrale 🕹️", font=("Arial", 22, "bold")).pack(pady=30)

        self.create_sidebar_button("🏗️ Spielplätze", "spielplaetze")
        self.create_sidebar_button("👥 Nutzerverwaltung", "nutzer")
        self.create_sidebar_button("📥 Vorschläge", "vorschlaege")
        self.create_sidebar_button("💬 Feedback", "feedback")

        # --- MAIN ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.current_table = "spielplaetze"
        self.full_df = pd.DataFrame()
        self.switch_view("spielplaetze")

    def create_sidebar_button(self, text, table):
        btn = ctk.CTkButton(self.sidebar, text=text, command=lambda: self.switch_view(table))
        btn.pack(pady=10, padx=20)

    def switch_view(self, table_name):
        self.current_table = table_name
        for widget in self.main_frame.winfo_children(): widget.destroy()
        
        # Top Bar mit Suche
        top = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(top, text=f"Verwaltung: {table_name.upper()}", font=("Arial", 20, "bold")).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_data)
        ctk.CTkEntry(top, placeholder_text="🔍 Live-Suche...", textvariable=self.search_var, width=350).pack(side="right")

        # Tabelle
        cols_map = {
            "spielplaetze": ["id", "Standort", "stadt", "status", "plz"],
            "nutzer": ["id", "benutzername", "email", "rolle"],
            "vorschlaege": ["id", "standort", "stadt", "status"],
            "feedback": ["id", "nutzername", "nachricht"]
        }
        self.current_cols = cols_map.get(table_name, ["id"])

        tree_frame = ctk.CTkFrame(self.main_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=self.current_cols, show="headings")
        for col in self.current_cols:
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=150, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.refresh_table_data()

        # Footer Buttons
        btns = ctk.CTkFrame(self.main_frame, height=80)
        btns.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(btns, text="🗑️ Markierten Eintrag löschen", fg_color="#922b21", command=self.handle_delete).pack(side="left", padx=10)
        
        if table_name == "nutzer":
            ctk.CTkButton(btns, text="🚫 Sperren", fg_color="#d35400", command=lambda: self.handle_status("gesperrt")).pack(side="left", padx=5)
            ctk.CTkButton(btns, text="✅ Aktivieren", fg_color="#1e8449", command=lambda: self.handle_status("user")).pack(side="left", padx=5)

    def refresh_table_data(self):
        self.full_df = db.hole_df(self.current_table)
        self.update_tree(self.full_df)

    def update_tree(self, df):
        for item in self.tree.get_children(): self.tree.delete(item)
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=[row.get(c, "") for c in self.current_cols])

    def filter_data(self, *args):
        q = self.search_var.get().lower()
        filtered = self.full_df[self.full_df.apply(lambda r: q in str(r).lower(), axis=1)]
        self.update_tree(filtered)

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l): self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def on_double_click(self, event):
        sel = self.tree.selection()
        if not sel: return
        item_id = self.tree.item(sel[0])['values'][0]
        row_data = self.full_df[self.full_df['id'] == int(item_id)].iloc[0].to_dict()

        def save_callback(neue_daten):
            if db.aktualisiere_spielplatz(item_id, neue_daten):
                self.refresh_table_data()

        EditDialog(self, f"Editor - {self.current_table.capitalize()}", row_data, save_callback)

    def handle_delete(self):
        sel = self.tree.selection()
        if not sel: return
        item_id = self.tree.item(sel[0])['values'][0]
        if self.current_table == "spielplaetze": db.loesche_spielplatz(item_id)
        elif self.current_table == "nutzer": db.loesche_nutzer(item_id)
        self.refresh_table_data()

    def handle_status(self, stat):
        sel = self.tree.selection()
        if not sel: return
        db.setze_nutzer_status(self.tree.item(sel[0])['values'][0], stat)
        self.refresh_table_data()

if __name__ == "__main__":
    app = WuselMasterConsole()
    app.mainloop()