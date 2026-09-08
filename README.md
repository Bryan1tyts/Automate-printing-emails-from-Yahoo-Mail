# Automate-printing-emails-from-Yahoo-Mail
Automate printing emails from Yahoo Mail. Not print as in print but rather to have PDF Copy of the email.

## Yahoo Email Exporter
A desktop GUI that searches a Yahoo Mail folder via IMAP for messages matching a criteria (e.g. sender domain), and exports each match to a PDF — including a header block (Subject, From, To, Date) mimicking Yahoo's native print format.

## Requirements
- Python 3
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) installed on your system
- `pip install pdfkit`

## Setup

1. Generate a Yahoo app password ([Account Security settings → Generate app password](https://login.yahoo.com/myaccount/security?.scrumb=CmNiy0%2FIH6b)). Your regular password won't work over IMAP.
2. Run:

   ```
   python yahoo_exporter_gui.py
   ```

3. Fill in your Yahoo email and app password, then click **List Folders** to auto-populate the folder dropdown instead of guessing the exact IMAP folder name.
4. Set your search criteria (e.g. `FROM "domain.com"`, or `ALL` for every email in the folder — leaving it blank will cause an IMAP error, since `ALL` is the required syntax for "no filter"), pick an output folder, confirm the wkhtmltopdf path, and click **Run Export**. Progress and errors are shown in the log box.

## Building a standalone .exe

The GUI script can be packaged into a Windows executable with PyInstaller. This must be run **on Windows** — PyInstaller builds only for the OS it's run on, so this produces a Windows-only `.exe`; there's no cross-platform build from a single run.

```
pip install pyinstaller pdfkit
pyinstaller --onefile --windowed --name YahooEmailExporter yahoo_exporter_gui.py
```

The finished `.exe` will be in the generated `dist/` folder. Note that `wkhtmltopdf` itself is **not** bundled into the exe — it still needs to be installed separately on any machine that runs it, since PyInstaller only packages the Python code, not external binaries it calls out to.

## Notes
- The folder you select must be one Yahoo actually reports over IMAP — use the **List Folders** button if unsure of the exact name.
- Inline images referenced via `Content-ID` (`cid:`) in the original email will not render in the PDF — this covers the visible HTML/text content only.
- Running the GUI requires manual interaction each time (filling fields, clicking Run) — it does not support unattended/scheduled runs.
