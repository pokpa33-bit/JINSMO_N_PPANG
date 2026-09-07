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
    {"이름": "홍기동", "G핸디": -0.1, "금일타수": 77},
    {"이름": "박대환", "G핸디": -0.2, "금일타수": 77},
    {"이름": "유순창", "G핸디": -0.3, "금일타수": 77},
    {"이름": "박두진", "G핸디": -0.4, "금일타수": 77}
]

if "df_data" not in st.session_state:
    st.session_state.df_data = pd.DataFrame(init_data)

st.subheader("📋 참석자 명단 입력")

# 인원 추가 및 삭제 가이드 강력 강조
st.error("🚨 **[필독] 인원 추가 방법: 명단 표 맨 아래 왼쪽의 [+] 버튼을 누르면 줄이 늘어납니다!**")
st.warning("🗑️ **[필독] 실수로 만든 줄 삭제 방법: 지우고 싶은 줄(행)을 마우스나 손가락으로 한 번 터치(선정)한 후, 키보드의 [Delete] 또는 [Backspace] 키를 누르면 즉시 지워집니다!**")

if st.button("🔄 표 전체 초기화 (새로 쓰기)"):
    st.session_state.df_data = pd.DataFrame([{"이름": "", "G핸디": 0.0, "금일타수": 0}])
    st.rerun()

st.info("💡 각 칸을 더블클릭하면 이름, 핸디, 타수를 수정할 수 있습니다.")

edited_df = st.data_editor(st.session_state.df_data, num_rows="dynamic", use_container_width=True)
st.session_state.df_data = edited_df

# 천원 단위 사사오입(반올림) 함수 정의
def round_to_thousand(amount):
    return int(round(amount / 1000) * 1000)

# 2. 계산 및 정산문구 생성 버튼
if st.button("🏆 순위 산정 및 카톡 정산문구 만들기", type="primary"):
    valid_df = edited_df.dropna(subset=["이름"])
    valid_df = valid_df[(valid_df["이름"].str.strip() != "") & (valid_df["이름"] != "None") & (valid_df["금일타수"] > 0)]
    
    total_players = len(valid_df)
    
    if total_players == 0:
        st.error("참석자를 최소 1명 이상 정확히 입력해 주세요.")
    else:
        # [동타 처리 및 우선순위 정렬 규칙 반영]
        sorted_df = valid_df.sort_values(by=["금일타수", "G핸디"], ascending=True).reset_index(drop=True)
        
        # 인당 기본 비용 (스크린 14,000원 + 밥값 6,900원 = 20,900원)
        base_golf = 14000
        base_meal = 6900
        total_per_person = base_golf + base_meal
        total_budget = total_players * total_per_person
        
        result_text = f"[진스모 새벽모임 정산 안내]\n\n"
        result_text += f"금일 모임(총 {total_players}명) 스크린골프비 및 밥값 일괄 정산 내역입니다.\n"
        result_text += f"총액: {total_budget:,}원 (인당 기본 {total_per_person:,}원 산정)\n"
        result_text += f"정렬 기준: 금일타수 기준 (동타 시 G핸디가 낮은 사람 우선)\n\n"
        result_text += "🏆 최종 성적 및 입금 금액\n"
        
        # 등수별 금액 할당 로직 (요청 반영: 4인 기준 하위 26,000원 절대 고정)
        for idx, row in sorted_df.iterrows():
            rank = idx + 1
            name = row["이름"]
            handi = row["G핸디"]
            score = row["금일타수"]
            
            # 정확히 3명일 때
            if total_players == 3:
                if rank == 1: pay_amount = 16000
                elif rank == 2: pay_amount = 22000
                else: pay_amount = 26000
                
            # ⭐ 4명일 때 (요청 반영: 하위 순위 무조건 26,000원 고정 구조)
            elif total_players == 4:
                if rank == 1: pay_amount = 16000
                elif rank == 2 or rank == 3: pay_amount = 22000
                else: pay_amount = 26000  # 4등 26,000원 무조건 고정
                
            # 7명일 때 (상위 2명 16,000원 고정 / 하위 2명 26,000원 고정 / 중간 3명은 사사오입 계산)
            elif total_players == 7:
                if rank == 1 or rank == 2:
                    pay_amount = 16000
                elif rank == 6 or rank == 7:
                    pay_amount = 26000
                else:
                    rem_budget = total_budget - (16000 * 2) - (26000 * 2)
                    pay_amount = round_to_thousand(rem_budget / 3)
                    
            # 그 외 13명~15명 대규모 인원일 때 상위/하위 33% 적용 로직
            else:
                group_size = total_players // 3
                if rank <= group_size:
                    pay_amount = 16000
                elif rank > total_players - group_size:
                    pay_amount = 26000
                else:
                    middle_players = total_players - (group_size * 2)
                    rem_budget = total_budget - (16000 * group_size) - (26000 * group_size)
                    pay_amount = round_to_thousand(rem_budget / middle_players)
                
            result_text += f"  - {rank}등: {name} (타수:{score} / 핸디:{handi}) ➡️ {pay_amount:,}원\n"
            
        result_text += "\n🏦 입금 계좌: 카카오뱅크 3333358864688 박대환"
        result_text += "\n\n당일 원활한 정산을 위해 확인하시는 대로 빠른 입금 부탁드립니다. 오늘 모두 고생 많으셨습니다! ⛳️"
        
        st.subheader("✨ 자동 정산 결과")
        st.text_area("아래 문구를 전체 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=350)
        st.success("정산 문구 생성이 완료되었습니다! 복사해서 단톡방에 공유하세요.")
