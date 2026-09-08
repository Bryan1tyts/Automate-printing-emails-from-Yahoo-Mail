# Automate-printing-emails-from-Yahoo-Mail
Automate printing emails from Yahoo Mail. Not print as in print but rather to have PDF Copy of the email. 
Yahoo Email Exporter

Searches a Yahoo Mail folder via IMAP for messages matching a criteria (e.g. sender domain), and exports each match to a PDF — including a header block (Subject, From, To, Date) mimicking Yahoo's native print format.

Requirements
Python 3
wkhtmltopdf installed on your system
pip install pdfkit
Setup
Generate a Yahoo app password (Account Security settings → Generate app password). Your regular password won't work over IMAP. (https://login.yahoo.com/myaccount/security?.scrumb=CmNiy0%2FIH6b)
Set environment variables before running:
   set YAHOO_EMAIL=your_email@yahoo.com
   set WKHTMLTOPDF_PATH=C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
   set FOLDER_NAME=INBOX (or where are the emails you would like to be downloaded)
   set SEARCH_CRITERIA=FROM "domain of what you're searching for eg. google.com"

(On Windows Command Prompt, use set VAR=value. On PowerShell, use $env:VAR="value". Or you could just use an IDE to edit the values)

Run:
   python yahoo_email_export.py

You'll be prompted for your app password at runtime (input is hidden).

Notes
FOLDER_NAME must exactly match how Yahoo reports the folder over IMAP — list your folders with a simple mail.list() call if unsure.
Inline images referenced via Content-ID (cid:) in the original email will not render in the PDF — this covers the visible HTML/text content only.
Output PDFs are saved to output_pdfs/, which is gitignored — they aren't meant to be committed.
