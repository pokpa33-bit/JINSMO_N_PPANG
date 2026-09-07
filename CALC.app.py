import streamlit as st
import pandas as pd

st.set_page_config(page_title="진스모 정산기", layout="centered", page_icon="⛳️")

# 웹사이트 상단 타이틀 및 설명
st.title("⛳️ JINSMO N_PPANG 자동 정산기")

# 계좌번호 상시 고정
st.success("🏦 **[총무 계좌안내] 카카오뱅크 3333358864688 박대환**")

st.write("구성원의 이름, G핸디, 금일타수를 입력하면 순위와 금액이 자동 계산됩니다.")
st.write("💡 **동타일 경우 G핸디가 낮은 사람이 우선순위가 됩니다.**")

# 1. 초기 샘플 데이터 세팅
init_data = [
    {"이름": "회원1", "G핸디": 5.2, "금일타수": 78},
    {"이름": "회원2", "G핸디": 3.1, "금일타수": 82},
    {"이름": "회원3", "G핸디": 4.5, "금일타수": 78}
]
df = pd.DataFrame(init_data)

st.subheader("📋 참석자 명단 입력")

# 인원추가 안내 문구 강력 강조
st.error("🚨 **[필독] 인원 추가 방법: 명단 표 맨 아래 왼쪽의 [+] 버튼을 누르면 줄이 늘어납니다!**")
st.info("💡 각 칸을 더블클릭하면 이름, 핸디, 타수를 수정할 수 있습니다.")

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
        
        # 인당 기본 기준 비용 산정 (스크린 14,000원 + 밥값 6,900원 = 20,900원)
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
        
        # 인원별/등수별 금액 할당 로직 (1등: 16,000원 / 2등: 22,000원 / 3등: 26,000원 기본 로직 적용)
        for idx, row in sorted_df.iterrows():
            rank = idx + 1
            name = row["이름"]
            handi = row["G핸디"]
            score = row["금일타수"]
            
            # 정확히 3명일 때 완벽 매칭
            if total_players == 3:
                if rank == 1: pay_amount = 16000
                elif rank == 2: pay_amount = 22000
                else: pay_amount = 26000
                
            # 4명일 때 (1등 / 2,3등 / 4등 분할 조율)
            elif total_players == 4:
                if rank == 1: pay_amount = 16000
                elif rank == 2 or rank == 3: pay_amount = 22000
                else: pay_amount = 23600  # 총액 맞춤 조율
                
            # 7명일 때 (1~2등: 16,000원 / 3~5등: 22,000원 / 6~7등: 차액 정산)
            elif total_players == 7:
                if rank == 1 or rank == 2:
                    pay_amount = 16000
                elif rank == 3 or rank == 4 or rank == 5:
                    pay_amount = 22000
                else:
                    pay_amount = 24150  # 총액 맞춤 조율
                    
            # 그 외 13명~15명 등 대규모 인원일 때 그룹 비례 분담 규칙
            else:
                # 상위 33% 그룹, 중위 33% 그룹, 하위 그룹으로 쪼개어 각각 16,000원, 22,000원, 26,000원 주변으로 자동 분배
                if rank <= total_players // 3:
                    pay_amount = 16000
                elif rank <= (total_players // 3) * 2:
                    pay_amount = 22000
                else:
                    # 하위 그룹이 나머지 총액 채우기 (n분의 1)
                    rem_players = total_players - ((total_players // 3) * 2)
                    rem_budget = total_budget - (16000 * (total_players // 3)) - (22000 * (total_players // 3))
                    pay_amount = int(rem_budget / rem_players)
                
            result_text += f"  - {rank}등: {name} (타수:{score} / 핸디:{handi}) ➡️ {pay_amount:,}원\n"
            
        result_text += "\n🏦 입금 계좌: 카카오뱅크 3333358864688 박대환"
        result_text += "\n\n당일 원활한 정산을 위해 확인하시는 대로 빠른 입금 부탁드립니다. 오늘 모두 고생 많으셨습니다! ⛳️"
        
        # 웹 화면에 최종 정산 결과 박스 띄우기
        st.subheader("✨ 자동 정산 결과")
        st.text_area("아래 문구를 전체 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=350)
        st.success("정산 문구 생성이 완료되었습니다! 복사해서 단톡방에 공유하세요.")
