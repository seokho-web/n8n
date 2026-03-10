import requests
from bs4 import BeautifulSoup
import os

# --- 설정 ---
TOKEN = "8515226652:AAErrx7L5viImyMOvu3Q8la5lMcLYjtJm28"
CHAT_ID = "8367349099"
# 수습CPA 전용 필터가 걸린 정확한 URL입니다.
URL = "https://www.kicpa.or.kr/portal/recruitment/job/list.do?searchJobSeCode=02"

def check_kicpa():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        # 1. 수습CPA 전용 페이지 접속
        res = requests.get(URL, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. 게시글 목록 찾기 (공지사항 제외한 진짜 첫 번째 줄)
        # KICPA 사이트 특성상 tbl_board_list 클래스를 사용함
        rows = soup.select('table.tbl_board_list tbody tr:not(.notice)')
        
        if not rows:
            print("현재 등록된 수습CPA 공고가 없습니다.")
            return

        # 가장 최상단 글 선택
        target_post = rows[0]

        # 3. 정보 추출
        # 글번호(num), 제목(subject > a), 날짜(date) 등
        post_id = target_post.select_one('td.num').text.strip()
        title_elem = target_post.select_one('td.subject a')
        title = title_elem.text.strip()
        
        # 링크 추출 및 절대경로 변환
        link_href = title_elem.get('href', '')
        link = "https://www.kicpa.or.kr" + link_href

        # 4. 책갈피 확인 (중복 알림 방지)
        last_id = ""
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r") as f:
                last_id = f.read().strip()

        # 5. 새 글이면 텔레그램 발송
        if post_id != last_id:
            message = f"🔔 [수습CPA 신규공고]\n\n제목: {title}\n링크: {link}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          data={'chat_id': CHAT_ID, 'text': message})
            
            # 새 글 ID 저장
            with open("last_id.txt", "w") as f:
                f.write(post_id)
            print(f"새 공고 발견 및 알림 전송: {title}")
        else:
            print(f"새로운 수습 공고 없음 (최신글 ID: {post_id})")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_kicpa()
