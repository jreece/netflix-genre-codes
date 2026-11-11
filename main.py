"""Local Netflix genre explorer. Run: python main.py"""
import json
import sys
import webbrowser
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "netflix_codes.json"
# Save preferences outside the app folder so packaged builds can persist favorites.
USER_DIR = Path.home() / ".netflix_code_explorer"
FAV_PATH = USER_DIR / "favorites.json"
NETFLIX_URL = "https://www.netflix.com/browse/genre/{}"


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return default


def save_favorites(favorites):
    try:
        USER_DIR.mkdir(parents=True, exist_ok=True)
        FAV_PATH.write_text(json.dumps(sorted(favorites), indent=2), encoding="utf-8")
    except OSError as exc:
        messagebox.showerror("Unable to save favorites", str(exc))


def resource_path(filename):
    # PyInstaller bundles data in _MEIPASS.
    return Path(getattr(sys, "_MEIPASS", BASE)) / filename


class NetflixExplorer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Netflix Code Explorer")
        self.geometry("1280x1020")
        self.minsize(1000, 800)
        self.configure(fg_color="#141414")
        self.data = load_json(resource_path("netflix_codes.json"), [])
        if not self.data:
            messagebox.showerror("Missing data", "Could not load netflix_codes.json")
        self.favorites = set(str(x) for x in load_json(FAV_PATH, []))
        self.search = ctk.StringVar()
        self.group = ctk.StringVar(value="All genres")
        self.sort = ctk.StringVar(value="Grouped")
        self.favorites_only = False
        self.build_ui()
        self.render()
        self.search_after_id = None

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=26, pady=(24, 10))
        ctk.CTkLabel(header, text="NETFLIX CODE EXPLORER", text_color="#E50914",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Browse hidden genre categories • Open them directly in Netflix",
                     text_color="#AAAAAA", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(4, 0))

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=26, pady=(12, 8))
        search = ctk.CTkEntry(controls, textvariable=self.search,
                              placeholder_text="Search by genre, group, or code...", height=40)
        search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search.trace_add("write", lambda *_: self.schedule_search_render())
        groups = ["All genres"] + sorted({x["group"] for x in self.data})
        ctk.CTkOptionMenu(controls, variable=self.group, values=groups,
                          width=185, height=40, command=lambda _: self.render()).pack(side="left", padx=(0, 10))
        ctk.CTkOptionMenu(controls, variable=self.sort,
                          values=["Grouped", "Name A–Z", "Code ascending"],
                          width=150, height=40, command=lambda _: self.render()).pack(side="left")

        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", padx=26, pady=(8, 10))
        self.all_btn = ctk.CTkButton(tabs, text="All categories", width=140,
                                     command=lambda: self.set_tab(False))
        self.all_btn.pack(side="left", padx=(0, 8))
        self.fav_btn = ctk.CTkButton(tabs, text="★ Favorites", width=140,
                                     command=lambda: self.set_tab(True))
        self.fav_btn.pack(side="left")
        self.summary = ctk.CTkLabel(tabs, text="", text_color="#AAAAAA")
        self.summary.pack(side="right")

        self.results = ctk.CTkScrollableFrame(self, fg_color="#191919", corner_radius=12)
        self.results.pack(fill="both", expand=True, padx=26, pady=(0, 10))
        self.results.grid_columnconfigure(0, weight=1)
        self.results.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Independent local browser • Netflix login and internet required for links • Codes may vary by region",
                     text_color="#888888", font=ctk.CTkFont(size=11)).pack(pady=(0, 12))

    def set_tab(self, favorites_only):
        self.favorites_only = favorites_only
        self.render()

    def toggle_favorite(self, code):
        if code in self.favorites:
            self.favorites.remove(code)
        else:
            self.favorites.add(code)
        save_favorites(self.favorites)
        self.render()

    def render(self):
        if not hasattr(self, "results"):
            return
        query = self.search.get().strip().casefold()
        group = self.group.get()
        items = [x for x in self.data
                 if (group == "All genres" or x["group"] == group)
                 and (not query or query in (x["name"] + " " + x["group"] + " " + x["code"]).casefold())
                 and (not self.favorites_only or x["code"] in self.favorites)]
        if self.sort.get() == "Name A–Z":
            items.sort(key=lambda x: x["name"].casefold())
        elif self.sort.get() == "Code ascending":
            items.sort(key=lambda x: int(x["code"]))
        else:
            items.sort(key=lambda x: (x["group"].casefold(), x["name"].casefold()))
        self.all_btn.configure(fg_color="#E50914" if not self.favorites_only else "#393939")
        self.fav_btn.configure(fg_color="#E50914" if self.favorites_only else "#393939")
        self.summary.configure(text=f"{len(items)} categories  •  {len(self.favorites)} favorites")
        for child in self.results.winfo_children():
            child.destroy()
        if not items:
            ctk.CTkLabel(self.results, text="No matching categories. Try another search or filter.",
                         text_color="#AAAAAA").grid(row=0, column=0, columnspan=2, pady=40)
            return
        for index, item in enumerate(items):
            self.add_card(item, index // 2, index % 2)

    def add_card(self, item, row, col):
        card = ctk.CTkFrame(self.results, fg_color="#282828", corner_radius=10)
        card.grid(row=row, column=col, sticky="nsew", padx=7, pady=7)
        ctk.CTkLabel(card, text=item["group"].upper(), text_color="#A0A0A0",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=14, pady=(12, 3))
        ctk.CTkLabel(card, text=item["name"], anchor="w", wraplength=360,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(fill="x", padx=14)
        bottom = ctk.CTkFrame(card, fg_color="transparent")
        bottom.pack(fill="x", padx=14, pady=(10, 12))
        ctk.CTkLabel(bottom, text="#" + item["code"], text_color="#BBBBBB").pack(side="left")
        ctk.CTkButton(bottom, text="Open ↗", width=72, height=30, fg_color="#E50914",
                      hover_color="#B20710", command=lambda c=item["code"]: webbrowser.open(NETFLIX_URL.format(c))).pack(side="right")
        ctk.CTkButton(bottom, text="★" if item["code"] in self.favorites else "☆",
                      width=36, height=30, fg_color="#444444", hover_color="#666666",
                      command=lambda c=item["code"]: self.toggle_favorite(c)).pack(side="right", padx=(0, 7))
        ctk.CTkButton(bottom, text="Copy", width=52, height=30, fg_color="#444444",
                      hover_color="#666666", command=lambda c=item["code"]: self.copy_code(c)).pack(side="right", padx=(0, 7))

    def copy_code(self, code):
        self.clipboard_clear()
        self.clipboard_append(code)
        self.update()  # Keep clipboard available after the app closes.

    # Add this method to NetflixExplorer
    def schedule_search_render(self):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(250, self.render)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    NetflixExplorer().mainloop()
