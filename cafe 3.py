import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os

class RestaurantPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Bite Me Café ")
        self.root.geometry("1250x850")
        self.root.configure(bg="#AA1616")

        # Premium Color Palette
        self.colors = {
            "bg": "#f8fafc",
            "sidebar": "#ffffff",
            "header": "#0f172a",
            "accent": "#3b82f6",
            "success": "#22c55e",
            "danger": "#ef4444",
            "border": "#e2e8f0",
            "text_main": "#1e293b",
            "text_muted": "#64748b"
        }

        # Database Setup
        self.conn = sqlite3.connect('restaurant_pro.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

        # State
        self.cart = []
        self.tax_rate = 0.05
        
        self.setup_styles()
        self.setup_ui()
        self.load_menu_data()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS menu 
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                               name TEXT NOT NULL, 
                               price REAL NOT NULL, 
                               category TEXT)''')
        
        self.cursor.execute("SELECT count(*) FROM menu")
        if self.cursor.fetchone()[0] == 0:
            extended_menu = [
                # --- SIGNATURE MAINS ---
                ('Lobster Thermidor', 145.00, 'Main'),
                ('Beef Ribeye w/ Truffle', 135.00, 'Main'),
                ('Pan-Seared Sea Bass', 130.50, 'Main'),
                ('Duck Confit Orange', 130.00, 'Main'),
                ('Wild Mushroom ', 125.00, 'Main'),
                ('Rack of Lamb', 135.00, 'Main'),
                ('Grilled Salmon Steak', 24.50, 'Main'),
                ('Spicy Chicken Tikka', 16.00, 'Main'),
                ('Creamy Alfredo Pasta', 14.50, 'Main'),
                ('Vegetable Stir Fry', 12.00, 'Main'),
                ('Classic Burger', 18.50, 'Main'),
                ('Truffle Mushroom Pizza', 22.00, 'Main'),
                # --- EXQUISITE DESSERTS ---
                ('Gold Leaf Lava Cake', 15.00, 'Dessert'),
                ('Macaron Tower (6pc)', 18.00, 'Dessert'),
                ('Baked Alaska', 14.00, 'Dessert'),
                ('Classic Crème Brûlée', 11.00, 'Dessert'),
                ('New York Cheesecake', 8.50, 'Dessert'),
                ('Tiramisu Classico', 9.00, 'Dessert'),
                ('Belgian Waffle w/ Berry', 7.50, 'Dessert'),
                ('Mango Panna Cotta', 8.00, 'Dessert'),
                ('Soufflé du Jour', 13.50, 'Dessert'),
                # --- SIDES & BEVERAGES ---
                ('Artisan Iced Latte', 5.75, 'Beverage'),
                ('Vintage Red Wine (G)', 12.00, 'Beverage'),
                ('Parmesan Truffle Fries', 9.00, 'Side'),
                ('Garlic Butter Prawns', 14.00, 'Side'),
                ('Roasted Asparagus', 8.50, 'Side')
            ]
            self.cursor.executemany("INSERT INTO menu (name, price, category) VALUES (?, ?, ?)", extended_menu)
            self.conn.commit()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=self.colors['text_main'], 
                        rowheight=40, fieldbackground="white", font=("Inter", 10))
        style.map("Treeview", background=[('selected', self.colors['accent'])])
        style.configure("Treeview.Heading", font=("Inter", 11, "bold"), background="#f1f5f9", relief="flat")

    def setup_ui(self):
        # --- HEADER ---
        header = tk.Frame(self.root, bg=self.colors['header'], height=80)
        header.pack(fill="x")
        
        title_frame = tk.Frame(header, bg=self.colors['header'])
        title_frame.pack(side="left", padx=30, pady=10)
        
        tk.Label(title_frame, text="⚜ Bite Me Café ", font=("Helvetica", 22, "bold"), 
                 fg="white", bg=self.colors['header']).pack(anchor="w")
        
        # --- MAIN BODY ---
        main_body = tk.Frame(self.root, bg=self.colors['bg'])
        main_body.pack(fill="both", expand=True, padx=25, pady=25)

        # LEFT SIDE: MENU
        menu_frame = tk.Frame(main_body, bg=self.colors['bg'])
        menu_frame.place(relx=0, rely=0, relwidth=0.62, relheight=1)

        tk.Label(menu_frame, text="Gourmet Selection", font=("Inter", 16, "bold"), 
                 bg=self.colors['bg'], fg=self.colors['text_main']).pack(anchor="w", pady=(0, 10))

        # Menu Table
        cols = ("ID", "Name", "Price", "Category")
        self.menu_tree = ttk.Treeview(menu_frame, columns=cols, show="headings")
        for col in cols:
            self.menu_tree.heading(col, text=col.upper())
            self.menu_tree.column(col, width=80 if col == "ID" else (100 if col != "Name" else 280), anchor="center")
        
        self.menu_tree.tag_configure('oddrow', background='#f8fafc')
        self.menu_tree.tag_configure('evenrow', background='#ffffff')
        self.menu_tree.bind("<Double-1>", lambda e: self.add_to_cart())
        self.menu_tree.pack(fill="both", expand=True)

        # QUICK MANAGEMENT PANEL
        admin_frame = tk.LabelFrame(menu_frame, text=" ⚙️ Inventory Control ", font=("Inter", 9, "bold"),
                                   bg="white", relief="flat", bd=1, padx=20, pady=20)
        admin_frame.pack(fill="x", pady=(15, 0))

        tk.Label(admin_frame, text="New Item Name", bg="white", font=("Inter", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.ent_name = tk.Entry(admin_frame, width=22, relief="solid", bd=1, font=("Inter", 10))
        self.ent_name.grid(row=1, column=0, padx=(0, 15), pady=5)

        tk.Label(admin_frame, text="Price ($)", bg="white", font=("Inter", 8, "bold")).grid(row=0, column=1, sticky="w")
        self.ent_price = tk.Entry(admin_frame, width=12, relief="solid", bd=1, font=("Inter", 10))
        self.ent_price.grid(row=1, column=1, padx=(0, 15), pady=5)

        tk.Label(admin_frame, text="Category", bg="white", font=("Inter", 8, "bold")).grid(row=0, column=2, sticky="w")
        self.ent_cat = ttk.Combobox(admin_frame, values=["Main", "Beverage", "Dessert", "Side"], width=14, font=("Inter", 10))
        self.ent_cat.grid(row=1, column=2, padx=(0, 15), pady=5)

        tk.Button(admin_frame, text="Add Dish", command=self.db_add_item, bg=self.colors['success'], 
                  fg="white", font=("Inter", 9, "bold"), relief="flat", width=12, pady=5).grid(row=1, column=3, padx=5)
        tk.Button(admin_frame, text="Remove Dish", command=self.db_delete_item, bg=self.colors['danger'], 
                  fg="white", font=("Inter", 9, "bold"), relief="flat", width=12, pady=5).grid(row=1, column=4)

        # RIGHT SIDE: BILLING
        billing_frame = tk.Frame(main_body, bg="white", bd=1, relief="solid", highlightbackground=self.colors['border'])
        billing_frame.place(relx=0.65, rely=0, relwidth=0.35, relheight=1)

        tk.Label(billing_frame, text="Current Order", font=("Inter", 16, "bold"), bg="white").pack(pady=25)
        
        # Scrollable Cart
        cart_scroll = tk.Scrollbar(billing_frame)
        cart_scroll.pack(side="right", fill="y")
        
        self.cart_list = tk.Listbox(billing_frame, font=("Courier New", 11), bd=0, bg="#fcfcfc", 
                                   yscrollcommand=cart_scroll.set, selectmode="none", highlightthickness=0)
        self.cart_list.pack(fill="both", expand=True, padx=20)
        cart_scroll.config(command=self.cart_list.yview)

        # TOTALS SECTION
        totals_frame = tk.Frame(billing_frame, bg="#f8fafc", pady=25, padx=30)
        totals_frame.pack(fill="x")

        def add_summary_line(label, value_label, size=10, is_bold=False, color=None):
            f = tk.Frame(totals_frame, bg="#f8fafc")
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, bg="#f8fafc", font=("Inter", size), fg=self.colors['text_muted']).pack(side="left")
            lbl = tk.Label(f, text=value_label, bg="#f8fafc", font=("Inter", size, "bold" if is_bold else "normal"), fg=color if color else self.colors['text_main'])
            lbl.pack(side="right")
            return lbl

        self.lbl_subtotal = add_summary_line("Subtotal", "$0.00")
        self.lbl_tax = add_summary_line(f"Tax ({int(self.tax_rate*100)}%)", "$0.00")
        tk.Frame(totals_frame, height=1, bg="#e2e8f0").pack(fill="x", pady=15)
        self.lbl_total = add_summary_line("GRAND TOTAL", "$0.00", size=15, is_bold=True, color=self.colors['accent'])

        # FOOTER ACTION
        btn_box = tk.Frame(billing_frame, bg="white", pady=20)
        btn_box.pack(fill="x")
        
        tk.Button(btn_box, text="Discard Cart", command=self.clear_cart, bg="#94a3b8", fg="white", 
                  relief="flat", width=12, pady=8).pack(side="left", padx=20)
        tk.Button(btn_box, text="Complete Order 🧾", command=self.checkout, bg=self.colors['header'], 
                  fg="white", font=("Inter", 11, "bold"), relief="flat", padx=25, pady=10).pack(side="right", padx=20)

    # --- LOGIC METHODS ---

    def load_menu_data(self):
        for i in self.menu_tree.get_children():
            self.menu_tree.delete(i)
        self.cursor.execute("SELECT * FROM menu")
        for idx, row in enumerate(self.cursor.fetchall()):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.menu_tree.insert("", "end", values=row, tags=(tag,))

    def db_add_item(self):
        name, price, cat = self.ent_name.get(), self.ent_price.get(), self.ent_cat.get()
        if name and price:
            try:
                self.cursor.execute("INSERT INTO menu (name, price, category) VALUES (?, ?, ?)", (name, float(price), cat))
                self.conn.commit()
                self.load_menu_data()
                self.ent_name.delete(0, 'end'); self.ent_price.delete(0, 'end')
            except: messagebox.showerror("Database Error", "Please ensure price is a valid number.")
        else: messagebox.showwarning("Incomplete Data", "All fields are required to add a new dish.")

    def db_delete_item(self):
        sel = self.menu_tree.selection()
        if not sel: return
        item_id = self.menu_tree.item(sel)['values'][0]
        if messagebox.askyesno("Confirm Removal", "Delete this item from the active menu?"):
            self.cursor.execute("DELETE FROM menu WHERE id=?", (item_id,))
            self.conn.commit()
            self.load_menu_data()

    def add_to_cart(self):
        sel = self.menu_tree.selection()
        if not sel: return
        vals = self.menu_tree.item(sel)['values']
        name, price = vals[1], float(vals[2])
        self.cart.append((name, price))
        self.cart_list.insert("end", f" {name[:18].ljust(20)} ${price:>8.2f}")
        self.cart_list.see("end") 
        self.update_totals()

    def update_totals(self):
        sub = sum(i[1] for i in self.cart)
        tax = sub * self.tax_rate
        self.lbl_subtotal.config(text=f"${sub:.2f}")
        self.lbl_tax.config(text=f"${tax:.2f}")
        self.lbl_total.config(text=f"${(sub + tax):.2f}")

    def clear_cart(self):
        if self.cart and messagebox.askyesno("Clear Order", "Are you sure you want to discard the current order?"):
            self.cart = []
            self.cart_list.delete(0, "end")
            self.update_totals()

    def checkout(self):
        if not self.cart: 
            messagebox.showwarning("Empty Cart", "Cannot checkout an empty order.")
            return
            
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        sub = sum(i[1] for i in self.cart)
        tax = sub * self.tax_rate
        total = sub + tax
        
        # Build Receipt Content
        receipt =  "      ⚜ ELITE DINING ⚜\n"
        receipt += "       Customer Receipt\n"
        receipt += "  " + "="*28 + "\n"
        receipt += f"  Date: {timestamp}\n"
        receipt += f"  Order ID: #ED-{file_timestamp}\n"
        receipt += "  " + "-"*28 + "\n"
        for n, p in self.cart:
            receipt += f"  {n[:16].ljust(18)} ${p:>7.2f}\n"
        receipt += "  " + "-"*28 + "\n"
        receipt += f"  Subtotal:        ${sub:>7.2f}\n"
        receipt += f"  Service Tax:     ${tax:>7.2f}\n"
        receipt += f"  GRAND TOTAL:     ${total:>7.2f}\n"
        receipt += "  " + "="*28 + "\n"
        receipt += "\n    Thank you for choosing\n       Elite Dining!\n"

        # Show Confirmation and Print Option
        if messagebox.askyesno("Complete Order", f"Total Amount: ${total:.2f}\n\nWould you like to generate/print a digital receipt?"):
            self.print_receipt(receipt, f"Receipt_ED_{file_timestamp}.txt")
            
        self.cart = []
        self.cart_list.delete(0, "end")
        self.update_totals()

    def print_receipt(self, content, filename):
        """Simulates printing by saving to a text file."""
        try:
            # Create 'receipts' folder if it doesn't exist
            if not os.path.exists('receipts'):
                os.makedirs('receipts')
                
            path = os.path.join('receipts', filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            messagebox.showinfo("Success", f"Digital Receipt Generated:\n{path}")
            # Optionally open the file for the user
            os.startfile(path) if os.name == 'nt' else None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate receipt: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    # High-DPI support
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = RestaurantPro(root)
    root.mainloop()