# Automate-printing-emails-from-Yahoo-Mail
Automate printing emails from Yahoo Mail. Not print as in print but rather to have PDF Copy of the email.

## Yahoo Email Exporter
Searches a Yahoo Mail folder via IMAP for messages matching a criteria (e.g. sender domain), and exports each match to a PDF — including a header block (Subject, From, To, Date) mimicking Yahoo's native print format.

Two ways to use this: a command-line script, or a desktop GUI.

## Requirements
- Python 3
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) installed on your system
- `pip install pdfkit`

## Setup — Command Line (`yahoo_hubstaff_export.py`)

1. Generate a Yahoo app password ([Account Security settings → Generate app password](https://login.yahoo.com/myaccount/security?.scrumb=CmNiy0%2FIH6b)). Your regular password won't work over IMAP.
2. Set environment variables before running:

   ```
   set YAHOO_EMAIL=your_email@yahoo.com
   set WKHTMLTOPDF_PATH=C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
   set FOLDER_NAME=INBOX (or wherever the emails you want to download are)
   set SEARCH_CRITERIA=FROM "domain of what you're searching for, e.g. google.com"
   ```

   (On Windows Command Prompt, use `set VAR=value`. On PowerShell, use `$env:VAR="value"`. Or just use an IDE to edit the values directly in the script.)

   To download **every** email in the folder with no filter, set `SEARCH_CRITERIA=ALL` — leaving it blank will cause an IMAP error, since `ALL` is the required syntax for "no filter."

3. Run:

   ```
   python yahoo_hubstaff_export.py
   ```

   You'll be prompted for your app password at runtime (input is hidden).

## Setup — GUI (`yahoo_exporter_gui.py`)

A desktop window with fields for email, app password, IMAP folder, search criteria, output folder, and the wkhtmltopdf path — no environment variables needed.

1. Run:

   ```
   python yahoo_exporter_gui.py
   ```

2. Fill in your Yahoo email and app password, then click **List Folders** to auto-populate the folder dropdown instead of guessing the exact IMAP folder name.
3. Set your search criteria (or `ALL` for everything in the folder), pick an output folder, confirm the wkhtmltopdf path, and click **Run Export**. Progress and errors are shown in the log box.

### Building a standalone .exe from the GUI

The GUI script can be packaged into a Windows executable with PyInstaller. This must be run **on Windows** — PyInstaller builds only for the OS it's run on, so this produces a Windows-only `.exe`; there's no cross-platform build from a single run.

```
pip install pyinstaller pdfkit
pyinstaller --onefile --windowed --name YahooEmailExporter yahoo_exporter_gui.py
```

The finished `.exe` will be in the generated `dist/` folder. Note that `wkhtmltopdf` itself is **not** bundled into the exe — it still needs to be installed separately on any machine that runs it, since PyInstaller only packages the Python code, not external binaries it calls out to.

## Notes
- `FOLDER_NAME` must exactly match how Yahoo reports the folder over IMAP — use the GUI's **List Folders** button, or run a simple `mail.list()` call, if unsure of the exact name.
- Inline images referenced via `Content-ID` (`cid:`) in the original email will not render in the PDF — this covers the visible HTML/text content only.
- Output PDFs are saved to `output_pdfs/`, which is gitignored — they aren't meant to be committed.
