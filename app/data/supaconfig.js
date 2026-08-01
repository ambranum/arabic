// Supabase connection — PUBLIC values only.
// The anon key is designed to live in browser code; it grants nothing on its own. What actually
// protects each user's data is the row-level-security policy on the `progress` table (a user can
// only read/write the row where user_id = their own auth id). The SECRET service_role key and the
// database password must NEVER appear here.
window.SUPA = {
  url:  'https://dwpswqccyddplvvqltjb.supabase.co',
  anon: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cHN3cWNjeWRkcGx2dnFsdGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU1Njc3MDIsImV4cCI6MjEwMTE0MzcwMn0.4PzS6yffM_bcZ5NUeuGkMoLQ1cFtTd3qLh3LpxStBwU',
};
