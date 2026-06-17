-- ============================================================
--  Athenaeum Academy — Complete Database Setup
--  Run this in: Supabase Dashboard → SQL Editor
--  Project: hgbaqaofrkljmrvcaisp
-- ============================================================


-- ── 1. PROFILES TABLE ──────────────────────────────────────
--  Stores extra user info beyond what auth.users provides
-- ───────────────────────────────────────────────────────────
create table if not exists public.profiles (
  id            uuid        references auth.users(id) on delete cascade primary key,
  full_name     text,
  role          text        default 'Student' check (role in ('Student','Parent','Teacher')),
  plan_type     text        default 'trial'   check (plan_type in ('trial','paid','free')),
  trial_start   timestamptz default now(),
  trial_end     timestamptz default (now() + interval '3 days'),
  phone         text,
  avatar_url    text,
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

-- Enable Row Level Security
alter table public.profiles enable row level security;

-- RLS Policies for profiles
create policy "Users can view own profile"
  on public.profiles for select
  to authenticated
  using ( (select auth.uid()) = id );

create policy "Users can update own profile"
  on public.profiles for update
  to authenticated
  using ( (select auth.uid()) = id )
  with check ( (select auth.uid()) = id );


-- ── 2. AUTO-CREATE PROFILE ON SIGNUP ───────────────────────
--  Trigger: jab bhi new user signup kare, profile auto-bane
-- ───────────────────────────────────────────────────────────
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  insert into public.profiles (id, full_name, role, plan_type)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
    coalesce(new.raw_user_meta_data->>'role', 'Student'),
    'trial'   -- Har naya user trial se start kare
  );
  return new;
end;
$$;

-- Drop existing trigger if any, then recreate
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();


-- ── 3. AI USAGE TRACKING TABLE ─────────────────────────────
--  Tracks daily question & quiz counts per user
-- ───────────────────────────────────────────────────────────
create table if not exists public.ai_usage (
  id            bigint      generated always as identity primary key,
  user_id       uuid        references auth.users(id) on delete cascade not null,
  usage_date    date        default current_date not null,
  questions_used int        default 0,
  quizzes_used  int        default 0,
  updated_at    timestamptz default now(),
  unique(user_id, usage_date)
);

alter table public.ai_usage enable row level security;

create policy "Users can view own AI usage"
  on public.ai_usage for select
  to authenticated
  using ( (select auth.uid()) = user_id );

create policy "Users can upsert own AI usage"
  on public.ai_usage for insert
  to authenticated
  with check ( (select auth.uid()) = user_id );

create policy "Users can update own AI usage"
  on public.ai_usage for update
  to authenticated
  using ( (select auth.uid()) = user_id )
  with check ( (select auth.uid()) = user_id );


-- ── 4. UPDATED_AT AUTO-TRIGGER ─────────────────────────────
create or replace function public.set_updated_at()
returns trigger language plpgsql security invoker
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_updated_at
  before update on public.profiles
  for each row execute procedure public.set_updated_at();

create trigger ai_usage_updated_at
  before update on public.ai_usage
  for each row execute procedure public.set_updated_at();


-- ── 5. COURSE ENROLLMENTS TABLE ────────────────────────────
create table if not exists public.enrollments (
  id          bigint      generated always as identity primary key,
  user_id     uuid        references auth.users(id) on delete cascade not null,
  course_name text        not null,
  enrolled_at timestamptz default now(),
  unique(user_id, course_name)
);

alter table public.enrollments enable row level security;

create policy "Users can view own enrollments"
  on public.enrollments for select
  to authenticated
  using ( (select auth.uid()) = user_id );


-- ── 6. GRANT API ACCESS ────────────────────────────────────
grant usage on schema public to anon, authenticated;
grant select on public.profiles to authenticated;
grant update on public.profiles to authenticated;
grant select, insert, update on public.ai_usage to authenticated;
grant select on public.enrollments to authenticated;


-- ── DONE! ─────────────────────────────────────────────────
select 'Athenaeum database setup complete! ✅' as status;
