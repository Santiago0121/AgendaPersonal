from config import supabase, supabase_admin
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("VERIFICANDO CONEXIÓN CON SUPABASE")
print("=" * 50)

# 1. Conexión básica
try:
    res = supabase_admin.table("tenants").select("*").execute()
    print(f"✅ Conexión OK — {len(res.data)} tenant(s) encontrado(s)")
    for t in res.data:
        print(f"   → {t['nombre']} | {t['email']} | plan: {t['plan']}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")

print()

# 2. Verificar usuarios vinculados
try:
    res = supabase_admin.table("usuarios").select("*, tenants(nombre)").execute()
    print(f"✅ Usuarios en BD — {len(res.data)} usuario(s)")
    for u in res.data:
        print(f"   → {u['nombre']} | rol: {u['rol']} | tenant: {u['tenants']['nombre']}")
except Exception as e:
    print(f"❌ Error leyendo usuarios: {e}")

print()

# 3. Verificar Supabase Auth
try:
    res = supabase_admin.auth.admin.list_users()
    print(f"✅ Auth users — {len(res)} usuario(s) en Supabase Auth")
    for u in res:
        print(f"   → {u.email} | confirmado: {u.email_confirmed_at is not None}")
except Exception as e:
    print(f"❌ Error leyendo Auth: {e}")

print()
print("=" * 50)