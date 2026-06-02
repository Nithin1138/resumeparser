import re
import spacy
import pdfplumber
from docx import Document

nlp = spacy.load("en_core_web_sm")

# ── Skill keywords ──────────────────────────────────────────────────────────
SKILLS_DB = [
    "python", "java", "javascript", "typescript", "react", "node.js", "nodejs",
    "angular", "vue", "django", "flask", "fastapi", "spring", "sql", "mysql",
    "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws", "azure",
    "gcp", "git", "linux", "machine learning", "deep learning", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy", "opencv", "nlp", "html",
    "css", "tailwind", "rest api", "graphql", "ci/cd", "jenkins", "figma",
    "excel", "power bi", "tableau", "c", "c++", "rust", "go", "kotlin", "swift",
]

# ── Section headers ──────────────────────────────────────────────────────────
SECTION_HEADERS = {
    "education":    ["education", "academic", "qualification", "degree"],
    "experience":   ["experience", "work history", "employment", "internship"],
    "skills":       ["skills", "technical skills", "technologies", "tools"],
    "projects":     ["projects", "personal projects", "academic projects"],
    "summary":      ["summary", "objective", "profile", "about"],
    "certifications": ["certification", "certificate", "courses", "achievements"],
}


# ── Text extraction ──────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    import io
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    import io
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


# ── Field extractors ─────────────────────────────────────────────────────────

def extract_email(text: str) -> str | None:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0).lower() if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(
        r"(\+?\d{1,3}[\s\-]?)?(\(?\d{3,5}\)?[\s\-]?)(\d{3,4}[\s\-]?\d{3,4})", text
    )
    return re.sub(r"\s+", " ", match.group(0)).strip() if match else None


def extract_linkedin(text: str) -> str | None:
    match = re.search(r"linkedin\.com/in/[a-zA-Z0-9\-_%]+", text, re.IGNORECASE)
    return "https://" + match.group(0) if match else None


def extract_github(text: str) -> str | None:
    match = re.search(r"github\.com/[a-zA-Z0-9\-_%]+", text, re.IGNORECASE)
    return "https://" + match.group(0) if match else None


def extract_name(text: str) -> str | None:
    """Use spaCy NER to find PERSON entity in first 300 chars."""
    doc = nlp(text[:300])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()
    # fallback: first non-empty line
    for line in text.splitlines():
        line = line.strip()
        if line and len(line.split()) <= 5 and not re.search(r"[@|/]", line):
            return line
    return None


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_sections(text: str) -> dict:
    lines = text.splitlines()
    sections: dict[str, list[str]] = {}
    current_section = "other"

    for line in lines:
        line_lower = line.lower().strip()
        matched = False
        for section, keywords in SECTION_HEADERS.items():
            if any(kw in line_lower for kw in keywords) and len(line_lower) < 40:
                current_section = section
                matched = True
                break
        if not matched:
            sections.setdefault(current_section, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


def extract_years_experience(text: str) -> int | None:
    """Look for explicit mention like '3 years of experience'."""
    match = re.search(
        r"(\d+)\+?\s+years?\s+(of\s+)?(experience|exp)", text, re.IGNORECASE
    )
    if match:
        return int(match.group(1))
    return None


# ── Main parse function ──────────────────────────────────────────────────────

def parse_text(text: str) -> dict:
    sections = extract_sections(text)

    return {
        "name":             extract_name(text),
        "email":            extract_email(text),
        "phone":            extract_phone(text),
        "linkedin":         extract_linkedin(text),
        "github":           extract_github(text),
        "skills":           extract_skills(text),
        "years_experience": extract_years_experience(text),
        "sections": {
            "summary":        sections.get("summary"),
            "experience":     sections.get("experience"),
            "education":      sections.get("education"),
            "projects":       sections.get("projects"),
            "certifications": sections.get("certifications"),
        },
        "raw_text_length": len(text),
    }


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith((".docx", ".doc")):
        text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Upload PDF or DOCX.")

    return parse_text(text)
