"""
Mess Menu Parser Agent
-----------------------
Parses raw text, PDF-extracted text, or image OCR text into a
structured weekly mess menu JSON.
"""

from app.agents.base import BaseAgent, extract_json

SYSTEM_PROMPT = """You are a menu parsing AI that extracts structured meal data from hostel mess menus.

Given raw text from a mess menu (which may be messy, OCR'd, or poorly formatted),
extract the weekly meal schedule into clean JSON.

Rules:
1. Return ONLY valid JSON — no prose, no markdown fences.
2. Map meals to: breakfast, lunch, dinner (and snacks if present).
3. Days must use full names: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.
4. Food items must be clean strings (remove codes, prices, abbreviations).
5. If a day is missing, include it with empty arrays.
6. Handle common Indian menu formats.

Return this exact structure:
{
  "Monday": {
    "breakfast": ["Aloo Paratha", "Dahi", "Boiled Eggs"],
    "lunch": ["Rice", "Palak Dal", "Bhindi Fry", "Roti"],
    "dinner": ["Methi Paratha", "Dal Tadka", "Salad"],
    "snacks": ["Banana", "Chai"]
  },
  "Tuesday": { ... },
  "Wednesday": { ... },
  "Thursday": { ... },
  "Friday": { ... },
  "Saturday": { ... },
  "Sunday": { ... }
}"""


class MessParserAgent(BaseAgent):

    def parse_menu(self, raw_text: str) -> dict:
        """
        Parse raw mess menu text into structured JSON.

        Args:
            raw_text: Raw text from PDF, image OCR, or manual input.

        Returns:
            Structured menu dict.
        """
        if not raw_text or not raw_text.strip():
            return self._empty_menu()

        user_message = f"""Parse this hostel mess menu into the specified JSON format:

---
{raw_text[:4000]}
---

Extract all days, meals (breakfast/lunch/dinner/snacks), and food items."""

        raw = self._call(SYSTEM_PROMPT, user_message, max_tokens=2048)

        try:
            result = extract_json(raw)
            # Ensure all 7 days present
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in days:
                if day not in result:
                    result[day] = {"breakfast": [], "lunch": [], "dinner": [], "snacks": []}
            return result
        except ValueError:
            return self._empty_menu()

    def _empty_menu(self) -> dict:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return {
            day: {"breakfast": [], "lunch": [], "dinner": [], "snacks": []}
            for day in days
        }

    def parse_from_pdf(self, pdf_path: str) -> dict:
        """Extract text from PDF and parse."""
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            raw_text = "\n".join(text_parts)
        except Exception as e:
            return self._empty_menu()
        return self.parse_menu(raw_text)

    def parse_from_image(self, image_bytes: bytes) -> dict:
        """OCR an image and parse the extracted text."""
        try:
            from PIL import Image
            import pytesseract
            import io
            image = Image.open(io.BytesIO(image_bytes))
            raw_text = pytesseract.image_to_string(image)
        except Exception as e:
            raw_text = ""
        return self.parse_menu(raw_text)
