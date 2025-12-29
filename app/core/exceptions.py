class JobNotFoundError(Exception):
    """Raised when a job is not found or the user is not authorized to access it."""
    pass

class RecruiterNotFoundError(Exception):
    """Raised when a recruiter profile does not exist for the given user."""
    pass

class CandidateNotFoundError(Exception):
    """Raised when a candidate profile is not found."""
    pass

class CandidateAlreadyExistsError(Exception):
    """Raised when a candidate tries to create a profile but already has one."""
    pass

class CandidatePreferenceNotFoundError(Exception):
    """Raised when candidate preferences are not found."""
    pass

class CandidatePreferenceAlreadyExistsError(Exception):
    """Raised when a candidate already has preferences."""
    pass

class CVNotFoundError(Exception):
    """Raised when a CV record is not found."""
    pass

class CVUploadError(Exception):
    """Raised when CV upload or processing fails."""
    pass

class CVDownloadError(Exception):
    """Raised when CV download"""
    pass

class JobApplicationNotFoundError(Exception):
    """Raised when a job application is not found."""
    pass

class JobApplicationAlreadyExistsError(Exception):
    """Raised when a candidate tries to apply to the same job twice."""
    pass

class JobApplicationPermissionError(Exception):
    """Raised when a user lacks permission to perform an action on a job application."""
    pass

class AIScreeningNotFoundError(Exception):
    """Raised when AI screening results are not found for a job."""
    pass


class AIInterviewQuestionNotFoundError(Exception):
    """Raised when AI interview questions are not found for a job."""
    pass


class AIScreeningNotReadyError(Exception):
    """
    Raised when a job is not closed yet or AI screening
    has not been generated.
    """
    pass