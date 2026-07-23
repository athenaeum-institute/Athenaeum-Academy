CREATE OR REPLACE FUNCTION public.admin_delete_live_class(class_id UUID, caller_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_role TEXT;
BEGIN
  -- Get the caller's role directly using the ID passed from the frontend
  SELECT role INTO v_role FROM public.profiles WHERE id = caller_id;
  
  -- Check if that ID belongs to an admin
  IF TRIM(LOWER(v_role)) = 'admin' THEN
    -- Force delete bypassing RLS
    DELETE FROM public.live_classes WHERE id = class_id;
    RETURN TRUE;
  END IF;
  
  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
