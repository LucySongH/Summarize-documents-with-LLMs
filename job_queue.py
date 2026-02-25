"""
  - Model should be loaded ONCE and reused
  - Multiple documents can be queued without blocking the UI
  - Frontend polls for status instead of waiting frozen
"""

import asyncio
import uuid
import time
import logging
from enum import Enum
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    QUEUED     = "queued"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"


class Job:
    def __init__(self, text: str, model_name: str, summary_type: str):
        self.job_id    = str(uuid.uuid4())
        self.text      = text
        self.model_name = model_name
        self.summary_type = summary_type

        # Result fields
        self.status: JobStatus       = JobStatus.QUEUED
        self.summary: Optional[str]  = None
        self.error: Optional[str]    = None
        self.time_taken: Optional[float] = None

        # Timestamps
        self.submitted_at  = datetime.now().isoformat()
        self.completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "job_id":       self.job_id,
            "model":        self.model_name,
            "summary_type": self.summary_type,
            "status":       self.status,
            "summary":      self.summary,
            "error":        self.error,
            "time":         self.time_taken,
            "submitted_at": self.submitted_at,
            "completed_at": self.completed_at,
        }


class SummarizationQueue:
    """
    Async queue that processes one job at a time.
    The LLM stays loaded between jobs — no repeated cold starts.
    """

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._jobs: Dict[str, Job] = {}   # job_id → Job

    async def submit(self, text: str, model_name: str, summary_type: str) -> str:
        """Add a job to the queue. Returns job_id immediately."""
        job = Job(text=text, model_name=model_name, summary_type=summary_type)
        self._jobs[job.job_id] = job
        await self._queue.put(job)
        logger.info(f"Job {job.job_id[:8]} queued | model={model_name} | type={summary_type}")
        return job.job_id

    def get_status(self, job_id: str) -> Optional[dict]:
        """Return current state of a job, or None if not found."""
        job = self._jobs.get(job_id)
        return job.to_dict() if job else None

    def get_stats(self) -> dict:
        """Queue-level statistics."""
        statuses = [j.status for j in self._jobs.values()]
        return {
            "pending":    self._queue.qsize(),
            "total":      len(self._jobs),
            "queued":     statuses.count(JobStatus.QUEUED),
            "processing": statuses.count(JobStatus.PROCESSING),
            "completed":  statuses.count(JobStatus.COMPLETED),
            "failed":     statuses.count(JobStatus.FAILED),
        }

    async def worker(self, summarize_fn):
        """
        Background worker loop.
        Calls summarize_fn(text, model_name, summary_type) → str for each job.
        Runs forever — started once on app startup.
        """
        logger.info("Queue worker started.")
        while True:
            job: Job = await self._queue.get()

            job.status = JobStatus.PROCESSING
            start = time.time()
            logger.info(f"Processing job {job.job_id[:8]} with {job.model_name}...")

            try:
                # Run the blocking Ollama call in a thread so the event loop stays free
                summary = await asyncio.get_event_loop().run_in_executor(
                    None,
                    summarize_fn,
                    job.text,
                    job.model_name,
                    job.summary_type,
                )
                job.summary    = summary
                job.status     = JobStatus.COMPLETED
                job.time_taken = round(time.time() - start, 2)
                logger.info(f"Job {job.job_id[:8]} done in {job.time_taken}s")

            except Exception as e:
                job.status     = JobStatus.FAILED
                job.error      = str(e)
                job.time_taken = round(time.time() - start, 2)
                logger.error(f"Job {job.job_id[:8]} failed: {e}")

            finally:
                job.completed_at = datetime.now().isoformat()
                self._queue.task_done()
