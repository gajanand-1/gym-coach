import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, metric_card, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.services.auth_service import AuthService
from app.services.macro_calculator import MacroCalculator
from app.utils.helpers import goal_label, activity_label

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

user = get_current_user()
if not user:
    st.error("User not found.")
    st.stop()

st.markdown("## 👤 Your Profile")
st.markdown("Update your details below — macros recalculate automatically.")
st.divider()

# ── Current Macro Summary ────────────────────────────────────────────────
if user.target_calories:
    st.markdown(section_header("🎯 Current Targets"), unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(metric_card("BMR",      f"{user.bmr:.0f}",   "kcal/day"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("TDEE",     f"{user.tdee:.0f}",  "kcal/day"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("Calories", f"{user.target_calories:.0f}", "kcal/day"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("Protein",  f"{user.protein_target_g:.0f}g", "per day"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card("Water",    f"{user.water_target_liters:.1f}L", "per day"), unsafe_allow_html=True)
    st.divider()

# ── Profile Form ─────────────────────────────────────────────────────────
st.markdown(section_header("✏️ Edit Profile"), unsafe_allow_html=True)

with st.form("profile_form"):
    col1, col2 = st.columns(2)

    with col1:
        name     = st.text_input("Full Name",   value=user.name or "")
        age      = st.number_input("Age",        value=user.age,    min_value=13, max_value=80)
        gender   = st.selectbox("Gender",        ["male", "female"],
                                index=0 if user.gender == "male" else 1)
        height   = st.number_input("Height (cm)", value=float(user.height_cm),
                                    min_value=100.0, max_value=250.0, step=0.5)
        weight   = st.number_input("Current Weight (kg)", value=float(user.weight_kg),
                                    min_value=30.0, max_value=300.0, step=0.1)
        t_weight = st.number_input("Target Weight (kg)",  value=float(user.target_weight_kg),
                                    min_value=30.0, max_value=300.0, step=0.1)

    with col2:
        goal = st.selectbox("Goal", ["fat_loss", "muscle_gain", "maintenance"],
                             index=["fat_loss", "muscle_gain", "maintenance"].index(user.goal))
        activity = st.selectbox(
            "Activity Level",
            ["sedentary", "light", "moderate", "active", "very_active"],
            index=["sedentary", "light", "moderate", "active", "very_active"].index(user.activity_level),
            format_func=activity_label,
        )
        experience = st.selectbox(
            "Gym Experience",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(user.gym_experience),
        )
        split = st.selectbox(
            "Workout Split",
            ["push_pull_legs", "upper_lower", "full_body"],
            index=["push_pull_legs", "upper_lower", "full_body"].index(user.workout_split),
            format_func=lambda x: x.replace("_", " ").title(),
        )
        sleep_hrs = st.number_input("Average Sleep (hours)", value=float(user.sleep_hours),
                                     min_value=3.0, max_value=12.0, step=0.5)
        allergies_raw = st.text_input("Allergies (comma-separated)",
                                       value=", ".join(user.allergies or []))

    submitted = st.form_submit_button("💾 Save & Recalculate Macros", use_container_width=True)

if submitted:
    allergies = [a.strip() for a in allergies_raw.split(",") if a.strip()]
    db = SessionLocal()
    auth_svc = AuthService(db)
    updated = auth_svc.save_profile_and_recalculate(
        user_id,
        name=name, age=age, gender=gender,
        height_cm=height, weight_kg=weight, target_weight_kg=t_weight,
        goal=goal, activity_level=activity,
        gym_experience=experience, workout_split=split,
        sleep_hours=sleep_hrs, allergies=allergies,
    )
    db.close()
    if updated:
        result = MacroCalculator.calculate_targets(weight, height, age, gender, activity, goal)
        st.success("✅ Profile saved! Macros recalculated.")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("BMR",      f"{result.bmr:.0f} kcal")
        with c2: st.metric("TDEE",     f"{result.tdee:.0f} kcal")
        with c3: st.metric("Target Cal", f"{result.target_calories:.0f} kcal")
        with c4: st.metric("Protein",  f"{result.protein_g:.0f}g/day")
        st.rerun()
    else:
        st.error("Failed to save profile.")

# ── Change Password ──────────────────────────────────────────────────────
st.divider()
st.markdown(section_header("🔒 Change Password"), unsafe_allow_html=True)

with st.form("password_form"):
    new_pw  = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    pw_submit = st.form_submit_button("Update Password")

if pw_submit:
    if new_pw != confirm:
        st.error("Passwords do not match.")
    elif len(new_pw) < 6:
        st.error("Password must be at least 6 characters.")
    else:
        from app.storage.user_store import UserStore
        db = SessionLocal()
        store = UserStore(db)
        store.update_profile(user_id, hashed_password=UserStore.hash_password(new_pw))
        db.close()
        st.success("Password updated!")
