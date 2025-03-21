# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Tuple

from nvflare.apis.event_type import EventType
from nvflare.apis.fl_component import FLComponent
from nvflare.apis.fl_constant import FLContextKey
from nvflare.apis.fl_context import FLContext
from nvflare.apis.job_def import JobMetaKey


class CustomSecurityHandler(FLComponent):
    def handle_event(self, event_type: str, fl_ctx: FLContext):
        if event_type == EventType.AUTHORIZE_COMMAND_CHECK:
            result, reason = self.authorize(fl_ctx=fl_ctx)
            if not result:
                fl_ctx.set_prop(FLContextKey.AUTHORIZATION_RESULT, False, sticky=False)
                fl_ctx.set_prop(FLContextKey.AUTHORIZATION_REASON, reason, sticky=False)

    def authorize(self, fl_ctx: FLContext) -> Tuple[bool, str]:
        command = fl_ctx.get_prop(FLContextKey.COMMAND_NAME)
        if command in ["check_resources"]:
            security_items = fl_ctx.get_prop(FLContextKey.SECURITY_ITEMS)
            job_meta = security_items.get(FLContextKey.JOB_META)
            if job_meta.get(JobMetaKey.JOB_NAME) == "secret-job":
                return False, f"Not authorized to execute: {command}"
            else:
                return True, ""
        else:
            return True, ""
