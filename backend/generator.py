

import os
from openai import OpenAI


class GrokGenerator:

    def __init__(self, api_key: str = None):
        
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
        
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks):
            score = chunk.get("score", 0)
            context_parts.append(f"[Source {i + 1}] (relevance: {score:.2f})\n{chunk['text']}")

        context = "\n\n".join(context_parts)

        # Build the prompt
        system_prompt = """You are AkramAI, a personal AI assistant that knows everything about Akram Ali Faridi. 
You answer questions ONLY based on the provided data of Akram.

Rules:
1. Answer ONLY based on the provided data of Akram. Do not make up information.
2. If the data doesn't contain enough information to answer, say "I don't have enough information about this sorry."
3. Be conversational, friendly, and speak in third person about Akram (e.g., "Akram is..." or "He studied...").
4. Keep answers concise but informative.
5. If asked who you are or how you are trained, say EXACTLY: "it is trained on akram dataset i am model trained on data of akram"
6. When providing an answer based on the retrieved information, ALWAYS start or include the phrase "As per data of Akram" instead of "based on the context".
7. Reference specific details from the data of Akram to make answers accurate and trustworthy."""

        user_prompt = f"""Data of Akram:
---
{context}
---

Question: {question}

Please provide an accurate answer based on the data of Akram above. Remember to use the phrase "As per data of Akram"."""

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
