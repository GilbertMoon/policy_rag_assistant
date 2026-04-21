from app.db import get_connection

def test_connection():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1) DB 연결 확인
        print("DB 연결 성공")

        # 2) 현재 DB 확인
        cursor.execute("SELECT DATABASE();")
        current_db = cursor.fetchone()[0]
        print("현재 연결된 DB:", current_db)

        # 3) MySQL 버전 확인
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()[0]
        print("MySQL 버전:", version)

        # 4) 간단한 쿼리 실행 확인
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()[0]
        print("테스트 쿼리 결과:", result)

        print("모든 테스트 통과")

    except Exception as e:
        print("DB 연결 또는 쿼리 실행 실패")
        print("에러 내용:", e)

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
            print("DB 연결 종료")

if __name__ == "__main__":
    test_connection()