import { createClient } from '@supabase/supabase-js'

// these values come from our .env file, never hardcoded directly here
// vite only exposes env variables that start with VITE_
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// this creates one single supabase client we can import and reuse
// anywhere in the app that needs to talk to the database
export const supabase = createClient(supabaseUrl, supabaseAnonKey)