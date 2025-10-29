from prometheus_client import Counter, Histogram, Info
import time

# Define metrics
REQUESTS_TOTAL = Counter(
    "career_navigator_requests_total",
    "Total number of requests by path and method",
    ["path", "method"]
)

REQUESTS_LATENCY = Histogram(
    "career_navigator_request_latency_seconds",
    "Request latency by path and method",
    ["path", "method"]
)

RESUME_UPLOADS = Counter(
    "career_navigator_resume_uploads_total",
    "Total number of resume uploads",
    ["file_type"]
)

JOB_MATCHES = Counter(
    "career_navigator_job_matches_total",
    "Total number of job matching requests"
)

DB_OPERATIONS = Counter(
    "career_navigator_db_operations_total",
    "Total number of database operations",
    ["operation", "collection"]
)

API_INFO = Info("career_navigator_api", "API information")