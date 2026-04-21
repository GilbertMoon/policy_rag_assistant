from app.db import get_connection

sample_docs = [
    {
        "doc_name": "재택근무 정책",
        "doc_category": "hr_policy",
        "raw_text": """
재택근무는 최소 하루 전에 신청해야 하며 팀장 승인 후 인사 시스템에 등록해야 한다.
보안 교육을 이수하지 않은 직원은 재택근무를 신청할 수 없다.
재택근무 중에는 회사 VPN에 반드시 접속해야 한다.
"""
    },
    {
        "doc_name": "요금제 변경 공지",
        "doc_category": "pricing",
        "raw_text": """
Basic 요금제는 2026년 5월 1일부터 월 11,900원으로 인상된다.
Pro 요금제는 기존 가격을 유지한다.
"""
    },
    {
        "doc_name": "환불 정책",
        "doc_category": "refund",
        "raw_text": """
환불은 결제 후 7일 이내 가능하지만, 콘텐츠를 30% 이상 시청한 경우 제한될 수 있다.
기술 오류로 접속이 불가능한 경우 예외적으로 환불이 허용될 수 있다.
이벤트 상품은 별도 환불 규정을 따른다.
"""
    }
]

def insert_sample_docs():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO documents (doc_name, doc_category, raw_text)
        VALUES (%s, %s, %s)
        """

        for doc in sample_docs:
            cursor.execute(sql, (
                doc["doc_name"],
                doc["doc_category"],
                doc["raw_text"]
            ))

        conn.commit()
        print(f"{len(sample_docs)}개 문서 저장 완료")

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

if __name__ == "__main__":
    insert_sample_docs()