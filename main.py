import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import os
import re
import subprocess
import platform
import sys
import threading
import time
from typing import Optional, List, Dict
from urllib.parse import quote

def install_required_packages():
    """Automatically install required packages if not available"""
    try:
        import requests
    except ImportError:
        print("Installing requests library...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests>=2.31.0'])
            print("requests library installed successfully!")
            import requests
        except Exception as e:
            print(f"Failed to install library: {e}")
            sys.exit(1)

install_required_packages()
import requests


class RedmineWikiDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Redmine Wiki Downloader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Set window icon
        try:
            if platform.system() == "Windows":
                if os.path.exists("favicon.ico"):
                    self.root.iconbitmap("favicon.ico")
            else:
                if os.path.exists("favicon.png"):
                    icon_image = tk.PhotoImage(file="favicon.png")
                    self.root.iconphoto(False, icon_image)
        except Exception as e:
            print(f"Failed to set icon: {e}")

        # Variables
        self.redmine_url = tk.StringVar(value="https://your-redmine-domain.com")
        self.api_key = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.auth_mode = tk.StringVar(value="id_pw")  # "api_key" or "id_pw"
        self.save_path = tk.StringVar(value="./wiki")
        self.download_mode = tk.StringVar(value="project")
        self.error_message = tk.StringVar()

        # State
        self.projects_data = []
        self.selected_project = None
        self.is_downloading = False
        self.cancel_download = False

        # Progress tracking
        self.current_status = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.current_url = tk.StringVar()

        self.setup_main_window()

        # Window close event handling
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def setup_main_window(self):
        """Setup main window"""
        # Title
        title_label = tk.Label(
            self.root,
            text="** Redmine Wiki Downloader **",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(20, 30))

        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=40, fill="x")

        # Redmine URL
        url_frame = tk.Frame(input_frame)
        url_frame.pack(fill="x", pady=5)
        tk.Label(url_frame, text="Redmine URL:", width=15, anchor="w").pack(side="left")
        url_entry = tk.Entry(url_frame, textvariable=self.redmine_url, width=40)
        url_entry.pack(side="left", fill="x", expand=True)

        # File path
        path_frame = tk.Frame(input_frame)
        path_frame.pack(fill="x", pady=5)
        tk.Label(path_frame, text="Save Path:", width=15, anchor="w").pack(side="left")
        path_entry = tk.Entry(path_frame, textvariable=self.save_path, width=30)
        path_entry.pack(side="left", fill="x", expand=True)
        browse_btn = tk.Button(path_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side="right", padx=(5, 0))

        # Download mode
        mode_frame = tk.Frame(input_frame)
        mode_frame.pack(fill="x", pady=5)
        tk.Label(mode_frame, text="Download Mode:", width=15, anchor="w").pack(side="left")
        mode_radio_frame = tk.Frame(mode_frame)
        mode_radio_frame.pack(side="left")
        tk.Radiobutton(mode_radio_frame, text="Project", variable=self.download_mode, value="project").pack(side="left")
        tk.Radiobutton(mode_radio_frame, text="All", variable=self.download_mode, value="all").pack(side="left", padx=(10, 0))

        # Authentication method selection
        auth_mode_frame = tk.Frame(input_frame)
        auth_mode_frame.pack(fill="x", pady=5)
        tk.Label(auth_mode_frame, text="Authentication:", width=15, anchor="w").pack(side="left")
        auth_radio_frame = tk.Frame(auth_mode_frame)
        auth_radio_frame.pack(side="left")
        tk.Radiobutton(auth_radio_frame, text="API Key", variable=self.auth_mode, value="api_key",
                      command=self.on_auth_mode_changed).pack(side="left")
        tk.Radiobutton(auth_radio_frame, text="ID/PW", variable=self.auth_mode, value="id_pw",
                      command=self.on_auth_mode_changed).pack(side="left", padx=(10, 0))

        # API key input frame
        self.api_frame = tk.Frame(input_frame)
        self.api_frame.pack(fill="x", pady=5)
        tk.Label(self.api_frame, text="API Key:", width=15, anchor="w").pack(side="left")
        self.api_entry = tk.Entry(self.api_frame, textvariable=self.api_key, width=40)
        self.api_entry.pack(side="left", fill="x", expand=True)

        # ID/PW input frames
        self.username_frame = tk.Frame(input_frame)
        tk.Label(self.username_frame, text="Username:", width=15, anchor="w").pack(side="left")
        self.username_entry = tk.Entry(self.username_frame, textvariable=self.username, width=40)
        self.username_entry.pack(side="left", fill="x", expand=True)

        self.password_frame = tk.Frame(input_frame)
        tk.Label(self.password_frame, text="Password:", width=15, anchor="w").pack(side="left")
        self.password_entry = tk.Entry(self.password_frame, textvariable=self.password, width=40, show="*")
        self.password_entry.pack(side="left", fill="x", expand=True)

        # Show UI based on initial authentication method
        self.on_auth_mode_changed()

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=30)

        # Error message
        error_label = tk.Label(button_frame, textvariable=self.error_message, fg="red")
        error_label.pack(side="left", padx=(0, 10))

        # Next button
        next_btn = tk.Button(button_frame, text="Next", command=self.on_next_clicked, width=10)
        next_btn.pack(side="left", padx=5)

        # Close button
        close_btn = tk.Button(button_frame, text="Close", command=self.root.quit, width=10)
        close_btn.pack(side="left", padx=5)

    def on_auth_mode_changed(self):
        """Update UI when authentication method changes"""
        if self.auth_mode.get() == "api_key":
            # API Key mode: Show only API key input field
            self.api_frame.pack(fill="x", pady=5)
            self.username_frame.pack_forget()
            self.password_frame.pack_forget()
        else:
            # ID/PW mode: Show only ID/PW input fields
            self.api_frame.pack_forget()
            self.username_frame.pack(fill="x", pady=5)
            self.password_frame.pack(fill="x", pady=5)

    def browse_folder(self):
        """Folder selection dialog"""
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)

    def validate_inputs(self) -> bool:
        """Validate input values"""
        if not self.redmine_url.get().strip():
            self.error_message.set("Please fill in all fields")
            return False

        # Validation based on authentication method
        if self.auth_mode.get() == "api_key":
            if not self.api_key.get().strip():
                self.error_message.set("Please fill in all fields")
                return False
        else:  # id_pw
            if not self.username.get().strip() or not self.password.get().strip():
                self.error_message.set("Please fill in all fields")
                return False

        if not self.save_path.get().strip():
            self.save_path.set("wiki")  # Set default value

        # Convert all paths to absolute paths (handles both relative and absolute paths)
        save_path = self.save_path.get().strip()
        absolute_path = os.path.abspath(save_path)
        self.save_path.set(absolute_path)

        self.error_message.set("")
        return True

    def on_next_clicked(self):
        """Next button click event"""
        if not self.validate_inputs():
            return

        try:
            # Test API connection and fetch project list
            self.projects_data = self.fetch_projects()

            if self.download_mode.get() == "all":
                self.download_all_projects()
            else:
                self.show_project_selection()

        except Exception as e:
            messagebox.showerror("Error", f"API connection failed: {str(e)}")

    def get_auth_params(self):
        """Return parameters and authentication headers based on authentication method"""
        if self.auth_mode.get() == "api_key":
            return {"key": self.api_key.get()}, None
        else:
            return {}, (self.username.get(), self.password.get())

    def fetch_projects(self) -> List[Dict]:
        """Fetch all projects using pagination"""
        params, auth = self.get_auth_params()
        url = f"{self.redmine_url.get()}/projects.xml"

        all_projects = []
        offset = 0
        limit = 100

        while True:
            params["limit"] = limit
            params["offset"] = offset

            response = requests.get(url, params=params, auth=auth)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            # Get pagination info
            total_count = int(root.get('total_count', 0))
            current_limit = int(root.get('limit', limit))
            current_offset = int(root.get('offset', offset))

            # Extract projects from current page
            projects_in_page = []
            for project in root.findall('project'):
                name = project.find('name').text
                identifier = project.find('identifier').text
                projects_in_page.append({'name': name, 'identifier': identifier})

            all_projects.extend(projects_in_page)

            # Check if we have more pages
            if current_offset + current_limit >= total_count or len(projects_in_page) == 0:
                break

            offset += limit

        return all_projects

    def show_project_selection(self):
        """Show project selection screen"""
        # Hide existing widgets
        for widget in self.root.winfo_children():
            widget.pack_forget()

        # Project selection UI
        title_label = tk.Label(
            self.root,
            text="** Select Project to Download **",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(20, 30))

        # Project list
        list_frame = tk.Frame(self.root)
        list_frame.pack(padx=40, pady=20, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.project_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.project_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.project_listbox.yview)

        for project in self.projects_data:
            self.project_listbox.insert(tk.END, project['name'])

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        download_btn = tk.Button(button_frame, text="Download", command=self.download_selected_project, width=10)
        download_btn.pack(side="left", padx=5)

        back_btn = tk.Button(button_frame, text="Back", command=self.show_main_window, width=10)
        back_btn.pack(side="left", padx=5)

        close_btn = tk.Button(button_frame, text="Close", command=self.root.quit, width=10)
        close_btn.pack(side="left", padx=5)

    def show_main_window(self):
        """Return to main window"""
        for widget in self.root.winfo_children():
            widget.pack_forget()
        self.setup_main_window()

    def download_selected_project(self):
        """Download selected project"""
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project.")
            return

        selected_index = selection[0]
        self.selected_project = self.projects_data[selected_index]

        # Show progress screen and start download in thread
        self.show_progress_screen()
        self.start_download_thread([self.selected_project])

    def download_all_projects(self):
        """Download all projects"""
        # Show progress screen and start download in thread
        self.show_progress_screen()
        self.start_download_thread(self.projects_data)

    def start_download_thread(self, projects_to_download):
        """Execute download in separate thread"""
        self.is_downloading = True
        self.cancel_download = False

        def download_worker():
            try:
                total_projects = len(projects_to_download)
                self.add_log(f"Download started - Total {total_projects} projects")

                for i, project in enumerate(projects_to_download):
                    if self.cancel_download:
                        self.add_log("Download cancelled by user.")
                        break

                    self.current_status.set(f"Downloading project '{project['name']}'...")
                    self.progress_var.set((i / total_projects) * 100)
                    self.add_log(f"Starting project '{project['name']}'...")
                    self.root.update_idletasks()

                    self.download_project_wiki_threaded(project)

                if not self.cancel_download:
                    self.current_status.set("Download completed!")
                    self.progress_var.set(100)
                    self.add_log("All downloads completed!")
                    self.root.update_idletasks()
                    time.sleep(1)
                    self.root.after(0, self.show_completion_screen)
                else:
                    self.current_status.set("Download cancelled.")
                    self.root.update_idletasks()
                    time.sleep(2)
                    self.root.after(0, self.show_main_window)

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error occurred during download: {str(e)}"))
                self.root.after(0, self.show_main_window)
            finally:
                self.is_downloading = False

        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()

    def show_progress_screen(self):
        """Show download progress screen"""
        for widget in self.root.winfo_children():
            widget.pack_forget()

        # Adjust window size slightly larger for progress screen
        self.root.geometry("700x500")

        # Progress UI
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(expand=True, padx=40, pady=20)

        # Title
        title_label = tk.Label(
            progress_frame,
            text="** Download in Progress **",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 30))

        # Current status (fixed size)
        status_label = tk.Label(
            progress_frame,
            textvariable=self.current_status,
            font=("Arial", 10),
            wraplength=450,
            width=60,  # 고정 폭 (문자 개수)
            height=3,  # 고정 높이 (줄 수)
            justify="left",
            anchor="w"
        )
        status_label.pack(pady=10)

        # Progress bar
        progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        progress_bar.pack(pady=20)

        # Progress log text area (fixed size)
        log_frame = tk.Frame(progress_frame)
        log_frame.pack(pady=10, fill="x")

        # Text widget with scrollbar
        log_scrollbar = tk.Scrollbar(log_frame)
        log_scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_frame,
            width=70,
            height=6,  # Reduced height from 8 to 6
            font=("Consolas", 9),
            wrap=tk.NONE,  # No line wrapping
            yscrollcommand=log_scrollbar.set,
            state=tk.DISABLED  # Read-only
        )
        self.log_text.pack(side="left", fill="x", expand=True)
        log_scrollbar.config(command=self.log_text.yview)

        # Cancel button
        cancel_btn = tk.Button(
            progress_frame,
            text="Cancel",
            command=self.on_cancel_download,
            width=10
        )
        cancel_btn.pack(pady=20)

    def on_cancel_download(self):
        """Confirm download cancellation"""
        if messagebox.askyesno("Confirm", "Do you want to stop the task?"):
            self.cancel_download = True

    def on_window_close(self):
        """Handle window close event"""
        if self.is_downloading:
            if messagebox.askyesno("Confirm", "Download is in progress. Do you want to stop the task and exit the program?"):
                self.cancel_download = True
                self.root.quit()
        else:
            self.root.quit()

    def download_project_wiki_threaded(self, project: Dict):
        """Project wiki download executed in thread"""
        identifier = project['identifier']
        project_name = project['name']

        # Create project folder (both single/all create project name folders)
        save_dir = self.save_path.get()
        project_dir = os.path.join(save_dir, self.sanitize_filename(project_name))

        os.makedirs(project_dir, exist_ok=True)

        # Fetch wiki page list
        self.add_log(f"Fetching wiki list for project '{project_name}'...")
        wiki_pages = self.fetch_wiki_pages_threaded(identifier)

        if not wiki_pages:
            self.add_log(f"No wiki pages found in project '{project_name}'.")
            return

        self.add_log(f"Found {len(wiki_pages)} wiki pages in project '{project_name}'")

        # Download each wiki page
        for i, page_title in enumerate(wiki_pages):
            if self.cancel_download:
                break

            # Display abbreviated text
            truncated_project = self.truncate_text(project_name, 20)
            truncated_page = self.truncate_text(page_title, 30)
            self.current_status.set(f"Project '{truncated_project}' - Downloading page '{truncated_page}'... ({i+1}/{len(wiki_pages)})")

            # Add detailed information to log
            self.add_log(f"Downloading: {page_title} ({i+1}/{len(wiki_pages)})")
            self.root.update_idletasks()

            success = self.download_wiki_page_threaded(identifier, page_title, project_dir)
            if success:
                self.add_log(f"Completed: {page_title}")
            else:
                self.add_log(f"Failed: {page_title}")

        self.add_log(f"Project '{project_name}' download completed")

    def fetch_wiki_pages_threaded(self, identifier: str) -> List[str]:
        """Fetch all wiki pages using pagination executed in thread"""
        params, auth = self.get_auth_params()
        url = f"{self.redmine_url.get()}/projects/{identifier}/wiki/index.xml"

        all_pages = []
        offset = 0
        limit = 100

        try:
            while True:
                params["limit"] = limit
                params["offset"] = offset

                response = requests.get(url, params=params, auth=auth)
                if response.status_code == 404:
                    return []  # Project without wiki

                response.raise_for_status()

                root = ET.fromstring(response.content)

                # Get pagination info
                total_count = int(root.get('total_count', 0))
                current_limit = int(root.get('limit', limit))
                current_offset = int(root.get('offset', offset))

                # Extract pages from current page
                pages_in_page = []
                for page in root.findall('wiki_page'):
                    title = page.find('title').text
                    pages_in_page.append(title)

                all_pages.extend(pages_in_page)

                # Check if we have more pages
                if current_offset + current_limit >= total_count or len(pages_in_page) == 0:
                    break

                offset += limit

            return all_pages
        except Exception as e:
            print(f"Failed to fetch wiki page list: {e}")
            return []

    def download_wiki_page_threaded(self, identifier: str, title: str, save_dir: str) -> bool:
        """Individual wiki page download executed in thread"""
        try:
            params, auth = self.get_auth_params()
            encoded_title = quote(title, safe='')
            url = f"{self.redmine_url.get()}/projects/{identifier}/wiki/{encoded_title}.xml"

            response = requests.get(url, params=params, auth=auth)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            page_title = root.find('title').text
            page_text = root.find('text').text or ""

            # Save as markdown file
            filename = f"{self.sanitize_filename(page_title)}.md"
            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {page_title}\n\n")
                f.write(page_text)

            return True

        except Exception as e:
            print(f"Failed to download wiki page '{title}': {e}")
            return False

    def download_project_wiki(self, project: Dict):
        """Download wiki for specific project"""
        identifier = project['identifier']
        project_name = project['name']

        # Create project folder (both single/all create project name folders)
        save_dir = self.save_path.get()
        project_dir = os.path.join(save_dir, self.sanitize_filename(project_name))

        os.makedirs(project_dir, exist_ok=True)

        # Fetch wiki page list
        wiki_pages = self.fetch_wiki_pages(identifier)

        # Download each wiki page
        for page_title in wiki_pages:
            self.download_wiki_page(identifier, page_title, project_dir)

    def fetch_wiki_pages(self, identifier: str) -> List[str]:
        """Fetch all wiki pages using pagination (deprecated - use threaded version)"""
        params, auth = self.get_auth_params()
        url = f"{self.redmine_url.get()}/projects/{identifier}/wiki/index.xml"

        all_pages = []
        offset = 0
        limit = 100

        while True:
            params["limit"] = limit
            params["offset"] = offset

            response = requests.get(url, params=params, auth=auth)
            if response.status_code == 404:
                return []  # Project without wiki

            response.raise_for_status()

            root = ET.fromstring(response.content)

            # Get pagination info
            total_count = int(root.get('total_count', 0))
            current_limit = int(root.get('limit', limit))
            current_offset = int(root.get('offset', offset))

            # Extract pages from current page
            pages_in_page = []
            for page in root.findall('wiki_page'):
                title = page.find('title').text
                pages_in_page.append(title)

            all_pages.extend(pages_in_page)

            # Check if we have more pages
            if current_offset + current_limit >= total_count or len(pages_in_page) == 0:
                break

            offset += limit

        return all_pages

    def download_wiki_page(self, identifier: str, title: str, save_dir: str):
        """Download individual wiki page"""
        encoded_title = quote(title, safe='')
        url = f"{self.redmine_url.get()}/projects/{identifier}/wiki/{encoded_title}.xml?key={self.api_key.get()}"

        response = requests.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        page_title = root.find('title').text
        page_text = root.find('text').text or ""

        # Save as markdown file
        filename = f"{self.sanitize_filename(page_title)}.md"
        filepath = os.path.join(save_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {page_title}\n\n")
            f.write(page_text)

    def sanitize_filename(self, filename: str) -> str:
        """Remove special characters from filename"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def truncate_text(self, text: str, max_length: int = 50) -> str:
        """Truncate text if too long"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def add_log(self, message: str):
        """Add message to log text area"""
        if hasattr(self, 'log_text'):
            # Temporarily set text widget to editable
            self.log_text.config(state=tk.NORMAL)
            # Add message (with timestamp)
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            # Auto scroll (to bottom)
            self.log_text.see(tk.END)
            # Set back to read-only
            self.log_text.config(state=tk.DISABLED)
            # Update UI
            self.root.update_idletasks()

    def show_completion_screen(self):
        """Show completion screen"""
        for widget in self.root.winfo_children():
            widget.pack_forget()

        # Completion message
        completion_frame = tk.Frame(self.root)
        completion_frame.pack(expand=True)

        title_label = tk.Label(
            completion_frame,
            text="** Save Completed **",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)

        path_label = tk.Label(
            completion_frame,
            text=f"Save Path: {self.save_path.get()}",
            font=("Arial", 12)
        )
        path_label.pack(pady=10)

        # Button frame
        button_frame = tk.Frame(completion_frame)
        button_frame.pack(pady=30)

        open_btn = tk.Button(button_frame, text="Open", command=self.open_save_directory, width=10)
        open_btn.pack(side="left", padx=5)

        close_btn = tk.Button(button_frame, text="Close", command=self.root.quit, width=10)
        close_btn.pack(side="left", padx=5)

    def open_save_directory(self):
        """Open save directory"""
        path = self.save_path.get()
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open folder: {str(e)}")

    def run(self):
        """Run application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = RedmineWikiDownloader()
    app.run()