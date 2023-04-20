# from datetime import datetime
# from enum import Enum
# from pydantic import BaseModel, Field
# from typing import Optional, Any


# class QueryBasic(BaseModel):
#     limit: Optional[int] = 10
#     offset: Optional[int] = 0
#     order_by: Optional[str]


# class Connction(BaseModel):
#     connection_id: str
#     conn_type: str
#     host: Optional[str]
#     login: Optional[str]
#     schema_: Optional[str] = Field(alias="schema")
#     port: Optional[int]
#     password: Optional[str]
#     extra: Optional[str]


# class ScheduleInterval(BaseModel):
#     type: Optional[str]
#     days: Optional[int]
#     seconds: Optional[int]
#     microseconds: Optional[int]
#     years: Optional[int]
#     months: Optional[int]
#     leapdays: Optional[int]
#     hours: Optional[int]
#     minutes: Optional[int]
#     year: Optional[int]
#     month: Optional[int]
#     day: Optional[int]
#     hour: Optional[int]
#     minute: Optional[int]
#     second: Optional[int]
#     microsecond: Optional[int]
#     value: Optional[str]


# class PatchDAG(BaseModel):
#     is_paused: Optional[bool]
#     schedule_interval: Optional[ScheduleInterval]


# class ClearTaskInstance(BaseModel):

#     dry_run: Optional[bool]
#     task_ids: Optional[list[str]]
#     start_date: Optional[str]
#     end_date: Optional[str]
#     only_failed: Optional[bool]
#     only_running: Optional[bool]
#     include_subdags: Optional[bool]
#     include_parentdag: Optional[bool]
#     reset_dag_runs: Optional[bool]


# class ClearTaskInstanceState(BaseModel):

#     dry_run: Optional[bool]
#     task_id: Optional[str]
#     execution_date: Optional[str]
#     include_upstream: Optional[bool]
#     include_downstream: Optional[bool]
#     include_future: Optional[bool]
#     include_past: Optional[bool]
#     new_state: Optional[str]


# class DagRunsBasic(BaseModel):
#     execution_date_gte: Optional[datetime]
#     execution_date_lte: Optional[datetime]
#     start_date_gte: Optional[datetime]
#     start_date_lte: Optional[datetime]
#     end_date_gte: Optional[datetime]
#     end_date_lte: Optional[datetime]
#     order_by: Optional[str]


# class DagRunsQuery(DagRunsBasic):
#     limit: Optional[int]
#     offset: Optional[int]


# class DagRunsBatchQuery(BaseModel):
#     page_limit: Optional[int] = 30
#     page_offset: Optional[int]
#     dag_ids: Optional[list[str]]


# class DagState(Enum):
#     QUEUED = "queued"
#     RUNNING = "running"
#     SUCCESS = "success"
#     FAILED = "failed"


# class DagRun(BaseModel):
#     dag_run_id: Optional[
#         str
#     ]  # The value of this field can be set only when creating the object.
#     logical_date: Optional[
#         str
#     ]  # The logical date (previously called execution date). This is the time or interval covered by this DAG run, according to the DAG definition.  The value of this field can be set only when creating the object. If you try to modify the field of an existing object, the request fails with an BAD_REQUEST error.  This together with DAG_ID are a unique key. . [optional]  # noqa: E501
#     execution_date: Optional[
#         datetime
#     ]  # The execution date. This is the same as logical_date, kept for backwards compatibility. If both this field and logical_date are provided but with different values, the request will fail with an BAD_REQUEST error. . [optional]  # noqa: E501
#     start_date: Optional[datetime]
#     end_date: Optional[datetime]
#     state: Optional[DagState]
#     external_trigger: Optional[bool]
#     conf: Optional[Any]

#     class Config:
#         use_enum_values = True


# class DagRunState(Enum):
#     SUCCESS = "success"
#     FAILED = "failed"


# class DagRunStateConfig(BaseModel):
#     state: DagRunState

#     class Config:
#         use_enum_values = True


# class TaskInstanceQuery(DagRunsQuery):
#     duration_gte: Optional[datetime]
#     duration_lte: Optional[datetime]
#     state: Optional[list[DagState]]
#     pool: Optional[list[str]]
#     queue: Optional[list[str]]


# class TaskInstanceBatchQuery(TaskInstanceQuery):
#     dag_ids: Optional[list[str]]


# class TaskLog(BaseModel):
#     full_content: Optional[bool]
#     token: Optional[str]


# class Pool(BaseModel):
#     name: Optional[str]
#     slots: Optional[int]


# class Variable(BaseModel):
#     key: Optional[str]
#     value: Optional[str]
