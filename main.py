import requests
from bs4 import BeautifulSoup
import os

# --- 설정 (GitHub Secrets에서 환경변수로 읽어옴) ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# iframe 내부 실제 데이터 URL (ijEmpSep=02 = 수습CPA)
URL = "https://www.kicpa.or.kr/home/jobOffrSrchNewGnrl/list.face?listCnt=20&ijEmpSep=02"

def check_kicpa():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.kicpa.or.kr/portal/default/kicpa/gnb/kr_pc/menu05/menu09/menu07.page',
    }
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # iframe 내부 테이블 구조: table.table_st02 tbody tr
        rows = soup.select('table.table_st02 tbody tr')

        if not rows:
            print("현재 등록된 수습CPA 공고가 없거나 파싱 실패.")
            print("HTML 일부:", res.text[:500])  # 디버깅용
            return

        # 첫 번째 행(최신 공고)
        target_post = rows[0]
        tds = target_post.find_all('td')

        if len(tds) < 2:
            print("예상과 다른 테이블 구조:", target_post)
            return

        # 번호(첫 번째 td), 제목 링크(두 번째 td의 a태그)
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

        # 중복 알림 방지
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
