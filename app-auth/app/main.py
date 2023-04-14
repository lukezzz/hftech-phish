from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.config import settings
from app.common.fastapi_logger import fastapi_logger

from app.db.session import engine
from app.api import (
    auth,
    user,
)
from app.common.redis import register_auth_redis, register_data_redis
from app.openapidoc import tags_metadata


# Base.metadata.create_all(bind=engine)


from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import add_pagination

app: Any = FastAPI(title=settings.app_title, openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# set log level
fastapi_logger.setLevel(settings.LOGGING_LEVEL)

app_trace = None

# if settings.OTELE_TRACE == True:
#     from opentelemetry import trace
#     from opentelemetry.exporter import jaeger
#     from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
#         OTLPSpanExporter,
#     )
#     from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
#     from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
#     from opentelemetry.sdk.resources import Resource

#     # from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
#     from opentelemetry.sdk.trace import TracerProvider
#     from opentelemetry.sdk.trace.export import BatchSpanProcessor

#     resource = Resource(attributes={"service.name": settings.app_title})
#     trace.set_tracer_provider(TracerProvider(resource=resource))
#     tracer = trace.get_tracer(__name__)

#     otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)

#     span_processor = BatchSpanProcessor(otlp_exporter)

#     trace.get_tracer_provider().add_span_processor(span_processor)

#     FastAPIInstrumentor.instrument_app(app)

#     SQLAlchemyInstrumentor().instrument(engine=engine)

#     app_trace = trace
# else:
#     pass


@AuthJWT.load_config
def get_config():
    return settings


app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user_account")

# pagination
add_pagination(app)

# auth redis
register_auth_redis(app, settings.AUTH_REDIS_URI)

# register data redis
register_data_redis(app, settings.MESSAGE_REDIS_URI)

# mongodb client
# register_mongodb_client(app, settings.MONGODB_URL)
