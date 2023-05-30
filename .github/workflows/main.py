import fastapi
from fastapi import Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import openai
import asyncio
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

        
auth_scheme = HTTPBearer()
app = fastapi.FastAPI()

# 허용할 IP 주소 목록
allowed_ips = ["127.0.0.1", "10.200.22.232"]
        
origins = [
    "http://localhost:8000",  # Adjust the origins according to your needs
    "http://localhost", 
    "http://localhost:8080",
]
# origins = [
#     "http://117.52.164.141:8000",  # Adjust the origins according to your needs
#     "http://117.52.164.141", 
#     "http://117.52.164.141:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = api_key

@app.middleware("http")
async def check_ip_address(request: Request, call_next):
    # 클라이언트의 IP 주소 확인
    client_ip = request.client.host

    # 허용된 IP 주소인지 확인
    if client_ip not in allowed_ips:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 다음 미들웨어 또는 핸들러 함수 호출
    response = await call_next(request)
    return response


@app.get("/api/question")
async def get_answerhandle_question(question: str):
    # OpenAI API call

    return StreamingResponse(answer_gpt(question), media_type="text/event-stream")

async def answer_gpt(prompt) -> None:
    async for chunk in await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You're a training expert who answers questions from students. Short answer."},
                  {"role": "user", "content": prompt}],
        stream=True,
        temperature=1,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=[" Human:", " AI:"]
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            yield f"data: {content}\n\n"

 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="117.52.164.141", port=8000)
