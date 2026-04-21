import os
import time
from dotenv import load_dotenv

from app.prompt_builder import build_answer_prompt
from app.gemini_client import ask_gemini
from app.retrieval import Retriever, load_chunks_from_db

load_dotenv()


def load_system_prompt() -> str:
    """
    prompts 폴더에서 현재 PROMPT_VERSION에 해당하는 프롬프트 파일을 읽어온다.
    예: PROMPT_VERSION=answer_prompt_v1
    -> prompts/answer_prompt_v1.txt
    """
    prompt_version = os.getenv("PROMPT_VERSION", "answer_prompt_v1")
    prompt_path = os.path.join("prompts", f"{prompt_version}.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def run_rag_service(question: str, retriever, system_prompt: str, top_k: int = 3):
    start = time.time()

    retrieved_docs = retriever.retrieve(question, top_k=top_k)
    prompt = build_answer_prompt(question, retrieved_docs, system_prompt)
    answer = ask_gemini(prompt, os.getenv("MODEL_VERSION"))

    latency_ms = int((time.time() - start) * 1000)

    return {
        "question": question,
        "retrieved_docs": retrieved_docs,
        "answer": answer,
        "latency_ms": latency_ms,
        "prompt_version": os.getenv("PROMPT_VERSION"),
        "retrieval_version": os.getenv("RETRIEVAL_VERSION"),
        "model_version": os.getenv("MODEL_VERSION")
    }


if __name__ == "__main__":
    # 1) DB에서 chunk 불러오기
    chunk_rows = load_chunks_from_db()

    if not chunk_rows:
        print("document_chunks 테이블에 데이터가 없습니다.")
    else:
        # 2) retriever 생성
        retriever = Retriever(chunk_rows)

        # 3) system prompt 로드
        system_prompt = load_system_prompt()

        # 4) 테스트 질문
        question = "환불 가능한 경우와 예외 조건을 알려줘."

        # 5) 서비스 실행
        result = run_rag_service(
            question=question,
            retriever=retriever,
            system_prompt=system_prompt,
            top_k=3
        )

        print("\n=== 질문 ===")
        print(result["question"])

        print("\n=== 검색 결과 ===")
        for doc in result["retrieved_docs"]:
            print(doc)

        print("\n=== 답변 ===")
        print(result["answer"])

        print("\n=== 메타데이터 ===")
        print("latency_ms:", result["latency_ms"])
        print("prompt_version:", result["prompt_version"])
        print("retrieval_version:", result["retrieval_version"])
        print("model_version:", result["model_version"])