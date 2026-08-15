import json
import os
import random
import sys
import tkinter as tk
from tkinter import messagebox

PROFILE_FILE = os.path.join(os.path.dirname(__file__), "player_progress.json")


def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}

    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def save_profiles(profiles):
    with open(PROFILE_FILE, "w", encoding="utf-8") as file:
        json.dump(profiles, file, indent=2)


def choose_player_name():
    profiles = load_profiles()
    existing_users = sorted(profiles.keys())

    selector = tk.Tk()
    selector.title("Choose Your Profile")
    selector.geometry("420x420")
    selector.configure(bg="#2b2b2b")
    selector.resizable(False, False)

    result = {"username": ""}

    def finalize_selection():
        username = name_entry.get().strip()
        if not username and selector_listbox.curselection():
            username = selector_listbox.get(selector_listbox.curselection()[0])

        if not username:
            messagebox.showwarning(
                "Missing Profile",
                "Please select an existing user or enter a new username.",
                parent=selector,
            )
            return

        result["username"] = username
        selector.destroy()

    def cancel_selection():
        selector.destroy()

    title_label = tk.Label(
        selector,
        text="Select an existing player or create a new one",
        font=("Arial", 16, "bold"),
        bg="#2b2b2b",
        fg="white",
    )
    title_label.pack(pady=(20, 10))

    selector_listbox = tk.Listbox(
        selector,
        width=28,
        height=10,
        font=("Arial", 12),
        exportselection=False,
    )
    if existing_users:
        for user in existing_users:
            selector_listbox.insert(tk.END, user)
    else:
        selector_listbox.insert(tk.END, "No saved players yet")
        selector_listbox.config(state="disabled")
    selector_listbox.pack(pady=10)

    def fill_from_selection(event=None):
        if selector_listbox.curselection() and selector_listbox["state"] != "disabled":
            selected_user = selector_listbox.get(selector_listbox.curselection()[0])
            name_entry.delete(0, tk.END)
            name_entry.insert(0, selected_user)

    selector_listbox.bind("<<ListboxSelect>>", fill_from_selection)

    tk.Label(
        selector,
        text="New username:",
        font=("Arial", 11, "bold"),
        bg="#2b2b2b",
        fg="white",
    ).pack()

    name_entry = tk.Entry(selector, width=28, font=("Arial", 12))
    name_entry.pack(pady=(0, 15))

    actions = tk.Frame(selector, bg="#2b2b2b")
    actions.pack()
    tk.Button(
        actions,
        text="Start Game",
        width=14,
        height=2,
        font=("Arial", 11, "bold"),
        command=finalize_selection,
    ).pack(side=tk.LEFT, padx=8)
    tk.Button(
        actions,
        text="Exit",
        width=10,
        height=2,
        font=("Arial", 11, "bold"),
        command=cancel_selection,
    ).pack(side=tk.LEFT, padx=8)

    selector.protocol("WM_DELETE_WINDOW", cancel_selection)
    selector.mainloop()
    return result["username"]


class VaultDilemma:
    def __init__(self, root, username):
        self.root = root
        self.username = username.strip() or "Player"
        self.profiles = load_profiles()
        self.profile = self.profiles.setdefault(
            self.username,
            {
                "username": self.username,
                "best_score": 0,
                "games_played": 0,
                "game_state": {},
            },
        )

        self.root.title(f"The Vault Dilemma - {self.username}")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))
        self.root.configure(bg="#2b2b2b")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.all_values = [1, 5, 10, 50, 100, 250, 500, 750,
                           1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000]
        self.vault_contents = self.all_values.copy()
        random.shuffle(self.vault_contents)

        self.my_vault = None
        self.my_vault_value = None
        self.vaults_opened = 0
        self.opened_vaults = []
        self.buttons = []

        self.info_label = tk.Label(
            root,
            text="Step 1: Pick your personal vault!",
            font=("Arial", 16, "bold"),
            bg="#2b2b2b",
            fg="white",
        )
        self.info_label.pack(pady=20)

        self.grid_frame = tk.Frame(root, bg="#2b2b2b")
        self.grid_frame.pack()

        for i in range(16):
            btn = tk.Button(
                self.grid_frame,
                text=f"Vault {i+1}",
                width=10,
                height=3,
                font=("Arial", 12, "bold"),
                bg="#d9d9d9",
                command=lambda idx=i: self.vault_clicked(idx),
            )
            row = i // 4
            col = i % 4
            btn.grid(row=row, column=col, padx=10, pady=10)
            self.buttons.append(btn)

        self.load_saved_progress()
        self.refresh_board()

    def load_saved_progress(self):
        saved_state = self.profile.get("game_state", {})
        if not saved_state:
            return

        if saved_state.get("active") and messagebox.askyesno(
            "Resume Progress",
            f"Welcome back, {self.username}! Resume your saved game?",
        ):
            self.my_vault = saved_state.get("my_vault")
            self.my_vault_value = saved_state.get("my_vault_value")
            self.vaults_opened = saved_state.get("vaults_opened", 0)
            self.opened_vaults = saved_state.get("opened_vaults", [])
            self.all_values = saved_state.get("all_values", self.all_values)
            self.vault_contents = saved_state.get("vault_contents", self.vault_contents)
            self.info_label.config(text=saved_state.get("status", "Continue your game."))
            return

        self.profile["game_state"] = {}
        save_profiles(self.profiles)

    def save_current_progress(self):
        self.profile["game_state"] = {
            "active": True,
            "my_vault": self.my_vault,
            "my_vault_value": self.my_vault_value,
            "vaults_opened": self.vaults_opened,
            "opened_vaults": self.opened_vaults,
            "all_values": self.all_values,
            "vault_contents": self.vault_contents,
            "status": self.info_label.cget("text"),
        }
        save_profiles(self.profiles)

    def clear_progress(self):
        self.profile["game_state"] = {}
        save_profiles(self.profiles)

    def refresh_board(self):
        for index, btn in enumerate(self.buttons):
            value = self.vault_contents[index]

            if self.my_vault == index:
                btn.config(text="MY VAULT", bg="gold", state="disabled")
            elif index in self.opened_vaults:
                btn.config(text=f"${value:,}", bg="#ff4d4d", state="disabled")
            else:
                btn.config(text=f"Vault {index + 1}", bg="#d9d9d9", state="normal")

    def finish_game(self, won, final_amount):
        self.profile["games_played"] = self.profile.get("games_played", 0) + 1
        self.profile["best_score"] = max(self.profile.get("best_score", 0), final_amount)
        self.profile["game_state"] = {}
        save_profiles(self.profiles)

        if won:
            messagebox.showinfo("Game Over", f"You kept your vault!\nInside was: ${self.my_vault_value:,}")
        else:
            messagebox.showinfo("Deal!", f"You took the deal for ${final_amount:,}!\nYour original vault had ${self.my_vault_value:,}.")

        self.root.destroy()

    def on_close(self):
        if self.my_vault is not None:
            self.save_current_progress()
        self.root.destroy()

    def vault_clicked(self, index):
        btn = self.buttons[index]
        value = self.vault_contents[index]

        if self.my_vault is None:
            self.my_vault = index
            self.my_vault_value = value
            btn.config(bg="gold", text="MY VAULT", state="disabled")
            self.info_label.config(text="Now, open vaults to eliminate values.")
            self.save_current_progress()
            return

        if index in self.opened_vaults:
            return

        self.opened_vaults.append(index)
        btn.config(text=f"${value:,}", state="disabled", bg="#ff4d4d")

        if value in self.all_values:
            self.all_values.remove(value)

        self.vaults_opened += 1
        self.save_current_progress()

        if self.vaults_opened % 3 == 0 and len(self.all_values) > 1:
            self.make_offer()

        if len(self.all_values) == 1:
            self.finish_game(True, self.my_vault_value)

    def make_offer(self):
        if len(self.all_values) <= 1:
            return

        average = sum(self.all_values) / len(self.all_values)
        offer = int(average * 0.8)

        response = messagebox.askyesno(
            "The Merchant Offers...",
            f"The Merchant offers to buy your vault for: ${offer:,}\n\nDeal or No Deal?",
        )

        if response:
            self.finish_game(False, offer)
        else:
            self.info_label.config(text="No Deal! Keep opening vaults.")
            self.save_current_progress()


if __name__ == "__main__":
    try:
        player_name = choose_player_name()
    except SystemExit:
        sys.exit()

    if not player_name:
        sys.exit()

    window = tk.Tk()
    game = VaultDilemma(window, player_name)
    window.mainloop()