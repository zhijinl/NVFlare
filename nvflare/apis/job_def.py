# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
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

from enum import Enum
from typing import Dict, List, Optional

from nvflare.apis.fl_constant import SystemComponents
from nvflare.apis.fl_context import FLContext


class RunStatus(str, Enum):

    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    DISPATCHED = "DISPATCHED"
    RUNNING = "RUNNING"
    FINISHED_COMPLETED = "FINISHED:COMPLETED"
    FINISHED_ABORTED = "FINISHED:ABORTED"


class JobMetaKey(str, Enum):
    STUDY_NAME = "study_name"
    JOB_ID = "job_id"
    JOB_FOLDER_NAME = "job_folder_name"
    STATUS = "status"
    DEPLOY_MAP = "deploy_map"
    RESOURCE_SPEC = "resource_spec"
    CONTENT_LOCATION = "content_location"
    RESULT_LOCATION = "result_location"
    APPROVALS = "approvals"
    MIN_CLIENTS = "min_clients"
    MANDATORY_CLIENTS = "mandatory_clients"
    SUBMIT_TIME = "submit_time"
    SUBMIT_TIME_ISO = "submit_time_iso"

    def __repr__(self):
        return self.value


class Job:
    def __init__(
        self,
        job_id: str,
        study_name: str,
        resource_spec: Dict[str, Dict],
        deploy_map: Dict[str, List[str]],
        meta,
        min_sites: int = 1,
        required_sites: Optional[List[str]] = None,
    ):
        """Job object containing the job metadata.

        Args:
            job_id: Job ID
            study_name: Study name
            resource_spec: Resource specification with information on the resources of each client
            deploy_map: Deploy map specifying each app and the sites that it should be deployed to
            meta: full contents of the persisted metadata for the job for persistent storage
            min_sites (int): minimum number of sites
            required_sites: A list of required site names
        """
        self.job_id = job_id
        self.study = study_name
        self.resource_spec = resource_spec  # resource_requirements should be {site name: resource}
        self.deploy_map = deploy_map  # should be {app name: a list of sites}

        self.meta = meta
        self.min_sites = min_sites
        self.required_sites = required_sites
        if not self.required_sites:
            self.required_sites = []

        self.dispatcher_id = None
        self.dispatch_time = None

        self.submit_time = None

        self.run_record = None  # run number, dispatched time/UUID, finished time, completion code (normal, aborted)

    def get_deployment(self) -> Dict[str, List[str]]:
        """Returns the deployment configuration.

        ::

            "deploy_map": {
                "hello-numpy-sag-server": [
                  "server"
                ],
                "hello-numpy-sag-client": [
                  "client1",
                  "client2"
                ],
                "hello-numpy-sag-client3": [
                  "client3"
                ]
              },

        Returns:
            Contents of deploy_map as a dictionary of strings of app names with their corresponding sites
        """
        return self.deploy_map

    def get_application(self, app_name, fl_ctx: FLContext) -> bytes:
        """Get the application content in bytes for the specified participant."""
        # application_name = self.get_application_name(participant)
        engine = fl_ctx.get_engine()
        job_def_manager = engine.get_component(SystemComponents.JOB_MANAGER)
        # # if not isinstance(job_def_manager, JobDefManagerSpec):
        # #     raise TypeError(f"job_def_manager must be JobDefManagerSpec type. Got: {type(job_def_manager)}")
        return job_def_manager.get_app(self, app_name, fl_ctx)

    def get_application_name(self, participant):
        """Get the application name for the specified participant."""
        for app in self.deploy_map:
            for site in self.deploy_map[app]:
                if site == participant:
                    return app
        return None

    def get_resource_requirements(self):
        """Returns app resource requirements.

        Returns:
            A dict of {site_name: resource}
        """
        return self.resource_spec

    def __eq__(self, other):
        return self.job_id == other.job_id


def job_from_meta(meta: dict) -> Job:
    """Converts information in meta into a Job object.

    Args:
        meta: dict of meta information

    Returns:
        A Job object.
    """
    job = Job(
        meta.get(JobMetaKey.JOB_ID),
        meta.get(JobMetaKey.STUDY_NAME),
        meta.get(JobMetaKey.RESOURCE_SPEC),
        meta.get(JobMetaKey.DEPLOY_MAP),
        meta,
    )
    return job