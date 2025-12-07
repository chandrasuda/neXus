'use client';

import { useState } from 'react';
import { Send, RefreshCw, Database, Sparkles } from 'lucide-react';

export default function RAGPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string; sources?: any[] }[]>([]);
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);

  const handleIngest = async () => {
    setIngesting(true);
    try {
      const res = await fetch('http://localhost:8000/api/rag/ingest-profiles', {
        method: 'POST',
      });
      const data = await res.json();
      alert(`Ingestion Complete: ${data.message} (${data.profiles_ingested} profiles)`);
    } catch (error) {
      console.error(error);
      alert('Failed to ingest profiles');
    } finally {
      setIngesting(false);
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const newMsg = { role: 'user' as const, content: query };
    setMessages((prev) => [...prev, newMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: newMsg.content }),
      });
      
      if (!res.ok) throw new Error('Query failed');

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error while processing your request.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-neutral-800 pb-6">
          <div className="flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-blue-500" />
            <h1 className="text-3xl font-bold">neXus Intelligence</h1>
          </div>
          <button
            onClick={handleIngest}
            disabled={ingesting}
            className="flex items-center gap-2 px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {ingesting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />}
            {ingesting ? 'Ingesting...' : 'Sync Knowledge Base'}
          </button>
        </div>

        {/* Chat Interface */}
        <div className="bg-neutral-900 rounded-xl border border-neutral-800 h-[600px] flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 && (
              <div className="text-center text-neutral-500 mt-20">
                <p>Ask anything about your network...</p>
                <p className="text-sm mt-2">"Who works at xAI?"</p>
                <p className="text-sm">"Who are the most influential people in my feed?"</p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl p-4 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-neutral-800 text-neutral-200'
                }`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  
                  {/* Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <p className="text-xs font-semibold mb-2 opacity-70">Sources:</p>
                      <div className="space-y-2">
                        {msg.sources.map((source: any, sIdx: number) => (
                          <div key={sIdx} className="text-xs bg-black/20 p-2 rounded">
                            <span className="font-bold">@{source.metadata.username}</span>: {source.content.slice(0, 100)}...
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-neutral-800 rounded-2xl p-4 flex gap-2">
                  <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-neutral-800">
            <form onSubmit={handleQuery} className="flex gap-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about your network..."
                className="flex-1 bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>

      </div>
    </div>
  );
}
