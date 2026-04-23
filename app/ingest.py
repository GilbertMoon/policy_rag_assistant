from pathlib import Path

from app.db import get_connection


DEFAULT_DATA_PATH = Path("data/sample_docs.txt")


sample_docs = [
    {
        "doc_name": "재택근무 정책",
        "doc_category": "hr_policy",
        "raw_text": """
재택근무는 최소 하루 전에 신청해야 하며 팀장 승인 후 인사 시스템에 등록해야 한다.
보안 교육을 이수하지 않은 직원은 재택근무를 신청할 수 없다.
재택근무 중에는 회사 VPN에 반드시 접속해야 한다.
""".strip()
    },
    {
        "doc_name": "요금제 변경 공지",
        "doc_category": "pricing",
        "raw_text": """
Basic 요금제는 2026년 5월 1일부터 월 11,900원으로 인상된다.
Pro 요금제는 기존 가격을 유지한다.
""".strip()
    },
    {
        "doc_name": "환불 정책",
        "doc_category": "refund",
        "raw_text": """
환불은 결제 후 7일 이내 가능하지만, 콘텐츠를 30% 이상 시청한 경우 제한될 수 있다.
기술 오류로 접속이 불가능한 경우 예외적으로 환불이 허용될 수 있다.
이벤트 상품은 별도 환불 규정을 따른다.
""".strip()
    }
]


def parse_docs_file(file_path: str | Path = DEFAULT_DATA_PATH) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        print(f"문서 파일이 없어 기본 샘플 문서를 사용합니다: {path}")
        return sample_docs

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        print(f"문서 파일이 비어 있어 기본 샘플 문서를 사용합니다: {path}")
        return sample_docs

    blocks = [block.strip() for block in content.split("\n===\n") if block.strip()]
    docs = []

    for index, block in enumerate(blocks, start=1):
        lines = block.splitlines()

        if len(lines) < 4:
            raise ValueError(
                f"문서 블록 {index} 형식이 잘못되었습니다. 최소 4줄(doc_name, doc_category, --- , 본문)이 필요합니다."
            )

        doc_name_line = lines[0].strip()
        doc_category_line = lines[1].strip()
        separator_line = lines[2].strip()

        if not doc_name_line.startswith("doc_name:"):
            raise ValueError(f"문서 블록 {index} 첫 줄은 'doc_name:' 으로 시작해야 합니다.")
        if not doc_category_line.startswith("doc_category:"):
            raise ValueError(f"문서 블록 {index} 둘째 줄은 'doc_category:' 로 시작해야 합니다.")
        if separator_line != "---":
            raise ValueError(f"문서 블록 {index} 셋째 줄은 구분자 '---' 여야 합니다.")

        doc_name = doc_name_line.split(":", 1)[1].strip()
        doc_category = doc_category_line.split(":", 1)[1].strip() or None
        raw_text = "\n".join(lines[3:]).strip()

        if not doc_name:
            raise ValueError(f"문서 블록 {index}의 doc_name 값이 비어 있습니다.")
        if not raw_text:
            raise ValueError(f"문서 블록 {index}의 본문이 비어 있습니다.")

        docs.append({
            "doc_name": doc_name,
            "doc_category": doc_category,
            "raw_text": raw_text
        })

    return docs


def insert_docs(docs: list[dict]):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_sql = """
        INSERT INTO documents (doc_name, doc_category, raw_text)
        VALUES (%s, %s, %s)
        """

        update_sql = """
        UPDATE documents
        SET doc_category = %s,
            raw_text = %s
        WHERE id = %s
        """

        select_sql = "SELECT id FROM documents WHERE doc_name = %s"

        inserted_count = 0
        updated_count = 0

        for doc in docs:
            cursor.execute(select_sql, (doc["doc_name"],))
            existing = cursor.fetchone()

            if existing:
                cursor.execute(update_sql, (
                    doc["doc_category"],
                    doc["raw_text"],
                    existing[0]
                ))
                updated_count += 1
            else:
                cursor.execute(insert_sql, (
                    doc["doc_name"],
                    doc["doc_category"],
                    doc["raw_text"]
                ))
                inserted_count += 1

        conn.commit()
        print(f"문서 저장 완료 (신규 {inserted_count}건, 수정 {updated_count}건)")

    except Exception as e:
        print("문서 저장 실패")
        print("에러:", e)
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def insert_sample_docs(file_path: str | Path = DEFAULT_DATA_PATH):
    docs = parse_docs_file(file_path)
    insert_docs(docs)


if __name__ == "__main__":
    insert_sample_docs()