from config import supabase

class Cancion:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.tabla = "canciones"

    def crear(self, datos: dict) -> dict:
        datos["tenant_id"] = self.tenant_id
        res = supabase.table(self.tabla).insert(datos).execute()
        return res.data[0]

    def listar(self, estado: str = None) -> list:
        query = supabase.table(self.tabla)\
                        .select("*")\
                        .eq("tenant_id", self.tenant_id)\
                        .order("titulo")
        if estado:
            query = query.eq("estado", estado)
        return query.execute().data

    def obtener(self, cancion_id: str) -> dict:
        res = supabase.table(self.tabla)\
                      .select("*")\
                      .eq("id", cancion_id)\
                      .eq("tenant_id", self.tenant_id)\
                      .single()\
                      .execute()
        return res.data

    def actualizar(self, cancion_id: str, datos: dict) -> dict:
        res = supabase.table(self.tabla)\
                      .update(datos)\
                      .eq("id", cancion_id)\
                      .eq("tenant_id", self.tenant_id)\
                      .execute()
        return res.data[0]

    def eliminar(self, cancion_id: str) -> bool:
        supabase.table(self.tabla)\
                .delete()\
                .eq("id", cancion_id)\
                .eq("tenant_id", self.tenant_id)\
                .execute()
        return True