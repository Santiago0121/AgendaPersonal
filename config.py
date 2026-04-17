import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # para operaciones admin
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")  # tu email de admin

# Cliente normal (anon key) — para operaciones de usuario
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cliente admin (service role key) — para crear usuarios y tenants
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)