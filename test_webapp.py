import streamlit as st
import requests
import uuid  # Libreria per generare un UUID unico
import time

import pandas as pd

################################################################################
#                           Page Configuration and Favicon                     #
################################################################################


# Set up the favicon and page title
st.set_page_config(
    page_title="TaxFinder",
    page_icon="https://em-content.zobj.net/source/apple/391/balance-scale_2696-fe0f.png",  # Ensure favicon.ico is in the root directory
    layout="wide"  # Adjust layout as needed
)


################################################################################
#                                Custom CSS                                    #
################################################################################

# CSS to hide all "Share" buttons and toolbar action buttons
hide_buttons_css = """
    <style>
    /* Hide share and tool buttons */
    [data-testid="stBaseButton-header"], [data-testid="stToolbarActionButton"] {
        display: none;
    }

    div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    div[data-testid="stDecoration"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    div[data-testid="stStatusWidget"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    #MainMenu {
    visibility: hidden;
    height: 0%;
    }
    header {
    visibility: hidden;
    height: 0%;
    }
    footer {
    visibility: hidden;
    height: 0%;
    }
    </style>
"""

# Applying the CSS
st.markdown(hide_buttons_css, unsafe_allow_html=True)


################################################################################
#                              Support Functions                               #
################################################################################

# Function to make API request
def get_bot_response(question, session_id):
    url = "https://chat-api-v2-774603275806.europe-west1.run.app/ask"
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


# Function to extract only the date from document_id
def extract_date(document_id):
    parts = document_id.split("-")
    title_part = parts[0] if parts else ""

    # Look for date in format dd/mm/yyyy within title_part
    for word in title_part.split():
        if "/" in word:
            return word
    return "Data non disponibile"

# Function to extract the title, including the date
def extract_title(document_id):
    parts = document_id.split("-")
    title_part = parts[0] if parts else "Titolo Sconosciuto"

    # Extract the date
    date = extract_date(document_id)

    # Include the date in the title if found
    return f"{title_part.strip()} {date}" if date != "Data non disponibile" else title_part.strip()


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
st.title("TaxFinder")
st.subheader("Riduci i tempi di ricerca grazie all'Intelligenza Artificiale")
st.markdown("""
Ti diamo il benvenuto sulla _beta_ del nostro Assistente AI sul ***Diritto Tributario***.
Il chatbot è in grado di basare le proprie risposte su tutte le *Circolari*, *Provvedimenti*, *Risoluzioni*, e
*Risposte* presenti negli archivi dell' Agenzia delle Entrate.

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
if prompt := st.chat_input("Scrivi un messaggio a TaxFinder"):

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
        if answer.lower() != "Mi dispiace, ma non sono in grado di fornire una risposta.".lower():

            # Remove duplicate sources
            # filenames = list(set(sources))

            # Rimozione delle fonti duplicate
            filenames = list({source["document_id"]: source for source in sources}.values())

            if filenames:

                st.write("\n\n**Fonti:**\n\n")

                # Costruiamo la lista dei dati con i link HTML per la colonna "Titolo"
                data = []
                for filename in filenames:
                    document_url = filename.get("url", "#")  # Default a '#' se l'URL è mancante
                    title = extract_title(filename["document_id"])
                    date = extract_date(filename["document_id"])
                    summary = filename.get("summary", "Descrizione non disponibile")
                    legal_citations = "\n".join(filename.get("legal_citations", []))  # Passaggi rilevanti

                    # Aggiungi i dati alla tabella
                    data.append({
                        "Titolo": f'<a href="{document_url}" target="_blank">{title}</a>',
                        "Data": date,
                        "Summary": summary #,
                        # "Passaggi Rilevanti": legal_citations
                    })

                # Creiamo il DataFrame
                df_sources = pd.DataFrame(data)

                # Mostriamo la tabella in Streamlit con i link HTML abilitati
                st.markdown(df_sources.to_html(escape=False, index=False), unsafe_allow_html=True)



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
    to_email = "x+1208632639979553@mail.asana.com"
    #subject = "RAG Feedback - Tax bot"
    subject = f"User Feedback: {feedback}"

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
        st.error(f"Non è stato possibile inviare la email: {e}")




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
