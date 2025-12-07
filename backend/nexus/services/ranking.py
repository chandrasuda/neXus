import networkx as nx
from typing import List, Dict, Any, Tuple

class GraphRanker:
    def __init__(self):
        pass

    def build_graph(self, nodes: List[Dict[str, Any]], edges: List[Tuple[str, str]]) -> nx.DiGraph:
        G = nx.DiGraph()
        for node in nodes:
            G.add_node(node['id'], **node)
        G.add_edges_from(edges)
        return G

    def rank_nodes(self, nodes: List[Dict[str, Any]], edges: List[Tuple[str, str]], method: str = "pagerank") -> Dict[str, float]:
        if not nodes:
            return {}

        G = self.build_graph(nodes, edges)

        if method == "pagerank":
            try:
                scores = nx.pagerank(G)
            except:
                scores = {node['id']: 0.0 for node in nodes}
        elif method == "hits":
             try:
                hubs, authorities = nx.hits(G)
                scores = authorities
             except:
                scores = {node['id']: 0.0 for node in nodes}
        else:
             scores = nx.degree_centrality(G)

        return scores

    def rerank_search_results(self, search_results: List[Dict[str, Any]], edges: List[Tuple[str, str]], alpha: float = 0.5) -> List[Dict[str, Any]]:
        if not search_results:
            return []
            
        graph_scores = self.rank_nodes(search_results, edges)
        
        reranked_results = []
        for doc in search_results:
            doc_id = doc.get('id')
            search_score = doc.get('score', 0)
            graph_score = graph_scores.get(doc_id, 0)
            
            final_score = (alpha * search_score) + ((1 - alpha) * graph_score)
            
            doc_with_rank = doc.copy()
            doc_with_rank['final_score'] = final_score
            doc_with_rank['graph_score'] = graph_score
            reranked_results.append(doc_with_rank)
            
        reranked_results.sort(key=lambda x: x['final_score'], reverse=True)
        return reranked_results
