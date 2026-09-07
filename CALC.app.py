import streamlit as st
import pandas as pd

st.set_page_config(page_title="진스모 정산기", layout="centered", page_icon="⛳️")

# 웹사이트 상단 타이틀 및 설명
st.title("⛳️ JINSMO N_PPANG 플렉시블 정산기")

# 계좌번호 상시 고정
st.success("🏦 **[총무 계좌안내] 카카오뱅크 3333358864688 박대환**")

st.write("구성원의 이름, G핸디, 금일타수를 입력하면 순위와 정산 금액이 자동 계산됩니다.")
st.write("💡 **4명부터 17명까지 완벽 대응! 상위 30% 16,000원 / 하위 30% 최대 26,000원 한도 고정**")

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
st.error("🚨 **[필독] 인원 추가: 명단 표 맨 아래 왼쪽의 [+] 버튼을 누르세요! (4명 ~ 17명 가능)**")
st.warning("🗑️ **[필독] 줄 삭제: 줄을 선택한 후 키보드의 [Delete] 또는 [Backspace]를 누르세요!**")

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
if st.button("🏆 진스모 하이브리드 정산문구 생성", type="primary"):
    valid_df = edited_df.dropna(subset=["이름"])
    valid_df = valid_df[(valid_df["이름"].str.strip() != "") & (valid_df["이름"] != "None") & (valid_df["금일타수"] > 0)]
    total_players = len(valid_df)
    
    if total_players < 4:
        st.error("진스모 규칙은 최소 4명 이상 입력해야 정확하게 계산됩니다. 인원을 추가해 주세요.")
    elif total_players > 17:
        st.error("최대 17명까지만 지원합니다. 인원을 확인해 주세요.")
    else:
        # [동타 처리 및 우선순위 정렬 규칙 반영] 1순위 타수 오름차순, 2순위 핸디 오름차순
        sorted_df = valid_df.sort_values(by=["금일타수", "G핸디"], ascending=True).reset_index(drop=True)
        
        # 총 스크린골프 비용 (인당 14,000원) 및 국밥 비용 (인당 6,900원) 계산
        total_golf_budget = total_players * 14000
        total_meal_budget = total_players * 6900
        total_overall_budget = total_golf_budget + total_meal_budget
        
        result_text = f"[진스모 새벽모임 최종 정산 안내]\n\n"
        result_text += f"금일 모임(총 {total_players}명) 하이브리드 정산 내역입니다.\n"
        result_text += f"정렬 기준: 금일타수 기준 (동타 시 G핸디가 낮은 사람 우선)\n"
        result_text += f"원칙: 상위 30% 그룹 16,000원 고정 / 하위 30% 그룹 최대 26,000원 한도 제한 적용\n\n"
        
        # 밥값, 스크린비 총액 정리 부분 출력
        result_text += f"💰 [금일 지출 총액 내역]\n"
        result_text += f"  - 스크린골프 총액: {total_golf_budget:,}원 ({total_players}명 × 14,000원)\n"
        result_text += f"  - 식사(국밥) 총액: {total_meal_budget:,}원 ({total_players}명 × 6,900원)\n"
        result_text += f"  👉 모임 전체 합산 총액: {total_overall_budget:,}원\n\n"
        
        result_text += "🏆 최종 성적 및 역할별 분담 금액\n"
        
        pay_amounts = [0] * total_players
        pay_types = [""] * total_players
        
        # 플렉시블 인원별 상하위 그룹 인원 배분 규칙 (형님 지정 예외 포함)
        if total_players == 4:
            top_count, bottom_count = 1, 1
        elif total_players == 7:
            top_count, bottom_count = 2, 2
        elif total_players == 10:
            top_count, bottom_count = 3, 4
        else:
            top_count = max(1, int(total_players * 0.3))
            bottom_count = max(1, int(total_players * 0.3))
            
        middle_indices = []
        collected_cash = 0
        
        # 1차 패스: 고정 현금 그룹 먼저 확정
        for idx in range(total_players):
            rank = idx + 1
            if rank <= top_count:
                pay_amounts[idx] = 16000
                pay_types[idx] = "현금 송금"
                collected_cash += 16000
            elif rank > (total_players - bottom_count):
                pay_amounts[idx] = 26000  # 하위 등수 무조건 26,000원 한도 고정
                pay_types[idx] = "현금 송금"
                collected_cash += 26000
            else:
                middle_indices.append(idx)
                pay_types[idx] = "식당 카드 결제"
                
        # 2차 패스: 중간 그룹 카드 분담액 자동 역산 및 사사오입
        if middle_indices:
            remaining_budget = total_overall_budget - collected_cash
            per_middle_card = remaining_budget / len(middle_indices)
            rounded_card_amount = round_to_thousand(per_middle_card)
            for m_idx in middle_indices:
                pay_amounts[m_idx] = rounded_card_amount

        # 텍스트 출력 빌드
        cash_total = 0
        card_total = 0
        for idx, row in sorted_df.iterrows():
            rank = idx + 1
            name = row["이름"]
            handi = row["G핸디"]
            score = row["금일타수"]
            amt = pay_amounts[idx]
            ptype = pay_types[idx]
            
            if ptype == "현금 송금":
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ {amt:,}원 [총무 계좌 송금]\n"
                cash_total += amt
            else:
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ {amt:,}원 [식당 카드 결제]\n"
                card_total += amt
                
        # 총무 검증용 테이블 출력
        result_text += f"\n📊 [총무 정산 검증 테이블]\n"
        result_text += f"  - 실제 걷히는 현금 총액: {cash_total:,}원\n"
        result_text += f"  - 실제 식당 카드 결제 총액: {card_total:,}원\n"
        result_text += f"  - 실제 정산 처리 합산액: {cash_total+card_total:,}원\n"
        result_text += "\n🏦 입금 계좌: 카카오뱅크 3333358864688 박대환"
        result_text += "\n⚠️ 식당 카드 결제 인원은 식당 계산대에서 위 금액만큼 결제해 주시면 됩니다."
        result_text += "\n\n오늘 모두 고생 많으셨습니다! 즐거운 하루 되세요. ⛳️"
        
        st.subheader("✨ 자동 정산 결과")
        st.text_area("아래 문구를 전체 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=450)
        st.success("4인~17인 완벽 대응 진스모 하이브리드 정산 양식이 업데이트되었습니다!")
