import httpx
import asyncio

async def verify_rag():
    base_url = "http://127.0.0.1:8000/api/rag"
    
    print("1. Adding sample documents...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/add-documents",
                json={
                    "documents": [
                        {"id": "test1", "content": "The neXus project integrates Grok AI for social analysis.", "metadata": {"source": "test"}},
                        {"id": "test2", "content": "RAG systems combine retrieval and generation.", "metadata": {"source": "test"}}
                    ],
                    "edges": [
                        {"source": "test1", "target": "test2"}
                    ]
                }
            )
            resp.raise_for_status()
            print(f"✅ Add Documents Success: {resp.json()}")
    except Exception as e:
        print(f"❌ Add Documents Failed: {e}")
        return

    print("\n2. Querying RAG system...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url}/query",
                json={
                    "query": "What is the purpose of neXus?",
                    "use_graph_ranking": True,
                    "top_k": 2
                }
            )
            resp.raise_for_status()
            data = resp.json()
            print(f"✅ Query Success!")
            print(f"Answer: {data['answer']}")
            print(f"Sources: {[s['id'] for s in data['sources']]}")
    except Exception as e:
        print(f"❌ Query Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_rag())
