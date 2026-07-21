import os, streamlit as st
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_store")

@st.cache_resource
def get_collection(doc_count: int):
    """Cached at resource level — only initialises once per session."""
    from utils.data_loader import load_specs
    specs_df = load_specs()
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        ef = embedding_functions.DefaultEmbeddingFunction()
        ef(["probe"])
    except Exception:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
        class TfIdf:
            def __init__(self): self._v = TfidfVectorizer(max_features=512); self._fit = False
            def name(self): return "tfidf"
            def __call__(self, input):
                if not self._fit: self._v.fit(input); self._fit = True
                vecs = self._v.transform(input).toarray()
                if vecs.shape[1] < 512:
                    vecs = np.hstack([vecs, np.zeros((vecs.shape[0], 512 - vecs.shape[1]))])
                return vecs.tolist()
        ef = TfIdf()
    col = client.get_or_create_collection("epc_docs", embedding_function=ef)
    if col.count() == 0:
        col.add(ids=specs_df["doc_id"].tolist(), documents=specs_df["content"].tolist(),
                metadatas=specs_df[["doc_type","asset_id","title"]].to_dict("records"))
    return col

def retrieve(col, query, n=4):
    res = col.query(query_texts=[query], n_results=n)
    if not res or not res.get("documents"): return []
    return [{"content": d, "title": m.get("title"), "doc_type": m.get("doc_type")}
            for d, m in zip(res["documents"][0], res["metadatas"][0])]

def ask(col, query):
    chunks = retrieve(col, query)
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        lines = [f"**Relevant project documents for:** _{query}_\n"]
        for c in chunks:
            lines.append(f"**{c['title']}** ({c['doc_type']})\n{c['content']}\n")
        return {"answer": "\n".join(lines), "sources": chunks}
    try:
        from groq import Groq
        ctx = "\n\n".join(f"[{c['title']} — {c['doc_type']}]\n{c['content']}" for c in chunks)
        prompt = f"""You are an AI Copilot for a Data Centre EPC project. Answer using ONLY the context below. Be concise and structured. Cite sources by title.

CONTEXT:
{ctx}

QUESTION: {query}
ANSWER:"""
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return {"answer": resp.choices[0].message.content, "sources": chunks}
    except Exception as e:
        lines = [f"_(Groq unavailable: {str(e)[:80]})_\n"]
        for c in chunks:
            lines.append(f"**{c['title']}**\n{c['content']}\n")
        return {"answer": "\n".join(lines), "sources": chunks}