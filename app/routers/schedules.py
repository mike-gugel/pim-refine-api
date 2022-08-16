from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from apscheduler.triggers.cron import CronTrigger
from fastapi import (APIRouter, Depends, HTTPException, status)

from app.models.job import (
    JobCreateDeleteResponse,
    CurrentScheduledJobsResponse
    )
from app.db.users import User
from app.utils.dependencies import get_current_admin
from app.utils.scheduler import get_scheduler
from app.scheduler.jobs import scheduler_jobs



router = APIRouter()


@router.get("/scheduler/", response_model = CurrentScheduledJobsResponse, tags=["scheduler"])
async def get_scheduled_jobs(admin: User = Depends(get_current_admin())):
    """
    Will provide a list of currently Scheduled Tasks
    """
    schedules = []
    for job in get_scheduler().get_jobs():
        schedules.append({"job_id": str(job.id), "run_frequency": str(job.trigger), "next_run": str(job.next_run_time)})
    return {"jobs": schedules}


@router.post("/scheduler/", response_model = JobCreateDeleteResponse, tags=["scheduler"])
async def schedule_job(
    crontab_expression: str = '0 5 * * *',
    name = "crawlab_import",
    admin: User = Depends(get_current_admin())
    ):
    """
    Adds a New Job to a Schedule
    """
    try:
        job = get_scheduler().add_job(scheduler_jobs[name], CronTrigger.from_crontab(crontab_expression), id=name)
        return {"scheduled": True, "job_id": job.id}
    except ConflictingIdError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job with this name already exists",
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No job with this name found",
        )


@router.delete("/scheduler/", response_model = JobCreateDeleteResponse, tags=["scheduler"])
async def remove_job(name="crawlab_import", admin: User = Depends(get_current_admin())):
    """
    Removes a Job from a Schedule
    """
    try:
        get_scheduler().remove_job(name)
        return {"scheduled": False, "job_id": name}
    except JobLookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job doesn't exist",
        )
