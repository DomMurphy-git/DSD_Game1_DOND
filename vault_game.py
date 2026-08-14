import tkinter as tk
from tkinter import messagebox
import random

class VaultDilemma:
    def __init__(self, root):
        self.root = root
        self.root.title("The Vault Dilemma")
        self.root.geometry("600x500")
        self.root.configure(bg="#2b2b2b")

        # Game Data
        self.all_values = [1, 5, 10, 50, 100, 250, 500, 750, 
                           1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000]
        self.vault_contents = self.all_values.copy()
        random.shuffle(self.vault_contents) # Shuffle the money into random vaults
        
        self.my_vault = None
        self.my_vault_value = None
        self.vaults_opened = 0
        self.buttons = []

        # UI Setup
        self.info_label = tk.Label(root, text="Step 1: Pick your personal vault!", 
                                   font=("Arial", 16, "bold"), bg="#2b2b2b", fg="white")
        self.info_label.pack(pady=20)

        # Create a grid for the 16 Vaults
        self.grid_frame = tk.Frame(root, bg="#2b2b2b")
        self.grid_frame.pack()

        for i in range(16):
            btn = tk.Button(self.grid_frame, text=f"Vault {i+1}", width=10, height=3, 
                            font=("Arial", 12, "bold"), bg="#d9d9d9",
                            command=lambda idx=i: self.vault_clicked(idx))
            
            # Math to arrange buttons in a 4x4 grid
            row = i // 4
            col = i % 4
            btn.grid(row=row, column=col, padx=10, pady=10)
            self.buttons.append(btn)

    def vault_clicked(self, index):
        btn = self.buttons[index]
        value = self.vault_contents[index]

        # State 1: Picking your own vault
        if self.my_vault is None:
            self.my_vault = index
            self.my_vault_value = value
            btn.config(bg="gold", text="MY VAULT", state="disabled")
            self.info_label.config(text="Now, open vaults to eliminate values.")
            return

        # State 2: Opening other vaults
        btn.config(text=f"${value:,}", state="disabled", bg="#ff4d4d")
        self.all_values.remove(value)
        self.vaults_opened += 1

        # State 3: The "Banker" Offer (every 3 vaults opened)
        if self.vaults_opened % 3 == 0 and len(self.all_values) > 1:
            self.make_offer()
            
        # State 4: End of Game (Only your vault is left)
        if len(self.all_values) == 1:
            messagebox.showinfo("Game Over", f"You kept your vault!\nInside was: ${self.my_vault_value:,}")
            self.root.destroy()

    def make_offer(self):
        # Offer is roughly the average of remaining values
        average = sum(self.all_values) / len(self.all_values)
        offer = int(average * 0.8) # Banker undercuts the true average slightly
        
        response = messagebox.askyesno("The Merchant Offers...", 
                                       f"The Merchant offers to buy your vault for: ${offer:,}\n\nDeal or No Deal?")
        
        if response: # Player clicked Yes (Deal)
            messagebox.showinfo("Deal!", f"You took the deal for ${offer:,}!\nYour original vault had ${self.my_vault_value:,}.")
            self.root.destroy()
        else: # Player clicked No (No Deal)
            self.info_label.config(text="No Deal! Keep opening vaults.")

if __name__ == "__main__":
    window = tk.Tk()
    game = VaultDilemma(window)
    window.mainloop()