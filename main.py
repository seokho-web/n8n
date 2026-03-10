import requests
from bs4 import BeautifulSoup
import os

# --- 설정 (이전 정보 그대로 사용) ---
TOKEN = "8515226652:AAErrx7L5viImyMOvu3Q8la5lMcLYjtJm28"
CHAT_ID = "8367349099"
URL = "https://www.kicpa.or.kr/portal/recruitment/job/list.do"

def check_kicpa():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(URL, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 첫 번째 일반 게시글 찾기
        post = soup.select_one('table.tbl_board_list tbody tr:not(.notice)')
        if not post: return

        post_id = post.select_one('td.num').text.strip()
        title_elem = post.select_one('td.subject a')
        title = title_elem.text.strip()
        link = "https://www.kicpa.or.kr" + title_elem['href']

        # 이전에 저장된 ID 확인
        last_id = ""
        if os.path.exists("last_id.txt"):
            with open("last_id.txt", "r") as f:
                last_id = f.read().strip()

        # 새 글이 올라왔고 '수습' 키워드가 있다면 발송
        if post_id != last_id:
            if "수습" in title:
                msg = f"🔔 [KICPA] 새 수습공고!\n\n제목: {title}\n링크: {link}"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              data={'chat_id': CHAT_ID, 'text': msg})
            
            # 새 글 ID 저장
            with open("last_id.txt", "w") as f:
                f.write(post_id)
            return True # 변경사항 있음
        return False # 변경사항 없음
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_kicpa()
