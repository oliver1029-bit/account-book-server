from fastapi import FastAPI
from pydantic import BaseModel
import re
import uvicorn

# 1. FastAPI 미니 서버 생성
app = FastAPI(title="가계부 자동화 서버")

# 2. 앱에서 받을 데이터의 형태(구조) 정의
class SMSRequest(BaseModel):
    text: str

# 3. 아까 완성한 파싱 로직 (그대로 가져옴)
def parse_payment_sms(text: str):
    if '입금' in text or '취소' in text:
        transaction_type = "수입"
    elif '출금' in text or '승인' in text:
        transaction_type = "지출"
    else:
        transaction_type = "알 수 없음"

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    shop_name = "알 수 없음"
    payment_method = "알 수 없음"
    amount = 0
    
    for line in lines:
        if any(keyword in line for keyword in ['카드', '은행', '뱅크']):
            words = line.split()
            for word in words:
                if '카드' in word or '은행' in word or '뱅크' in word:
                    payment_method = word
                    break
        if payment_method != "알 수 없음":
            break
            
    for i, line in enumerate(lines):
        if '원' in line and '잔액' not in line:
            amount_match = re.search(r'([0-9,]+)', line)
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
            if i > 0:
                shop_name = lines[i-1]
            break
            
    final_amount = amount if transaction_type == "수입" else -amount
            
    return {
        "payment_method": payment_method,
        "type": transaction_type,
        "title": shop_name,
        "amount": final_amount
    }

# 4. 앱에서 데이터를 쏠 '주소(Endpoint)' 만들기
@app.post("/api/parse")
def parse_sms_endpoint(request: SMSRequest):
    # 플러터 앱에서 보낸 문자 텍스트를 파싱 로직에 넣고 돌림
    result = parse_payment_sms(request.text)
    
    # 처리된 예쁜 데이터를 다시 앱으로 돌려줌
    return {
        "status": "success",
        "data": result
    }

# 5. 서버 실행 명령 (▷ 버튼을 누르면 작동)
if __name__ == "__main__":
    print("🚀 가계부 미니 서버가 시작됩니다! (포트: 8000)")
    uvicorn.run(app, host="0.0.0.0", port=8000)