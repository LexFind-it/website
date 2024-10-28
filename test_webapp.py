import streamlit as st
import requests
import uuid  # Libreria per generare un UUID unico
import time

from google.cloud import bigquery
import pandas as pd


################################################################################
#                                BigQuery Setup                                #
################################################################################

# Load the JSON key from Streamlit secrets and set up credentials
service_account_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
client = bigquery.Client.from_service_account_info(service_account_info)

BIG_QUERY_TABLE = "taxfinder-mvp.sources_metadata.documents_agenzia_entrate"


################################################################################
#                              Support Functions                               #
################################################################################

# Function to make API request
def get_bot_response(question, session_id):
    url = "https://chat-api-1087014169033.europe-west1.run.app/ask"
    headers = {"Content-Type": "application/json"}
    data = {
        "question": question,
        "session_id": session_id
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Generator to simulate streaming
def simulate_stream(response):
    """Simulates a text stream by yielding small chunks of the response."""
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

# Function to retrieve documents metadata from BigQuery
def get_source_metadata(filename):

    transformed_filename = filename.replace("_", "/").replace(".pdf", "")

    query = f"""
    SELECT url, original_summary
    FROM {BIG_QUERY_TABLE}
    WHERE title = '{transformed_filename}'
    """  # filename is now correctly enclosed in single quotes
    query_job = client.query(query)
    results = query_job.result()
    for row in results:
        return {"url": row.url, "summary": row.original_summary}
    return {"url": "#", "summary": "Non disponibile"}


################################################################################
#                                 Chatbot Core                                 #
################################################################################

# Initialize session state for the conversation and feedback
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'feedback_given' not in st.session_state:
    st.session_state['feedback_given'] = False
if 'feedback_text' not in st.session_state:
    st.session_state['feedback_text'] = ""
if 'input_key' not in st.session_state:
    st.session_state['input_key'] = str(uuid.uuid4())  # Use a unique key for each session

# Show title, claim, and description.
st.title("Lex Find it")
st.subheader("Riduci i tempi di ricerca grazie all'Intelligenza Artificiale")
st.markdown("""
Ti diamo il benvenuto sul _prototipo_ del nostro Assistente AI sul ***Diritto Tributario***.
Il chatbot è in grado di basare le proprie risposte sulle *Circolari*, sui *Provvedimenti*, sulle *Risoluzioni*, e sulle
*Risposte* del ministero per gli anni 2023 e 2024.

***Nota**: Questo bot va inteso come un prototipo, pertanto ti invitiamo a verificare la correttezza delle risposte.*

""")

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("Scrivi un messaggio a LexFind.it"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show a loading spinner while waiting for bot response
    with st.spinner("Ricerca delle fonti per il tuo caso in corso..."):
        try:
            # Call the chatbot API to get the response
            result = get_bot_response(prompt, st.session_state.session_id)
            answer = result['answer']
            sources = result['sources']

        except Exception as e:
            st.error(f"Ci dispiace, qualcosa non ha funzionato: {e}")



    # Use st.write_stream with the simulated stream to display the response
    with st.chat_message("assistant"):
        st.write_stream(simulate_stream(answer))  # Pass the generator directly to st.write_stream

        # If the answer is not "I don't know.", include sources as clickable links
        if answer.lower() != "i don't know.":
            # Remove duplicate sources
            filenames = list(set(sources))

            if filenames:

                st.write("\n\n**Fonti:**\n\n")

                # Costruiamo la lista dei dati con i link HTML per la colonna "Titolo"
                data = []
                for filename in filenames:
                    metadata = get_source_metadata(filename)
                    link = f'<a href="{metadata["url"]}" target="_blank">{filename}</a>'
                    data.append({"Titolo": link, "Descrizione": metadata["summary"]})

                # Creiamo il DataFrame
                df = pd.DataFrame(data)

                # Mostriamo la tabella in Streamlit con i link HTML abilitati
                st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)


    st.session_state.messages.append({"role": "assistant", "content": answer})


################################################################################
#                            Sidebar for Feedback                              #
################################################################################

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from_email = st.secrets['EMAIL_USER']
email_password = st.secrets['EMAIL_PASS']

# Function to send feedback email
def send_email(feedback, conversation):
    to_email = "work.paolopiacenti@gmail.com"
    subject = "RAG Feedback - Tax bot"

    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    # Construct the email body
    email_body = f"User Feedback:\n{feedback}\n\nConversation History:\n{conversation}"
    message.attach(MIMEText(email_body, "plain"))

    try:
        # Sending the mail using Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, email_password)  # Use the app password loaded from env variable
        text = message.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        st.success("Il tuo feedback è stato inviato. Grazie!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")




with st.sidebar:
    st.subheader("La tua opinione conta")

    # Show feedback input if feedback not already given
    if not st.session_state['feedback_given']:
        st.session_state['feedback_text'] = st.text_area("Condividi qui le tue considerazione o idee di miglioramento per questo strumento.", value=st.session_state['feedback_text'])

        # Submit feedback button
        if st.button("Invia Feedback", key="feedback_button"):
            if st.session_state['feedback_text']:
                # Construct the conversation history as a string
                conversation = "\n".join([f"{msg['type'].capitalize()}: {msg['content']}" for msg in st.session_state['history']])

                # Send the email with the feedback and conversation
                send_email(st.session_state['feedback_text'], conversation)

                # Mark feedback as given
                st.session_state['feedback_given'] = True
            else:
                st.warning("Per favore, scrivi qualcosa prima di inviare un messaggio.")
    else:
        st.info("Il tuo feedback è stato già inviato. Grazie!")
