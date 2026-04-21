from app.db import get_connection

def split_by_paragraph_or_sentence(text: str) -> list[str]:
    """
    줄(개행) 기준으로 문서를 나누고,
    빈 줄은 제거한 뒤 chunk 리스트를 반환
    """
    parts = [line.strip() for line in text.split("\n") if line.strip()]
    return parts


def save_chunks_to_db():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 1) documents 테이블에서 원문 문서 조회
        cursor.execute("""
            SELECT id, doc_name, raw_text
            FROM documents
            ORDER BY id
        """)
        documents = cursor.fetchall()

        if not documents:
            print("documents 테이블에 문서가 없습니다.")
            return

        print(f"총 {len(documents)}개 문서를 불러왔습니다.")

        # 2) 각 문서를 chunk로 나누고 저장
        for doc in documents:
            document_id = doc["id"]
            doc_name = doc["doc_name"]
            raw_text = doc["raw_text"] or ""

            chunks = split_by_paragraph_or_sentence(raw_text)

            print(f"\n[문서] {doc_name} (id={document_id})")
            print(f" -> 생성된 chunk 수: {len(chunks)}")

            # 기존 chunk가 있으면 삭제 후 다시 저장
            cursor.execute(
                "DELETE FROM document_chunks WHERE document_id = %s",
                (document_id,)
            )

            insert_sql = """
                INSERT INTO document_chunks (document_id, chunk_order, chunk_text)
                VALUES (%s, %s, %s)
            """

            for idx, chunk in enumerate(chunks, start=1):
                cursor.execute(insert_sql, (document_id, idx, chunk))
                print(f"    저장 완료: chunk_order={idx} | {chunk[:50]}")

        conn.commit()
        print("\n모든 chunk 저장 완료")

    except Exception as e:
        print("chunk 저장 중 오류 발생")
        print("에러:", e)
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("DB 연결 종료")


if __name__ == "__main__":
    save_chunks_to_db()