ScreenSense AI is a context-aware desktop assistant that observes the user's active screen (apps, browser tabs, content) and provides real-time, privacy-first assistance through a floating chat widget.

It focuses on:

Contextual understanding
Smart suggestions & automation
Strong privacy & user consent
🚀 Primary Capabilities
1. Active Window Detection
Detects foreground app (title, process, URL)
Classifies app type:
Browser (Amazon, YouTube, Gmail)
Spreadsheet (Excel)
Editor (VS Code, Notepad)
PDF, Terminal, Media Player, etc.
2. Screen Content Extraction
Screenshot capture (only with consent)
OCR text extraction
Structured data parsing (tables, grids)
Direct file reading via APIs (e.g., Excel using pandas/openpyxl)
3. Contextual Understanding
Infers user intent from:
UI elements
Text content
Window metadata
Detects domains:
Billing sheets
Shopping carts
Code errors
Emails
4. Suggestions & Actions
Natural language suggestions
Error detection (e.g., Excel formulas)
Automation with:
Preview
One-click confirmation
5. Interaction Modes
Floating chat widget
Optional voice input/output
Action buttons:
Explain
Fix
Summarize
Ignore
Show Source
🔒 Principles & Rules
A. Privacy & Consent
Explicit permission before:
Screen capture
File access
Sensitive data handling:
Passwords, OTPs, cards → redacted
No transmission without user consent
B. Transparency

Each suggestion includes:

Reason
Source of data
Confidence level
C. Minimal Data Transfer
Local-first processing
Send only:
Extracted text
Metadata
No raw screenshots unless required
D. Safety
No destructive actions without confirmation
Always preview automation
