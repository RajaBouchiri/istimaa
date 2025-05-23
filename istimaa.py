import streamlit as st
import json
import os
import datetime
import textwrap
import hashlib

# === CONFIGURATION ===
MESSAGE_FILE = "messages.json"
PROF_PASSWORD = "prof123"

# === INITIALISATION DU FICHIER ===
if not os.path.exists(MESSAGE_FILE):
    with open(MESSAGE_FILE, "w") as f:
        json.dump([], f)

# === FONCTIONS ===
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_messages():
    with open(MESSAGE_FILE, "r") as f:
        return json.load(f)

def save_all_messages(messages):
    with open(MESSAGE_FILE, "w") as f:
        json.dump(messages, f, indent=4)

def save_message(message_data):
    messages = load_messages()
    messages.append(message_data)
    save_all_messages(messages)

def reformulate_message(original_message):
    wrapped = textwrap.fill(original_message, width=80)
    return f"رسالة التلميذ معاد صياغتها:\n{wrapped}"

# === INTERFACE STREAMLIT ===
st.set_page_config(page_title="نظام التبليغ عن الصعوبات", layout="centered")
st.title("📚 نظام التبليغ عن الصعوبات ")

role = st.selectbox(":اختر دورك ", ["تلميذ(ة)", "الأستاذ"])

# === INTERFACE ÉLÈVE ===
if role == "تلميذ(ة)":
    st.subheader("✏الاِبلاغ عن صعوبة")
    name = st.text_input("اسمك الكامل ")
    student_pass = st.text_input("رمزك السري (رقم مسار مثلاً)")
    difficulty = st.text_area("صف صعوبتك هنا")

    if st.button("إرسال الصعوبة"):
        if name.strip() == "" or difficulty.strip() == "" or student_pass.strip() == "":
            st.warning("يرجى ملء جميع الخانات. شكرا")
        else:
            message_data = {
                "nom": name.strip(),
                "motdepasse": hash_pass(student_pass.strip()),
                "date": datetime.datetime.now().isoformat(),
                "conversation": [
                    {
                        "role": "student",
                        "content": difficulty.strip(),
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                ]
            }
            save_message(message_data)
            st.success("تم إرسال رسالتك إلى الأستاذ. شكرا!")

    st.markdown("---")
    st.subheader("📬 متابعة المحادثة مع الأستاذ")
    search_name = st.text_input("أدخل اسمك")
    search_pass = st.text_input("أدخل رمزك السري", type="password")
    new_reply = st.text_area("أضف تعقيبًا أو رسالة جديدة", key="student_reply")

    if st.button("عرض المحادثة و/أو إرسال رسالة جديدة"):
        messages = load_messages()
        found = False
        for i, msg in enumerate(messages):
            if (
                msg["nom"].strip().lower() == search_name.strip().lower() and
                msg.get("motdepasse", "") == hash_pass(search_pass.strip())
            ):
                found = True
                date_display = datetime.datetime.fromisoformat(msg["date"]).strftime("%d-%m-%Y %H:%M")
                st.subheader(f"المحادثة مع الأستاذ (منذ {date_display})")
                for entry in msg.get("conversation", []):
                    sender = "أنت" if entry["role"] == "student" else "الأستاذ"
                    st.markdown(f"{sender}:** {entry['content']}")

                if new_reply.strip():
                    msg["conversation"].append({
                        "role": "student",
                        "content": new_reply.strip(),
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    save_all_messages(messages)
                    st.success("تم إرسال تعقيبك بنجاح!")
                break
        if not found:
            st.warning("لم يتم العثور على محادثة بهذا الاسم أو الرمز السري")

# === INTERFACE PROFESSEUR ===
elif role == "الأستاذ":
    st.subheader("تسجيل دخول الأستاذ")
    password = st.text_input("كلمة المرور", type="password")

    if password == PROF_PASSWORD:
        st.success("✅ تم تسجيل الدخول بنجاح")
        st.subheader("📥 الرسائل الواردة من التلاميذ")
        messages = load_messages()

        if not messages:
            st.info("لا توجد رسائل حالياً")
        else:
            for i, msg in enumerate(reversed(messages)):
                index = len(messages) - 1 - i
                date_str = msg.get("date", "تاريخ غير متوفر").split("T")[0]
                with st.expander(f"{msg['nom']} — {date_str}"):
                    for entry in msg.get("conversation", []):
                        sender = "التلميذ(ة)" if entry["role"] == "student" else "الأستاذ"
                        st.markdown(f"{sender}:** {entry['content']}")
                        if entry["role"] == "student":
                            st.info(reformulate_message(entry["content"]))

                    response = st.text_area("اكتب ردك هنا", key=f"response_{index}")
                    if st.button("إرسال الرد", key=f"send_{index}"):
                        if response.strip():
                            msg["conversation"].append({
                                "role": "prof",
                                "content": response.strip(),
                                "timestamp": datetime.datetime.now().isoformat()
                            })
                            save_all_messages(messages)
                            st.success("تم إرسال الرد")
    elif password:
        st.error("❌ كلمة المرور غير صحيحة")