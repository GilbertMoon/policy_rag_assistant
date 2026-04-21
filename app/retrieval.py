from app.db import get_connection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    def __init__(self, chunk_rows):
        self.chunk_rows = chunk_rows
        self.chunk_texts = [row["chunk_text"] for row in chunk_rows]

        # 한국어에서 단순 단어 단위보다 조금 더 안정적으로 유사도를 보기 위한 문자 n-gram 방식
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        self.doc_vectors = self.vectorizer.fit_transform(self.chunk_texts)

    def retrieve(self, query: str, top_k: int = 3):
        query_vector = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vector, self.doc_vectors)[0]
        ranked = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_k]:
            row = self.chunk_rows[idx]
            results.append({
                "chunk_id": row["id"],
                "document_id": row["document_id"],
                "chunk_text": row["chunk_text"],
                "score": float(score)
            })
        return results


def load_chunks_from_db():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, document_id, chunk_order, chunk_text
            FROM document_chunks
            ORDER BY document_id, chunk_order
        """)
        rows = cursor.fetchall()
        return rows

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    chunk_rows = load_chunks_from_db()

    if not chunk_rows:
        print("document_chunks 테이블에 데이터가 없습니다.")
    else:
        retriever = Retriever(chunk_rows)

        query = "재택근무 신청 조건과 주의사항을 알려줘."
        results = retriever.retrieve(query, top_k=3)

        print(f"\n질문: {query}")
        print("\n=== 검색 결과 ===")
        for r in results:
            print(r)