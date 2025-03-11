from email.policy import default
from fastapi import FastAPI, HTTPException

from .models import Vote, Votes, PollCreateUpdateDto, Poll, VoteCreateUpdateDto

app=FastAPI( )

@app.get("/")
async def root() :
  return {"message" : "Hello World"}

polls_cache: dict[int, Poll] = dict() ##
votes_cache: dict[int, Votes] = dict() ## poll_id -> list[Votes]

def valid_poll_id(id: int) -> bool:
  return id in polls_cache.keys()

@app.get("/polls")
async def get_all_polls() -> list[Poll]:
  return polls_cache.values()

@app.get("/polls/{poll_id}")
async def get_poll(poll_id: int):
  if not valid_poll_id(poll_id):
    return HTTPException(status_code=404, detail="Invalid poll_id")
  return polls_cache[poll_id]

@app.post("/polls")
async def create_poll(req: PollCreateUpdateDto) -> Poll:
  id = max(polls_cache.keys(), default=0) + 1
  poll = Poll(
    id=id,
    poll_title=req.poll_title,
    questions=req.questions
  )
  polls_cache[id] = poll
  votes_cache[id] = Votes(poll_id=id, votes=[])
  return poll

@app.put("/polls/{poll_id}")
async def update_poll(poll_id: int, req: PollCreateUpdateDto):
  poll = Poll(
    id=poll_id,
    poll_title=req.poll_title,
    questions=req.questions
  )
  polls_cache[poll_id] = poll
  votes_cache[id] = Votes(poll_id=id, votes=[])
  return poll

@app.delete("/polls/{poll_id}")
async def delete_poll(poll_id: int):
  if not valid_poll_id(poll_id):
    return HTTPException(status_code=404, detail="Invalid poll_id")
  del polls_cache[poll_id]
  del votes_cache[poll_id]
  return True

@app.get("/polls/{poll_id}/votes")
async def get_all_votes(poll_id: int):
  return votes_cache[poll_id]

@app.get("/polls/{poll_id}/votes/{vote_id}")
async def get_vote(poll_id: int, vote_id: int):
  return votes_cache[poll_id].votes[vote_id]

@app.post("/polls/{poll_id}/votes")
async def vote(poll_id: int, req: VoteCreateUpdateDto):
  id = max((vote.id for vote in votes_cache[poll_id].votes), default=0) + 1
  vote = Vote(
    id=id,
    options=req.options,
  )
  votes_cache[poll_id].votes.append(vote)
  return vote

@app.put("/polls/{poll_id}/votes/{vote_id}")
async def update_poll(poll_id: int, vote_id: int, req: VoteCreateUpdateDto):
  vote = Vote(
    id=vote_id,
    options=req.options,
  )
  if not valid_poll_id(poll_id):
    return HTTPException(status_code=404, detail="Invalid poll_id")
  for idx, v in enumerate(votes_cache[poll_id].votes):
    if v.id == vote_id:
      votes_cache[poll_id].votes[idx] = vote
      return vote
  votes_cache[poll_id].votes.append(vote)
  return vote

@app.delete("/polls/{poll_id}/votes/{vote_id}")
async def delete_vote(poll_id: int, vote_id: int):
  if poll_id not in polls_cache.keys() or vote_id not in (v.id for v in votes_cache[poll_id].votes):
    return HTTPException(status_code=404, detail="Invalid poll_id or vote_id")
  to_remove = None
  for vote in votes_cache[poll_id].votes:  # lst[:] creates a shallow copy of the list
    if vote.id == vote_id:
      to_remove = vote
      break
  votes_cache[poll_id].votes.remove(to_remove)
  return True
  