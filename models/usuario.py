from config import supabase, supabase_admin

class Usuario:
    @staticmethod
    def obtener_por_auth_id(auth_user_id: str) -> dict:
        res = supabase.table("usuarios")\
                      .select("*, tenants(*)")\
                      .eq("auth_user_id", auth_user_id)\
                      .single()\
                      .execute()
        return res.data

    @staticmethod
    def crear(auth_user_id: str, tenant_id: str, nombre: str, rol: str = "usuario") -> dict:
        res = supabase_admin.table("usuarios").insert({
            "auth_user_id": auth_user_id,
            "tenant_id": tenant_id,
            "nombre": nombre,
            "rol": rol
        }).execute()
        return res.data[0]

    @staticmethod
    def es_admin(auth_user_id: str) -> bool:
        res = supabase.table("usuarios")\
                      .select("rol")\
                      .eq("auth_user_id", auth_user_id)\
                      .single()\
                      .execute()
        return res.data and res.data["rol"] == "admin"