# Bu kod, Streamlit ile oluşturulmuş bir web arayüzüdür. Amaç: kullanıcıdan gelen mesajları alıp, LLM destekli ajana göndererek yanıtları ekranda göstermek.
from utils import get_session_id
# Streamlit kütüphanesi içe aktarılıyor – web arayüzünü oluşturmak için.
import streamlit as st

# Mesajları yazdırmak için yardımcı fonksiyon (utils.py içinde tanımlı)
from utils import write_message

# Ajan tarafından yanıt üretmek için kullanılan fonksiyon 
from agent import generate_response

# Streamlit sayfa başlığı ve favicon (🎙️ mikrofon ikonu) ayarlanıyor.
st.set_page_config("Ebert", page_icon="🎙️")

# st.write("Session ID:", get_session_id())

# Kullanıcının mesajlarını saklamak için session_state kullanılıyor.
# Eğer mesajlar daha önce başlatılmadıysa, ilk sistem mesajı (karşılama mesajı) ekleniyor.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm the GraphAcademy Chatbot!  How can I help you?"},
    ]


# Kullanıcının girdiği mesajı alır, LLM'e gönderir, yanıtı gösterir.
def handle_submit(message):
    """
    Submit handler:
    Kullanıcıdan gelen mesajı alıp, LLM ajanına göndererek yanıt alır.
    """
    # Yanıt beklenirken bir yükleniyor animasyonu gösterilir.
    with st.spinner('Thinking...'):
        # Ajan çağrılır (Neo4j + vektör arama + tool'lar burada devreye girer)
        response = generate_response(message)

        # Asistanın yanıtı arayüze yazılır ve oturum geçmişine eklenir
        write_message('assistant', response)


# Oturum geçmişindeki tüm mesajlar tek tek ekranda yazdırılır
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)


# Kullanıcıdan chat giriş kutusu ile yeni mesaj alınır
if prompt := st.chat_input("What is up?"):
    # Kullanıcının mesajı ekrana yazdırılır ve geçmişe kaydedilir
    write_message('user', prompt)

    # Mesaj işlenir, ajan çağrılır ve yanıt oluşturulur
    handle_submit(prompt)