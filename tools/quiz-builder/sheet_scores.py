#!/usr/bin/env python3
"""Pull team names + scores from the quiz sheet's SCORES tab into rounds.py (HALFTIME / FINAL lists).
Usage: sheet_scores.py half|final   (needs the service-account key; see ../../../CLAUDE.md)"""
import os, re, sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
SID, TAB = "1lDtdsYenHt9ION29XpP09DxkkE1-mCgl6w3KUI8un9A", "#7 SCORES"
KEY = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", os.path.expanduser("~/.config/gcp/nostalgia-sheets-sa.json"))
which = sys.argv[1]; col, var = {"half": (5, "HALFTIME"), "final": (9, "FINAL")}[which]
svc = build("sheets", "v4", credentials=service_account.Credentials.from_service_account_file(
    KEY, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])).spreadsheets()
rows = svc.values().get(spreadsheetId=SID, range=f"'{TAB}'!A2:J60").execute().get("values", [])
teams = [(r[1].strip(), int(float(r[col]))) for r in rows if len(r) > col and r[1].strip() and str(r[col]).strip() not in ("", "0")]
body = "".join(f"    ({n!r}, {p}),\n" for n, p in teams)
block = f"{var} = [  # from the '{TAB}' tab via sheet_scores.py\n{body}]\n"
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rounds.py"); s = open(p).read()
s = re.sub(rf"^{var} = \[.*?^\]\n", block, s, count=1, flags=re.S | re.M) if re.search(rf"^{var} = \[", s, re.M) else s.rstrip() + "\n\n" + block
open(p, "w").write(s); print(f"{var}: {len(teams)} teams")
