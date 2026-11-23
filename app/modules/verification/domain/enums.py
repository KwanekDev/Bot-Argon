from enum import Enum


class VerificationStatus(str, Enum):
    SUCCESS = "success"
    FAIL_CODE = "fail_code"
    FAIL_NOTFOUND = "fail_notfound"
    FAIL_EXPIRED = "fail_expired"
    ALREADY_LINKED = "already_linked"
    NO_PENDING = "no_pending"

