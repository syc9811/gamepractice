import streamlit as st
import openai
import random
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화 (최신 API 방식)
client = openai.Client(api_key=OPENAI_API_KEY)

# Streamlit 페이지 설정
st.set_page_config(page_title="역사적 인물 맞추기 스무고개", layout="centered")
st.title("🕵️‍♂️ 역사적 인물 맞추기 스무고개")

# 선택 가능한 역사적 인물 리스트
historical_figures = [
    "나폴레옹", "아인슈타인", "레오나르도 다빈치", "링컨", "마리 퀴리",
    "간디", "처칠", "조지 워싱턴", "세종대왕", "이순신", "알렉산더 대왕",
    "갈릴레오 갈릴레이", "율리우스 카이사르", "클레오파트라","이순신","에디슨","셰익스피어","공자"
]

# AI가 랜덤으로 인물 선택 (세션 초기화)
if "target_figure" not in st.session_state:
    st.session_state.target_figure = random.choice(historical_figures)
    st.session_state.questions = []
    st.session_state.hints_given = 0
    st.session_state.game_over = False

# 게임 진행 상태 출력
st.subheader("20번 안에 인물을 맞혀보세요!")

# 사용자의 질문 입력
question = st.text_input("질문을 입력하세요 (예/아니오로 답할 수 있는 질문)")

# OpenAI GPT API를 이용해 질문 분석 및 응답
def ask_gpt(question, target_figure):
    prompt = f"""
    너는 역사 전문가야. 사용자가 특정 인물({target_figure})을 맞추려고 해.
    사용자가 하는 질문에 대해 '예', '아니오', 또는 '잘 모르겠다' 중 하나로만 대답해.

    예시 질문과 답변:
    Q: 이 인물은 미국인인가요?  
    A: 예  
    Q: 이 인물은 물리학자인가요?  
    A: 아니오  
    Q: 이 인물은 20세기에 살았나요?  
    A: 예  

    이제 사용자의 질문에 대답해:
    Q: {question}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 역사적 인물 전문가야."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=20
    )
    return response.choices[0].message.content.strip()

# 질문 제출 처리
if st.button("질문하기") and question:
    if st.session_state.game_over:
        st.warning("게임이 이미 종료되었습니다. 새로고침하여 다시 시작하세요!")
    else:
        response = ask_gpt(question, st.session_state.target_figure)
        st.session_state.questions.append((question, response))

# 질문 목록 출력
if st.session_state.questions:
    st.subheader("질문 기록")
    for i, (q, a) in enumerate(st.session_state.questions, start=1):
        st.write(f"**{i}. {q}** → {a}")

# 힌트 기능 (5번째, 10번째 질문 시 제공)
if len(st.session_state.questions) in [5, 10] and st.session_state.hints_given < 2:
    hint_prompt = f"""
    {st.session_state.target_figure}에 대한 힌트를 하나 제공해줘.
    예시: 이 인물은 프랑스 출신입니다.
    """
    hint_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 역사적 인물 전문가야."},
            {"role": "user", "content": hint_prompt}
        ],
        max_tokens=50
    )
    
    st.session_state.hints_given += 1
    st.success(f"🔍 힌트: {hint_response.choices[0].message.content.strip()}")

# 정답 입력 기능
st.subheader("정답을 맞혀보세요!")
answer_guess = st.text_input("이 인물의 이름을 입력하세요")

if st.button("정답 확인") and answer_guess:
    if st.session_state.game_over:
        st.warning("게임이 이미 종료되었습니다. 새로고침하여 다시 시작하세요!")
    else:
        if answer_guess.strip() == st.session_state.target_figure:
            st.success(f"🎉 정답입니다! {st.session_state.target_figure}을(를) 맞추셨습니다!")
            st.session_state.game_over = True
        else:
            st.error("❌ 틀렸습니다! 다시 시도해보세요.")

# 질문 20개 초과 시 게임 종료
if len(st.session_state.questions) >= 20:
    st.session_state.game_over = True
    st.error(f"💀 20번의 질문을 모두 사용했습니다! 정답은 **{st.session_state.target_figure}** 입니다.")

