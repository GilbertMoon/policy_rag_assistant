from datetime import datetime
import json
import os
from dotenv import load_dotenv

from app.db import get_connection
from app.retrieval import Retriever, load_chunks_from_db
from app.service import run_rag_service, load_system_prompt

load_dotenv()


def estimate_tokens(question: str, retrieved_docs: list[dict], answer: str) -> int:
    """
    아주 단순한 토큰 추정 함수
    실제 API billing token과 다를 수 있지만,
    길이가 길수록 비용이 증가한다는 감각을 보기 위한 용도
    """
    context_text = " ".join(doc["chunk_text"] for doc in retrieved_docs)
    total_text = f"{question} {context_text} {answer}"
    return len(total_text.split())


def save_qa_log(
    question: str,
    final_answer: str,
    retrieved_docs: list[dict],
    latency_ms: int,
    estimated_tokens: int,
    prompt_version: str,
    retrieval_version: str,
    model_version: str,
    feedback_score: int | None = None,
    feedback_comment: str | None = None
):
    """
    qa_logs 테이블에 질의응답 로그 저장
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        source_chunk_ids = ",".join(str(doc["chunk_id"]) for doc in retrieved_docs)

        sql = """
        INSERT INTO qa_logs (
            question,
            final_answer,
            source_chunk_ids,
            latency_ms,
            estimated_tokens,
            prompt_version,
            retrieval_version,
            model_version,
            feedback_score,
            feedback_comment
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            question,
            final_answer,
            source_chunk_ids,
            latency_ms,
            estimated_tokens,
            prompt_version,
            retrieval_version,
            model_version,
            feedback_score,
            feedback_comment
        ))

        conn.commit()
        print("로그 저장 완료")

    except Exception as e:
        print("로그 저장 실패")
        print("에러:", e)
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def print_retrieved_docs(retrieved_docs: list[dict]):
    print("\n=== 검색된 문서(chunk) ===")
    for i, doc in enumerate(retrieved_docs, start=1):
        print(f"[{i}] chunk_id={doc['chunk_id']} | document_id={doc['document_id']} | score={doc['score']:.4f}")
        print(f"    {doc['chunk_text']}")


def print_result(result: dict):
    print("\n=== 질문 ===")
    print(result["question"])

    print_retrieved_docs(result["retrieved_docs"])

    print("\n=== 최종 답변 ===")
    print(result["answer"])

    print("\n=== 실행 정보 ===")
    print("latency_ms:", result["latency_ms"])
    print("prompt_version:", result["prompt_version"])
    print("retrieval_version:", result["retrieval_version"])
    print("model_version:", result["model_version"])


def ask_feedback():
    """
    간단한 사용자 피드백 입력
    """
    raw_score = input("\n피드백 점수 입력 (1~5, 생략 가능): ").strip()
    feedback_score = None

    if raw_score:
        try:
            score = int(raw_score)
            if 1 <= score <= 5:
                feedback_score = score
            else:
                print("1~5 사이 숫자만 저장합니다. 점수는 저장하지 않습니다.")
        except ValueError:
            print("숫자가 아니므로 점수는 저장하지 않습니다.")

    feedback_comment = input("피드백 코멘트 입력 (생략 가능): ").strip()
    if feedback_comment == "":
        feedback_comment = None

    return feedback_score, feedback_comment


def main():
    print("=== Policy RAG Assistant ===")

    try:
        top_k_raw = input("top_k 값을 입력하세요 (기본 3): ").strip()
        top_k = int(top_k_raw) if top_k_raw else 3
    except ValueError:
        print("숫자가 아니므로 top_k=3으로 진행합니다.")
        top_k = 3

    # 1) DB에서 chunk 로드
    chunk_rows = load_chunks_from_db()

    if not chunk_rows:
        print("document_chunks 테이블에 데이터가 없습니다.")
        print("먼저 Step 10까지 실행해서 chunk를 저장해 주세요.")
        return

    print(f"총 {len(chunk_rows)}개의 chunk를 불러왔습니다.")

    # 2) Retriever 생성
    retriever = Retriever(chunk_rows)

    # 3) system prompt 로드
    try:
        system_prompt = load_system_prompt()
    except FileNotFoundError as e:
        print("프롬프트 파일을 찾을 수 없습니다.")
        print("에러:", e)
        return

    print("시스템 프롬프트 로드 완료")
    print(f"PROMPT_VERSION={os.getenv('PROMPT_VERSION')}")
    print(f"RETRIEVAL_VERSION={os.getenv('RETRIEVAL_VERSION')}")
    print(f"MODEL_VERSION={os.getenv('MODEL_VERSION')}")

    while True:
        question = input("\n질문을 입력하세요 (종료: exit): ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("프로그램을 종료합니다.")
            break

        if not question:
            print("질문이 비어 있습니다. 다시 입력해 주세요.")
            continue

        try:
            # 4) RAG 서비스 실행
            result = run_rag_service(
                question=question,
                retriever=retriever,
                system_prompt=system_prompt,
                top_k=top_k
            )

            # 5) 결과 출력
            print_result(result)

            # 6) 토큰 수 추정
            estimated_tokens = estimate_tokens(
                question=result["question"],
                retrieved_docs=result["retrieved_docs"],
                answer=result["answer"]
            )
            print("estimated_tokens:", estimated_tokens)

            # 7) 피드백 입력
            feedback_score, feedback_comment = ask_feedback()

            # 8) 로그 저장
            save_qa_log(
                question=result["question"],
                final_answer=result["answer"],
                retrieved_docs=result["retrieved_docs"],
                latency_ms=result["latency_ms"],
                estimated_tokens=estimated_tokens,
                prompt_version=result["prompt_version"],
                retrieval_version=result["retrieval_version"],
                model_version=result["model_version"],
                feedback_score=feedback_score,
                feedback_comment=feedback_comment
            )

        except Exception as e:
            print("\n질의응답 처리 중 오류 발생")
            print("에러:", e)


if __name__ == "__main__":
    main()