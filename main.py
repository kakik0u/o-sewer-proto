import cohere
import streamlit as st
from dotenv import load_dotenv
import os
load_dotenv()

cohere_api_key = os.environ['cohere_api_key']
cohere_model_id = 'command-a-03-2025'

def generate_ans(hinagata, mail, user_info=None):
    
  prompt = """
雛形にあわせてメールを作成してください。雛形内の必要な情報を以下に提示します。また、このメールが返信のメールであった場合は今までのメールの流れも提示します。メールの流れ上、ひな形と合わない場合はその部分を削除してください。また、今までの流れの中に情報があれば自動で保管してください。\n以下が必ず守るべきルールです。\n・情報を勝手に付け足さないでください。\n・新しく必要な情報がある場合は[]で囲み情報を付け足す必要がある旨を強調してください。・メール本文は"-----"で囲ってください。\n

"""
  if user_info and len(user_info) > 0:
    prompt += "\n<個人情報>:\n"
    for info in user_info:
      prompt += f"{info['title']}: {info['value']}\n"
  
  prompt += f"\n<雛形>:\n{hinagata}\n"
  
  if mail:
    prompt += f"\n今までのメールの流れ:\n{mail}\n"

  print(prompt)
  response = co.chat(model=cohere_model_id, messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ])

  bot_answer = response.message.content[0].text
  print(bot_answer)

  return bot_answer



if "user_info" not in st.session_state:
    st.session_state.user_info = []


common_titles = ["自分の名前", "メールアドレス", "会社名", "部署名", "役職", "電話番号", "署名", "挨拶文"]


st.title("O-sewer Prototype")


st.subheader("自分の情報")


col1, col2 = st.columns(2)
with col1:
    if st.button("情報を追加"):
        st.session_state.user_info.append({"title": "", "value": ""})
        st.experimental_rerun()
with col2:
    if st.button("情報を削除") and st.session_state.user_info:
        st.session_state.user_info.pop()
        st.experimental_rerun()


for i, info in enumerate(st.session_state.user_info):
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            title_type = st.radio(f"追加情報 {i+1}", ["選択肢から選ぶ", "カスタム"], key=f"title_type_{i}")
            
            if title_type == "選択肢から選ぶ":
                title = st.selectbox("タイトル", common_titles, key=f"title_select_{i}")
            else:
                title = st.text_input("カスタムタイトル", value=info["title"], key=f"title_custom_{i}")
                
            st.session_state.user_info[i]["title"] = title
            
        with col2:
            value = st.text_input("値", value=info["value"], key=f"value_{i}")
            st.session_state.user_info[i]["value"] = value


form = st.form(key="user_settings")
with form:
  #cohere_api_key = st.text_input('Cohere API Key:', type='password')
  #cohere_model_id = st.text_input('Cohere Model Id:')

  if not cohere_api_key and not cohere_model_id:
    st.info("有効なCohere APIキーとモデルIDを入力してください")
    update_api_keys = form.form_submit_button("APIキーを登録する")
    st.stop()

  co = cohere.ClientV2(cohere_api_key)

  st.write("雛形をコピペして入力")

  hinagata_input = st.text_area("雛の形", key = "hinagata_input")
  mail_input = st.text_area("今までのメール", key = "mail_input")
    
  generate_button = form.form_submit_button("結果を出力")

  if generate_button:
    if hinagata_input == "":
      st.error("Question field cannot be blank")
    else:
      my_bar = st.progress(0.05)
      st.subheader("結果:")

      for i in range(1):
          ans = generate_ans(hinagata_input, mail_input, st.session_state.user_info)
          st.text(ans)
          my_bar.progress((i+1)/1)

