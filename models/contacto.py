from config import supabase

class Contacto:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.tabla = "contactos"

    def crear(self, datos: dict) -> dict:
        datos["tenant_id"] = self.tenant_id
        res = supabase.table(self.tabla).insert(datos).execute()
        return res.data[0]

    def listar(self) -> list:
        return supabase.table(self.tabla)\
                       .select("*")\
                       .eq("tenant_id", self.tenant_id)\
                       .order("nombre")\
                       .execute().data

    def obtener(self, contacto_id: str) -> dict:
        res = supabase.table(self.tabla)\
                      .select("*")\
                      .eq("id", contacto_id)\
                      .eq("tenant_id", self.tenant_id)\
                      .single()\
                      .execute()
        return res.data

    def actualizar(self, contacto_id: str, datos: dict) -> dict:
        res = supabase.table(self.tabla)\
                      .update(datos)\
                      .eq("id", contacto_id)\
                      .eq("tenant_id", self.tenant_id)\
                      .execute()
        return res.data[0]

    def eliminar(self, contacto_id: str) -> bool:
        supabase.table(self.tabla)\
                .delete()\
                .eq("id", contacto_id)\
                .eq("tenant_id", self.tenant_id)\
                .execute()
        return True