def format_job_response(job):
    return job.to_dict() if hasattr(job, "to_dict") else dict(job)
