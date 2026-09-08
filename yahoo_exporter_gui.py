import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import imaplib
import email
import os
import re
from email.utils import parsedate_to_datetime

try:
    import pdfkit
except ImportError:
    pdfkit = None


def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", text)[:100]


def format_date(date_header):
    try:
        dt = parsedate_to_datetime(date_header)
        offset = dt.utcoffset()
        hours = int(offset.total_seconds() // 3600) if offset else 0
        gmt_str = f"GMT{'+' if hours >= 0 else ''}{hours}"
        return dt.strftime("%A, %B %d, %Y at %I:%M %p").lstrip("0").replace(" 0", " ") + f" {gmt_str}"
    except Exception:
        return date_header


def parse_folder_name(raw_line):
    decoded = raw_line.decode() if isinstance(raw_line, bytes) else raw_line
    match = re.search(r'"([^"]*)"$', decoded)
    if match:
        return match.group(1)
    return decoded.split()[-1].strip('"')


def build_header_html(subject, from_, to_, date_str):
    return f"""
    <div style="font-family: Arial, sans-serif; margin-bottom: 20px;">
        <h2 style="font-weight: normal; border-bottom: 1px solid #ccc; padding-bottom: 10px;">{subject}</h2>
        <table style="font-size: 14px; color: #333;">
            <tr><td style="padding: 2px 10px 2px 0; color: #888;">From:</td><td>{from_}</td></tr>
            <tr><td style="padding: 2px 10px 2px 0; color: #888;">To:</td><td>{to_}</td></tr>
            <tr><td style="padding: 2px 10px 2px 0; color: #888;">Date:</td><td>{date_str}</td></tr>
        </table>
        <hr style="border: none; border-top: 1px solid #ccc; margin-top: 10px;">
    </div>
    """


class ExporterApp:
    def __init__(self, root):
        self.root = root
        root.title("Yahoo Email PDF Exporter")
        root.geometry("560x520")

        pad = {"padx": 8, "pady": 4}

        ttk.Label(root, text="Yahoo Email:").grid(row=0, column=0, sticky="e", **pad)
        self.email_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.email_var, width=40).grid(row=0, column=1, columnspan=2, sticky="w", **pad)

        ttk.Label(root, text="App Password:").grid(row=1, column=0, sticky="e", **pad)
        self.password_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.password_var, width=40, show="*").grid(row=1, column=1, columnspan=2, sticky="w", **pad)

        ttk.Label(root, text="IMAP Folder Name:").grid(row=2, column=0, sticky="e", **pad)
        self.folder_var = tk.StringVar(value="INBOX")
        self.folder_combo = ttk.Combobox(root, textvariable=self.folder_var, width=28, values=["INBOX"])
        self.folder_combo.grid(row=2, column=1, sticky="w", **pad)
        ttk.Button(root, text="List Folders", command=self.start_list_folders).grid(row=2, column=2, sticky="w", **pad)

        ttk.Label(root, text="Search Criteria:").grid(row=3, column=0, sticky="e", **pad)
        self.search_var = tk.StringVar(value='FROM "hubstaff.com"')
        ttk.Entry(root, textvariable=self.search_var, width=40).grid(row=3, column=1, columnspan=2, sticky="w", **pad)

        ttk.Label(root, text="Output Folder:").grid(row=4, column=0, sticky="e", **pad)
        self.output_var = tk.StringVar(value=os.path.join(os.getcwd(), "output_pdfs"))
        ttk.Entry(root, textvariable=self.output_var, width=32).grid(row=4, column=1, sticky="w", **pad)
        ttk.Button(root, text="Browse...", command=self.browse_output).grid(row=4, column=2, sticky="w", **pad)

        ttk.Label(root, text="wkhtmltopdf.exe Path:").grid(row=5, column=0, sticky="e", **pad)
        self.wk_var = tk.StringVar(value=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
        ttk.Entry(root, textvariable=self.wk_var, width=32).grid(row=5, column=1, sticky="w", **pad)
        ttk.Button(root, text="Browse...", command=self.browse_wk).grid(row=5, column=2, sticky="w", **pad)

        self.run_button = ttk.Button(root, text="Run Export", command=self.start_export)
        self.run_button.grid(row=6, column=0, columnspan=3, pady=10)

        self.log_box = scrolledtext.ScrolledText(root, width=68, height=18, state="disabled")
        self.log_box.grid(row=7, column=0, columnspan=3, padx=8, pady=8)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_var.set(path)

    def browse_wk(self):
        path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if path:
            self.wk_var.set(path)

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def start_list_folders(self):
        yahoo_email = self.email_var.get().strip()
        app_password = self.password_var.get()
        if not yahoo_email or not app_password:
            self.log("ERROR: Enter your email and app password first, then click List Folders.")
            return
        thread = threading.Thread(target=self.list_folders, args=(yahoo_email, app_password), daemon=True)
        thread.start()

    def list_folders(self, yahoo_email, app_password):
        try:
            mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
            mail.login(yahoo_email, app_password)
        except Exception as e:
            self.log(f"ERROR: Login failed while listing folders: {e}")
            return

        try:
            status, folders = mail.list()
            if status != "OK":
                self.log("ERROR: Could not retrieve folder list.")
                return
            folder_names = [parse_folder_name(f) for f in folders]
            self.folder_combo["values"] = folder_names
            self.log(f"Found {len(folder_names)} folders — select one from the dropdown.")
        except Exception as e:
            self.log(f"ERROR: Failed to list folders: {e}")
        finally:
            mail.logout()

    def start_export(self):
        if pdfkit is None:
            self.log("ERROR: pdfkit is not installed. Run: pip install pdfkit")
            return
        self.run_button.configure(state="disabled")
        thread = threading.Thread(target=self.run_export, daemon=True)
        thread.start()

    def run_export(self):
        yahoo_email = self.email_var.get().strip()
        app_password = self.password_var.get()
        folder_name = self.folder_var.get().strip() or "INBOX"
        search_criteria = self.search_var.get().strip() or "ALL"
        output_folder = self.output_var.get().strip()
        wk_path = self.wk_var.get().strip()

        if not yahoo_email or not app_password:
            self.log("ERROR: Email and app password are required.")
            self.run_button.configure(state="normal")
            return

        os.makedirs(output_folder, exist_ok=True)
        config = pdfkit.configuration(wkhtmltopdf=wk_path)

        try:
            mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
            mail.login(yahoo_email, app_password)
        except Exception as e:
            self.log(f"ERROR: Login failed: {e}")
            self.run_button.configure(state="normal")
            return

        status, _ = mail.select(folder_name)
        if status != "OK":
            self.log(f"ERROR: Could not select folder '{folder_name}'. Check the exact folder name.")
            self.run_button.configure(state="normal")
            return

        status, data = mail.search(None, search_criteria)
        email_ids = data[0].split()
        self.log(f"Found {len(email_ids)} matching emails")

        for i, eid in enumerate(email_ids, start=1):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg.get("Subject", f"email_{i}")
            from_ = msg.get("From", "")
            to_ = msg.get("To") or msg.get("Delivered-To") or msg.get("X-Original-To") or yahoo_email
            date_str = format_date(msg.get("Date", ""))

            html_body = None
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        charset = part.get_content_charset() or "utf-8"
                        html_body = part.get_payload(decode=True).decode(charset, errors="replace")
                        break
            else:
                if msg.get_content_type() == "text/html":
                    charset = msg.get_content_charset() or "utf-8"
                    html_body = msg.get_payload(decode=True).decode(charset, errors="replace")

            if html_body is None:
                self.log(f"[{i}] No HTML part found for '{subject}' — skipping")
                continue

            full_html = build_header_html(subject, from_, to_, date_str) + html_body
            filename = sanitize_filename(f"{i}_{subject}") + ".pdf"
            filepath = os.path.join(output_folder, filename)

            try:
                pdf_options = {'load-error-handling': 'ignore', 'load-media-error-handling': 'ignore'}
                pdfkit.from_string(full_html, filepath, configuration=config, options=pdf_options)
                self.log(f"[{i}] Saved: {filename}")
            except Exception as e:
                self.log(f"[{i}] Failed to convert '{subject}': {e}")

        mail.logout()
        self.log("Done.")
        self.run_button.configure(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Yahoo Email Exporter", "Yahoo Email Exporter\nMade by Xhris Bryan")
    root.deiconify()
    app = ExporterApp(root)
    root.mainloop()
