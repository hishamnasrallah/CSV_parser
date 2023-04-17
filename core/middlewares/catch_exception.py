import logging
import time
from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware
from core.middlewares import log_requests
from utils.http_response import http_response

logger = logging.getLogger(__name__)


class ExceptionMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await log_requests(request, call_next)
            return response
        except Exception as e:
            wrap = "\""
            print("-> error log <-")
            logger.info(f"{wrap}request: {request.method} {request.url.path} "
                        f"{request.url.query}{wrap}")
            print("request body:", Request.body.__dict__)
            start_time = time.time()
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = '{0:.2f}'.format(process_time)
            print("Response:")
            try:
                status = e.args[1]

                if len(e.args) == 3:
                    message = {e.args[2]: e.args[0][e.args[2]]}
                    logger.error(
                        f"{wrap}response: {400} in {formatted_process_time}ms{wrap}, message: {message}, field: {e.args[2]} ")


                elif len(e.args) == 2:
                    message = e.args[0]

                    logger.error(
                        f"{wrap}response: {400} in {formatted_process_time}ms{wrap}, message: {message['en']}")
                return http_response(status=status, message=message)
            except:
                logger.error(
                    f"{wrap}response: {500} in {formatted_process_time}ms{wrap}, message: {e} ")
                return http_response(status=500, message=str(e))
