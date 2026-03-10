import requests
from bs4 import BeautifulSoup
import os

# --- 설정 (GitHub Secrets에서 환경변수로 읽어옴) ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# iframe 내부 실제 데이터 URL - 수습CPA 페이지
URL = "https://www.kicpa.or.kr/home/jobOffrSrchNewGnrl/list.face?listCnt=20&ijEmpSep=all&"

def check_kicpa():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.kicpa.or.kr/portal/default/kicpa/gnb/kr_pc/menu05/menu09/menu07.page',
    }
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 디버깅: 테이블 구조 확인
        tables = soup.find_all('table')
        print(f"테이블 수: {len(tables)}")
        for i, t in enumerate(tables):
            print(f"  테이블{i} class: {t.get('class')}")

        print("=== HTML 500자 ===")
        print(res.text[:500])

        rows = soup.select('table.table_st02 tbody tr')
        print(f"rows 수: {len(rows)}")

        if not rows:
            print("파싱 실패 - 테이블을 찾지 못함")
            return

        target_post = rows[0]
        tds = target_post.find_all('td')
        print(f"td 수: {len(tds)}")
        for i, td in enumerate(tds):
            print(f"  td{i}: {td.get_text(strip=True)[:50]}")

        if len(tds) < 2:
            print("예상과 다른 테이블 구조:", target_post)
            return

        post_id = tds[0].get_text(strip=True)
        title_elem = target_post.find('a')

        if not title_elem:
            print("제목 링크를 찾을 수 없음")
            return

        title = title_elem.get_text(strip=True)
        link_href = title_elem.get('href', '')
        if link_href.startswith('http'):
            link = link_href
        else:
            link = "https://www.kicpa.or.kr" + link_href

        last_id = ""
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r") as f:
                last_id = f.read().strip()

        print(f"최신 공고 ID: {post_id}, 저장된 ID: {last_id}")

        if post_id != last_id:
            message = f"🔔 [수습CPA 신규공고]\n\n제목: {title}\n링크: {link}"
            r = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={'chat_id': CHAT_ID, 'text': message}
            )
            print(f"텔레그램 전송 결과: {r.status_code}")

            with open("last_id.txt", "w") as f:
                f.write(post_id)
            print(f"새 공고 발견 및 알림 전송: {title}")
        else:
            print(f"새로운 수습 공고 없음 (최신글 ID: {post_id})")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_kicpa()
