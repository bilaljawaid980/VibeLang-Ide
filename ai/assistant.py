from __future__ import annotations

import os
import re

from openai import OpenAI

from compiler.compiler import compile_source


SYSTEM_PROMPT = """You are an assistant for the VibeLang compiler.
Only use supported VibeLang syntax.
Rules:
- Statements end with semicolons.
- Use declare variable, print, if ... then ... end if;, while ... do ... end while;
- For declarations with values, use exactly: declare variable name = expression;
- Never use phrases like 'declare x as 5;' or any syntax outside the compiler grammar.
- Do not invent arrays, functions, booleans, objects, or unsupported features.
- Keep explanations beginner-friendly and concise.
"""


class AIAssistant:
    def __init__(self):
        self.api_key = os.getenv("AI_GATEWAY_API_KEY", "").strip()
        self.base_url = os.getenv("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1").strip()
        self.model = os.getenv("AI_MODEL", "openai/gpt-4.1-nano").strip()
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def config_summary(self) -> dict:
        return {
            "configured": self.is_configured(),
            "base_url": self.base_url,
            "model": self.model,
        }

    def explain_error(self, source_code: str, error: dict) -> str:
        prompt = (
            "Explain this compiler error in simple words and suggest a likely fix.\n\n"
            f"Source Code:\n{source_code}\n\n"
            f"Error:\n{error}\n"
        )
        return self._complete(prompt)

    def suggest_fix(self, source_code: str, errors: list[dict]) -> str:
        prompt = (
            "Suggest a corrected version of this VibeLang code. Return only VibeLang code.\n\n"
            f"Source Code:\n{source_code}\n\n"
            f"Errors:\n{errors}\n"
        )
        return self._complete(prompt, require_valid_code=True)

    def explain_code(self, source_code: str, tac: list[str]) -> str:
        prompt = (
            "Explain what this VibeLang program does for a beginner.\n\n"
            f"Source Code:\n{source_code}\n\n"
            f"Three-Address Code:\n{tac}\n"
        )
        return self._complete(prompt)

    def natural_language_to_vibelang(self, prompt_text: str) -> str:
        prompt = (
            "Convert this request into valid VibeLang code. Return only VibeLang code.\n\n"
            f"Request:\n{prompt_text}\n"
        )
        return self._complete(prompt, require_valid_code=True)

    def _complete(self, prompt: str, require_valid_code: bool = False) -> str:
        if not self.is_configured():
            raise RuntimeError("AI Gateway is not configured.")
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_output_tokens=500,
        )
        text = response.output_text.strip()
        if require_valid_code:
            return self._ensure_valid_code(text, prompt)
        return text

    def _ensure_valid_code(self, text: str, original_prompt: str) -> str:
        normalized = self._normalize_generated_code(text)
        first_pass = compile_source(normalized)
        if first_pass["success"]:
            return normalized

        repair_prompt = (
            "Your previous answer was not valid VibeLang for this compiler.\n\n"
            f"Original request:\n{original_prompt}\n\n"
            f"Previous output:\n{normalized}\n\n"
            f"Compiler errors:\n{first_pass['errors']}\n\n"
            "Return only corrected VibeLang code that follows the exact compiler grammar."
        )
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": repair_prompt},
            ],
            max_output_tokens=500,
        )
        repaired = self._normalize_generated_code(response.output_text.strip())
        second_pass = compile_source(repaired)
        if second_pass["success"]:
            return repaired
        raise RuntimeError(
            "AI generated code, but it did not pass VibeLang validation. "
            f"Latest compiler errors: {second_pass['errors']}"
        )

    def _normalize_generated_code(self, text: str) -> str:
        normalized = text.strip()
        normalized = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", normalized)
        normalized = re.sub(r"\s*```$", "", normalized)
        normalized = re.sub(
            r"\bdeclare\s+variable\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+([^;\n]+);",
            r"declare variable \1 = \2;",
            normalized,
            flags=re.IGNORECASE,
        )
        normalized = re.sub(
            r"\bdeclare\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+([^;\n]+);",
            r"declare variable \1 = \2;",
            normalized,
            flags=re.IGNORECASE,
        )
        normalized = re.sub(
            r"\bdeclare\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^;\n]+);",
            r"declare variable \1 = \2;",
            normalized,
            flags=re.IGNORECASE,
        )
        normalized = re.sub(
            r"\bdeclare\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;",
            r"declare variable \1;",
            normalized,
            flags=re.IGNORECASE,
        )
        return normalized.strip()
