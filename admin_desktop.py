import customtkinter as ctk
from tkinter import ttk, filedialog
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import database_manager as db 
from PIL import Image
import io
import base64
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, data, save_callback, is_new=False):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x900")
        self.save_callback = save_callback
        self.entries = {}
        self.current_image_base64 = data.get("bild_data", "")
        
        self.attributes("-topmost", True)
        self.grab_set()

        ctk.CTkLabel(self, text="Eintrag Details", font=("Arial", 22, "bold")).pack(pady=10)

        # --- BILD BEREICH ---
        self.img_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.img_frame.pack(pady=10)
        
        self.img_label = ctk.CTkLabel(self.img_frame, text="Kein Bild vorhanden")
        self.img_label.pack()
        
        self.update_image_preview(self.current_image_base64)

        ctk.CTkButton(self.img_frame, text="📷 Bild auswählen", 
                      command=self.choose_image, fg_color="#5dade2").pack(pady=5)

        # --- SCROLL BEREICH ---
        scroll = ctk.CTkScrollableFrame(self, width=550, height=450)
        scroll.pack(padx=20, pady=10, fill="both", expand=True)

        for key in sorted(data.keys()):
            if key in ["id", "created_at", "updated_at", "bild_data", "distance"]: continue
            
            frame = ctk.CTkFrame(scroll, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=key.capitalize(), width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            val = data[key]
            entry.insert(0, str(val) if val is not None and str(val).lower() != "nan" else "")
            entry.pack(side="right", expand=True, fill="x")
            self.entries[key] = entry

        # --- BUTTONS ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", padx=50)

        btn_text = "✨ Erstellen" if is_new else "💾 Speichern"
        ctk.CTkButton(btn_frame, text=btn_text, fg_color="#1e8449", height=45,
                      command=self.save).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(btn_frame, text="Abbrechen", fg_color="#922b21", height=45,
                      command=self.destroy).pack(side="left", expand=True, padx=5)

    def update_image_preview(self, b64_str):
        if b64_str and str(b64_str).lower() != "nan":
            try:
                img_bytes = base64.b64decode(b64_str)
                img = Image.open(io.BytesIO(img_bytes))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 150))
                self.img_label.configure(image=ctk_img, text="")
            except:
                self.img_label.configure(text="Bildfehler")

    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Bilder", "*.jpg *.jpeg *.png")])
        if file_path:
            with open(file_path, "rb") as f:
                optimized = db.optimiere_bild(f) # Nutzt deine Funktion aus dem DB Manager
                if optimized:
                    self.current_image_base64 = optimized
                    self.update_image_preview(optimized)

    def save(self):
        daten = {k: v.get() for k, v in self.entries.items()}
        daten["bild_data"] = self.current_image_base64
        if self.save_callback(daten):
            self.destroy()

class WuselMasterConsole(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WuselMap - Master Control Center")
        self.geometry("1400x900")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # LOGO LADEN
        try:
            logo_img = Image.open("logo.png")
            self.logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(180, 180))
            ctk.CTkLabel(self.sidebar, image=self.logo, text="").pack(pady=20)
        except:
            ctk.CTkLabel(self.sidebar, text="WUSELMAP", font=("Arial", 24, "bold")).pack(pady=20)

        self.create_sidebar_button("🏗️ Spielplätze", "spielplaetze")
        self.create_sidebar_button("👥 Nutzer", "nutzer")
        self.create_sidebar_button("📥 Vorschläge", "vorschlaege")
        self.create_sidebar_button("💬 Feedback", "feedback")

        # --- MAIN ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.current_table = "spielplaetze"
        self.full_df = pd.DataFrame()
        self.switch_view("spielplaetze")

    def create_sidebar_button(self, text, table):
        btn = ctk.CTkButton(self.sidebar, text=text, command=lambda: self.switch_view(table), 
                            height=40, font=("Arial", 14))
        btn.pack(pady=5, padx=20, fill="x")

    def switch_view(self, table_name):
        self.current_table = table_name
        for widget in self.main_frame.winfo_children(): widget.destroy()
        
        # Header & Suche
        top = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(top, text=f"Modul: {table_name.upper()}", font=("Arial", 20, "bold")).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_data)
        ctk.CTkEntry(top, placeholder_text="🔍 Suchen...", textvariable=self.search_var, width=300).pack(side="right")

        # Tabelle (Treeview)
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
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=150, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.refresh_table_data()

        # Footer Buttons
        btns = ctk.CTkFrame(self.main_frame, height=80, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(btns, text="➕ Neu", fg_color="#28b463", command=self.handle_add_new).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🗑️ Löschen", fg_color="#922b21", command=self.handle_delete).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🔄 Aktualisieren", command=self.refresh_table_data).pack(side="left", padx=5)

    def refresh_table_data(self):
        self.full_df = db.hole_df(self.current_table)
        self.update_tree(self.full_df)

    def update_tree(self, df):
        for item in self.tree.get_children(): self.tree.delete(item)
        for _, row in df.iterrows():
            # Kleine Spielerei: Markiere inaktive rot (theoretisch über Tags möglich)
            self.tree.insert("", "end", values=[row.get(c, "") for c in self.current_cols])

    def filter_data(self, *args):
        q = self.search_var.get().lower()
        if self.full_df.empty: return
        filtered = self.full_df[self.full_df.apply(lambda r: q in str(r).lower(), axis=1)]
        self.update_tree(filtered)

    def on_double_click(self, event):
        sel = self.tree.selection()
        if not sel: return
        item_id = self.tree.item(sel[0])['values'][0]
        row_data = self.full_df[self.full_df['id'] == int(item_id)].iloc[0].to_dict()

        def save_callback(neue_daten):
            if db.aktualisiere_eintrag(self.current_table, item_id, neue_daten):
                self.refresh_table_data()
                return True
            return False

        EditDialog(self, f"Edit ID: {item_id}", row_data, save_callback)

    def handle_add_new(self):
        if self.full_df.empty: return
        leere_daten = {col: "" for col in self.full_df.columns if col not in ["id", "created_at"]}
        
        def save_callback(neue_daten):
            # Wir nutzen deine speichere_spielplatz Funktion (Beispielhaft)
            success = db.speichere_spielplatz(
                neue_daten.get('Standort', 'Neu'), neue_daten.get('lat', 0), neue_daten.get('lon', 0),
                neue_daten.get('altersfreigabe', ''), neue_daten.get('bundesland', ''),
                neue_daten.get('plz', ''), neue_daten.get('stadt', ''),
                neue_daten.get('bild_data', ''), 'aktiv', neue_daten.get('ausstattung', ''),
                neue_daten.get('hat_schatten', 0), neue_daten.get('hat_sitze', 0),
                neue_daten.get('hat_wc', 0), neue_daten.get('adresse', ''), neue_daten.get('hat_parkplatz', 0)
            )
            if success: self.refresh_table_data(); return True
            return False

        EditDialog(self, "Neuer Eintrag", leere_daten, save_callback, is_new=True)

    def handle_delete(self):
        sel = self.tree.selection()
        if not sel: return
        item_id = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Löschen", "Diesen Eintrag wirklich löschen?"):
            if db.loesche_eintrag(self.current_table, item_id):
                self.refresh_table_data()

if __name__ == "__main__":
    app = WuselMasterConsole()
    app.mainloop()