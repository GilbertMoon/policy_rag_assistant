def build_answer_prompt(question: str, retrieved_docs: list[dict], system_prompt: str) -> str:
    context = "\n\n".join([
        f"[Chunk {doc['chunk_id']}]\n{doc['chunk_text']}"
        for doc in retrieved_docs
    ])

    return f"""{system_prompt}

Documents:
{context}

Question:
{question}
"""


if __name__ == "__main__":
    system_prompt = """You are a document-grounded assistant.
Answer only using the provided documents.
Do not guess.
Use this format:

Answer:
- ...

Caution:
- ...

Sources:
- ...
"""

    sample_retrieved_docs = [
        {
            "chunk_id": 1,
            "chunk_text": "재택근무는 최소 하루 전에 신청해야 하며 팀장 승인 후 인사 시스템에 등록해야 한다."
        },
        {
            "chunk_id": 2,
            "chunk_text": "보안 교육을 이수하지 않은 직원은 재택근무를 신청할 수 없다."
        },
        {
            "chunk_id": 3,
            "chunk_text": "재택근무 중에는 회사 VPN에 반드시 접속해야 한다."
        }
    ]

    question = "재택근무 신청 조건과 주의사항을 알려줘."

    prompt = build_answer_prompt(
        question=question,
        retrieved_docs=sample_retrieved_docs,
        system_prompt=system_prompt
    )

    print("=== 생성된 프롬프트 ===")
    print(prompt)