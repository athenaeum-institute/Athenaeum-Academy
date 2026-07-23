-- CHECK 1: Apni own profile ki role dekhen
SELECT id, email, role FROM public.profiles WHERE id = auth.uid();
