

import os
from openai import OpenAI


class GrokGenerator:
    """Answer generator using Groq's lightning fast API."""

    def __init__(self, api_key: str = None):
        # We still use GROK_API_KEY from .env since that's what's in the file, 
        # but we point it to the Groq servers!
        self.api_key = api_key or os.getenv("GROK_API_KEY")

        if not self.api_key:
            raise ValueError(
                "❌ Groq API key not found in .env!"
            )

        # Groq API is OpenAI-compatible
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        # Using Llama 3.1 8B Instant since Versatile is not preferred
        self.model = "llama-3.1-8b-instant"
        print(f"🤖 Groq API initialized (model: {self.model})")

    def generate_answer(self, question: str, context_chunks: list[dict]) -> dict:
        """
        Generate an answer using Groq API with retrieved context.
        """
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks):
            score = chunk.get("score", 0)
            context_parts.append(f"[Source {i + 1}] (relevance: {score:.2f})\n{chunk['text']}")

        context = "\n\n".join(context_parts)

        # Build the prompt
        system_prompt = """You are AkramAI, a personal AI assistant that knows everything about Akram Ali Faridi. 
You answer questions ONLY based on the provided context from Akram's personal document.

Rules:
1. Answer ONLY based on the provided context. Do not make up information.
2. If the context doesn't contain enough information to answer, say "I don't have enough information about this sorry."
3. Be conversational, friendly, and speak in third person about Akram (e.g., "Akram is..." or "He studied...").
4. Keep answers concise but informative.
5. If asked who you are, say you're AkramAI — a personal AI assistant built to share information about Akram Ali Faridi.
6. Reference specific details from the context to make answers accurate and trustworthy."""

        user_prompt = f"""Context from Akram's personal document:
---
{context}
---

Question: {question}

Please provide an accurate answer based on the context above."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=256
            )

            answer = response.choices[0].message.content

            # Calculate confidence based on retrieval scores
            avg_score = sum(c.get("score", 0) for c in context_chunks) / max(len(context_chunks), 1)
            confidence = min(avg_score * 100, 99.9)

            return {
                "answer": answer,
                "confidence": round(confidence, 1),
                "sources_used": len(context_chunks),
                "model": "Groq: " + self.model
            }

        except Exception as e:
            error_msg = str(e).lower()
            if "413" in error_msg or "429" in error_msg or "rate limit" in error_msg or "limit" in error_msg or "tokens" in error_msg:
                answer = "enough for today"
            else:
                answer = f"I encountered an error while generating a response. Please try again. Error: {str(e)}"
                
            return {
                "answer": answer,
                "confidence": 0,
                "sources_used": 0,
                "model": "Groq Error"
            }
