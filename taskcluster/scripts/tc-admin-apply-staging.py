# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess

import taskcluster

assert "TASKCLUSTER_PROXY_URL" in os.environ
options = {"rootUrl": os.environ["TASKCLUSTER_PROXY_URL"]}
secrets = taskcluster.Secrets(options)

result = secrets.get("project/releng/fxci-config/taskcluster-stage-client")
assert result

auth = result["secret"]
assert isinstance(auth, dict)

env = {
    "TASKCLUSTER_ROOT_URL": "https://stage.taskcluster.nonprod.cloudops.mozgcp.net",
    "TASKCLUSTER_CLIENT_ID": auth["clientId"],
    "TASKCLUSTER_ACCESS_TOKEN": auth["accessToken"],
}
subprocess.run(["tc-admin", "apply", "--environment=staging"], env=env, check=True)
