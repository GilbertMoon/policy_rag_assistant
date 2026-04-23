# policy_rag_assistant

정책/공지 문서를 MySQL에 저장하고, 문서를 chunk로 분리한 뒤, Gemini 기반 RAG 질의응답을 실행하는 간단한 예제 프로젝트입니다.

## 1. 사전 준비

- Python 3.11 이상 권장
- 로컬 MySQL 서버 실행
- Gemini API Key 준비

## 2. 프로젝트 클론

```bash
git clone https://github.com/GilbertMoon/policy_rag_assistant.git
cd policy_rag_assistant
```

## 3. 가상환경 생성 및 패키지 설치

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. 로컬 MySQL 서버 준비

로컬 MySQL 서버가 실행 중인지 먼저 확인합니다.

예시 접속 정보:

- host: `localhost`
- port: `3306`
- database: `policy_rag`

## 5. DDL 실행

[db/ddl.sql](db/ddl.sql) 파일을 사용해서 데이터베이스와 테이블을 생성합니다.

### 방법 1: MySQL CLI 사용

```bash
mysql -u root -p < db/ddl.sql
```

### 방법 2: MySQL Workbench 사용

1. MySQL Workbench에서 로컬 서버에 접속합니다.
2. [db/ddl.sql](db/ddl.sql) 파일을 엽니다.
3. 전체 SQL을 실행합니다.

## 6. 환경 변수 설정

루트 경로에 `.env` 파일을 만들고 아래 값을 설정합니다.

```env
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=policy_rag
DB_USER=your_mysql_user
DB_PASS=your_mysql_password
PROMPT_VERSION=answer_prompt_v1
RETRIEVAL_VERSION=tfidf_top3_v1
MODEL_VERSION=gemini-3.1-flash-lite-preview
```

원하면 [.env.example](.env.example) 파일을 복사해서 사용할 수 있습니다.

## 7. DB 연결 테스트

아래 명령으로 MySQL 연결이 정상인지 확인합니다.

```bash
python test_db_connection.py
```

정상이라면 현재 DB명, MySQL 버전, 테스트 쿼리 결과가 출력됩니다.

## 8. 문서 파일 작성

문서 원본은 [data/sample_docs.txt](data/sample_docs.txt) 파일에 저장합니다.

파일 형식은 아래와 같습니다.

```text
doc_name: 문서명
doc_category: 카테고리
---
문서 본문 1줄
문서 본문 2줄

===
doc_name: 다음 문서명
doc_category: another_category
---
다음 문서 본문
```

규칙:

- 문서 하나는 `===` 로 구분합니다.
- 각 문서는 첫 줄에 `doc_name:`, 둘째 줄에 `doc_category:` 를 작성합니다.
- 셋째 줄은 반드시 `---` 이어야 합니다.
- 넷째 줄부터 문서 본문입니다.

## 9. 문서 적재

아래 명령을 실행하면 [data/sample_docs.txt](data/sample_docs.txt)의 문서를 읽어 [documents](db/ddl.sql) 테이블에 저장합니다.

```bash
python -m app.ingest
```

동일한 `doc_name` 이 이미 있으면 새로 추가하지 않고 내용을 갱신합니다.

## 10. Chunk 생성 및 저장

아래 명령으로 [documents](db/ddl.sql) 테이블의 원문을 읽어서 [document_chunks](db/ddl.sql) 테이블에 chunk를 저장합니다.

```bash
python -m app.chunking
```

현재 chunk 기준은 줄바꿈 단위입니다. 즉, 문서 본문의 각 줄이 하나의 chunk로 저장됩니다.

## 11. 프로그램 실행

이제 메인 프로그램을 실행합니다.

```bash
python main.py
```

실행 흐름:

1. `top_k` 값을 입력합니다. 기본값은 3입니다.
2. 질문을 입력합니다.
3. 검색된 chunk와 최종 답변을 확인합니다.
4. 원하면 피드백 점수와 코멘트를 입력합니다.
5. 종료하려면 `exit` 를 입력합니다.

## 12. 전체 실행 순서 요약

```bash
python test_db_connection.py
python -m app.ingest
python -m app.chunking
python main.py
```

## 13. 참고 파일

- [main.py](main.py): 메인 실행 파일
- [app/ingest.py](app/ingest.py): 문서 파일을 DB에 적재
- [app/chunking.py](app/chunking.py): 문서 chunk 생성 및 저장
- [app/service.py](app/service.py): RAG 서비스 실행
- [db/ddl.sql](db/ddl.sql): 데이터베이스 DDL
- [data/sample_docs.txt](data/sample_docs.txt): 입력 문서 예시