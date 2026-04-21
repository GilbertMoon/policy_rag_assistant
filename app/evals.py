import json
import os
from datetime import datetime
from dotenv import load_dotenv

from app.retrieval import Retriever, load_chunks_from_db
from app.service import run_rag_service, load_system_prompt

load_dotenv()


eval_set = [
    {"id": 1, "type": "fact", "question": "Basic 요금제 가격은 얼마인가요?"},
    {"id": 2, "type": "condition", "question": "보안 교육 미이수자는 재택근무 가능한가요?"},
    {"id": 3, "type": "explanation", "question": "환불 가능한 경우와 예외 조건을 설명해줘."},
    {"id": 4, "type": "explanation", "question": "재택근무 신청 조건과 주의사항을 정리해줘."}
]


def run_eval_set(top_k: int = 3):
    chunk_rows = load_chunks_from_db()

    if not chunk_rows:
        print("document_chunks 테이블에 데이터가 없습니다.")
        return []

    retriever = Retriever(chunk_rows)
    system_prompt = load_system_prompt()

    results = []

    for item in eval_set:
        result = run_rag_service(
            question=item["question"],
            retriever=retriever,
            system_prompt=system_prompt,
            top_k=top_k
        )

        row = {
            "eval_id": item["id"],
            "question_type": item["type"],
            "question": item["question"],
            "answer": result["answer"],
            "sources": [doc["chunk_id"] for doc in result["retrieved_docs"]],
            "latency_ms": result["latency_ms"],
            "prompt_version": result["prompt_version"],
            "retrieval_version": result["retrieval_version"],
            "model_version": result["model_version"]
        }
        results.append(row)

    return results


def save_eval_results(results: list):
    os.makedirs("logs", exist_ok=True)

    filename = f"logs/eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n평가 결과 저장 완료: {filename}")


if __name__ == "__main__":
    results = run_eval_set(top_k=3)

    if results:
        print("\n=== EVAL RESULTS ===")
        for row in results:
            print(f"\n[Q{row['eval_id']}] ({row['question_type']}) {row['question']}")
            print("답변:", row["answer"])
            print("출처:", row["sources"])
            print("latency_ms:", row["latency_ms"])

        save_eval_results(results)