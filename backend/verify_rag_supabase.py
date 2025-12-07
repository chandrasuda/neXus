import httpx
import asyncio

async def verify_supabase_rag():
    base_url = "http://127.0.0.1:8000/api/rag"
    
    print("1. Ingesting profiles from Supabase...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{base_url}/ingest-profiles")
            resp.raise_for_status()
            data = resp.json()
            print(f"✅ Ingestion Success: {data}")
            
            if data.get("profiles_ingested", 0) == 0:
                print("⚠️ Warning: No profiles were found in Supabase. The RAG system is empty.")
                return
    except Exception as e:
        print(f"❌ Ingestion Failed: {e}")
        return

    print("\n2. Querying RAG system about Supabase data...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Ask a generic question to list users, which validates data retrieval
            resp = await client.post(
                f"{base_url}/query",
                json={
                    "query": "Who are the users in my network and what are their bios?",
                    "use_graph_ranking": True,
                    "top_k": 5
                }
            )
            resp.raise_for_status()
            data = resp.json()
            print(f"✅ Query Success!")
            print(f"Answer: {data['answer']}")
            
            print("\nSources used:")
            for source in data.get('sources', []):
                meta = source.get('metadata', {})
                print(f"- {meta.get('name', 'Unknown')} (@{meta.get('username', 'unknown')})")

    except Exception as e:
        print(f"❌ Query Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_supabase_rag())
