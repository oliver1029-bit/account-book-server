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
    
    # 결제 수단(카드사) 찾기
    for line in lines:
        if any(keyword in line for keyword in ['카드', '은행', '뱅크']):
            words = line.split()
            for word in words:
                if '카드' in word or '은행' in word or '뱅크' in word:
                    payment_method = word
                    break
        if payment_method != "알 수 없음":
            break
            
    # 1. 금액 찾기
    for i, line in enumerate(lines):
        if ('원' in line or re.fullmatch(r'[0-9,]+', line.strip())) and '잔액' not in line and '누적' not in line:
            amount_match = re.search(r'([0-9,]+)', line)
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
            break
            
    # 2. 상호명 찾기 (똑똑한 필터링)
    for line in lines:
        if '카드' in line or '승인' in line or '취소' in line: continue
        if '*' in line: continue # 이름 마스킹(문*철) 제외
        if '원' in line and bool(re.search(r'[0-9]', line)): continue # 133,000원 등 숫자+원 제외
        if '/' in line or ':' in line: continue # 날짜와 시간(07/31 11:50) 제외
        if '누적' in line or '잔액' in line: continue
        
        # 위 조건에 걸리지 않은 순수한 글자 줄을 상호명으로 채택!
        shop_name = line.strip()
        break
            
    final_amount = amount if transaction_type == "수입" else -amount
            
    return {
        "payment_method": payment_method,
        "type": transaction_type,
        "title": shop_name,
        "amount": final_amount
    }
