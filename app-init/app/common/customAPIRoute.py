# fastapi 自定义Route Response Handle
# 统一格式化repsonse json格式
"""
{
    "success": False,
    "data": "",
    "errorMessage": exc.errors(),
    "traceId": traceId,
    "app": settings.app_title,
    }
"""
## 使用方式： from app.common.customAPIRoute import HandleResponseRoute
"""
router = APIRouter(
    route_class=HandleResponseRoute,
    prefix="/admin",
    tags=["admin_auth"],
    responses={404: {"detail": "Not found"}},
)
"""
## 异常处理


from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from airflow_client.client.exceptions import ApiException
import json
from fastapi.encoders import jsonable_encoder

from app.config import settings


class HandleResponseRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                response: Response = await original_route_handler(request)
                # 下面url bypass response格式化处理
                if request.url.path in [
                    "/login",
                    "/refresh",
                    "/logout",
                    "/auth/login",
                    "/auth/refresh",
                    "/auth/logout",
                ]:
                    return response
                else:
                    body = json.loads(response.body)

                    content = {
                        "success": True,
                        "data": body,
                        "errorMessage": "",
                    }

                    return JSONResponse(
                        content=content,
                        status_code=response.status_code,
                    )
            # 异常分类
            except RequestValidationError as exc:
                traceId = ""
                if settings.OTELE_TRACE == True:
                    from app.main import app_trace

                    span = app_trace.get_current_span()
                    if span:
                        traceId = "{:x}".format(span.get_span_context().trace_id)
                content = {
                    "success": False,
                    "data": "",
                    "errorMessage": exc.errors(),
                    "traceId": traceId,
                    "app": settings.app_title,
                }
                return JSONResponse(
                    status_code=422,
                    content=jsonable_encoder(content),
                )

            except AuthJWTException as exc:
                content = {
                    "success": False,
                    "data": "token",
                    "errorMessage": exc.message,
                    "traceId": "",
                    "app": settings.app_title,
                }
                return JSONResponse(status_code=401, content=content)

            except ApiException as exc:
                content = {
                    "success": False,
                    "errorMessage": exc.reason,
                    "traceId": "",
                    "app": settings.app_title,
                }
                return JSONResponse(status_code=exc.status, content=content)

            except HTTPException as exc:
                status_code = exc.status_code
                errorMessage = exc.detail

                traceId = ""
                if settings.OTELE_TRACE == True:
                    from app.main import app_trace

                    span = app_trace.get_current_span()
                    if span:
                        # FIXME if some request error, async request raise runtime error
                        try:
                            request_params = await request.json()
                            span.set_attribute("query", json.dumps(request_params))
                        except RuntimeError as e:
                            print(e)
                        except Exception as e:
                            print(e)

                        traceId = "{:x}".format(span.get_span_context().trace_id)

                content = {
                    "success": False,
                    "data": "",
                    "errorMessage": errorMessage,
                    "traceId": traceId,
                    "app": settings.app_title,
                }

                return JSONResponse(
                    content=content,
                    status_code=status_code,
                )

        return custom_route_handler
