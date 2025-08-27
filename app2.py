import streamlit as st
import random
import time
from supabase import create_client
from fractions import Fraction
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from streamlit_autorefresh import st_autorefresh

# ----------------- Config -----------------
NUM_PUZZLES = 5
MAX_WRONG = 3
GAME_DURATION = 90  # seconds

st.set_page_config(page_title="Unlock the Professor's Safe", page_icon="🧩", layout="centered")

# ----------------- DB Helpers -----------------
@st.cache_resource
def get_db():
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def log_result_once(
    student_name: str,
    puzzles_solved: int,
    wrong_attempts: int,
    finished: int,
    safe_unlocked: int,
    safe_code: str,
    digit_rule: str,
    total_time_seconds: int,
    user_answers: list[str]
):
    if st.session_state.get("result_logged", False):
        return

    supabase = get_db()
    data = {
        "student_name": student_name,
        "puzzles_solved": puzzles_solved,
        "wrong_attempts": wrong_attempts,
        "finished": finished,
        "safe_unlocked": safe_unlocked,
        "safe_code": safe_code,
        "digit_rule": digit_rule,
        "total_time_seconds": total_time_seconds,
        "user_answers": "|".join(user_answers or []),
    }

    try:
        supabase.table("results").insert(data).execute()
        st.session_state.result_logged = True
    except Exception as e:
        st.error(f"❌ Failed to log result: {e}")


# ----------------- Header -----------------
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.image("header_img.png", width=200)
with col2:
    st.markdown(
        "<h2 style='text-align:center; color:#FF5733;'>Unlock the Professor's Safe — v1.2</h2>",
        unsafe_allow_html=True,
    )
with col3:
    st.empty()

# ----------------- Helpers -----------------
def normalize_answer(ans):
    if isinstance(ans, float) and ans.is_integer():
        return str(int(ans))
    return str(ans)

def check_answer(user_input, correct_answer):
    try:
        return float(user_input) == float(correct_answer)
    except Exception:
        return user_input.strip() == str(correct_answer)

# Puzzle generators
def gen_arithmetic():
    a, b = random.randint(2, 60), random.randint(2, 60)
    op = random.choice(["+", "-", "*"])
    if op == "+":
        return f"{a} + {b} = ?", a + b
    if op == "-":
        return f"{max(a,b)} - {min(a,b)} = ?", abs(a - b)
    a, b = random.randint(2, 12), random.randint(2, 12)
    return f"{a} × {b} = ?", a * b

def gen_linear():
    x = random.randint(0, 20)
    a, b = random.randint(1, 9), random.randint(0, 20)
    c = a * x + b
    return f"Solve for x: {a}x + {b} = {c}", x

def gen_date_puzzle():
    start_date = datetime(2023, random.randint(1, 12), random.randint(1, 28))
    if random.choice([True, False]):
        elapsed_days = random.randint(5, 60)
        finish_date = start_date + timedelta(days=elapsed_days)
        question = (
            f"Start Date: {start_date.strftime('%d-%b-%Y')}, Elapsed Time: {elapsed_days} days. "
            f"Find the Finish Date (format: DDMMYYYY)."
        )
    else:
        elapsed_months = random.randint(1, 6)
        elapsed_days = random.randint(0, 20)
        finish_date = start_date + relativedelta(months=elapsed_months, days=elapsed_days)
        question = (
            f"Start Date: {start_date.strftime('%d-%b-%Y')}, Elapsed Time: {elapsed_months} months {elapsed_days} days. "
            f"Find the Finish Date (format: DDMMYYYY)."
        )
    return question, finish_date.strftime("%d%m%Y")

def gen_triangle_area():
    base, height = random.randint(4, 40), random.randint(2, 30)
    if (base * height) % 2:
        height += 1
    area = (base * height) / 2
    return f"Triangle base={base}, height={height}. Area of Triangle= ?", area

def gen_percentage():
    base = random.choice([50, 75, 100, 120, 200, 1960, 2500, 4000])
    p = random.choice([10, 15, 20, 25, 30, 35, 40, 50])
    return f"What is {p}% of {base}?", base * p / 100

def gen_probability():
    balls = random.choice([(2, 3), (3, 5), (4, 6)])
    total = balls[0] + balls[1]
    colour = random.choice(["red", "blue"])
    if colour == "red":
        prob = Fraction(balls[0], total)
        return (
            f"A bag has {balls[0]} red and {balls[1]} blue balls. "
            f"Probability of drawing red = ? (Hint: Answer in fraction)"
        ), str(prob)
    else:
        prob = Fraction(balls[1], total)
        return (
            f"A bag has {balls[0]} red and {balls[1]} blue balls. "
            f"Probability of drawing blue = ? (Hint: Answer in fraction)"
        ), str(prob)

def gen_pythagoras():
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    a, b, c = random.choice(triples)
    if random.choice([True, False]):
        return f"Right triangle legs = {a} and {b}. Hypotenuse = ?", c
    else:
        if random.choice([True, False]):
            return f"Hypotenuse = {c}, one leg = {a}. Other leg = ?", b
        else:
            return f"Hypotenuse = {c}, one leg = {b}. Other leg = ?", a

def gen_distance():
    deltas = [(3, 4), (5, 12), (6, 8), (8, 15), (7, 24)]
    dx, dy = random.choice(deltas)
    x1 = random.randint(-10, 10)
    y1 = random.randint(-10, 10)
    x2 = x1 + random.choice([dx, -dx])
    y2 = y1 + random.choice([dy, -dy])
    dist = int((dx * dx + dy * dy) ** 0.5)
    return f"Distance between ({x1},{y1}) and ({x2},{y2}) = ?", dist

def gen_basic():
    qas = [
        ("Find the HCF of 360 and 961", 1),
        ("What is the sum of all angles in a pentagon?", 540),
        ("If radius of circle is 7 units, What will be its area? (Answer the multiple of π)", 49),
        ("What is the largest 3-digit perfect square number?", 961),
        ("If the probability of an event is 0.24, what is the probability of its complement?", 0.76),
        ("The perimeter of a square is 64 cm. What is the area of the square?", 256),
        ("What is the value of π (up to 3 decimal places)?", 3.142),
        ("How many months have 30 days?", 4),
        ("If a set has 3 elements, how many proper subsets does it have", 7),
        ("What is 90 divided by half?", 180),
    ]
    return random.choice(qas)

def gen_riddle():
    qas = [
        ("I am an odd number. Take away one letter and I become even. What number am I?", 7),
        ("If you multiply me by any other number, the answer will always remain the same. Who am I?", 0),
        ("I am a number. Double me and add 10, the result is 30. Who am I?", 10),
        ("What number do you get when you multiply all the numbers on a telephone’s keypad?", 0),
    ]
    return random.choice(qas)

GENERATORS = [
    gen_basic,
    gen_linear,
    gen_triangle_area,
    gen_percentage,
    gen_probability,
    gen_pythagoras,
    gen_distance,
    gen_basic,
    gen_riddle,
    gen_date_puzzle,
]

# ----------------- Session State -----------------
if "started" not in st.session_state:
    st.session_state.started = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "digit_rule" not in st.session_state:
    st.session_state.digit_rule = random.choice(["first", "last"])
if "puzzles" not in st.session_state:
    st.session_state.puzzles = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "wrong" not in st.session_state:
    st.session_state.wrong = 0
if "finished" not in st.session_state:
    st.session_state.finished = False
if "safe_code" not in st.session_state:
    st.session_state.safe_code = ""
if "safe_unlocked" not in st.session_state:
    st.session_state.safe_unlocked = False
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "result_logged" not in st.session_state:
    st.session_state.result_logged = False

# ----------------- Start Screen -----------------
if not st.session_state.started:
    st.subheader("🎭 Can you unlock the safe before time runs out?")

    st.session_state.student_name = st.text_input(
        "Enter your Name to start:", value=st.session_state.student_name
    ).strip()

    st.info(
        f"""
        **Game Rules:**
        - You have **{GAME_DURATION} seconds** to solve the puzzles and unlock the safe.
        - You can make up to **{MAX_WRONG} wrong attempts** before the police arrive.
        - Keep track of *your own answers* — you will need them at the end!
        """
    )
    disabled = len(st.session_state.student_name) == 0
    if st.button("▶ Start Game", disabled=disabled):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.puzzles = []
        st.session_state.answers = []
        st.session_state.user_answers = []
        st.session_state.current_idx = 0
        st.session_state.wrong = 0
        st.session_state.finished = False
        st.session_state.safe_code = ""
        st.session_state.safe_unlocked = False
        st.session_state.result_logged = False

        for g in random.sample(GENERATORS, NUM_PUZZLES):
            q, a = g()
            st.session_state.puzzles.append(q)
            st.session_state.answers.append(normalize_answer(a))
        st.rerun()

# ----------------- Gameplay -----------------
else:
    if st.session_state.start_time is None:
        remaining = 0
        elapsed_total = 0
    elif st.session_state.safe_unlocked:   # ✅ NEW CONDITION: freeze timer if safe is open
        remaining = 0
        elapsed_total = int(time.time() - st.session_state.start_time)
    else:
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, GAME_DURATION - int(elapsed))
        elapsed_total = int(elapsed)


    if remaining <= 0 and not st.session_state.finished:
        st.session_state.finished = True
        st.session_state.start_time = None
        st.error("⏰ Time's up! The police arrived before you cracked the safe.")

    if not st.session_state.safe_unlocked and not st.session_state.finished:
        st_autorefresh(interval=1000, key="timer")

    # Display metrics (removed digit rule here)
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Time Left", f"{remaining}s")
    with m2:
        st.metric("Wrong Attempts", f"{st.session_state.wrong}/{MAX_WRONG}")

    st.progress(st.session_state.current_idx / NUM_PUZZLES)

    if remaining > 0 and (not st.session_state.finished) and (st.session_state.current_idx < NUM_PUZZLES):
        q = st.session_state.puzzles[st.session_state.current_idx]
        st.markdown(
            f"<h3 style='color:blue;'>Puzzle {st.session_state.current_idx+1}/{NUM_PUZZLES}</h3>",
            unsafe_allow_html=True,
        )
        st.write(q)

        key_input = f"user_ans_{st.session_state.current_idx}"
        if key_input not in st.session_state:
            st.session_state[key_input] = ""

        with st.form(key=f"form{st.session_state.current_idx}", clear_on_submit=False):
            ans = st.text_input("Enter your answer", key=key_input)
            submitted = st.form_submit_button("Submit")
            if submitted:
                user = ans.strip()
                correct = st.session_state.answers[st.session_state.current_idx]

                if check_answer(user, correct):
                    st.success("✅ Correct!")
                    st.session_state.user_answers.append(user)

                    st.session_state.current_idx += 1
                    if st.session_state.current_idx == NUM_PUZZLES:
                        st.session_state.finished = True
                    st.rerun()
                else:
                    st.session_state.wrong += 1
                    if st.session_state.wrong >= MAX_WRONG:
                        st.error(f"Game Over! You reached {MAX_WRONG} wrong attempts.")
                        st.session_state.finished = True
                        st.session_state.start_time = None
                    else:
                        st.warning(
                            f"❌ Wrong answer! You have {MAX_WRONG - st.session_state.wrong} attempts left."
                        )
                    st.rerun()

    if st.session_state.finished:
        can_enter_code = (st.session_state.current_idx == NUM_PUZZLES) and (remaining > 0)

        if can_enter_code and not st.session_state.safe_code:
            digits = []
            for a in st.session_state.user_answers:
                s = str(a)
                digits.append(s[0] if st.session_state.digit_rule == "first" else s[-1])
            st.session_state.safe_code = "".join(digits)

        if can_enter_code:
            st.success(
                "🎉 All puzzles solved! To unlock the safe, enter the secret code built from the "
                f"**{st.session_state.digit_rule} digit of each answer you wrote**, in order."
            )
            code = st.text_input("🔑 Enter Safe Code", type="password")

            if st.button("🔓 Unlock Safe") or st.session_state.safe_unlocked:
                if code == st.session_state.safe_code or st.session_state.safe_unlocked:
                    st.session_state.safe_unlocked = True
                    st.balloons()
                    st.success("🎉 YOU WIN! Safe unlocked successfully.")
                    log_result_once(
                        student_name=st.session_state.student_name,
                        puzzles_solved=NUM_PUZZLES,
                        wrong_attempts=st.session_state.wrong,
                        finished=1,
                        safe_unlocked=1,
                        safe_code=st.session_state.safe_code,
                        digit_rule=st.session_state.digit_rule,
                        total_time_seconds=elapsed_total,
                        user_answers=st.session_state.user_answers,
                    )
                else:
                    st.error("❌ Wrong Code! Safe remains locked.")
        else:
            st.error("💀 Mission Failed! Time's up or you didn't solve all puzzles.")
            if st.session_state.user_answers:
                st.info(
                    "You can review what you wrote: "
                    + ", ".join([str(u) for u in st.session_state.user_answers])
                )
            log_result_once(
                student_name=st.session_state.student_name or "Unknown",
                puzzles_solved=st.session_state.current_idx,
                wrong_attempts=st.session_state.wrong,
                finished=1,
                safe_unlocked=0,
                safe_code=st.session_state.safe_code,
                digit_rule=st.session_state.digit_rule,
                total_time_seconds=elapsed_total,
                user_answers=st.session_state.user_answers,
            )
