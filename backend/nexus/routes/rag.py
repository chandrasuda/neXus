from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from nexus.services.rag import GrokService
from nexus.services.search import SearchEngine
from nexus.services.ranking import GraphRanker
from nexus.db.schema import XProfile, XConnection
from nexus.utils import get_db

router = APIRouter()

# In-memory storage for demo purposes
documents_store = []
edges_store = []

class Document(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}
    embedding: Optional[List[float]] = None

class Edge(BaseModel):
    source: str
    target: str

class RAGQueryRequest(BaseModel):
    query: str
    use_graph_ranking: bool = True
    top_k: int = 5

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@router.post("/add-documents")
async def add_documents(documents: List[Document], edges: List[Edge] = []):
    search_engine = SearchEngine()
    
    for doc in documents:
        if not doc.embedding:
            doc.embedding = search_engine.get_embedding(doc.content)
        
        existing = next((d for d in documents_store if d['id'] == doc.id), None)
        if existing:
            documents_store.remove(existing)
        
        documents_store.append(doc.dict())

    for edge in edges:
        edges_store.append((edge.source, edge.target))
        
    return {"message": f"Added {len(documents)} documents and {len(edges)} edges"}

@router.post("/ingest-profiles")
async def ingest_profiles(db: AsyncSession = Depends(get_db)):
    """
    Fetch all profiles from Supabase/Postgres and ingest them into the RAG system.
    """
    # 1. Fetch Profiles
    result = await db.execute(select(XProfile))
    profiles = result.scalars().all()
    
    # 2. Fetch Connections (for graph)
    # Note: Fetching all connections might be heavy for a demo, so we'll limit or fetch all
    conn_result = await db.execute(select(XConnection))
    connections = conn_result.scalars().all()
    
    search_engine = SearchEngine()
    
    count = 0
    # 3. Convert to Documents
    for profile in profiles:
        # Create a rich text representation
        content = f"User: {profile.name} (@{profile.username}). "
        if profile.bio:
            content += f"Bio: {profile.bio}. "
        if profile.location:
            content += f"Location: {profile.location}. "
        content += f"Followers: {profile.followers_count}, Following: {profile.following_count}."
        
        embedding = search_engine.get_embedding(content)
        
        doc = {
            "id": str(profile.x_user_id),
            "content": content,
            "metadata": {
                "username": profile.username,
                "name": profile.name,
                "type": "profile"
            },
            "embedding": embedding
        }
        
        # Add to store
        existing = next((d for d in documents_store if d['id'] == doc['id']), None)
        if existing:
            documents_store.remove(existing)
        documents_store.append(doc)
        count += 1
        
    # 4. Process Edges
    edge_count = 0
    for conn in connections:
        source = str(conn.x_user_id)
        # mutual_ids is a list of user IDs
        if conn.mutual_ids:
            for target in conn.mutual_ids:
                edges_store.append((source, str(target)))
                edge_count += 1
                
    return {
        "message": "Ingestion complete", 
        "profiles_ingested": count, 
        "edges_ingested": edge_count
    }

@router.post("/query", response_model=RAGResponse)
async def query_rag(request: RAGQueryRequest):
    if not documents_store:
        raise HTTPException(status_code=404, detail="No documents in knowledge base. Run /ingest-profiles first.")

    search_engine = SearchEngine()
    ranker = GraphRanker()
    grok_service = GrokService()

    query_vector = search_engine.get_embedding(request.query)

    results = search_engine.search(query_vector, documents_store, top_k=request.top_k * 2)

    if request.use_graph_ranking and edges_store:
        results = ranker.rerank_search_results(results, edges_store)
    
    final_results = results[:request.top_k]
    
    context = [doc['content'] for doc in final_results]
    answer = await grok_service.generate_response(request.query, context)

    return RAGResponse(
        answer=answer,
        sources=final_results
    )
