from datetime import datetime
import json


def clean_text(text: str) -> str:
    """
    앞뒤 공백 제거 + 줄바꿈 정리용
    """
    if text is None:
        return ""
    return text.strip()


def estimate_tokens(text: str) -> int:
    """
    아주 단순한 토큰 수 추정
    실제 LLM billing token과는 다르지만,
    길이 기반 대략치 확인용으로 사용
    """
    if not text:
        return 0
    return len(text.split())


def estimate_total_tokens(question: str, retrieved_docs: list[dict], answer: str) -> int:
    """
    질문 + 검색 문서 + 답변을 합쳐서 전체 추정 토큰 계산
    """
    context_text = " ".join(doc["chunk_text"] for doc in retrieved_docs)
    total_text = f"{question} {context_text} {answer}"
    return estimate_tokens(total_text)


def get_now_str() -> str:
    """
    현재 시각을 ISO 형식 문자열로 반환
    """
    return datetime.now().isoformat()


def chunk_ids_to_string(retrieved_docs: list[dict]) -> str:
    """
    검색된 문서 목록에서 chunk_id만 뽑아 문자열로 변환
    예: '1,2,3'
    """
    return ",".join(str(doc["chunk_id"]) for doc in retrieved_docs)


def print_json(data: dict | list):
    """
    딕셔너리/리스트를 보기 좋게 출력
    """
    print(json.dumps(data, ensure_ascii=False, indent=2))