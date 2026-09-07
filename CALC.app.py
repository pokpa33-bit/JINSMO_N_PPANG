import streamlit as st
import pandas as pd

st.set_page_config(page_title="진스모 정산기", layout="centered", page_icon="⛳️")

# 웹사이트 상단 타이틀 및 설명
st.title("⛳️ JINSMO N_PPANG 영구 마스터 정산기")
st.success("🏦 **[총무 계좌안내] 카카오뱅크 3333358864688 박대환**")

st.write("구성원의 이름, G핸디, 금일타수를 입력하면 순위와 정산 금액이 자동 계산됩니다.")
st.write("💡 **[진스모 절대 규칙] 스크린비 원금(인당 14,000원)은 무조건 현금 총액으로 100% 온전히 확보됩니다.**")
st.write("💡 **1·2등 국밥 2그릇(13,800원) / 3등 국밥 3그릇 벌칙(20,700원) / 나머지 조원 스크린비 전액 균등 현금 엔빵**")

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

edited_df = st.data_editor(st.session_state.df_data, num_rows="dynamic", use_container_width=True)
st.session_state.df_data = edited_df

if st.button("🏆 진스모 중복 제로 정산문구 생성", type="primary"):
    valid_df = edited_df.dropna(subset=["이름"])
    valid_df = valid_df[(valid_df["이름"].str.strip() != "") & (valid_df["이름"] != "None") & (valid_df["금일타수"] > 0)]
    total_players = len(valid_df)
    
    if total_players < 4:
        st.error("진스모 규칙은 최소 4명 이상 입력해야 정확하게 계산됩니다. 인원을 추가해 주세요.")
    elif total_players > 20:
        st.error("최대 20명까지만 지원합니다. 인원을 확인해 주세요.")
    else:
        # [동타 처리 및 우선순위 정렬 규칙 반영] 1순위 타수 오름차순, 2순위 핸디 오름차순
        sorted_df = valid_df.sort_values(by=["금일타수", "G핸디"], ascending=True).reset_index(drop=True)
        
        # 총 스크린 매장비 원금 철저 보장 계산
        total_golf_budget = total_players * 14000
        total_meal_budget = total_players * 6900
        total_overall_budget = total_golf_budget + total_meal_budget
        
        result_text = f"[진스모 새벽모임 최종 정산 안내]\n\n"
        result_text += f"금일 모임(총 {total_players}명) 오리지널 최종 마스터 정산 내역입니다.\n"
        result_text += f"정렬 기준: 금일타수 기준 (동타 시 G핸디가 낮은 사람 우선)\n"
        result_text += f"원칙: 1·2등 국밥 2그릇(13,800원) / 3등 국밥 3그릇 벌칙(20,700원) / 나머지 조원 스크린비 균등 현금 송금\n\n"
        
        result_text += f"💰 [금일 매장 실제 지출 총액]\n"
        result_text += f"  - 스크린골프 총액: {total_golf_budget:,}원 (송금조 현금으로 100% 정액 회수)\n"
        result_text += f"  - 식사(국밥) 총액: {total_meal_budget:,}원 (카드조 결제액으로 100% 정액 처리)\n"
        result_text += f"  👉 모임 전체 합산 총액: {total_overall_budget:,}원\n\n"
        
        result_text += "🏆 최종 성적 및 역할별 분담 금액\n"
        
        golf_pays = * total_players
        meal_pays = * total_players
        
        card_count = min(3, total_players)
        cash_paying_count = total_players - card_count
        
        # 1등, 2등, 3등 포메이션 및 국밥 실비 매칭 수식 고정
        for idx in range(total_players):
            rank = idx + 1
            if rank == 1 or rank == 2:
                golf_pays[idx] = 0
                meal_pays[idx] = 13800  # 1,2등 국밥 2그릇 고정
            elif rank == 3:
                golf_pays[idx] = 0
                meal_pays[idx] = 20700  # 3등 국밥 3그릇 벌칙 고정
            else:
                # 4등부터는 스크린비 전체 원금을 머리수대로 균등 현금 엔빵
                golf_pays[idx] = int(total_golf_budget / cash_paying_count)
                meal_pays[idx] = 0
                
        # 1원 단위 최종 단수 오차 보정 (현금 오차 zero 락킹)
        if cash_paying_count > 0:
            golf_pays[-1] = total_golf_budget - sum(golf_pays[i] for i in range(total_players - 1))
        if card_count > 0:
            # 인원 변동 시 식당 실비 총액에 어긋나지 않도록 3등 카드 결제액 최종 미세 연동 보정
            meal_pays[min(2, total_players-1)] = total_meal_budget - sum(meal_pays[i] for i in range(total_players) if i != min(2, total_players-1))

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
                bowl_str = "2그릇 고정 👑" if rank <= 2 else "3그릇 벌칙 고정 🚨"
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 스크린비 [0원 면제] 🎉 + 국밥 {bowl_str} {m_p:,}원 [식당 카드결제]\n"
            else:
                result_text += f"  - {rank}등: {name} (타수:{score}/핸디:{handi}) ➡️ 총무 계좌로 스크린비 [ {g_p:,}원 ] 송금 💵 (식당 결제 없음 ❌)\n"
            cash_total += g_p
            card_total += m_p
                
        result_text += f"\n📊 [총무 정산 검증 테이블]\n"
        result_text += f"  - 실제 걷히는 현금 총액: {cash_total:,}원 (스크린비 총액 {total_golf_budget:,}원과 오차 0원 완벽 일치!)\n"
        result_text += f"  - 실제 식당 카드 결제 총액: {card_total:,}원 (국밥 대금 {total_meal_budget:,}원과 오차 0원 완벽 일치!)\n"
        result_text += f"  👉 정산 결과: 총무 주머니에 남거나 모자라는 현금은 정확히 [ 0원 ] 입니다.\n"
        result_text += "\n🏦 입금 계좌: 카카오뱅크 3333358864688 박대환"
        result_text += "\n⚠️ 식당 카드결제 조(1,2,3등)분들은 계산대에서 위 금액만큼 각자 카드로 결제해 주시면 오늘 정산은 완전히 종료됩니다."
        
        st.subheader("✨ 자동 정산 결과")
        st.text_area("아래 문구를 전체 복사해서 카톡방에 붙여넣으세요!", value=result_text, height=450)
        st.success("진스모 스크린비 현금 백프로 확보 마스터 정산기가 개설 완료되었습니다!")
