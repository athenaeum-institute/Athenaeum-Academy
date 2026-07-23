CREATE OR REPLACE FUNCTION public.admin_delete_live_class(class_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if the user is an admin
  IF public.is_admin() THEN
    -- Force delete bypassing RLS
    DELETE FROM public.live_classes WHERE id = class_id;
    RETURN TRUE;
  END IF;
  
  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
