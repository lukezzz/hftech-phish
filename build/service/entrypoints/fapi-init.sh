#!/bin/bash
set -e

sleep 2

export PYTHONPATH=/usr/src/app
cd /usr/src/app

#if (test ${ENVIRONMENT} != "development"); then echo "dev env"; else alembic upgrade head; fi

#Disabled opentelemetry-instrument with opentelemetry-instrumentation-sqlalchemy brake DefaultTraceProvider
# if [ $OTELE_TRACE = "True" ]
# then
#     echo "Running with OpenTelemetry"
    opentelemetry-instrument uvicorn app.main:app --workers 4 --host=0.0.0.0 --port=80 $(test ${ENVIRONMENT} != "production" && echo "--reload")
# else
    # echo "OpenTelemetry isn't enable"
# uvicorn app.main:app --host=0.0.0.0 $(tests ${ENVIRONMENT} = "development" && echo "--reload")
# fi
