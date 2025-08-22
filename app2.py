import streamlit as st
import random
import time

# Constants
NUM_PUZZLES = 3
MAX_WRONG = 3
GAME_DURATION = 90  # seconds

# ----------------- Header Section -----------------
col1, col2, col3 = st.columns([1,2,1])
with col1:
    # Header image
    st.image("header_img.png", width=200)  
with col2:
    # Game title
    st.markdown("<h2 style='text-align:center; color:#FF5733;'>Unlock the Professor's Safe- v1.0</h12", 
    unsafe_allow_html=True)

with col3:
    # You can leave this blank or add another image if needed
    st.empty()
# ----------------- Puzzle Generators -----------------
def gen_arithmetic():
    a, b = random.randint(2, 60), random.randint(2, 60)
    op = random.choice(['+','-','*'])
    if op == '+': return f"{a} + {b} = ?", a + b
    if op == '-': return f"{max(a,b)} - {min(a,b)} = ?", abs(a-b)
    a, b = random.randint(2, 12), random.randint(2, 12)
    return f"{a} × {b} = ?", a * b

def gen_linear():
    x = random.randint(0, 20)
    a, b = random.randint(1, 9), random.randint(0, 20)
    c = a*x + b
    return f"Solve for x: {a}x + {b} = {c}", x

def gen_triangle_area():
    base, height = random.randint(4, 40), random.randint(2, 30)
    if (base * height) % 2: height += 1
    area = (base * height) // 2
    return f"Triangle base={base}, height={height}. Area of Triangle= ?", area

def gen_percentage():
    base = random.choice([50,75,100,120,200,1960,2500,4000])
    p = random.choice([10,15,20,25,30,35,40,50])
    return f"What is {p}% of {base}?", base * p // 100

def gen_probability():
    balls = random.choice([(2,3),(3,5),(4,6)])
    total = balls[0] + balls[1]
    colour = random.choice(["red","blue"])
    if colour == "red":
        prob = f"{balls[0]}/{total}"
        return f"A bag has {balls[0]} red and {balls[1]} blue balls. Probability of drawing red = ? (Hint: Answer in fraction)", prob
    else:
        prob = f"{balls[1]}/{total}"
        return f"A bag has {balls[0]} red and {balls[1]} blue balls. Probability of drawing blue = ? (Hint: Answer in fraction)", prob

def gen_pythagoras():
    triples = [(3,4,5),(5,12,13),(8,15,17),(7,24,25)]
    a,b,c = random.choice(triples)
    if random.choice([True, False]):
        return f"Right triangle legs = {a} and {b}. Hypotenuse = ?", c
    else:
        # give hyp and one leg, ask missing leg
        if random.choice([True, False]):
            return f"Hypotenuse = {c}, one leg = {a}. Other leg = ?", b
        else:
            return f"Hypotenuse = {c}, one leg = {b}. Other leg = ?", a

def gen_distance():
    # make integer distances using common Pythagorean deltas
    deltas = [(3,4),(5,12),(6,8),(8,15),(7,24)]
    dx,dy = random.choice(deltas)
    x1 = random.randint(-10,10); y1 = random.randint(-10,10)
    x2 = x1 + random.choice([dx, -dx]); y2 = y1 + random.choice([dy, -dy])
    dist = int((dx*dx + dy*dy)**0.5)
    return f"Distance between ({x1},{y1}) and ({x2},{y2}) = ?", dist

def gen_basic():
    qas = [
        ("Find the HCF of 36 and 60", "12"),
        ("What is the sum of angles in a triangle?", "180"),
        ("If radius of circle is 7 units, What will be its area? (Answer the multiple of π)", "49"),
        ("What is the largest 3-digit perfect square number?", "961"),
        ("If the probability of an event is 0.24, what is the probability of its complement?", "0.76"),
        ("The perimeter of a square is 64 cm. What is the area of the square?", "256"),
        ("What is the next prime number after 31?", "37"),
        ("What is 15% of 200?", "30"),
        ("What is the square root of 484?", "22"),
        ("What is the value of π (up to 3 decimal places)?", "3.142" ),
        ("How many months have 30 days?", "4"),
        ("If a set has 3 elements, how many proper subsets does it have","7"),
        ("What is the only even prime number?", "2"),
        ("What is 90 divided by half?", "180")
    ]
    return random.choice(qas)

def gen_riddle():
    qas = [
        ("I am an odd number. Take away one letter and I become even. What number am I? (Hint: Answer in numeric only)", "7"),
        ("If you multiply me by any other number, the answer will always remain the same. Who am I?", "0"),
        ("I am a number. Double me and add 10, the result is 30. Who am I?", "10"),
        ("What number do you get when you multiply all the numbers on a telephone’s keypad?", "0"),
    ]
    return random.choice(qas)

GENERATORS = [
    gen_arithmetic, gen_linear, gen_triangle_area, gen_percentage, gen_probability, 
    gen_pythagoras, gen_distance, gen_basic, gen_riddle
]

from streamlit_autorefresh import st_autorefresh

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

# ----------------- Start Screen -----------------
if not st.session_state.started:
    st.subheader("🎭Can you unlock the safe before time runs out?")
    st.info(f"""
        **Game Rules:**
        - You have **{GAME_DURATION} seconds** to solve the puzzles and unlock the safe.
        - You can make up to **{MAX_WRONG} wrong attempts** before the police arrive.
        - Collect the **first or last digit** of each correct answer (as per the prompt below) to form the secret safe code.
        - Solve all puzzles to get the secret code digits.
        - Enter the correct **safe code** at the end to unlock the safe and win.
        - Each puzzle may have a **hint** to help you solve it.
        - Be careful! A wrong code entry at the safe will not unlock it.
        - Work quickly and accurately to escape before time runs out!
        """)
    st.warning(f"Collect the **{st.session_state.digit_rule} digit** of each correct answer to form the code.")
    
    if st.button("▶ Start Game"):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.puzzles = []
        st.session_state.answers = []
        st.session_state.current_idx = 0
        st.session_state.wrong = 0
        st.session_state.finished = False
        st.session_state.safe_code = ""
        # Generate puzzles
        for g in random.sample(GENERATORS, NUM_PUZZLES):
            q, a = g()
            st.session_state.puzzles.append(q)
            st.session_state.answers.append(a)
        st.rerun()

# ----------------- Gameplay -----------------
else:
    # Auto-refresh for timer
    st_autorefresh(interval=1000, key="timer")

    elapsed = time.time() - st.session_state.start_time
    remaining = GAME_DURATION - int(elapsed)

    # Timer and metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏳ Time Left", f"{remaining}s")
    with col2:
        st.metric("❌ Wrong Attempts", f"{st.session_state.wrong}/{MAX_WRONG}")
    with col3:
        st.metric("🔑 Rule", f"{st.session_state.digit_rule} digit")

    st.progress(st.session_state.current_idx / NUM_PUZZLES)

    # Time up
    if remaining <= 0:
        st.error("⏰ Time's up! The police arrived before you cracked the safe.")
        st.session_state.finished = True

    # Gameplay puzzles
    if not st.session_state.finished and st.session_state.current_idx < NUM_PUZZLES:
        q = st.session_state.puzzles[st.session_state.current_idx]
        st.markdown(f"<h3 style='color:blue;'>Puzzle {st.session_state.current_idx+1}/{NUM_PUZZLES}</h3>", unsafe_allow_html=True)
        st.write(q)
        
        # Preserve input across reruns
        key_input = f"user_ans_{st.session_state.current_idx}"
        if key_input not in st.session_state:
            st.session_state[key_input] = ""
        ans = st.text_input("✍ Enter your answer", key=key_input)

        if st.button("✅ Submit", key=f"btn{st.session_state.current_idx}"):
            user = ans.strip()
            correct = str(st.session_state.answers[st.session_state.current_idx])

            if user == correct:
                st.success("✅ Correct!")
                st.session_state.current_idx += 1
                if st.session_state.current_idx == NUM_PUZZLES:
                    st.session_state.finished = True
                st.rerun()
            else:
                st.session_state.wrong += 1

                if st.session_state.wrong >= MAX_WRONG:
                    # 3 wrong attempts reached → Game Over
                    st.error(f"❌ Game Over! You reached {MAX_WRONG} wrong attempts.")
                    st.session_state.finished = True  # Stop the game
                    st.session_state.start_time = time.time() - GAME_DURATION  # Stop timer
                else:
                    # Warn player about remaining attempts
                    st.warning(f"❌ Wrong answer! You have {MAX_WRONG - st.session_state.wrong} attempts left.")

                st.rerun()


    # ----------------- Final Safe Unlock -----------------
    if st.session_state.finished:
        # Generate safe code only if puzzles are solved
        if st.session_state.current_idx == NUM_PUZZLES:
            if not st.session_state.safe_code:
                digits = []
                for a in st.session_state.answers:
                    s = str(a)
                    digits.append(s[0] if st.session_state.digit_rule == "first" else s[-1])
                st.session_state.safe_code = "".join(digits)

            st.success("🎉 All puzzles solved! Enter the secret safe code to unlock the safe:")

            # Safe code input
            code = st.text_input("🔑 Enter Safe Code", type="password")

            if st.button("🔓 Unlock Safe") or st.session_state.safe_unlocked:
                if code == st.session_state.safe_code or st.session_state.safe_unlocked:
                    st.session_state.safe_unlocked = True
                    st.balloons()
                    st.success("🎉 YOU WIN! Safe unlocked successfully.")
                else:
                    st.error("❌ Wrong Code! Safe remains locked.")

        # Game Over due to wrong attempts or time up
        else:
            st.error("💀 Mission Failed! Better luck next time.")
            
    # ----------------- Replay Button -----------------
    if st.session_state.finished:
        if st.button("🔄 Replay Game"):
            st.session_state.started = False
            st.session_state.start_time = None
            st.session_state.digit_rule = random.choice(["first", "last"])
            st.session_state.puzzles = []
            st.session_state.answers = []
            st.session_state.current_idx = 0
            st.session_state.wrong = 0
            st.session_state.finished = False
            st.session_state.safe_code = ""
            st.session_state.safe_unlocked = False
            st.rerun()

