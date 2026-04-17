from config import supabase_admin, supabase

class Tenant:
    @staticmethod
    def listar() -> list:
        res = supabase_admin.table("tenants")\
                            .select("*, usuarios(count)")\
                            .order("creado_en", desc=True)\
                            .execute()
        return res.data

    @staticmethod
    def crear(nombre: str, email: str, plan: str = "free") -> dict:
        res = supabase_admin.table("tenants").insert({
            "nombre": nombre,
            "email":  email,
            "plan":   plan
        }).execute()
        return res.data[0]

    @staticmethod
    def obtener(tenant_id: str) -> dict:
        res = supabase.table("tenants")\
                      .select("*")\
                      .eq("id", tenant_id)\
                      .single()\
                      .execute()
        return res.data

    @staticmethod
    def actualizar_perfil(tenant_id: str, datos: dict) -> dict:
        res = supabase.table("tenants")\
                      .update(datos)\
                      .eq("id", tenant_id)\
                      .execute()
        return res.data[0]

    @staticmethod
    def eliminar(tenant_id: str) -> bool:
        from config import supabase_admin
        res = supabase_admin.table("usuarios")\
                            .select("auth_user_id")\
                            .eq("tenant_id", tenant_id)\
                            .execute()
        for usuario in res.data:
            try:
                supabase_admin.auth.admin.delete_user(usuario["auth_user_id"])
            except Exception:
                pass
        supabase_admin.table("tenants")\
                      .delete()\
                      .eq("id", tenant_id)\
                      .execute()
        return True