import streamlit as st
import requests
import uuid  # Libreria per generare un UUID unico
import time

import subprocess

#from LinkolnParser import LinkolnParser

import pandas as pd

################################################################################
#                           Page Configuration and Favicon                     #
################################################################################


# Set up the favicon and page title
st.set_page_config(
    page_title="TaxFinder",
    page_icon="https://em-content.zobj.net/source/apple/391/balance-scale_2696-fe0f.png",  # Ensure favicon.ico is in the root directory
    layout="centered"  # Adjust layout as needed
)


################################################################################
#                                Custom CSS                                    #
################################################################################

# Google Analytics Tracking Script
st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-T6BJ258E1W"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-T6BJ258E1W');
    </script>
""", unsafe_allow_html=True)

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

# JavaScript for link hover effects
st.components.v1.html("""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('a').forEach(link => {
                link.addEventListener('mouseover', () => {
                    link.style.color = 'blue';
                    link.style.textDecoration = 'underline';
                });
                link.addEventListener('mouseout', () => {
                    link.style.color = 'inherit';
                    link.style.textDecoration = 'none';
                });
            });
        });
    </script>
""", height=0)

################################################################################
#                              Support Functions                               #
################################################################################

# Function to make API request
def get_bot_response(question, session_id):
    url = "https://chat-api-v3-rollback-774603275806.europe-west1.run.app/ask"
    headers = {"Content-Type": "application/json"}
    data = {
        "question": question + "Per favore crea una risposta dettagliata citando le fonti.",
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

# Generatore per mostrare il testo arricchito come stream
def simulate_stream_with_links(response):
    try:
        # Arricchisci il testo con riferimenti normativi
        enriched_text = enrich_with_legal_references(response)

        # Accumula tutto il testo in una lista
        rendered_text = []
        for word in enriched_text.split():
            rendered_text.append(word)
            time.sleep(0.05)  # Simula il ritardo
        return " ".join(rendered_text)  # Restituisci il testo completo
    except Exception as e:
        st.error(f"Errore durante l'elaborazione del testo: {e}")
        return ""


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

    # Include the date in the title if found
    return title_part.strip()

################################################################################
#                       Include Lex References Hyperlinks                      #
################################################################################

def enrich_with_legal_references(text):
    try:
        # Esegui il parser tramite il wrapper Java
        result = subprocess.run(
            ["java", "-cp", ".:lib/linkoln2-parser.jar", "MainWrapper", text],
            capture_output=True,
            text=True
        )

        # Verifica eventuali errori
        if result.returncode != 0:
            raise Exception(f"Errore durante l'esecuzione del parser: {result.stderr}")

        # Prendi solo la parte HTML
        output_lines = result.stdout.split("\n")
        html_output = "\n".join(output_lines[output_lines.index("2) HTML:") + 1:]).strip()

        return html_output

    except Exception as e:
        raise Exception(f"Errore durante l'esecuzione del parser: {e}")


################################################################################
#                                 Chatbot Core                                 #
################################################################################

# Initialize session state for the conversation and feedback
if "messages" not in st.session_state: # This ensures that the messages persist across reruns.
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'feedback_given' not in st.session_state:
    st.session_state['feedback_given'] = False
if 'input_key' not in st.session_state:
    st.session_state['input_key'] = str(uuid.uuid4())  # Use a unique key for each session
if 'df_sources_html' not in st.session_state:
    st.session_state['df_sources_html'] = ""  # Store table HTML as a string for persistent display


# Show title, claim, and description.
st.title("TaxFinder")
st.subheader("Riduci i tempi di ricerca grazie all'Intelligenza Artificiale")
st.markdown("""
Ti diamo il benvenuto sulla _beta_ del nostro Assistente AI sul ***Diritto Tributario***.
Il chatbot è in grado di basare le proprie risposte su tutte le *Circolari*, *Provvedimenti*, *Risoluzioni*, e
*Risposte* presenti negli archivi dell' Agenzia delle Entrate.

***Nota**: Questo bot va inteso come un prototipo, pertanto ti invitiamo a verificare la correttezza delle risposte.*

""")


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
        # st.markdown(simulate_stream_with_links(answer), unsafe_allow_html=True)  # Pass the generator directly to st.write_stream
        with st.spinner("Sto formulando la risposta..."):
            try:
                st.markdown(enrich_with_legal_references(answer), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Errore durante la visualizzazione del messaggio: {e}")

        # If the answer is not "I don't know.", include sources as clickable links
        if answer.lower() != "Mi dispiace, ma non sono in grado di fornire una risposta.".lower():

            # Rimozione delle fonti duplicate
            filenames = list({source["title"]: source for source in sources}.values())

            if filenames:

                st.write("\n\n**Riferimenti Agenzia delle Entrate:**\n\n")

                # Costruiamo la lista dei dati con i link HTML per la colonna "Titolo"
                data = []
                for filename in filenames:
                    document_url = filename.get("url", "#")  # Default a '#' se l'URL è mancante
                    title = extract_title(filename["title"])
                    date = extract_date(filename["title"])
                    score = filename.get("score")
                    summary = filename.get("original_summary", "Descrizione non disponibile")
                    legal_citations = "\n".join(filename.get("legal_citations", []))  # Passaggi rilevanti

                    # Aggiungi i dati alla tabella
                    data.append({
                        "Titolo": f'<a href="{document_url}" target="_blank">{title}</a>',
                        "Rilevanza": f"{score*100:.2f}%",
                        # "Data": date,
                        "Summary": summary #,
                        # "Passaggi Rilevanti": legal_citations
                    })

                # Creiamo il DataFrame
                st.session_state['df_sources'] = pd.DataFrame(data)
                st.session_state['df_sources_html'] =  st.session_state['df_sources'].to_html(escape=False, index=False)

                # Access df_sources from session state whenever needed
                if not st.session_state['df_sources'].empty:
                    # Display the DataFrame in Streamlit
                    st.markdown(st.session_state['df_sources_html'], unsafe_allow_html=True)
                else:
                    st.write("Nessuna fonte disponibile.")



    st.session_state.messages.append({"role": "assistant", "content": answer})


################################################################################
#                            Sidebar for Feedback                              #
################################################################################

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

from_email = os.environ['EMAIL_USER']
email_password = os.environ['EMAIL_PASS']

# Function to send feedback email
def send_email(feedback, conversation, sources):
    to_email = "x+1208737819974597@mail.asana.com"
    subject = f"User Feedback: {feedback}"

    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    # Construct the email body
    email_body = f"User Feedback:\n{feedback}\n\nConversation History:\n{conversation}\n\nSources:\n{sources}"
    message.attach(MIMEText(email_body, "plain"))

    try:
        # Sending the mail using Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, email_password)
        server.sendmail(from_email, to_email, message.as_string())
        server.quit()
        st.success("Il tuo feedback è stato inviato. Grazie!")
    except Exception as e:
        st.error(f"Non è stato possibile inviare la email: {e}")

with st.sidebar:
    st.subheader("La tua opinione conta")

    # Initialize `df_sources` to prevent KeyError
    if 'df_sources' not in st.session_state:
        st.session_state['df_sources'] = pd.DataFrame()

    # Show feedback input if feedback not already given
    if not st.session_state['feedback_given']:
        # Feedback form
        reasons = st.multiselect(
            "Come è andata la tua esperienza con TaxFinder?",
            [
                "😊 Tutto perfetto!",
                "🐢 Risposta troppo lenta",
                "❌ Documento rilevante non trovato",
                "🔍 Troppi documenti non rilevanti",
                "🚫 Risposta incompleta o errata"
            ],
            help="Seleziona tutte le opzioni applicabili"
        )

        description = st.text_area("Dicci di più su come possiamo migliorare.")

        # Submit feedback button
        if st.button("Invia Feedback", key="feedback_button"):
            if reasons or description:
                subject = f"{'; '.join(reasons) or 'Altro'} - {description}"

                # Conversation history
                conversation = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state['messages']])

                # Sources, if available
                sources_html = st.session_state['df_sources'].to_html(escape=False, index=False) if not st.session_state['df_sources'].empty else "Nessuna fonte disponibile."

                # Send feedback
                send_email(subject, conversation, sources_html)

                # Mark feedback as given
                st.session_state['feedback_given'] = True
            else:
                st.warning("Per favore, compila almeno un motivo o una descrizione.")
    else:
        st.info("Il tuo feedback è stato già inviato. Grazie!")
