from pydantic import BaseModel, ConfigDict, Field


class MeetingSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    meeting_agenda: str = Field(description="회의 안건, 최대 3줄")
    issues: str = Field(description="회의 내용에서 확인된 문제점, 최대 3줄")
    solutions: str = Field(description="문제점에 대한 해결방안, 최대 3줄")
    conclusion: str = Field(description="회의 결론, 최대 3줄")


class TodoItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    task: str
    assignee: str | None = None
    due_date: str | None = None
    priority: str | None = None


class AnalysisResult(BaseModel):
    summary: MeetingSummary
    todos: list[TodoItem]
