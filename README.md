# House Bills — Documentation

A web app for splitting the Meralco electric bill between tenants and tracking monthly rent collection.
It replaces the manual workflow in `Meralco_Computation.xlsx` and uses the same formulas.

---

## 1. Overview

| | |
|---|---|
| **Purpose** | Compute each tenant's electric share per billing period, collect payments, track rent, produce reports |
| **Users** | House owner / admins (sign-in required when deployed) |
| **Tech** | Single-page app: one `index.html` (HTML + CSS + vanilla JavaScript), no build step |
| **Hosting** | Netlify (static, drag-and-drop) |
| **Database & login** | Supabase (Postgres + Auth), free tier |
| **Modes** | **Cloud mode** (Supabase configured) or **Local mode** (data in the browser only) |

---

## 2. Folder structure

```
House_Management/Prototype/
├── app/                      ← the website (deploy this folder to Netlify)
│   ├── index.html            ← the whole app
│   ├── config.js             ← Supabase URL + anon key (empty = local mode)
│   ├── _headers              ← Netlify security headers (no-index, no-frame, no-cache for config)
│   └── robots.txt            ← blocks search engines
├── house-bills-initial.json  ← spreadsheet data as an app backup (PRIVATE — do not deploy)
├── seed-data.js              ← spreadsheet data for local mode (PRIVATE — do not deploy)
├── import_from_excel.py      ← regenerates seed-data.js from the spreadsheet
├── supabase-setup.sql        ← creates the database table + security rules
├── SETUP.md                  ← go-live checklist
└── README.md                 ← this file
```

---

## 3. Concepts

| Term | Meaning |
|---|---|
| **Meter** | A Meralco account/main meter (e.g. *Anthony* = 1st floor, *Amorfino* = 2nd floor). Each has its own tenants and billing start day. |
| **Submeter** | A tenant's own meter inside a main meter. Billed by reading. |
| **Remainder tenant** | A tenant with no submeter (e.g. Star, Sean). Pays whatever is left of the Meralco bill. |
| **Billing period** | From the meter's start day to the day before it next month (default 25th → 24th). |
| **Rate** | ₱ per kWh charged to tenants for that period (entered per period). |
| **Minimum charge** | A floor amount for a tenant (e.g. ₱500 for Kuya Andrew, Tito Joel). |
| **Rent due** | Monthly rent on one or more due days (e.g. Tita Bheng: 10th & 25th, split in halves). |

---

## 4. Billing formulas

Same logic as the REPORT sheet.

| Item | Formula |
|---|---|
| Consumed (kWh) | `current reading − previous reading` |
| Submeter amount | `ROUNDUP(consumed × rate, 0)` |
| Minimum top-up | if amount < minimum → `minimum − amount`, else 0 |
| Remainder share | `Meralco bill − sum of submeter amounts` (before top-ups); split evenly if several remainder tenants |
| Adjustment | any ± amount typed manually per tenant |
| **Tenant total** | `amount + minimum top-up + adjustment` |
| Over/(under) bill | `total charged − Meralco bill` (surplus comes from minimum top-ups and adjustments) |
| Suggested rate | `bill ÷ (main meter current − previous)` (only when main readings are entered) |

Example (Aug 25 – Sep 24, 2026, Anthony, rate ₱17): Ninang Ada 28.0 kWh → ₱476; Star = ₱3,209 − ₱2,415 = ₱794.

---

## 5. Screens

### 5.1 Layout
- **Left sidebar** with Dashboard, Electric billing, Rent, Reports, Settings. The ☰ button collapses it to icons (desktop) or opens it as a drawer (phone).
- **Top bar**: sync status (cloud mode), today's date, sign-out, dark/light theme.
- Sidebar card shows how many meter readings are waiting.

### 5.2 Dashboard
Filters: **Billing period** (calendar), **Meter** (dropdown), **Tenant** (dropdown).
- KPI cards: kWh consumed (vs previous period), electric amount, rent amount, outstanding.
- Consumption statistic: kWh trend over the last 12 periods (per meter, or per tenant).
- Electric share: donut of each tenant's share (or the tenant vs others).
- Electric vs rent: bar chart per period.
- To collect: unpaid electric bills and rent due within 7 days / overdue, with **Copy message** and **Mark paid**.
- Tenants this period: readings, kWh, electric, rent, statuses, **Statement** (JPEG).

### 5.3 Electric billing
1. Choose the **meter** and **billing period** (calendar or ‹ › arrows).
2. Enter the **Meralco bill** and **rate** (main meter readings are optional).
3. Type each tenant's **current reading** — the previous reading is filled from last period. The cursor jumps to the next empty reading.
4. Amounts, minimum top-ups, remainder and totals compute instantly.
5. Tick **Paid** as tenants pay, or **Mark all paid**. **Copy all messages** copies ready-to-send bills for Messenger/SMS.
6. **+ New period** opens the next period (enabled once the current one is complete). The latest period can be deleted.
- Draft = readings or bill still missing; drafts don't count as money owed.

### 5.4 Rent
- Month picker (calendar). KPI cards: expected, collected, remaining, overdue.
- Table of every due date with status: *Upcoming*, *Due in Nd*, *Overdue*, *Paid (date)*, *Before tracking*.
- **Mark paid** (today's date, editable), **Undo**, **Copy reminder**.

### 5.5 Reports
| Tab | Contents | Export |
|---|---|---|
| **Anthony meter / Amorfino meter** (one tab per meter) | Period report like the REPORT sheet (with/without submeter, totals, overall bill), bill vs charged chart, usage per tenant chart | **Export PDF**, **All statements** (JPEG per tenant) |
| **Rent** | Monthly collection report + year overview grid (✓ paid · ! overdue · ○ upcoming · · before tracking) | **Export PDF** |
| **Tenant statements** | Pick tenant + period → preview of a one-page bill image | **Download JPEG**, **All tenants** |

PDF: the print dialog opens with only the report — choose **Save as PDF**.
Statement image contains: readings, kWh, rate, amount, top-ups/adjustments, electric total + paid status, rent dues in the period, earlier unpaid balance, and **Total amount due**.

### 5.6 Settings (expandable sections)
- **Meter setup** — add / edit / delete meters: name, floor/label, billing start day (1–28), Meralco account no. A meter with tenants can't be deleted. A new start day applies to the next period.
- **Tenants setup** — add / edit / delete tenants: name, contact no., meter, billing type (own submeter / no submeter), minimum charge, monthly rent, rent due day(s), move-in date, active. Deleting a tenant with history hides them but keeps past bills.
- **How amounts are computed** — the rules above.
- **Data & backup** — Export backup (.json), Import backup, Reset to spreadsheet data (local mode only).

---

## 6. Data

### 6.1 Storage
| Mode | Where data lives | Shared across devices |
|---|---|---|
| Cloud | Supabase table `house_data`, row `id = 'main'` (whole app state as JSON) + a cache in the browser | Yes (pulls latest when the window regains focus) |
| Local | Browser `localStorage` only | No |

Saving is automatic (≈0.7 s after a change). Status dot: green *Saved*, yellow *Saving…*, red *Not saved — retrying* (retries every 8 s and when back online). Closing the tab with unsaved changes shows a warning. If two people save at the same time, the last save wins.

### 6.2 Data model (simplified)
```json
{
  "version": 2,
  "meters":  [{ "id", "name", "floor", "startDay", "account" }],
  "tenants": [{ "id", "name", "phone", "meter", "type": "submeter|remainder",
                "min", "rent", "due": [25], "moveIn", "active", "deleted" }],
  "periods": [{ "id", "meter", "from", "to", "bill", "rate", "mainPrev", "mainCurr",
                "readings": { "<tenantId>": { "prev", "curr" } },
                "adj": { "<tenantId>": 0 }, "paid": { "<tenantId>": "YYYY-MM-DD" }, "note" }],
  "rent":    { "YYYY-MM": { "<tenantId>#<n>": { "on": "YYYY-MM-DD" } } },
  "rentStart": "YYYY-MM"
}
```

### 6.3 Initial data from the spreadsheet
- `import_from_excel.py` reads the **Anthony** and **Amorfino** sheets (date, bill, rate, main readings, each tenant's previous/current) and writes `seed-data.js`. Tenant rent/minimums are set in the script (from the RENT DUES and REPORT sheets).
- `house-bills-initial.json` is the same data as an app backup, for importing into cloud mode.
- Assumptions in the initial data: all periods before the latest billed one are marked **paid**; rent tracking starts **November 2026** (earlier months show *Before tracking*).
- The "Meralco account" sheet (email/password) is never imported.

Regenerate after editing the spreadsheet:
```bash
cd House_Management/Prototype
python3 import_from_excel.py      # needs: pip install openpyxl
```
Then local mode: Settings → Reset to spreadsheet data. (Cloud mode: enter new readings in the app instead.)

---

## 7. Security
- Login required in cloud mode (Supabase email + password). Public sign-ups should be **disabled**; admins are added in Supabase → Authentication → Users.
- Row Level Security: only signed-in users can read/write `house_data`; anonymous visitors get nothing.
- The anon key in `config.js` is public by design; it can't read data without a login.
- No tenant data is in the deployed files. `_headers` + `robots.txt` stop search indexing and framing.
- Sign-out clears the cached data from that browser.

---

## 8. Deployment & maintenance
Full checklist: **SETUP.md**. Summary:
1. Supabase: create project → run `supabase-setup.sql` → disable sign-ups → add user(s).
2. Paste Project URL + anon key into `app/config.js`.
3. Drag `app/` onto https://app.netlify.com/drop.
4. Sign in → Settings → Import backup → `house-bills-initial.json`.

| Task | How |
|---|---|
| Update the app | Replace files in `app/`, then Netlify → Deploys → drag `app/` again |
| Add an admin | Supabase → Authentication → Users → Add user |
| Reset a password | Supabase → Authentication → Users → … → Send recovery / set password |
| Backup | Settings → Export backup (monthly) |
| Restore | Settings → Import backup |
| Supabase paused (free tier, 1 week idle) | Supabase dashboard → Restore project |

---

## 9. Monthly workflow
1. Around the 24th–25th: read each submeter.
2. When the Meralco bill arrives: **Electric billing → + New period** (if not already open) → enter bill, rate, current readings.
3. **Copy all messages** (or send statements as JPEG) to tenants.
4. Tick **Paid** / **Mark paid** as payments arrive (electric and rent).
5. Check **Dashboard → To collect** for anything outstanding; export reports as needed.

---

## 10. Limitations / future ideas
- Last-write-wins sync; no real-time multi-user editing or change history.
- Only one shared dataset (one household).
- Payments are all-or-nothing per bill (no partial payments).
- Statements are images; no automatic SMS/Messenger sending.
- Possible next steps: partial payments, audit log, tenant self-view links, automatic reminders, receipts.

## 11. Troubleshooting
| Problem | Fix |
|---|---|
| Login says "Wrong email or password" | Check the user exists in Supabase and is confirmed |
| "Could not load data from the database" | Check `config.js` values and that `supabase-setup.sql` was run |
| Dashboard says "No data yet" | Import `house-bills-initial.json` in Settings |
| Red "Not saved — retrying" | Internet issue; it retries automatically — don't close the tab |
| Fonts look different | Poppins loads from Google Fonts; offline it falls back to system font |
| Multiple JPEG downloads blocked | Allow multiple downloads for the site in the browser prompt |
