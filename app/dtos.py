from dataclasses import dataclass

@dataclass
class TrackedJob():
    title: str
    company: str
    application_status: bool
    url: str