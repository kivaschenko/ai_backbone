"""
Task Scheduler
Manages scheduled tasks for data syncing and automation.
"""

from typing import Callable, Dict, Any, List
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks for automation."""

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[str, Any] = {}

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")

    def add_interval_job(
        self,
        job_id: str,
        func: Callable,
        minutes: int = None,
        hours: int = None,
        days: int = None,
        **kwargs,
    ):
        """
        Add a job that runs at regular intervals.

        Args:
            job_id: Unique identifier for the job
            func: Function to execute
            minutes: Interval in minutes
            hours: Interval in hours
            days: Interval in days
            **kwargs: Additional arguments to pass to the function
        """
        try:
            trigger = IntervalTrigger(
                minutes=minutes or 0, hours=hours or 0, days=days or 0
            )

            job = self.scheduler.add_job(
                func, trigger=trigger, id=job_id, kwargs=kwargs, replace_existing=True
            )

            self.jobs[job_id] = job
            logger.info(f"Added interval job: {job_id}")
            return job

        except Exception as e:
            logger.error(f"Failed to add interval job {job_id}: {str(e)}")
            raise

    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        cron_expression: str = None,
        hour: str = None,
        minute: str = None,
        day_of_week: str = None,
        **kwargs,
    ):
        """
        Add a job that runs on a cron schedule.

        Args:
            job_id: Unique identifier for the job
            func: Function to execute
            cron_expression: Full cron expression (alternative to individual params)
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            day_of_week: Day of week (mon, tue, wed, thu, fri, sat, sun)
            **kwargs: Additional arguments to pass to the function
        """
        try:
            if cron_expression:
                trigger = CronTrigger.from_crontab(cron_expression)
            else:
                trigger = CronTrigger(hour=hour, minute=minute, day_of_week=day_of_week)

            job = self.scheduler.add_job(
                func, trigger=trigger, id=job_id, kwargs=kwargs, replace_existing=True
            )

            self.jobs[job_id] = job
            logger.info(f"Added cron job: {job_id}")
            return job

        except Exception as e:
            logger.error(f"Failed to add cron job {job_id}: {str(e)}")
            raise

    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")

    def pause_job(self, job_id: str):
        """Pause a scheduled job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {str(e)}")

    def resume_job(self, job_id: str):
        """Resume a paused job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {str(e)}")

    def get_jobs(self) -> List[Dict[str, Any]]:
        """Get list of all scheduled jobs."""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time,
                    "trigger": str(job.trigger),
                }
            )
        return jobs_info


# Global scheduler instance
scheduler = TaskScheduler()
