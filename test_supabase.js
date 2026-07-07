const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://hgbaqaofrkljmrvcaisp.supabase.co';
const supabaseAnonKey = 'sb_publishable_FTsvy-qhy1vfn0idE04bPQ_dTLlQZm0';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function test() {
  const { data, error } = await supabase
    .from('enrollments')
    .select('*, courses(title)')
    .eq('payment_status', 'pending');

  if (error) {
    console.error('Error:', error);
  } else {
    console.log(`Found ${data.length} enrollments`);
    console.log(data);
  }
}

test();
