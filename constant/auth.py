WHITELIST_PATHS = [
    "/health-check", 
    "/docs",
    "/openapi.json",
    "/favicon.ico",
    "/api/jobs", 
    "/api/job", 
    "/api/related-jobs", 
    "/api/common/types",
    "/api/v2/common/types",
    "/api/ai/resume/enhance",
    "/api/qna/generate",
    "/api/qna/generate_v2",
    "/api/qna/questioning_v1",
    "/api/ai/jobs/questioning",
    "/api/admin/protected",
    "/api/admin/weaviate/create-job-class",
    "/api/admin/weaviate/create-jobqna-class",
    "/api/admin/weaviate/delete-class",
    "/api/admin/manual-sync-jobs",
    "/api/admin/manual-sync-resumes",
    "/api/all-jobs-for-seo",
    "/sitemap.xml",
    "/robots.txt",
    "/",
] 

ADMIN_PATHS = [
    "/api/analysis/top-job-titles",
    "/api/analysis/top-job-titles-salary",
    "/api/analysis/top-applied-job-titles",
    "/api/analysis/top-skills",
    "/api/analysis/job-company-type",
    "/api/analysis/new-user-in-time-range",
    "/api/analysis/count-user-by-role",
    "/api/analysis/job-status",
    "/api/analysis/top-recruiter-by-job-posting",
    "/api/analysis/top-viewed-job",
    "/api/analysis/top-work-titles",
    "/api/analysis/salary-change-by-time",
    "/api/analysis/salary-change-by-year",
    "/api/analysis/number-jobs-by-country",
    "/api/analysis/get-countries",
    "/api/analysis/get-common-job-titles",
    "/api/assistant/generate",
    "/api/assistant/questioning",
]

RECRUITER_PAHTS = [
    "/api/ai/resumes/questioning",
]

PATH_CHECKS_BODY = {
    "/api/candidate/update-saved-job": "candidate_id",
    "/api/recruiter/update-saved-talent": "recruiter_id",
    "/api/job/apply": "candidate_id",
    "/api/job/close": "recruiter_id",
    "/api/resume/delete": "candidate_id",
    "/api/ai/resumes/questioning": "recruiter_id",
}
        
PATH_CHECKS_FORM_DATA = {
    "/api/job/create": "recruiter_id",
    "/api/job/update": "recruiter_id",
    "/api/resume/create": "candidate_id",
}

PATH_CHECKS_QUERY_PARAMS = {
    "/api/resumes": "candidate_id",
    "/api/candidate/applied": "candidate_id",
    "/api/candidate/saved-jobs": "candidate_id",
    "/api/recruiter/jobs-posted": "recruiter_id",
    "/api/recruiter/candidates-saved": "recruiter_id",
    "/api/recommend-jobs": "user_id",
    "/api/job/applied-resumes": "recruiter_id",
}
