from apscheduler.triggers.interval import IntervalTrigger
from findrum.interfaces import Scheduler

class Every10SecondsScheduler(Scheduler):
    def register(self, scheduler):
        trigger = IntervalTrigger(seconds=10)
        job_id = self.pipeline_path.replace("/", "_")

        scheduler.add_job(
            func=self._run_pipeline,
            trigger=trigger,
            id=job_id,
            name=f"{job_id} (every 10s)",
            replace_existing=True
        )