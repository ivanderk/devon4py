from typing import List

from fastapi import Depends
from sse_starlette import ServerSentEvent

from app.business.todo_management.models.todo import TodoDto, CreateTodoRequest
from app.common.services.sse import EventPublisher
from app.domain.models.todo import Todo
from app.domain.repositories.todo import TodoSQLRepository, get_todo_repository


def parse_to_dto(todo_entity: Todo):
    return TodoDto(**todo_entity.dict())


class TodoService:
    # TODO: Currently EventPublisher is only supported when workers=1
    _todoEventPublisher = EventPublisher()

    def __init__(self, repository: TodoSQLRepository = Depends(get_todo_repository)):
        self.todo_repo = repository

    def get_pending_todos(self) -> List[TodoDto]:
        raw_todos = self.todo_repo.get_pending_todos()
        todo_dtos = map(parse_to_dto, raw_todos)
        return list(todo_dtos)

    def create_todo(self, create_req: CreateTodoRequest) -> TodoDto:
        raw_new_todo = self.todo_repo.create(description=create_req.description)
        todo_dto = parse_to_dto(raw_new_todo)
        self._notify_todo_added(todo_dto)
        return todo_dto

    def add_sse(self) -> ServerSentEvent:
        _, sse = self._todoEventPublisher.subscribe()
        return sse

    def _notify_todo_added(self, todo):
        # Publish the new to_do as an event on the topic "todo_added"
        self._todoEventPublisher.publish(todo, "todo_added")

