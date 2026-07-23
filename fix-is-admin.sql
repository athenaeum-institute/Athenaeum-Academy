-- Update is_admin function to be case-insensitive for role check
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    TRIM(LOWER(coalesce(current_setting('request.jwt.claims', true)::jsonb->'user_metadata'->>'role', ''))) = 'admin' OR
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND TRIM(LOWER(role)) = 'admin')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
