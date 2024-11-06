#!/usr/bin/env python3

import os
from pprint import pprint

import slugid
import taskcluster
from taskgraph.util.parameterization import resolve_timestamps
from taskgraph.util.time import current_json_time

INDEX_PATHS = ["gecko.v2.mozilla-central.latest.taskgraph.decision-os-integration"]

if "TASKCLUSTER_PROXY_URL" in os.environ:
    options = {"rootUrl": os.environ["TASKCLUSTER_PROXY_URL"]}
else:
    options = taskcluster.optionsFromEnvironment()

index = taskcluster.Index(options)
queue = taskcluster.Queue(options)
secrets = taskcluster.Secrets(options)

result = secrets.get("project/releng/fxci-config/taskcluster-stage-client")
assert result

stage_auth = result["secret"]
assert isinstance(stage_auth, dict)

print(f"clientId: {stage_auth['clientId']}")
queue_stage = taskcluster.Queue(
    {
        "rootUrl": "https://stage.taskcluster.nonprod.cloudops.mozgcp.net/",
        "credentials": stage_auth,
    }
)

for path in INDEX_PATHS:
    data = index.findTask(path)
    assert data
    task_id = data["taskId"]

    task_graph = queue.getLatestArtifact(task_id, "public/task-graph.json")
    assert task_graph

    for label, task in task_graph.items():
        assert isinstance(task, dict)
        if task.get("attributes", {}).get("unittest_variant") != "os-integration":
            continue

        task_def = task["task"]
        task_def["priority"] = "low"
        del task_def["dependencies"]
        del task_def["routes"]

        now = current_json_time(datetime_format=True)
        task_def = resolve_timestamps(now, task_def)

        pprint(task_def, indent=2)
        queue_stage.createTask(slugid.nice(), task_def)
