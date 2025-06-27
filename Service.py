from config.mongodb import get_mongo_client

def corregir_texto_mal_codificado(texto: str) -> str:
    try:
        return bytes(texto, 'latin1').decode('utf-8')
    except Exception:
        return texto

def recorrer_y_corregir(valor):
    if isinstance(valor, str):
        corregido = corregir_texto_mal_codificado(valor)
        return corregido
    elif isinstance(valor, dict):
        return {k: recorrer_y_corregir(v) for k, v in valor.items()}
    elif isinstance(valor, list):
        return [recorrer_y_corregir(v) for v in valor]
    else:
        return valor

if __name__ == "__main__":
    client = get_mongo_client()
    print("🧭 Bases de datos disponibles:", client.list_database_names())
    db = client["CALLCENTER-MONGODB"]
    print("📂 Colecciones en 'MONGODB':", db.list_collection_names())
    collection = db["ANALISIS-LLMS"]
    total = collection.count_documents({})
    print(f"🔢 Documentos en 'ANALISIS-LLMS': {total}")
    for doc in collection.find({}):
        doc_id = doc["_id"]
        print(f"🔍 Procesando documento {doc_id}...")
        original = {k: v for k, v in doc.items() if k != "_id"}
        corregido = recorrer_y_corregir(original)

        if corregido != original:
            # Mostrar diferencia por campo
            print(f"🛠 Documento {doc_id} será corregido:")
            for key in corregido:
                if corregido[key] != original.get(key):
                    print(f"  🔄 {key}:")
                    print(f"    Antes: {original.get(key)}")
                    print(f"    Después: {corregido[key]}")

            # Aplicar cambio
            collection.update_one({"_id": doc_id}, {"$set": corregido})
            print(f"✔ Documento {doc_id} corregido.\n")
        else:
            print(f"⏩ Documento {doc_id} no requería cambios.")
