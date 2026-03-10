import requests
from bs4 import BeautifulSoup
import os

# --- 설정 (GitHub Secrets에서 환경변수로 읽어옴) ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 수습CPA 구인 목록 URL
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

        rows = soup.select('table.table_st02 tbody tr')

        if not rows:
            print("공고 없음 또는 파싱 실패")
            return

        # 현재 공고 제목 전체 수집
        current_titles = set()
        for row in rows:
            title_elem = row.find('a')
            if title_elem:
                current_titles.add(title_elem.get_text(strip=True))

        print(f"현재 공고 수: {len(current_titles)}")

        # 이전 공고 목록 불러오기
        last_titles = set()
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r", encoding="utf-8") as f:
                last_titles = set(line.strip() for line in f if line.strip())

        # 새로 추가된 공고 찾기
        new_titles = current_titles - last_titles

        if new_titles:
            for title in new_titles:
                # 링크 찾기
                for row in rows:
                    title_elem = row.find('a')
                    if title_elem and title_elem.get_text(strip=True) == title:
                        link_href = title_elem.get('href', '')
                        link = link_href if link_href.startswith('http') else "https://www.kicpa.or.kr" + link_href
                        break
                else:
                    link = URL

                message = f"🔔 [수습CPA 신규공고]\n\n제목: {title}\n링크: {link}"
                r = requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={'chat_id': CHAT_ID, 'text': message}
                )
                print(f"알림 전송: {title} (결과: {r.status_code})")
        else:
            print("새로운 공고 없음")

        # 현재 공고 목록 저장
        with open("last_id.txt", "w", encoding="utf-8") as f:
            for title in current_titles:
                f.write(title + "\n")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_kicpa()
