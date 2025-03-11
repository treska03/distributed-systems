from pydantic import BaseModel


class Option(BaseModel):
  name: str
  value: bool = False

class Question(BaseModel):
  title: str
  options: list[Option]

class Poll(BaseModel):
  id: int
  poll_title: str
  questions: list[Question]

class PollCreateUpdateDto(BaseModel):
  poll_title: str
  questions: list[Question]

class VoteCreateUpdateDto(BaseModel):
  options: list[Option]

class Vote(BaseModel):
  id: int
  options: list[Option]

class Votes(BaseModel):
  poll_id: int
  votes: list[Vote]