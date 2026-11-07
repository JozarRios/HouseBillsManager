# House Bills — go-live setup (about 15 minutes)

Folder layout
- app/                     ← the website. Drag THIS folder onto Netlify.
- house-bills-initial.json ← your spreadsheet data (meters, tenants, all readings). Keep private, do NOT upload to Netlify.
- seed-data.js, import_from_excel.py ← used only when you open app/index.html locally.
- supabase-setup.sql       ← creates the database table.

## 1. Create the database (Supabase, free)
1. Sign up at https://supabase.com → New project (region: Southeast Asia / Singapore). Save the database password somewhere safe.
2. Left menu → SQL Editor → New query → paste everything from supabase-setup.sql → Run.
3. Authentication → Sign In / Providers → Email: turn OFF "Allow new users to sign up"
   (so strangers can't create accounts). Keep Email provider enabled.
4. Authentication → Users → Add user → Create new user: your email + a strong password,
   tick "Auto Confirm User". Repeat for anyone else who should have access.

## 2. Connect the app
1. Project Settings → API (Data API) → copy the Project URL and the "anon public" key.
2. Open app/config.js in a text editor and paste them:
       supabaseUrl: 'https://xxxx.supabase.co',
       supabaseAnonKey: 'eyJ...'
   (The anon key is designed to be public; login + row level security protect the data.)

## 3. Deploy
1. Go to https://app.netlify.com/drop and drag the app folder in.
2. Optional: Site configuration → change the site name for a nicer URL.
3. Updating later: Netlify → your site → Deploys → drag the app folder again.

## 4. Load your spreadsheet data (once)
1. Open the site, sign in.
2. Settings → Data & backup → Import backup → choose house-bills-initial.json.
   It saves to the cloud. Every device you sign in on now sees the same data.
   (If you recorded payments in the old local version, use Export backup there and import that file instead.)

## Good to know
- Changes save automatically (green "Saved" dot at the top). Switching devices pulls the latest.
- If two people edit at the exact same moment, the last save wins.
- Forgot password: Supabase → Authentication → Users → … → Send password recovery, or set a new one there.
- Free Supabase projects pause after 1 week of no use; open the Supabase dashboard and click "Restore" if that happens.
- Export a backup from Settings every month or so.
