# Bot Teaching Assistant for Data Science and AI Course
Welcome to the Bot Teaching Assistant! This project aims to help students easily retrieve course content from the Data Science and AI course by interacting with a chatbot fine-tuned using all the course PDFs.

# Features
- **Interactive Chatbot:** Ask the bot questions related to the course, and it will try to retrieve the most relevant information from the course materials.
- **PDF Fine-tuned:** The bot has been fine-tuned using the PDFs from the course, ensuring that it has access to all the content covered.
- **Simple Interface:** Designed using Streamlit, the interface is clean and easy to use.
- **Warnings on Accuracy:** While the bot is useful, it may provide some inaccurate answers. Please double-check the responseàs.

# Project Author
Paolo Piacenti, Batch #1758, LinkedIn https://www.linkedin.com/in/paolopiacenti/

# How to Run Locally

## Prerequisites
To run the project locally, you'll need the following installed:

- Python 3.10+
- pip (Python package installer)
- Virtual environment tools like pyenv or venv (optional but recommended)

## Steps to Run
1. Clone the repository:

git clone https://github.com/your-repo-url.git

2. Navigate to the project directory:

cd your-repo-name

3. Create a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

4. Install the required dependencies:

pip install -r requirements.txt

5. Create a .env file with your email credentials:

EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

6. Run the Streamlit app:

streamlit run webapp.py

7. Open your browser at http://localhost:8501/ to interact with the bot.

# Project Structure

.
├── webapp.py              # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # (Ignored) Environment variables for sensitive information
└── README.md              # Project documentation

# Notes
The bot was developed as a personal assistant to help students retrieve course materials quickly and efficiently.
While it’s trained with course content, it may still provide some inaccurate information, so please verify the responses.
