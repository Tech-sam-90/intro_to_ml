"""
Quiz Generator – Upload notes and practice questions to generate similar quizzes
using OpenAI's API.
"""

import io

import openai
import PyPDF2
import streamlit as st
from openai import OpenAI

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MAX_CHARS = 12_000  # keep prompts within a reasonable token budget


def extract_text_from_pdf(uploaded_file) -> str:
    """Return all text extracted from a PDF uploaded via Streamlit."""
    reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def truncate(text: str, max_chars: int = MAX_CHARS) -> str:
    """Truncate text to *max_chars* characters with an ellipsis."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[… content truncated for brevity …]"


def generate_quiz(
    notes_text: str,
    practice_text: str,
    num_questions: int,
    api_key: str,
    model: str = "gpt-4o",
) -> str:
    """
    Call the OpenAI Chat Completions API and return a generated quiz.

    Parameters
    ----------
    notes_text:     Combined text extracted from the uploaded notes PDFs.
    practice_text:  Combined text extracted from the uploaded practice-question PDFs.
    num_questions:  How many new questions to generate.
    api_key:        OpenAI API key supplied by the user.
    model:          OpenAI model to use (default: gpt-4o).
    """
    client = OpenAI(api_key=api_key)

    system_prompt = (
        "You are an expert educator and quiz designer. "
        "Your job is to create rigorous practice questions that closely "
        "mirror the style, format, and difficulty of the provided example "
        "questions, while drawing on topics covered in the provided notes."
    )

    user_prompt = f"""Below are course notes and example practice questions.

=== COURSE NOTES (excerpt) ===
{truncate(notes_text)}

=== EXAMPLE PRACTICE QUESTIONS (excerpt) ===
{truncate(practice_text)}

=== YOUR TASK ===
Generate {num_questions} new practice questions that:
1. Are similar in style, format, and difficulty to the example questions above.
2. Cover topics that appear in the course notes.
3. Include a brief answer / solution for each question.

Format each question as:
  Q<n>. <question text>
  Answer: <answer / solution>
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("The model returned an empty response. Please try again.")
    return content


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="ML Quiz Generator", page_icon="🎓", layout="centered")

st.title("🎓 ML Quiz Generator")
st.markdown(
    "Upload your **course notes** and **practice questions** (PDFs), then "
    "click **Generate Quiz** to create new questions in the same style."
)

# ── Sidebar – configuration ─────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-…",
        help="Your key is never stored or transmitted beyond this session.",
    )
    model = st.selectbox(
        "Model",
        options=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
    )
    num_questions = st.slider("Number of questions to generate", 1, 20, 5)

# ── File uploaders ───────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Notes")
    notes_files = st.file_uploader(
        "Upload notes PDFs",
        type="pdf",
        accept_multiple_files=True,
        key="notes",
    )

with col2:
    st.subheader("📝 Practice Questions")
    practice_files = st.file_uploader(
        "Upload practice question PDFs",
        type="pdf",
        accept_multiple_files=True,
        key="practice",
    )

# ── Generate button ──────────────────────────────────────────────────────────
st.divider()

if st.button("🚀 Generate Quiz", use_container_width=True, type="primary"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not notes_files and not practice_files:
        st.error("Please upload at least one notes PDF or practice questions PDF.")
    elif not practice_files:
        st.error("Please upload at least one practice questions PDF so the generator can match its style.")
    else:
        with st.spinner("Extracting text from PDFs…"):
            notes_text = "\n\n".join(
                extract_text_from_pdf(f) for f in notes_files
            ) if notes_files else ""
            practice_text = "\n\n".join(
                extract_text_from_pdf(f) for f in practice_files
            )

        with st.spinner(f"Generating {num_questions} questions with {model}…"):
            try:
                quiz = generate_quiz(
                    notes_text=notes_text,
                    practice_text=practice_text,
                    num_questions=num_questions,
                    api_key=api_key,
                    model=model,
                )
                st.success("Quiz generated!")
                st.markdown("---")
                st.markdown(quiz)

                st.download_button(
                    label="⬇️ Download Quiz (.txt)",
                    data=quiz,
                    file_name="generated_quiz.txt",
                    mime="text/plain",
                )
            except openai.AuthenticationError:
                st.error("Invalid OpenAI API key. Please check the key you entered in the sidebar.")
            except openai.RateLimitError:
                st.error("OpenAI rate limit reached. Please wait a moment and try again, or use a different API key.")
            except openai.APIConnectionError:
                st.error("Could not connect to the OpenAI API. Please check your internet connection and try again.")
            except openai.BadRequestError as exc:
                st.error(f"The request was rejected by OpenAI: {exc}")
            except Exception as exc:
                st.error(f"An unexpected error occurred: {exc}")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    "<br><hr><center style='color:grey;font-size:0.8em;'>"
    "Powered by OpenAI · Built for 18-661 Intro to ML</center>",
    unsafe_allow_html=True,
)
