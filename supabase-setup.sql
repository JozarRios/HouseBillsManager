-- House Bills: run once in Supabase → SQL Editor → New query → Run
create table if not exists public.house_data (
  id          text primary key,
  data        jsonb not null,
  updated_at  timestamptz not null default now(),
  updated_by  uuid references auth.users(id)
);

-- Only signed-in users can read or write. Visitors without an account get nothing.
alter table public.house_data enable row level security;

drop policy if exists "signed-in read"   on public.house_data;
drop policy if exists "signed-in insert" on public.house_data;
drop policy if exists "signed-in update" on public.house_data;

create policy "signed-in read"   on public.house_data for select to authenticated using (true);
create policy "signed-in insert" on public.house_data for insert to authenticated with check (true);
create policy "signed-in update" on public.house_data for update to authenticated using (true) with check (true);
