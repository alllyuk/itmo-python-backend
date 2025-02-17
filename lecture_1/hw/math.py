import json
from math import factorial
from urllib.parse import parse_qs


async def get_request_body(receive):
    body = b""
    more_body = True

    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    return body


async def send_response(send, status, body):
    if isinstance(body, dict):
        body = json.dumps(body)
        headers = [[b"content-type", b"application/json"]]
    else:
        body = str(body)
        headers = [[b"content-type", b"text/plain"]]

    await send({
        "type": "http.response.start",
        "status": status,
        "headers": headers,
    })
    await send({
        "type": "http.response.body",
        "body": body.encode("utf-8")
    })


def fibonacci(n: int) -> int:
    if n <= 2:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)


def mean(arr: list) -> float:
    return sum(arr) / len(arr)



async def app(scope, receive, send):

    if scope["method"] != "GET":
        status = 404
        body = "Not Found"

        await send_response(send, status, body)

    else:

        path = scope["path"].strip("/").split("/")
        method = path[0]

        if method== "factorial":
            try:
                n = int(parse_qs(scope["query_string"].decode("utf-8")).get("n")[0])
                if n < 0:
                    status = 400
                    body = "Bad Request"
                else:
                    status = 200
                    body = {"result": factorial(n)}

            except:
                status = 422
                body = "Unprocessed entity"

            await send_response(send, status, body)


        elif method == "fibonacci":
            if len(path) == 2:
                try:
                    n = int(path[1])
                    if n < 0:
                        status = 400
                        body = "Bad Request"
                    else:
                        status = 200
                        body = {"result": fibonacci(n)}
                except:
                    status = 422
                    body = "Unprocessable Entity"
                await send_response(send, status, body)

            else:
                status = 404
                body = "Not Found"

            await send_response(send, status, body)

        elif method == "mean":
            body = await get_request_body(receive)
            try:
                array = json.loads(body.decode("utf-8"))
                if not array:
                    status = 400
                    body = "Bad Request"
                else:
                    status = 200
                    body = {"result": mean(array)}

            except json.JSONDecodeError:
                status = 422
                body = "Unprocessable Entity"

            await send_response(send, status, body)

        else:
            response_body = "Not Found"
            await send_response(send, 404, response_body)
