from config import supabase

class Evento:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.tabla = "eventos"

    def crear(self, datos: dict) -> dict:
        datos["tenant_id"] = self.tenant_id
        res = supabase.table(self.tabla).insert(datos).execute()
        return res.data[0]

    def listar(self, tipo: str = None) -> list:
        query = supabase.table(self.tabla)\
                        .select("*")\
                        .eq("tenant_id", self.tenant_id)\
                        .order("fecha", desc=False)
        if tipo:
            query = query.eq("tipo", tipo)
        return query.execute().data

    def obtener(self, evento_id: str) -> dict:
        res = supabase.table(self.tabla)\
                      .select("*")\
                      .eq("id", evento_id)\
                      .eq("tenant_id", self.tenant_id)\
                      .single()\
                      .execute()
        return res.data

    def actualizar(self, evento_id: str, datos: dict) -> dict:
        res = supabase.table(self.tabla)\
                      .update(datos)\
                      .eq("id", evento_id)\
                      .eq("tenant_id", self.tenant_id)\
                      .execute()
        return res.data[0]

    def eliminar(self, evento_id: str) -> bool:
        supabase.table(self.tabla)\
                .delete()\
                .eq("id", evento_id)\
                .eq("tenant_id", self.tenant_id)\
                .execute()
        return True