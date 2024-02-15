from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta.threads import Run
from openai.types.beta.threads.runs import RunStep

from src.autobots.conn.openai.openai_assistants.openai_thread_runs.openai_thread_runs_model import (
    ThreadRunCreate,
    ThreadRunRetrieve,
    ThreadRunUpdate,
    ThreadRunList,
    ThreadRunSubmitToolOutputs,
    ThreadRunCancel,
    ThreadRunStepList,
    ThreadRunStepRetrieve,
)


class OpenaiThreadRuns:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create(self, thread_run_create: ThreadRunCreate) -> Run | None:
        try:
            return await self.client.beta.threads.runs.create(
                **thread_run_create.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def retrieve(self, thread_run_retrieve: ThreadRunRetrieve) -> Run | None:
        try:
            return await self.client.beta.threads.runs.retrieve(
                **thread_run_retrieve.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def update(self, thread_run_update: ThreadRunUpdate) -> Run | None:
        try:
            return await self.client.beta.threads.runs.update(
                **thread_run_update.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def list(
        self, thread_run_list: ThreadRunList
    ) -> AsyncPaginator[Run, AsyncCursorPage[Run]]:
        try:
            return await self.client.beta.threads.runs.list(
                **thread_run_list.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def submit_tool_outputs(
        self, thread_run_submit_tool_outputs: ThreadRunSubmitToolOutputs
    ) -> Run | None:
        try:
            return await self.client.beta.threads.runs.submit_tool_outputs(
                **thread_run_submit_tool_outputs.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def cancel(self, thread_run_cancel: ThreadRunCancel) -> Run | None:
        try:
            return await self.client.beta.threads.runs.cancel(
                **thread_run_cancel.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def retrieve_run_step(
        self, thread_run_step_retrieve: ThreadRunStepRetrieve
    ) -> RunStep | None:
        try:
            return await self.client.beta.threads.runs.steps.retrieve(
                **thread_run_step_retrieve.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def list_run_steps(
        self, thread_run_step_list: ThreadRunStepList
    ) -> AsyncPaginator[RunStep, AsyncCursorPage[RunStep]]:
        try:
            return await self.client.beta.threads.runs.steps.list(
                **thread_run_step_list.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))
