import streamlit as st
import pandas as pd

st.set_page_config(page_title="진스모 정산기", layout="centered", page_icon="⛳️")

# 웹사이트 상단 타이틀 및 설명
st.title("⛳️ JINSMO N_PPANG 자동 정산기")
st.write("구성원의 이름, G핸디, 금일타수를 입력하면 순위와 금액이 자동 계산됩니다.")
st.write("💡 **동타일 경우 G핸디가 낮은 사람이 우선순위가 됩니다.**")

# 1. 초기 샘플 데이터 세팅 (마우스로 행 추가 및 삭제 가능)
init_data = [
    {"이름": "회원1", "G핸디": 5.0, "금일타수": 80},
    {"이름": "회원2", "G핸디": 3.0, "금일타수": 85},
    {"이름": "회원3", "G핸디": 4.5, "금일타수": 80}
]
df = pd.DataFrame(init_data)

st.subheader("📋 참석자 명단 입력")
st.info("💡 표 아래의 **[+]** 버튼을 눌러 인원을 추가할 수 있습니다. 칸을 더블클릭하여 내용을 수정하세요.")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# 2. 계산 및 정산문구 생성 버튼
if st.button("🏆 순위 산정 및 카톡 정산문구 만들기", type="primary"):
    total_players = len(edited_df)
    
    if total_players == 0:
        st.error("참석자를 최소 1명 이상 입력해 주세요.")
    else:
        # [동타 처리 및 우선순위 정렬 규칙 반영]
        # 1순위: 금일타수 오름차순, 2순위: G핸디 오름차순
        sorted_df = edited_df.sort_values(by=["금일타수", "G핸디"], ascending=True).reset_index(drop=True)
        
        # 인당 기본 기준 비용 산정 (스크린 14,000원 + 밥값 6,900원)
        base_golf = 14000
        base_meal = 6900
        total_per_person = base_golf + base_meal
        total_budget = total_players * total_per_person
        
        # 카톡 공유용 결과 텍스트 빌드 시작
        result_text = f"[진스모 새벽모임 정산 안내]\n\n"
        result_text += f"금일 모임(총 {total_players}명) 스크린골프비 및 밥값 일괄 정산 내역입니다.\n"
        result_text += f"총액: {total_budget:,}원 (인당 기본 {total_per_person:,}원 산정)\n"
        result_text += f"정렬 기준: 금일타수 기준 (동타 시 G핸디가 낮은 사람 우선)\n\n"
        result_text += "🏆 최종 성적 및 입금 금액\n"
        
        # 인원별/등수별 금액 할당 로직
        for idx, row in sorted_df.iterrows():
            rank = idx + 1
            name = row["이름"]
            handi = row["G핸디"]
            score = row["금일타수"]
            
            # 7명 모임일 때 대화방 이미지 규칙 적용
            if total_players == 7:
                if rank in: pay_amount = 16000
                elif rank in: pay_amount = 21000
                else: pay_amount = 25650
            # 4명 모임일 때 대화방 이미지 규칙 적용
            elif total_players == 4:
                if rank == 1: pay_amount = 16000
                elif rank in: pay_amount = 21000
                else: pay_amount = 25600
            # 그 외 인원은 기본 균등 금액 적용 (당일 조율용)
            else:
                pay_amount = total_per_person
                
            result_text += f"  - {rank}등: {name} (타수:{score} / 핸디:{handi}) ➡️ {pay_amount:,}원\n"
            
        result_text += "\n🏦 입금 계좌: [총무님 은행 및 계좌번호를 적어주세요]"
        result_text += "\n\n당일 원활한 정산을 위해 확인하시는 대로 빠른 입금 부탁드립니다. 오늘 모두 고생 많으셨습니다! ⛳️"
        
        # 웹 화면에 최종 정산 결과 박스 띄우기
        st.subheader("✨ 자동 정산 결과")
        st.text_area("아래 문구를 전체 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=350)
        st.success("정산 문구 생성이 완료되었습니다! 복사해서 단톡방에 공유하세요.")
