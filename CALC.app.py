import streamlit as st
import pandas as pd

st.set_page_config(page_title="진스모 정산기", layout="centered", page_icon="⛳️")

# 웹사이트 상단 타이틀 및 설명
st.title("⛳️ JINSMO N_PPANG 영구 마스터 정산기")
st.success("🏦 **[총무 계좌안내] 카카오뱅크 3333358864688 박대환**")

st.write("구성원의 이름, G핸디, 금일타수를 입력하면 순위와 정산 금액이 자동 계산됩니다.")
st.write("💡 **[하위조 상한선 락] 하위권 패널티 송금액은 최대 26,000원을 절대 넘지 않습니다.**")
st.write("💡 **4인 이하 모임은 기본 N빵 정산 / 5인 이상 모임은 진스모 국밥 하이브리드 마스터 룰이 자동 적용됩니다.**")

init_data = [
    {"이름": "홍기동", "G핸디": -0.1, "금일타수": 77},
    {"이름": "박대환", "G핸디": -0.2, "금일타수": 77},
    {"이름": "유순창", "G핸디": -0.3, "금일타수": 77},
    {"이름": "박두진", "G핸디": -0.4, "금일타수": 77}
]

if "df_data" not in st.session_state:
    st.session_state.df_data = pd.DataFrame(init_data)

st.subheader("📋 참석자 명단 입력")
st.error("🚨 **[필독] 인원 추가: 명단 표 맨 아래 왼쪽의 [+] 버튼을 누르세요! (3명 ~ 20명 가능)**")
st.warning("🗑️ **[필독] 줄 삭제: 줄을 선택한 후 키보드의 [Delete] 또는 [Backspace]를 누르세요!**")

if st.button("🔄 표 전체 초기화 (새로 쓰기)"):
    st.session_state.df_data = pd.DataFrame([{"이름": "", "G핸디": 0.0, "금일타수": 0}])
    st.rerun()

edited_df = st.data_editor(st.session_state.df_data, num_rows="dynamic", use_container_width=True)
st.session_state.df_data = edited_df

# 1,000원 단위 사사오입 함수 정의
def round_to_thousand(amount):
    return int(round(amount / 1000) * 1000)

if st.button("🏆 진스모 하이브리드 정산문구 생성", type="primary"):
    valid_df = edited_df.dropna(subset=["이름"])
    valid_df = valid_df[(valid_df["이름"].str.strip() != "") & (valid_df["이름"] != "None") & (valid_df["금일타수"] > 0)]
    total_players = len(valid_df)
    
    if total_players < 3:
        st.error("진스모 규칙은 최소 3명 이상 입력해야 정확하게 계산됩니다. 인원을 추가해 주세요.")
    elif total_players > 20:
        st.error("최대 20명까지만 지원합니다. 인원을 확인해 주세요.")
    else:
        # [동타 처리 및 우선순위 정렬 규칙 반영] 1순위 타수 오름차순, 2순위 핸디 오름차순
        sorted_df = valid_df.sort_values(by=["금일타수", "G핸디"], ascending=True).reset_index(drop=True)
        
        total_golf_budget = total_players * 14000
        total_meal_budget = total_players * 6900
        total_overall_budget = total_golf_budget + total_meal_budget
        
        golf_pays = * total_players
        meal_pays = * total_players
        
        # 📌 인원별 정산 로직 분기
        if total_players <= 4:
            st.warning(f"⚠️ 금일 모임은 {total_players}명 소규모 라운딩이므로 기본 정산 방식(전원 스크린 N빵 + 국밥 각자결제)으로 계산됩니다.")
            result_text = f"[진스모 새벽모임 최종 정산 안내]\n\n"
            result_text += f"금일 모임(총 {total_players}명) 소규모 N빵 정산 내역입니다.\n"
            result_text += f"원칙: 스크린비 인당 14,000원 계좌이체 / 국밥값 각자 식당 카드 결제\n\n"
            
            for idx in range(total_players):
                golf_pays[idx] = 14000
                meal_pays[idx] = 6900
                
        else:
            st.info(f"🔥 5인 이상 진스모 정식 라운딩(총 {total_players}명)이 감지되었습니다! 최대 26,000원 상한 락 하이브리드 정산 룰을 가동합니다.")
            result_text = f"[진스모 새벽모임 최종 정산 안내]\n\n"
            result_text += f"금일 모임(총 {total_players}명) 하이브리드 마스터 정산 내역입니다.\n"
            result_text += f"원칙: 1·2등 국밥 2그릇(13,800원) 결제 / 하위조 최대 26,000원 송금 상한 잠금 / 잔여금액 중간조 분담\n\n"
            
            if total_players == 5: top_count, bottom_count = 1, 2
            elif total_players == 7: top_count, bottom_count = 2, 2
            elif total_players == 10: top_count, bottom_count = 3, 4
            else:
                top_count = max(1, int(total_players * 0.3))
                bottom_count = max(1, int(total_players * 0.3))
                
            middle_indices = []
            
            # 1차 패스: 상하위조 고정 금액 한도 적용 및 잠금
            for idx in range(total_players):
                rank = idx + 1
                if rank <= top_count:
                    golf_pays[idx] = 0
                    meal_pays[idx] = 13800  # 상위조 13,800원 카드결제 고정
                elif rank > (total_players - bottom_count):
                    golf_pays[idx] = 26000  # 🛑 하위조 최대 26,000원 현금송금 고정
                    meal_pays[idx] = 0      # 식당 카드결제 없음
                else:
                    middle_indices.append(idx)
                    meal_pays[idx] = 6900   # 중간조 본인 국밥값 카드결제 기본 고정
                    
            # 2차 패스: 중간 그룹이 남은 스크린비 잔액 전액 분담
            if middle_indices:
                collected_golf_cash = sum(golf_pays[i] for i in range(total_players) if i not in middle_indices)
                remaining_golf = total_golf_budget - collected_golf_cash
                per_middle_golf = int(remaining_golf / len(middle_indices))
                
                for m_idx in middle_indices:
                    golf_pays[m_idx] = per_middle_golf
                    
                # 현금 오차 0원 정밀 보정
                last_middle_idx = middle_indices[-1]
                golf_pays[last_middle_idx] = total_golf_budget - sum(golf_pays[i] for i in range(total_players) if i != last_middle_idx)
                
                # 3차 패스: 식당 카드결제 영수증 오차 0원 정밀 보정
                card_indices = list(range(0, total_players - bottom_count))
                last_card_idx = card_indices[-1] if card_indices else 0
                other_card_sum = sum(meal_pays[i] for i in range(total_players) if i != last_card_idx)
                meal_pays[last_card_idx] = total_meal_budget - other_card_sum

        # 공통 실제 지출 금액 출력 빌드
        result_text += f"💰 [금일 매장 실제 지출 총액]\n"
        result_text += f"  - 스크린골프 총액: {total_golf_budget:,}원\n"
        result_text += f"  - 식사(국밥) 총액: {total_meal_budget:,}원 (정확히 실제 {total_players}그릇 실비 마감)\n"
        result_text += f"  👉 모임 전체 합산 총액: {total_overall_budget:,}원\n\n"
        result_text += "🏆 최종 성적 및 역할별 분담 금액\n"
        
        cash_total = 0
        card_total = 0
        for idx, row in sorted_df.iterrows():
            rank = idx + 1
            name = row["이름"]
            handi = row["G핸디"]
            score = row["금일타수"]
            g_p = golf_pays[idx]
            m_p = meal_pays[idx]
            
            if total_players <= 4:
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 스크린비 [ 14,000원 ] 송금 💵 + 국밥값 [ 6,900원 ] 식당 카드결제\n"
            else:
                if g_p == 0:
                    result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 스크린비 [0원 면제] 🎉 + 국밥값 {m_p:,}원 [식당 카드결제]\n"
                elif m_p == 0:
                    result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 총무 계좌로 스크린비 [ {g_p:,}원 ] 송금 💵 (식당 결제 없음 ❌) (상한가 잠금 락 적용)\n"
                else:
                    result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 총무 계좌로 스크린비 [ {g_p:,}원 ] 송금 💵 + 국밥값 {m_p:,}원 [식당 카드결제]\n"
            cash_total += g_p
            card_total += m_p
                
        result_text += f"\n📊 [총무 정산 검증 테이블]\n"
        result_text += f"  - 실제 걷히는 현금 총액: {cash_total:,}원 (스크린비 총액 {total_golf_budget:,}원과 오차 0원 완벽 일치!)\n"
        result_text += f"  - 실제 식당 카드 결제 총액: {card_total:,}원 (국밥 대금 {total_meal_budget:,}원과 오차 0원 완벽 일치!)\n"
        result_text += f"  👉 정산 결과: 하위 그룹의 최대 지출액이 26,000원으로 완벽하게 제어되었으며 총무 장부 차액은 [ 0원 ] 입니다.\n"
        result_text += "\n🏦 입금 계좌: 카카오뱅크 3333358864688 박대환"
        result_text += "\n⚠️ 식당 카드결제 안내를 받으신 분들은 계산대에서 본인 적힌 금액만큼 각자 카드로 긁으시면 오늘 정산은 완벽 마감됩니다."
        
        st.subheader("✨ 자동 정산 결과")
        st.text_area("아래 문구를 전체 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=450)
        st.success("하위조 26,000원 상한 락 하이브리드 정산 시스템 세팅이 최종 완료되었습니다!")
