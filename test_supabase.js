const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://hgbaqaofrkljmrvcaisp.supabase.co';
const supabaseAnonKey = 'sb_publishable_FTsvy-qhy1vfn0idE04bPQ_dTLlQZm0';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function test() {
  const { data, error } = await supabase
    .from('courses')
    .select('*, profiles:instructor_id(full_name, avatar_url)')
    .eq('is_published', true)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Error:', error);
  } else {
    console.log(`Found ${data.length} courses`);
  }
}

test();
