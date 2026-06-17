async function fetchCourses() {
  const supabaseUrl = 'https://hgbaqaofrkljmrvcaisp.supabase.co';
  const supabaseAnonKey = 'sb_publishable_FTsvy-qhy1vfn0idE04bPQ_dTLlQZm0';
  const url = `${supabaseUrl}/rest/v1/courses?select=*`;
  try {
    const response = await fetch(url, {
      headers: {
        'apikey': supabaseAnonKey,
        'Authorization': `Bearer ${supabaseAnonKey}`
      }
    });
    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } catch(e) {
    console.error(e);
  }
}
fetchCourses();
