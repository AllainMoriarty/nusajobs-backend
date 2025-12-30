from sqlalchemy.orm import Session
from openai import OpenAI
from app.core.config import settings
from app.models.job import Job
from app.models.job_application import JobApplication
from app.models.candidate_cv import CandidateCV
from app.models.ai_screening import AIScreening
from app.models.ai_interview_question import AIInterviewQuestion
import json
import re

client = OpenAI(api_key=settings.GEMINI_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

class AIScreeningService:
    def _generate_reasoning(self, job_desc: str, cv_text: str) -> str:
        prompt = f"""
You are an AI recruiter.
Briefly explain why this candidate matches the job.

Job Description:
{job_desc}

Candidate CV:
{cv_text}
"""
        res = client.chat.completions.create(
            model="gemma-3-27b-it",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()

    def _safe_json_parse(self, text: str):
            try:
                # 1. Try direct parse
                return json.loads(text)
            except json.JSONDecodeError:
                # 2. Extract content between [ ] if model added extra text
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())
                    except:
                        pass
                # 3. Fallback
                return ["Tell me about your background.", "Why this role?"]

    def _generate_interview_questions(self, job_desc: str, cv_text: str) -> list[str]:
        prompt = f"""
Generate exactly 5 interview questions based on the job and candidate CV.
Return ONLY a JSON array of strings.

Job Description:
{job_desc}

Candidate CV:
{cv_text}
"""
        res = client.chat.completions.create(
            model="gemma-3-27b-it",
            messages=[{"role": "user", "content": prompt}]
        )

        content = res.choices[0].message.content
        return self._safe_json_parse(content)

    def run(self, db: Session, job: Job):
        """
        Run AI screening when job is closed
        """
        distance = CandidateCV.embedding.cosine_distance(job.embedding)

        results = (
            db.query(
                JobApplication,
                CandidateCV,
                distance.label("distance")
            )
            .join(CandidateCV, JobApplication.cv_id == CandidateCV.id)
            .filter(
                JobApplication.job_id == job.id,
                CandidateCV.embedding.isnot(None),
                JobApplication.status.in_(["applied", "screened"])
            )
            .order_by(distance)
            .limit(job.top_k)
            .all()
        )

        for rank, (application, cv, dist) in enumerate(results, start=1):
            score = 1 - float(dist)
            cv_text = cv.ocr_text if cv.ocr_text else ""

            reasoning = self._generate_reasoning(job.description, cv_text)
            questions = self._generate_interview_questions(job.description, cv_text)

            screening = AIScreening(
                job_id=job.id,
                job_application_id=application.id,
                score=score,
                rank=rank,
                reasoning=reasoning
            )

            interview = AIInterviewQuestion(
                job_id=job.id,
                candidate_id=application.candidate_id,
                questions=questions
            )

            db.add(screening)
            db.add(interview)

        db.commit()
