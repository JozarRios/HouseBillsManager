"""Regenerate seed-data.js from ../../Meralco_Computation.xlsx.
Run:  python3 import_from_excel.py   (needs: pip install openpyxl)
Local app: Settings -> Data & backup -> "Reset to spreadsheet data".
"""
import json, os, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, '..', '..', 'Meralco_Computation.xlsx')
wb = openpyxl.load_workbook(XLSX, data_only=True)
# meter id -> (sheet, {tenant id: (PREVIOUS col, CURRENT col)})
SPEC = {
    'anthony':  ('Anthony',  {'ninang': ('I', 'J'), 'andrew': ('M', 'N'), 'hazel': ('Q', 'R'), 'cy': ('U', 'V')}),
    'amorfino': ('Amorfino', {'cj': ('I', 'J'), 'bheng': ('M', 'N'), 'shenna': ('Q', 'R'), 'joel': ('U', 'V')}),
}
# Meter & tenant setup (min charge, rent, due days come from the RENT DUES sheet / REPORT sheet)
METERS = [
    {'id': 'anthony',  'name': 'Anthony',  'floor': '1st floor', 'startDay': 25, 'account': ''},
    {'id': 'amorfino', 'name': 'Amorfino', 'floor': '2nd floor', 'startDay': 25, 'account': ''},
]
TENANTS = [
    {'id': 'ninang', 'name': 'Ninang Ada',      'meter': 'anthony',  'type': 'submeter',  'min': 0,   'rent': 5500, 'due': [25]},
    {'id': 'andrew', 'name': 'Kuya Andrew',     'meter': 'anthony',  'type': 'submeter',  'min': 500, 'rent': 2500, 'due': [15]},
    {'id': 'hazel',  'name': 'Ate Hazel',       'meter': 'anthony',  'type': 'submeter',  'min': 0,   'rent': 2500, 'due': [25]},
    {'id': 'cy',     'name': 'Ate Cy',          'meter': 'anthony',  'type': 'submeter',  'min': 0,   'rent': 5000, 'due': [5]},
    {'id': 'star',   'name': 'Star',            'meter': 'anthony',  'type': 'remainder', 'min': 0,   'rent': 2000, 'due': [15]},
    {'id': 'cj',     'name': 'Tita CJ',         'meter': 'amorfino', 'type': 'submeter',  'min': 0,   'rent': 0,    'due': []},
    {'id': 'bheng',  'name': 'Tita Bheng',      'meter': 'amorfino', 'type': 'submeter',  'min': 0,   'rent': 2500, 'due': [10, 25]},
    {'id': 'shenna', 'name': 'Shenna',          'meter': 'amorfino', 'type': 'submeter',  'min': 0,   'rent': 0,    'due': []},
    {'id': 'joel',   'name': 'Tito Joel',       'meter': 'amorfino', 'type': 'submeter',  'min': 500, 'rent': 1000, 'due': [30]},
    {'id': 'sean',   'name': 'Sean Troy + Ref', 'meter': 'amorfino', 'type': 'remainder', 'min': 0,   'rent': 0,    'due': []},
]
def num(v): return round(v, 2) if isinstance(v, (int, float)) else None
out = []
for mid, (sheet, tenants) in SPEC.items():
    ws = wb[sheet]
    for r in range(4, ws.max_row + 1):
        f, t = ws[f'A{r}'].value, ws[f'B{r}'].value
        if not hasattr(f, 'strftime') or not hasattr(t, 'strftime'): continue
        rate = num(ws[f'H{r}'].value)
        rd = {}
        for tid, (p, c) in tenants.items():
            pv, cv = num(ws[f'{p}{r}'].value), num(ws[f'{c}{r}'].value)
            if cv is not None: rd[tid] = [pv if pv is not None else cv, cv]
        if rate is None or not rd: continue
        out.append({'m': mid, 'f': f.strftime('%Y-%m-%d'), 't': t.strftime('%Y-%m-%d'),
                    'b': num(ws[f'C{r}'].value), 'r': rate,
                    'mp': num(ws[f'E{r}'].value), 'mc': num(ws[f'D{r}'].value), 'rd': rd})
with open(os.path.join(HERE, 'seed-data.js'), 'w') as fh:
    fh.write('// Generated from Meralco_Computation.xlsx by import_from_excel.py\n')
    fh.write('window.SEED_PERIODS = ' + json.dumps(out, separators=(',', ':')) + ';\n')
    fh.write('window.SEED_METERS = ' + json.dumps(METERS) + ';\n')
    fh.write('window.SEED_TENANTS = ' + json.dumps(TENANTS) + ';\n')
print(f'Wrote {len(out)} billing periods to seed-data.js')
