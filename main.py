import requests
from bs4 import BeautifulSoup
import os

# --- 설정 ---
TOKEN = "8515226652:AAErrx7L5viImyMOvu3Q8la5lMcLYjtJm28"
CHAT_ID = "8367349099"
URL = "https://www.kicpa.or.kr/portal/recruitment/job/list.do"

def check_kicpa():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(URL, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 모든 게시글 행을 가져옵니다.
        rows = soup.select('table.tbl_board_list tbody tr:not(.notice)')
        if not rows: return

        # 2. 가장 위에 있는 '구인(수습CPA)' 말머리 글을 찾습니다.
        target_post = None
        for row in rows:
            # 말머리(카테고리) 텍스트 추출
            category = row.select_one('td.cate').text.strip() if row.select_one('td.cate') else ""
            
            if "수습CPA" in category:
                target_post = row
                break # 가장 최신 수습 공고 하나만 찾으면 중단
        
        if not target_post:
            print("현재 페이지에 수습CPA 공고가 없습니다.")
            return

        # 3. 데이터 추출
        post_id = target_post.select_one('td.num').text.strip()
        title_elem = target_post.select_one('td.subject a')
        title = title_elem.text.strip()
        link = "https://www.kicpa.or.kr" + title_elem['href']

        # 4. 책갈피(last_id.txt) 확인
        last_id = ""
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r") as f:
                last_id = f.read().strip()

        # 5. 새 글이면 알림 전송
        if post_id != last_id:
            message = f"📢 [KICPA] 신규 수습CPA 공고!\n\n제목: {title}\n링크: {link}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          data={'chat_id': CHAT_ID, 'text': message})
            
            # 새 글 ID 저장
            with open("last_id.txt", "w") as f:
                f.write(post_id)
            print(f"알림 발송 완료: {title}")
        else:
            print("새로운 수습 공고가 없습니다.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_kicpa()
