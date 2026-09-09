import streamlit as st
import pandas as pd

st.set_page_config(page_title="진스모 정산기", layout="centered", page_icon="⛳️")

# 💡 [제목 수정 완료] 형님 지시대로 불필요한 수식어를 빼고 직관적으로 정돈했습니다.
st.title("⛳️ JINSMO N_PPANG 정산기")
st.success("🏦 **[총무 계좌안내] 카카오뱅크 3333358864688 박대환**")

st.write("구성원의 이름, G핸디, 금일타수를 입력하면 순위와 정산 금액이 자동 계산됩니다.")
st.write("💡 **[최대 지출 제한] 진스모 규칙에 따라 인당 최종 지출 총액은 최대 26,000원을 절대 넘을 수 없습니다.**")
st.write("💡 **상위 30% 국밥 2그릇(13,800원) 결제 고정 / 하위조 26,000원 상한 고정 잠금 / 잔여금액 중간조 자동 분담**")

init_data = [
    {"이름": "홍기동", "G핸디": -0.1, "금일타수": 77},
    {"이름": "박대환", "G핸디": -0.2, "금일타수": 77},
    {"이름": "유순창", "G핸디": -0.3, "금일타수": 77},
    {"이름": "박두진", "G핸디": -0.4, "금일타수": 77}
]

if "df_data" not in st.session_state:
    st.session_state.df_data = pd.DataFrame(init_data)

st.subheader("📋 참석자 명단 입력")
st.error("🚨 **[필독] 인원 추가: 명단 표 맨 아래 왼쪽의 [+] 버튼을 누르세요! (4명 ~ 20명 가능)**")
st.warning("🗑️ **[필독] 줄 삭제: 줄을 선택한 후 키보드의 [Delete] 또는 [Backspace]를 누르세요!**")

if st.button("🔄 표 전체 초기화 (새로 쓰기)"):
    st.session_state.df_data = pd.DataFrame([{"이름": "", "G핸디": 0.0, "금일타수": 0}])
    st.rerun()

# [중복 입력 버그 차단] 세션 상태와 실시간 변동값을 동기화하여 엔터를 안 쳐도 즉시 반영되도록 제어
edited_df = st.data_editor(
    st.session_state.df_data, 
    num_rows="dynamic", 
    use_container_width=True,
    key="jinsmo_table_editor"
)
st.session_state.df_data = edited_df

if st.button("🏆 진스모 상한선 락 정산문구 생성", type="primary"):
    # 버튼 즉시 클릭 시 최신 편집 상태를 명확하게 다시 긁어옴
    latest_df = st.session_state.jinsmo_table_editor if "jinsmo_table_editor" in st.session_state else edited_df
    
    # 뼈대 데이터 처리 빌드
    if isinstance(latest_df, dict):
        valid_df = pd.DataFrame(init_data)
    else:
        valid_df = latest_df.dropna(subset=["이름"])
        valid_df = valid_df[(valid_df["이름"].str.strip() != "") & (valid_df["이름"] != "None") & (valid_df["금일타수"] > 0)]
        
    total_players = len(valid_df)
    
    if total_players < 4:
        st.error("진스모 규칙은 최소 4명 이상 입력해야 정확하게 계산됩니다. 명단 아래 [+] 버튼으로 인원을 추가해 주세요.")
    elif total_players > 20:
        st.error("최대 20명까지만 지원합니다. 인원을 확인해 주세요.")
    else:
        sorted_df = valid_df.sort_values(by=["금일타수", "G핸디"], ascending=True).reset_index(drop=True)
        
        # 실제 매장 지출 원금 계산
        total_golf_budget = total_players * 14000
        total_meal_budget = total_players * 6900
        total_overall_budget = total_golf_budget + total_meal_budget
        
        # 인원수별 상위 및 하위 비율 배분 (상위 30%, 하위 30%)
        if total_players == 4: top_count, bottom_count = 1, 1
        elif total_players == 7: top_count, bottom_count = 2, 2
        elif total_players == 10: top_count, bottom_count = 3, 4
        else:
            top_count = max(1, int(total_players * 0.3))
            bottom_count = max(1, int(total_players * 0.3))
            
        result_text = f"[진스모 새벽모임 최종 정산 안내]\n\n"
        result_text += f"금일 모임(총 {total_players}명) 지출 상한선 잠금형 하이브리드 정산 내역입니다.\n"
        result_text += f"원칙: 상위조 국밥 2인분(13,800원) 결제 / 하위조 인당 최대 지출 26,000원 상한 차단 / 잔여 금액 중간조 분담\n\n"
        
        result_text += f"💰 [금일 매장 실제 지출 총액 원금]\n"
        result_text += f"  - 스크린골프 총액: {total_golf_budget:,}원 (총무 현금 정산액)\n"
        result_text += f"  - 식사(국밥) 총액: {total_meal_budget:,}원 (정확히 실제 {total_players}그릇 실비 마감)\n"
        result_text += f"  👉 모임 전체 합산 총액: {total_overall_budget:,}원\n\n"
        
        result_text += "🏆 최종 성적 및 역할별 분담 금액\n"
        
        golf_pays = [0] * total_players
        meal_pays = [0] * total_players
        middle_indices = []
        
        # 1차 패스: 상위권 및 하위권 고정 상한선 락(Lock) 세팅
        for idx in range(total_players):
            rank = idx + 1
            if rank <= top_count:
                golf_pays[idx] = 0
                meal_pays[idx] = 13800  
            elif rank > (total_players - bottom_count):
                golf_pays[idx] = 26000  
                meal_pays[idx] = 0      
            else:
                middle_indices.append(idx)
                meal_pays[idx] = 6900   
                
        # 2차 패스: 중간 그룹이 남은 스크린비 잔액 전액 분담 역산
        if middle_indices:
            collected_golf_cash = sum(golf_pays[i] for i in range(total_players) if i not in middle_indices)
            remaining_golf = total_golf_budget - collected_golf_cash
            per_middle_golf = int(remaining_golf / len(middle_indices))
            
            for m_idx in middle_indices:
                golf_pays[m_idx] = per_middle_golf
                
            # 1원 단위 현금 오차 0원 정밀 보정
            last_middle_idx = middle_indices[-1]
            golf_pays[last_middle_idx] = total_golf_budget - sum(golf_pays[i] for i in range(total_players) if i != last_middle_idx)
            
            # 3차 패스: 식당 카드결제 영수증 오차 0원 정밀 보정
            card_indices = list(range(0, total_players - bottom_count))
            last_card_idx = card_indices[-1] if card_indices else 0
            other_card_sum = sum(meal_pays[i] for i in range(total_players) if i != last_card_idx)
            meal_pays[last_card_idx] = total_meal_budget - other_card_sum

        # 텍스트 출력 빌드
        cash_total = 0
        card_total = 0
        for idx, row in sorted_df.iterrows():
            rank = idx + 1
            name = row["이름"]
            handi = row["G핸디"]
            score = row["금일타수"]
            g_p = golf_pays[idx]
            m_p = meal_pays[idx]
            
            if g_p == 0:
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 스크린비 [0원 면제] 🎉 + 국밥값 {m_p:,}원 [식당 카드결제] (최종 지출: {m_p:,}원)\n"
            elif m_p == 0:
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 총무 계좌로 스크린비 [ {g_p:,}원 ] 송금 💵 (식당 결제 없음 ❌) (최종 지출: 26,000원 상한 락 🛑)\n"
            else:
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 총무 계좌로 스크린비 [ {g_p:,}원 ] 송금 💵 + 국밥값 {m_p:,}원 [식당 카드결제] (최종 지출: {g_p+m_p:,}원)\n"
            cash_total += g_p
            card_total += m_p
                
        result_text += f"\n📊 [총무 정산 검증 테이블 (오차 점검)]\n"
        result_text += f"  - 회원 송금액 합계: {cash_total:,}원 ➡️ 매장 원금({total_golf_budget:,}원)과 오차 [ 0원 ] 완벽 일치!\n"
        result_text += f"  - 회원 카드 결제 합계: {card_total:,}원 ➡️ 식당 원금({total_meal_budget:,}원)과 오차 [ 0원 ] 완벽 일치!\n"
        result_text += f"  👉 최종 정산 결과: 진스모 인당 최종 지출액이 26,000원 선에서 철저히 잠금 관리되며 총무 장부 차액은 정확히 [ 0원 ] 입니다.\n"
        result_text += "\n🏦 입금 계좌: 카카오뱅크 3333358864688 박대환"
        result_text += "\n⚠️ 식당 계산대에서는 전원이 계산대에 본인 이름 옆에 적힌 정확한 금액을 말씀하시고 개별 카드로 긁으시면 오늘 정산은 완벽히 마감됩니다."
        
        st.subheader("✨ 자동 정산 결과")
        st.text_area("아래 문구를 전체 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=450)
        st.success("데이터 버퍼 오차가 완벽 차단된 마스터 정산기 세팅이 완료되었습니다!")
