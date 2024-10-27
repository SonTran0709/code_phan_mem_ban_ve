import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error

class TicketSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống bán vé")
        self.root.geometry("800x600")
        self.root.configure(bg="#E0F7FA")  # Light cyan background

        self.conn = self.connect_to_database()
        if not self.conn:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu")
            root.destroy()
            return

        self.current_user = None
        self.create_widgets()

    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="ticket_system"
            )
            return connection
        except Error as e:
            print(f"Lỗi kết nối đến MySQL: {e}")
            return None

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#E0F7FA", font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12), background="#4DD0E1")
        style.map("TButton", background=[("active", "#26C6DA")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.login_frame = ttk.Frame(self.notebook)
        self.buyer_frame = ttk.Frame(self.notebook)
        self.seller_frame = ttk.Frame(self.notebook)
        self.admin_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.login_frame, text="Đăng nhập")
        self.create_login_widgets()

    def create_login_widgets(self):
        login_frame = self.create_scrollable_frame(self.login_frame)
        ttk.Label(login_frame, text="Tên đăng nhập:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(login_frame, text="Mật khẩu:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(login_frame, text="Đăng nhập", command=self.login).grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(login_frame, text="Đăng ký", command=self.show_register).grid(row=3, column=0, columnspan=2)

    def create_scrollable_frame(self, parent):
        canvas = tk.Canvas(parent, bg="#E0F7FA")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        return frame

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        user = self.authenticate_user(username, password)
        if user:
            self.current_user = user
            messagebox.showinfo("Thành công", f"Xin chào, {username}!")
            self.show_user_interface(user[3])  # user[3] is the user_type
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng")

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        return user

    def show_register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Đăng ký")
        register_window.geometry("400x300")
        register_window.configure(bg="#E0F7FA")

        ttk.Label(register_window, text="Tên đăng nhập:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        username_entry = ttk.Entry(register_window)
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(register_window, text="Mật khẩu:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        password_entry = ttk.Entry(register_window, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(register_window, text="Xác nhận mật khẩu:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        confirm_password_entry = ttk.Entry(register_window, show="*")
        confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)

        user_type = tk.StringVar(value="buyer")
        ttk.Radiobutton(register_window, text="Người mua", variable=user_type, value="buyer").grid(row=3, column=0, padx=10, pady=10)
        ttk.Radiobutton(register_window, text="Người bán", variable=user_type, value="seller").grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(register_window, text="Đăng ký", command=lambda: self.register(
            username_entry.get(),
            password_entry.get(),
            confirm_password_entry.get(),
            user_type.get(),
            register_window
        )).grid(row=4, column=0, columnspan=2, pady=20)

    def register(self, username, password, confirm_password, user_type, register_window):
        if not username or not password or not confirm_password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp")
            return

        if self.create_user(username, password, user_type):
            messagebox.showinfo("Thành công", "Đăng ký tài khoản thành công")
            register_window.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể đăng ký tài khoản")

    def create_user(self, username, password, user_type):
        cursor = self.conn.cursor()
        query = "INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)"
        try:
            cursor.execute(query, (username, password, user_type))
            self.conn.commit()
            return True
        except Error as e:
            print(f"Lỗi khi đăng ký: {e}")
            return False
        finally:
            cursor.close()

    def show_user_interface(self, user_type):
        if len(self.notebook.tabs()) > 1:  # Kiểm tra xem có ít nhất 2 tab
            self.notebook.forget(1)  # Remove any existing user interface
        if user_type == "buyer":
            self.notebook.add(self.buyer_frame, text="Người mua")
            self.create_buyer_widgets()
        elif user_type == "seller":
            self.notebook.add(self.seller_frame, text="Người bán")
            self.create_seller_widgets()
        elif user_type == "admin":
            self.notebook.add(self.admin_frame, text="Quản trị viên")
            self.create_admin_widgets()
        self.notebook.select(1)  # Switch to the user interface tab

    def create_buyer_widgets(self):
        frame = self.create_scrollable_frame(self.buyer_frame)
        ttk.Button(frame, text="Xem danh sách vé", command=self.view_tickets).grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Đặt vé", command=self.book_ticket).grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Hủy vé", command=self.cancel_ticket).grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Xem vé đã xác nhận", command=self.view_confirmed_tickets).grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Đăng xuất", command=self.logout).grid(row=4, column=0, pady=10, padx=10, sticky="ew")

    def create_seller_widgets(self):
        frame = self.create_scrollable_frame(self.seller_frame)
        ttk.Button(frame, text="Đăng bán vé", command=self.show_post_ticket).grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Xem danh sách đặt vé", command=self.view_bookings).grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Xác nhận đặt vé", command=self.confirm_booking).grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Xóa vé", command=self.delete_ticket).grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Đăng xuất", command=self.logout).grid(row=4, column=0, pady=10, padx=10, sticky="ew")

    def create_admin_widgets(self):
        frame = self.create_scrollable_frame(self.admin_frame)
        ttk.Button(frame, text="Xem danh sách vé", command=self.view_tickets).grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Xóa vé", command=self.delete_ticket).grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Xem danh sách tài khoản", command=self.view_accounts).grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Xóa tài khoản", command=self.delete_account).grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        ttk.Button(frame, text="Đăng xuất", command=self.logout).grid(row=4, column=0, pady=10, padx=10, sticky="ew")

    def logout(self):
        self.current_user = None
        self.notebook.forget(1)  # Remove the user interface tab
        self.notebook.select(0)  # Switch back to the login tab
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        messagebox.showinfo("Đăng xuất", "Bạn đã đăng xuất thành công")

    def view_tickets(self):
        tickets = self.get_all_tickets()
        self.show_data_in_treeview("Danh sách vé", ["ID", "Tên", "Giá", "Số lượng", "Người bán"], tickets)

    def get_all_tickets(self):
        cursor = self.conn.cursor()
        query = "SELECT t.id, t.name, t.price, t.quantity, u.username FROM tickets t JOIN users u ON t.seller_id = u.id"
        cursor.execute(query)
        tickets = cursor.fetchall()
        cursor.close()
        return tickets

    def book_ticket(self):
        ticket_id = simpledialog.askinteger("Đặt vé", "Nhập ID vé muốn đặt:")
        if ticket_id is not None:
            quantity = simpledialog.askinteger("Số lượng", "Nhập số lượng vé muốn mua:")
            if quantity is not None and quantity > 0:
                if self.create_booking(ticket_id, quantity):
                    messagebox.showinfo("Thành công", f"Đặt {quantity} vé thành công")
                else:
                    messagebox.showerror("Lỗi", "Không thể đặt vé")
            else:
                messagebox.showerror("Lỗi", "Số lượng vé không hợp lệ")

    def create_booking(self, ticket_id, quantity):
        cursor = self.conn.cursor()
        try:
            # Check if there are enough tickets available
            cursor.execute("SELECT quantity FROM tickets WHERE id = %s", (ticket_id,))
            available_quantity = cursor.fetchone()[0]
            if available_quantity < quantity:
                messagebox.showerror("Lỗi", "Không đủ số lượng vé")
                return False

            # Create the booking
            cursor.execute("INSERT INTO bookings (user_id, ticket_id, quantity, status) VALUES (%s, %s, %s, 'pending')",
                           (self.current_user[0], ticket_id,   quantity))
            
            # Update the available quantity
            cursor.execute("UPDATE tickets SET quantity = quantity - %s WHERE id = %s", (quantity, ticket_id))
            
            self.conn.commit()
            return True
        except Error as e:
            print(f"Lỗi khi đặt vé: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    def cancel_ticket(self):
        booking_id = simpledialog.askinteger("Hủy vé", "Nhập ID đặt vé muốn hủy:")
        if booking_id is not None:
            if self.delete_booking(booking_id):
                messagebox.showinfo("Thành công", "Hủy vé thành công")
            else:
                messagebox.showinfo("Thông báo", "Không tìm thấy đặt vé hoặc bạn không có quyền hủy")

    def delete_booking(self, booking_id):
        cursor = self.conn.cursor()
        try:
            # Get the ticket_id and quantity from the booking
            cursor.execute("SELECT ticket_id, quantity FROM bookings WHERE id = %s AND user_id = %s", 
                           (booking_id, self.current_user[0]))
            result = cursor.fetchone()
            if not result:
                return False
            ticket_id, quantity = result

            # Delete the booking
            cursor.execute("DELETE FROM bookings WHERE id = %s AND user_id = %s", (booking_id, self.current_user[0]))
            
            # Update the available quantity
            cursor.execute("UPDATE tickets SET quantity = quantity + %s WHERE id = %s", (quantity, ticket_id))
            
            self.conn.commit()
            return True
        except Error as e:
            print(f"Lỗi khi hủy vé: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    def view_confirmed_tickets(self):
        confirmed_tickets = self.get_confirmed_tickets()
        self.show_data_in_treeview("Vé đã xác nhận", ["ID", "Tên", "Giá", "Số lượng", "Trạng thái"], confirmed_tickets)

    def get_confirmed_tickets(self):
        cursor = self.conn.cursor()
        query = """
        SELECT b.id, t.name, t.price, b.quantity, b.status
        FROM bookings b
        JOIN tickets t ON b.ticket_id = t.id
        WHERE b.user_id = %s AND b.status = 'confirmed'
        """
        cursor.execute(query, (self.current_user[0],))
        confirmed_tickets = cursor.fetchall()
        cursor.close()
        return confirmed_tickets

    def show_post_ticket(self):
        ticket_window = tk.Toplevel(self.root)
        ticket_window.title("Đăng bán vé")
        ticket_window.geometry("300x200")

        ttk.Label(ticket_window, text="Tên vé:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_entry = ttk.Entry(ticket_window)
        name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(ticket_window, text="Giá:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        price_entry = ttk.Entry(ticket_window)
        price_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(ticket_window, text="Số lượng:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        quantity_entry = ttk.Entry(ticket_window)
        quantity_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(ticket_window, text="Đăng bán", command=lambda: self.post_ticket(
            name_entry.get(),
            price_entry.get(),
            quantity_entry.get(),
            ticket_window
        )).grid(row=3, column=0, columnspan=2, pady=20)

    def post_ticket(self, name, price, quantity, ticket_window):
        if not name or not price or not quantity:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá và số lượng phải là số")
            return

        if self.create_ticket(name, price, quantity):
            messagebox.showinfo("Thành công", "Đăng bán vé thành công")
            ticket_window.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể đăng bán vé")

    def create_ticket(self, name, price, quantity):
        cursor = self.conn.cursor()
        query = "INSERT INTO tickets (name, price, quantity, seller_id) VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(query, (name, price, quantity, self.current_user[0]))
            self.conn.commit()
            return True
        except Error as e:
            print(f"Lỗi khi đăng bán vé: {e}")
            return False
        finally:
            cursor.close()

    def view_bookings(self):
        bookings = self.get_seller_bookings()
        self.show_data_in_treeview("Danh sách đặt vé", ["ID", "Người đặt", "Tên vé", "Giá", "Số lượng", "Trạng thái"], bookings)

    def get_seller_bookings(self):
        cursor = self.conn.cursor()
        query = """
        SELECT b.id, u.username, t.name, t.price, b.quantity, b.status
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN tickets t ON b.ticket_id = t.id
        WHERE t.seller_id = %s
        """
        cursor.execute(query, (self.current_user[0],))
        bookings = cursor.fetchall()
        cursor.close()
        return bookings

    def confirm_booking(self):
        booking_id = simpledialog.askinteger("Xác nhận đặt vé", "Nhập ID đặt vé muốn xác nhận:")
        if booking_id is not None:
            if self.update_booking_status(booking_id, 'confirmed'):
                messagebox.showinfo("Thành công", "Xác nhận đặt vé thành công")
            else:
                messagebox.showinfo("Thông báo", "Không tìm thấy đặt vé hoặc bạn không có quyền xác nhận")

    def update_booking_status(self, booking_id, status):
        cursor = self.conn.cursor()
        query = """
        UPDATE bookings b
        JOIN tickets t ON b.ticket_id = t.id
        SET b.status = %s
        WHERE b.id = %s AND t.seller_id = %s
        """
        try:
            cursor.execute(query, (status, booking_id, self.current_user[0]))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Lỗi khi cập nhật trạng thái đặt vé: {e}")
            return False
        finally:
            cursor.close()

    def delete_ticket(self):
        ticket_id = simpledialog.askinteger("Xóa vé", "Nhập ID vé muốn xóa:")
        if ticket_id is not None:
            if self.remove_ticket(ticket_id):
                messagebox.showinfo("Thành công", "Xóa vé thành công")
            else:
                messagebox.showinfo("Thông báo", "Không tìm thấy vé hoặc bạn không có quyền xóa")

    def remove_ticket(self, ticket_id):
        cursor = self.conn.cursor()
        query = "DELETE FROM tickets WHERE id = %s"
        if self.current_user[3] != "admin":
            query += " AND seller_id = %s"
        try:
            if self.current_user[3] == "admin":
                cursor.execute(query, (ticket_id,))
            else:
                cursor.execute(query, (ticket_id, self.current_user[0]))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Lỗi khi xóa vé: {e}")
            return False
        finally:
            cursor.close()

    def view_accounts(self):
        accounts = self.get_all_accounts()
        self.show_data_in_treeview("Danh sách tài khoản", ["ID", "Tên đăng nhập", "Loại tài khoản"], accounts)

    def get_all_accounts(self):
        cursor = self.conn.cursor()
        query = "SELECT id, username, user_type FROM users"
        cursor.execute(query)
        accounts = cursor.fetchall()
        cursor.close()
        return accounts

    def delete_account(self):
        account_id = simpledialog.askinteger("Xóa tài khoản", "Nhập ID tài khoản muốn xóa:")
        if account_id is not None:
            if self.remove_account(account_id):
                messagebox.showinfo("Thành công", "Xóa tài khoản thành công")
            else:
                messagebox.showinfo("Thông báo", "Không tìm thấy tài khoản")

    def remove_account(self, account_id):
        cursor = self.conn.cursor()
        query = "DELETE FROM users WHERE id = %s"
        try:
            cursor.execute(query, (account_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Lỗi khi xóa tài khoản: {e}")
            return False
        finally:
            cursor.close()

    def show_data_in_treeview(self, title, columns, data):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("800x400")

        tree = ttk.Treeview(window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for item in data:
            tree.insert("", "end", values=item)

        tree.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketSystem(root)
    root.mainloop()