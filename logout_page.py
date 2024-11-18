import customtkinter as ctk
from PIL import Image
import os
import ZODB
import ZODB.FileStorage
import transaction
from tkinter import messagebox

class LoginPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Database connection
        self.setup_database()

        # Configure window
        self.title("KMITL Library Management System")
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.resizable(False, False)
        self.state('zoomed')
        self.bind('<Map>', lambda e: self.enforce_maximized())

        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="#f0f4ff", corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Blue top bar 
        self.top_bar = ctk.CTkFrame(self.main_container, height=150, fg_color="#1e88e5", corner_radius=0)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.grid_columnconfigure(1, weight=1)

        # Load logo
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "logos", "kmitlgo.png")
            
            if not os.path.exists(logo_path):
                alt_paths = [
                    os.path.join(current_dir, "kmitlgo.png"),
                    os.path.join(current_dir, "logos/kmitlgo.png"),
                    os.path.join(current_dir, "logo/kmitlgo.png"),
                    os.path.join(current_dir, "images/kmitlgo.png")
                ]
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        logo_path = alt_path
                        break

            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(120, 120)
            )
            self.logo_label = ctk.CTkLabel(
                self.top_bar, 
                image=self.logo_image, 
                text="",
                width=120,
                height=120
            )
            self.logo_label.grid(row=0, column=0, padx=40, pady=15)
        except Exception as e:
            print(f"Error loading logo: {e}")

        # Title next to logo
        self.title_label = ctk.CTkLabel(
            self.top_bar,
            text="KMITL Library Management System",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="white"
        )
        self.title_label.grid(row=0, column=1, padx=20, pady=25, sticky="w")

        # Contact Us button
        self.contact_button = ctk.CTkButton(
            self.top_bar,
            text="Contact Us",
            width=120,
            height=40,
            fg_color="transparent",
            border_color="white",
            border_width=2,
            text_color="white",
            hover_color=("#1976d2", "#1976d2"),
            corner_radius=5,
            command=self.show_contact_info
        )
        self.contact_button.grid(row=0, column=2, padx=30, pady=25, sticky="ne")

        # Create and show login frame initially
        self.show_login_frame()

    def show_login_frame(self):
        # Clear any existing frames in the main container's second row
        for widget in self.main_container.grid_slaves(row=1):
            widget.destroy()

        # Login container
        self.login_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.login_frame.grid(row=1, column=0, pady=60)

        # Student ID entry
        self.user_id = ctk.CTkEntry(
            self.login_frame,
            width=300,
            height=40,
            placeholder_text="User ID",
            border_color="#1e88e5",
            fg_color="white"
        )
        self.user_id.grid(row=0, column=0, padx=20, pady=10)

        # Password entry
        self.password = ctk.CTkEntry(
            self.login_frame,
            width=300,
            height=40,
            placeholder_text="Password",
            show="•",
            border_color="#1e88e5",
            fg_color="white"
        )
        self.password.grid(row=1, column=0, padx=20, pady=10)

        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            width=300,
            height=40,
            fg_color="#1e88e5",
            hover_color="#1976d2",
            corner_radius=5,
            command=self.login
        )
        self.login_button.grid(row=2, column=0, padx=20, pady=20)

        # Forgot Password link
        self.forgot_password = ctk.CTkLabel(
            self.login_frame,
            text="Forgot Password?",
            text_color="#1e88e5",
            font=ctk.CTkFont(size=12, underline=True),
            cursor="hand2"
        )
        self.forgot_password.grid(row=3, column=0, pady=(0, 20))
        self.forgot_password.bind("<Button-1>", self.forgot_password_event)

        # Error message label
        self.error_label = ctk.CTkLabel(
            self.login_frame,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.error_label.grid(row=4, column=0, pady=(0, 10))

    def show_success_message(self, is_admin=False, user_id=None):
        # Clear login frame
        for widget in self.main_container.grid_slaves(row=1):
            widget.destroy()

        # Create success message frame
        success_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        success_frame.grid(row=1, column=0, pady=60)

        # Success message
        success_label = ctk.CTkLabel(
            success_frame,
            text="Login Successful!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1e88e5"
        )
        success_label.pack(pady=(0, 20))

        # OK button
        ok_button = ctk.CTkButton(
            success_frame,
            text="OK",
            width=200,
            height=40,
            fg_color="#1e88e5",
            hover_color="#1976d2",
            corner_radius=5,
            command=lambda: self.proceed_to_next_page(is_admin, user_id)
        )
        ok_button.pack()

    def proceed_to_next_page(self, is_admin, user_id):
        try:
            # Clear current frame contents
            for widget in self.winfo_children():
                widget.destroy()
            
            # Create and show the next GUI based on user type
            if is_admin:
                from admin_homepage import AdminHomepage
                admin_frame = AdminHomepage(self)
                admin_frame.pack(fill='both', expand=True)
            else:
                from user_homepage import UserHomepage
                user_frame = UserHomepage(self, user_id)
                user_frame.pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open next window: {e}")
            self.destroy()

    def setup_database(self):
        """Initialize database connection"""
        try:
            self.storage = ZODB.FileStorage.FileStorage('library.fs')
            self.db = ZODB.DB(self.storage)
            self.connection = self.db.open()
            self.root = self.connection.root()
        except Exception as e:
            print(f"Database connection error: {e}")

    def close_database(self):
        """Safely close database connections"""
        try:
            if hasattr(self, 'connection'):
                self.connection.close()
            if hasattr(self, 'db'):
                self.db.close()
            if hasattr(self, 'storage'):
                self.storage.close()
        except Exception as e:
            print(f"Error closing database: {e}")

    def enforce_maximized(self):
        """Ensure window stays maximized"""
        self.state('zoomed')

    def login(self):
        """Handle login authentication and routing"""
        user_id = self.user_id.get()
        password = self.password.get()

        if not user_id or not password:
            self.error_label.configure(text="Please enter both User ID and Password")
            return

        try:
            # Check user table
            if hasattr(self.root, 'users') and user_id in self.root.users:
                user = self.root.users[user_id]
                if user.verify_password(password):
                    self.close_database()
                    messagebox.showinfo("Success", "Login Successful!")
                    # Create and show the next GUI based on user type
                    for widget in self.winfo_children():
                        widget.destroy()
                    from user_homepage import UserHomepage
                    user_frame = UserHomepage(self, user_id)
                    user_frame.pack(fill='both', expand=True)
                else:
                    self.error_label.configure(text="Invalid password")
            # Check staff table
            elif str(user_id)=="67011922":
                if str(password)=="1922":
                    self.close_database()
                    messagebox.showinfo("Success", "Login Successful!")
                    # Create and show admin GUI
                    for widget in self.winfo_children():
                        widget.destroy()
                    from admin_homepage import AdminHomepage
                    admin_frame = AdminHomepage(self)
                    admin_frame.pack(fill='both', expand=True)
                else:
                    self.error_label.configure(text="Invalid password")
            else:
                self.error_label.configure(text="User ID not found")
        except Exception as e:
            self.error_label.configure(text=f"Login error: {str(e)}")
    def show_contact_info(self):
        """Show contact information in a persistent popup window"""
        # Create contact window as an attribute so it persists
        self.contact_window = ctk.CTkToplevel()
        self.contact_window.title("Contact Information")
        self.contact_window.geometry("400x250")
        self.contact_window.resizable(False, False)
        
        # Make window stay on top and grab focus
        self.contact_window.transient(self)
        self.contact_window.grab_set()
        self.contact_window.focus_force()
        self.contact_window.lift()
        
        if hasattr(self.contact_window, 'attributes'):  # For Windows and Linux
            self.contact_window.attributes('-topmost', True)
        
        # Center the window on screen
        screen_width = self.contact_window.winfo_screenwidth()
        screen_height = self.contact_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 250) // 2
        self.contact_window.geometry(f"400x250+{x}+{y}")
        
        # Configure grid
        self.contact_window.grid_rowconfigure(0, weight=1)
        self.contact_window.grid_columnconfigure(0, weight=1)
        
        # Main frame with background color
        main_frame = ctk.CTkFrame(
            self.contact_window,
            fg_color="#f0f4ff",
            corner_radius=0
        )
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title frame with blue background
        title_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#1e88e5",
            height=60,
            corner_radius=0
        )
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)
        
        # Title
        ctk.CTkLabel(
            title_frame,
            text="Contact Us",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Contact details frame
        contact_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        contact_frame.pack(fill="both", expand=True, padx=20)
        
        # Line contact with copy button
        line_frame = ctk.CTkFrame(contact_frame, fg_color="white")
        line_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            line_frame,
            text="Line ID:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e88e5"
        ).pack(side="left", padx=10, pady=10)
        
        line_id = "@phoopwintchothar"
        ctk.CTkLabel(
            line_frame,
            text=line_id,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=10)
        
        copy_line_btn = ctk.CTkButton(
            line_frame,
            text="Copy",
            width=60,
            height=30,
            fg_color="#1e88e5",
            hover_color="#1976d2",
            command=lambda: self.copy_to_clipboard(line_id, "Line ID copied!")
        )
        copy_line_btn.pack(side="right", padx=10, pady=10)
        
        # Email contact with copy button
        email_frame = ctk.CTkFrame(contact_frame, fg_color="white")
        email_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e88e5"
        ).pack(side="left", padx=10, pady=10)
        
        email = "phoopwintchothar1@gmail.com"
        ctk.CTkLabel(
            email_frame,
            text=email,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=10)
        
        copy_email_btn = ctk.CTkButton(
            email_frame,
            text="Copy",
            width=60,
            height=30,
            fg_color="#1e88e5",
            hover_color="#1976d2",
            command=lambda: self.copy_to_clipboard(email, "Email copied!")
        )
        copy_email_btn.pack(side="right", padx=10, pady=10)
        

    def copy_to_clipboard(self, text, message):
        """Copy text to clipboard and show notification"""
        self.clipboard_clear()
        self.clipboard_append(text)
        
        # Show notification
        notification = ctk.CTkToplevel(self.contact_window)  # Make notification a child of contact window
        notification.attributes('-topmost', True)
        notification.overrideredirect(True)
        
        # Position notification near the cursor
        x = self.contact_window.winfo_pointerx() + 10
        y = self.contact_window.winfo_pointery() + 10
        
        # Ensure notification stays within screen bounds
        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        
        if x + 200 > screen_width:
            x = screen_width - 210
        if y + 40 > screen_height:
            y = screen_height - 50
            
        notification.geometry(f"200x40+{x}+{y}")
        
        # Notification label
        label = ctk.CTkLabel(
            notification,
            text=message,
            fg_color="#1e88e5",
            text_color="white",
            corner_radius=5
        )
        label.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Auto-close notification after 1.5 seconds
        notification.after(1500, notification.destroy)


    def forgot_password_event(self, event=None):
        """Handle forgot password click"""
        messagebox.showinfo(
            "Password Reset",
            "Please contact the library staff to reset your password.\n\n" +
            "Contact Information:\n" +
            "Line: @phoopwintchothar\n" +
            "Email: phoopwintchothar1@gmail.com"
        )

