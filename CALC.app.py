import streamlit as st
import pandas as pd

st.set_page_config(page_title="진스모 정산기", layout="centered")

st.title("⛳️ 진스모 새벽모임 자동 정산기")
st.write("이름, G핸디, 금일타수를 입력하면 순위와 금액이 자동 계산됩니다.")

# 초기 샘플 데이터 설정
init_data = [{"이름": "홍길동", "G핸디": 5.2, "금일타수": 78}]
df = pd.DataFrame(init_data)

st.subheader("📋 참석자 명단 입력")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("🏆 순위 산정 및 카톡 정산문구 만들기", type="primary"):
    total_players = len(edited_df)
    
    # [동타 처리 규칙] 1순위: 타수 오름차순, 2순위: G핸디 오름차순
    sorted_df = edited_df.sort_values(by=["금일타수", "G핸디"], ascending=True).reset_index(drop=True)
    
    base_golf = 14000
    base_meal = 6900
    total_per_person = base_golf + base_meal
    total_budget = total_players * total_per_person
    
    result_text = f"[진스모 새벽모임 정산 안내]\n\n"
    result_text += f"금일 모임(총 {total_players}명) 스크린골프비 및 밥값 일괄 정산 내역입니다.\n"
    result_text += f"총액: {total_budget:,}원 (인당 기본 {total_per_person:,}원 산정)\n\n"
    result_text += "🏆 최종 성적 및 입금 금액\n"
    
    for idx, row in sorted_df.iterrows():
        rank = idx + 1
        name = row["이름"]
        handi = row["G핸디"]
        score = row["금일타수"]
        
        # 진스모 이미지 규칙 반영 (7인/4인 예시 및 기본 예외 처리)
        if total_players == 7:
            if rank in: pay_amount = 16000
            elif rank in: pay_amount = 21000
            else: pay_amount = 25650
        elif total_players == 4:
            if rank == 1: pay_amount = 16000
            elif rank in: pay_amount = 21000
            else: pay_amount = 25600
        else:
            pay_amount = total_per_person
            
        result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ {pay_amount:,}원\n"
        
    result_text += "\n🏦 계좌번호: [총무 은행 및 계좌번호]"
    
    st.subheader("✨ 자동 정산 결과")
    st.text_area("아래 문구를 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=300)
