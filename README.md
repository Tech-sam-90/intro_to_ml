# Intro to ML – Quiz Generator

Generate practice quizzes from your own notes and example questions using AI.

## What it does

Upload any combination of:
- **Course notes** (PDF slides, handouts, etc.)
- **Practice questions** (past exams, problem sets, etc.)

The app will analyse the style and difficulty of your practice questions, combine that with the topics from your notes, and produce brand-new questions that look and feel like the originals.

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run quiz_generator.py
```

Your browser should open automatically at `http://localhost:8501`.

### 3. Configure and generate

1. Enter your **OpenAI API key** in the sidebar (never stored or sent anywhere other than the OpenAI API).
2. Choose the model (`gpt-4o` recommended) and the number of questions.
3. Upload one or more **notes PDFs** in the left column.
4. Upload one or more **practice question PDFs** in the right column.
5. Click **Generate Quiz**.

The generated questions (with answers) will appear on screen and can be downloaded as a `.txt` file.

## Repository layout

```
.
├── Notes/                  # Lecture handouts / annotated slides
├── Exam Practice/          # Past exams and solution keys
├── quiz_generator.py       # Streamlit quiz-generator app
└── requirements.txt        # Python dependencies
```

## Requirements

| Package | Minimum version |
|---------|-----------------|
| Python  | 3.9+            |
| streamlit | 1.32.0       |
| openai  | 1.14.0          |
| PyPDF2  | 3.0.0           |

You also need an [OpenAI API key](https://platform.openai.com/api-keys).
