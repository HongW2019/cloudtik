import copy
import os
import urllib
from unittest.mock import Mock

import pytest
import re
import tempfile
import threading
import time
import unittest
import yaml

from jsonschema.exceptions import ValidationError
from subprocess import CalledProcessError
from typing import Dict, Callable, List, Optional, Any


from cloudtik.core._private.cluster.cluster_scaler import ClusterScaler
from cloudtik.core._private.docker import validate_docker_config
from cloudtik.core._private.prometheus_metrics import ClusterPrometheusMetrics
from cloudtik.core._private.utils import prepare_config, validate_config, fillout_defaults, fill_node_type_min_max_workers
from cloudtik.core._private.cluster import cluster_operator
from cloudtik.core._private.cluster.cluster_metrics import ClusterMetrics
from cloudtik.core._private.providers import (
    _NODE_PROVIDERS, _DEFAULT_CONFIGS)

from cloudtik.core.node_provider import NodeProvider
from cloudtik.core.tags import CLOUDTIK_TAG_NODE_KIND, CLOUDTIK_TAG_NODE_STATUS, \
    CLOUDTIK_TAG_USER_NODE_TYPE, CLOUDTIK_TAG_CLUSTER_NAME


class MockNode:
    def __init__(self, node_id, tags, node_config, node_type,
                 unique_ips=False):
        self.node_id = node_id
        self.state = "pending"
        self.tags = {**tags, CLOUDTIK_TAG_USER_NODE_TYPE: "head.default"}
        self.external_ip = "1.2.3.4"
        self.internal_ip = "172.0.0.{}".format(self.node_id)
        if unique_ips:
            self.external_ip = f"1.2.3.{self.node_id}"

        self.node_config = node_config
        self.node_type = node_type

    def matches(self, tags):
        for k, v in tags.items():
            if k not in self.tags or self.tags[k] != v:
                return False
        return True


class MockProcessRunner:
    def __init__(self, fail_cmds=None, cmd_to_callback=None, print_out=False):
        self.calls = []
        self.cmd_to_callback = cmd_to_callback or {
        }  # type: Dict[str, Callable]
        self.print_out = print_out
        self.fail_cmds = fail_cmds or []
        self.call_response = {}
        self.ready_to_run = threading.Event()
        self.ready_to_run.set()

        self.lock = threading.RLock()

    def check_call(self, cmd, *args, **kwargs):
        with self.lock:
            self.ready_to_run.wait()
            self.calls.append(cmd)
            if self.print_out:
                print(f">>>Process runner: Executing \n {str(cmd)}")
            for token in self.cmd_to_callback:
                if token in str(cmd):
                    # Trigger a callback if token is in cmd.
                    # Can be used to simulate background events during a node
                    # update (e.g. node disconnected).
                    callback = self.cmd_to_callback[token]
                    callback()

            for token in self.fail_cmds:
                if token in str(cmd):
                    raise CalledProcessError(1, token,
                                             "Failing command on purpose")

    def check_output(self, cmd):
        with self.lock:
            self.check_call(cmd)
            return_string = "command-output"
            key_to_shrink = None
            for pattern, response_list in self.call_response.items():
                if pattern in str(cmd):
                    return_string = response_list[0]
                    key_to_shrink = pattern
                    break
            if key_to_shrink:
                self.call_response[key_to_shrink] = self.call_response[
                    key_to_shrink][1:]
                if len(self.call_response[key_to_shrink]) == 0:
                    del self.call_response[key_to_shrink]

            return return_string.encode()

    def assert_has_call(self,
                        ip: str,
                        pattern: Optional[str] = None,
                        exact: Optional[List[str]] = None):
        """Checks if the given value was called by this process runner.

        NOTE: Either pattern or exact must be specified, not both!

        Args:
            ip: IP address of the node that the given call was executed on.
            pattern: RegEx that matches one specific call.
            exact: List of strings that when joined exactly match one call.
        """
        with self.lock:
            assert bool(pattern) ^ bool(exact), \
                "Must specify either a pattern or exact match."
            debug_output = ""
            if pattern is not None:
                for cmd in self.command_history():
                    if ip in cmd:
                        debug_output += cmd
                        debug_output += "\n"
                    if re.search(pattern, cmd):
                        return True
                else:
                    raise Exception(
                        f"Did not find [{pattern}] in [{debug_output}] for "
                        f"ip={ip}.\n\nFull output: {self.command_history()}")
            elif exact is not None:
                exact_cmd = " ".join(exact)
                for cmd in self.command_history():
                    if ip in cmd:
                        debug_output += cmd
                        debug_output += "\n"
                    if cmd == exact_cmd:
                        return True
                raise Exception(
                    f"Did not find [{exact_cmd}] in [{debug_output}] for "
                    f"ip={ip}.\n\nFull output: {self.command_history()}")

    def assert_not_has_call(self, ip: str, pattern: str):
        """Ensure that the given regex pattern was never called.
        """
        with self.lock:
            out = ""
            for cmd in self.command_history():
                if ip in cmd:
                    out += cmd
                    out += "\n"
            if re.search(pattern, out):
                raise Exception("Found [{}] in [{}] for {}".format(
                    pattern, out, ip))
            else:
                return True

    def clear_history(self):
        with self.lock:
            self.calls = []

    def command_history(self):
        with self.lock:
            return [" ".join(cmd) for cmd in self.calls]

    def respond_to_call(self, pattern, response_list):
        with self.lock:
            self.call_response[pattern] = response_list


class MockProvider(NodeProvider):
    def __init__(self, cache_stopped=False, unique_ips=False):
        self.mock_nodes = {}
        self.next_id = 0
        self.throw = False
        self.error_creates = False
        self.fail_creates = False
        self.ready_to_create = threading.Event()
        self.ready_to_create.set()
        self.cache_stopped = cache_stopped
        self.unique_ips = unique_ips
        # Many of these functions are called by node_launcher or updater in
        # different threads. This can be treated as a global lock for
        # everything.
        self.num_non_terminated_nodes_calls = 0
        self.lock = threading.Lock()
        super().__init__(None, None)

    def non_terminated_nodes(self, tag_filters):
        with self.lock:
            if self.throw:
                raise Exception("oops")
            return [
                n.node_id for n in self.mock_nodes.values()
                if n.matches(tag_filters)
                and n.state not in ["stopped", "terminated"]
            ]

    def non_terminated_node_ips(self, tag_filters):
        with self.lock:
            if self.throw:
                raise Exception("oops")
            return [
                n.internal_ip for n in self.mock_nodes.values()
                if n.matches(tag_filters)
                and n.state not in ["stopped", "terminated"]
            ]

    def is_running(self, node_id):
        with self.lock:
            return self.mock_nodes[node_id].state == "running"

    def is_terminated(self, node_id):
        with self.lock:
            return self.mock_nodes[node_id].state in ["stopped", "terminated"]

    def node_tags(self, node_id):
        # Don't assume that node providers can retrieve tags from
        # terminated nodes.
        if self.is_terminated(node_id):
            raise Exception(f"The node with id {node_id} has been terminated!")
        with self.lock:
            return self.mock_nodes[node_id].tags

    def internal_ip(self, node_id):
        with self.lock:
            return self.mock_nodes[node_id].internal_ip

    def external_ip(self, node_id):
        with self.lock:
            return self.mock_nodes[node_id].external_ip

    def create_node(self, node_config, tags, count, _skip_wait=False):
        if self.error_creates:
            raise Exception
        if not _skip_wait:
            self.ready_to_create.wait()
        if self.fail_creates:
            return
        with self.lock:
            if self.cache_stopped:
                for node in self.mock_nodes.values():
                    if node.state == "stopped" and count > 0:
                        count -= 1
                        node.state = "pending"
                        node.tags.update(tags)
            for _ in range(count):
                self.mock_nodes[self.next_id] = MockNode(
                    self.next_id,
                    tags.copy(),
                    node_config,
                    tags.get(CLOUDTIK_TAG_USER_NODE_TYPE),
                    unique_ips=self.unique_ips)
                self.next_id += 1

    def set_node_tags(self, node_id, tags):
        with self.lock:
            self.mock_nodes[node_id].tags.update(tags)

    def terminate_node(self, node_id):
        with self.lock:
            if self.cache_stopped:
                self.mock_nodes[node_id].state = "stopped"
            else:
                self.mock_nodes[node_id].state = "terminated"

    def finish_starting_nodes(self):
        with self.lock:
            for node in self.mock_nodes.values():
                if node.state == "pending":
                    node.state = "running"

    def with_environment_variables(self, node_type_config: Dict[str, Any], node_id: str):
        return {}


class MockClusterScaler(ClusterScaler):
    """Test ClusterScaler constructed to verify the property that each
    ClusterScaler update issues at most one provider.non_terminated_nodes call.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_to_find_ip_during_drain = False

    def _publish_runtime_config(self, *args):
        return

    def _publish_runtime_configs(self):
        return

    def _update(self):
        # Only works with MockProvider
        assert isinstance(self.provider, MockProvider)
        start_calls = self.provider.num_non_terminated_nodes_calls
        super()._update()
        end_calls = self.provider.num_non_terminated_nodes_calls

        # Strict inequality if update is called twice within the throttling
        # interval `self.update_interval_s`
        assert end_calls <= start_calls + 1


SMALL_CLUSTER = {
    "cluster_name": "default",
    "min_workers": 2,
    "max_workers": 2,
    "idle_timeout_minutes": 5,
    "provider": {
        "type": "mock",
        "region": "us-east-1",
        "availability_zone": "us-east-1a",
    },
    "docker": {
        "enabled": True,
        "image": "example",
        "container_name": "mock",
    },
    "auth": {
        "ssh_user": "ubuntu",
        "ssh_private_key": os.devnull,
    },
    "head_node": {
        "TestProp": 1,
    },
    "file_mounts": {},
    "cluster_synced_files": [],
    "initialization_commands": ["init_cmd"],
    "setup_commands": ["setup_cmd"],
    "head_setup_commands": ["head_setup_cmd"],
    "worker_setup_commands": ["worker_setup_cmd"],
    "head_start_commands": ["head_start_cmd"],
    "worker_start_commands": ["worker_start_cmd"],
    "merged_commands": {},
    "runtime": {
        "types": ["spark", "ganglia"]
    },
}

MOCK_DEFAULT_CONFIG = {
    "cluster_name": "default",
    "max_workers": 2,
    "idle_timeout_minutes": 5,
    "provider": {
        "type": "aws",
        "region": "us-east-1",
        "availability_zone": "us-east-1a",
    },
    "docker": {
        "enabled": True,
        "image": "example",
        "container_name": "mock",
    },
    "auth": {
        "ssh_user": "ubuntu",
        "ssh_private_key": os.devnull,
    },
    "available_node_types": {
        "cloudtik.head.default": {
            "resources": {},
            "node_config": {
                "head_default_prop": 4
            }
        },
        "cloudtik.worker.default": {
            "min_workers": 0,
            "max_workers": 2,
            "resources": {},
            "node_config": {
                "worker_default_prop": 7
            }
        }
    },
    "head_node_type": "cloudtik.head.default",
    "head_node": {},
    "file_mounts": {},
    "cluster_synced_files": [],
    "initialization_commands": [],
    "setup_commands": [],
    "head_setup_commands": [],
    "worker_setup_commands": [],
    "head_start_commands": [],
    "worker_start_commands": [],
}

TYPES_A = {
    "empty_node": {
        "node_config": {
            "FooProperty": 42,
        },
        "resources": {},
        "max_workers": 0,
    },
    "m4.large": {
        "node_config": {},
        "resources": {
            "CPU": 2
        },
        "max_workers": 10,
    },
    "m4.4xlarge": {
        "node_config": {},
        "resources": {
            "CPU": 16
        },
        "max_workers": 8,
    },
    "m4.16xlarge": {
        "node_config": {},
        "resources": {
            "CPU": 64
        },
        "max_workers": 4,
    },
    "p2.xlarge": {
        "node_config": {},
        "resources": {
            "CPU": 16,
            "GPU": 1
        },
        "max_workers": 10,
    },
    "p2.8xlarge": {
        "node_config": {},
        "resources": {
            "CPU": 32,
            "GPU": 8
        },
        "max_workers": 4,
    },
}

MULTI_WORKER_CLUSTER = dict(
    SMALL_CLUSTER, **{
        "available_node_types": TYPES_A,
        "head_node_type": "empty_node"
    })


class ClusterMetricsTest(unittest.TestCase):
    def testHeartbeat(self):
        cluster_metrics = ClusterMetrics()
        cluster_metrics.update("1.1.1.1", b'\xb6\x80\xbdw\xbd\x1c\xee\xf6@\x11', None, {"CPU": 2}, {"CPU": 1}, {})
        cluster_metrics.mark_active("2.2.2.2")
        assert "1.1.1.1" in cluster_metrics.last_heartbeat_time_by_ip
        assert "2.2.2.2" in cluster_metrics.last_heartbeat_time_by_ip
        assert "3.3.3.3" not in cluster_metrics.last_heartbeat_time_by_ip


class CloudTikTest(unittest.TestCase):
    def setUp(self):
        _NODE_PROVIDERS["mock"] = lambda config: self.create_provider
        _DEFAULT_CONFIGS["mock"] = _DEFAULT_CONFIGS["aws"]
        self.provider = None
        self.tmpdir = tempfile.mkdtemp()

    def waitForNodes(self, expected, comparison=None, tag_filters=None):
        if tag_filters is None:
            tag_filters = {}

        MAX_ITER = 50
        for i in range(MAX_ITER):
            n = len(self.provider.non_terminated_nodes(tag_filters))
            if comparison is None:
                comparison = self.assertEqual
            try:
                comparison(n, expected, msg="Unexpected node quantity.")
                return
            except Exception:
                if i == MAX_ITER - 1:
                    raise
            time.sleep(.1)

    def create_provider(self, config, cluster_name):
        assert self.provider
        return self.provider

    def write_config(self, config, call_prepare_config=True):
        new_config = copy.deepcopy(config)
        if call_prepare_config:
            with_defaults = fillout_defaults(config)
            validate_docker_config(with_defaults)
            fill_node_type_min_max_workers(with_defaults)
            new_config = with_defaults
        path = os.path.join(self.tmpdir, "simple.yaml")
        with open(path, "w") as f:
            f.write(yaml.dump(new_config))
        return path

    def testValidateDefaultConfig(self):
        config = {"provider": {
            "type": "aws",
            "region": "us-east-1",
            "availability_zone": "us-east-1a",
        }}
        config = prepare_config(config)
        try:
            validate_config(config)
        except ValidationError:
            self.fail("Default config did not pass validation test!")

    def testValidation(self):
        """Ensures that schema validation is working."""
        config = copy.deepcopy(MOCK_DEFAULT_CONFIG)
        try:
            validate_config(config)
        except Exception:
            self.fail("Test config did not pass validation test!")

        config["blah"] = "blah"
        with pytest.raises(ValidationError):
            validate_config(config)
        del config["blah"]

        del config["provider"]
        with pytest.raises(ValidationError):
            validate_config(config)

    def testClusterScalerConfigValidationFailNotFatal(self):
        invalid_config = {**SMALL_CLUSTER, "invalid_property_12345": "test"}
        # First check that this config is actually invalid
        with pytest.raises(ValidationError):
            validate_config(invalid_config)
        config_path = self.write_config(invalid_config)
        self.provider = MockProvider()
        runner = MockProcessRunner()
        autoscaler = MockClusterScaler(
            config_path,
            ClusterMetrics(),
            max_failures=0,
            process_runner=runner,
            update_interval_s=0,
        )
        assert len(self.provider.non_terminated_nodes({})) == 0
        autoscaler.update()
        self.waitForNodes(2)
        autoscaler.update()
        self.waitForNodes(2)

    def testGetRunningHeadNode(self):
        config = copy.deepcopy(SMALL_CLUSTER)
        self.provider = MockProvider()

        # Node 0 is failed.
        self.provider.create_node({}, {
            CLOUDTIK_TAG_CLUSTER_NAME: "default",
            CLOUDTIK_TAG_NODE_KIND: "head",
            CLOUDTIK_TAG_NODE_STATUS: "update-failed"
        }, 1)

        # `_allow_uninitialized_state` should return the head node
        # in the `update-failed` state.
        allow_failed = cluster_operator._get_running_head_node(
            config,
            _provider=self.provider,
            _allow_uninitialized_state=True)

        assert allow_failed == 0

        # Node 1 is okay.
        self.provider.create_node({}, {
            CLOUDTIK_TAG_CLUSTER_NAME: "default",
            CLOUDTIK_TAG_NODE_KIND: "head",
            CLOUDTIK_TAG_NODE_STATUS: "up-to-date"
        }, 1)

        node = cluster_operator._get_running_head_node(
            config,
            _provider=self.provider)

        assert node == 1

        # `_allow_uninitialized_state` should return the up-to-date head node
        # if it is present.
        optionally_failed = cluster_operator._get_running_head_node(
            config,
            _provider=self.provider,
            _allow_uninitialized_state=True)

        assert optionally_failed == 1

    def testDefaultMinMaxWorkers(self):
        config = copy.deepcopy(MOCK_DEFAULT_CONFIG)
        config = prepare_config(config)
        node_types = config["available_node_types"]
        head_node_config = node_types["cloudtik.head.default"]
        assert head_node_config["min_workers"] == 0
        assert head_node_config["max_workers"] == 0

    def testValidateNetworkConfig(self):
        web_yaml = ("https://raw.githubusercontent.com/oap-project/cloudtik/main/python/cloudtik/templates/aws/small"
                    ".yaml")
        response = urllib.request.urlopen(web_yaml, timeout=5)
        content = response.read()
        with tempfile.TemporaryFile() as f:
            f.write(content)
            f.seek(0)
            config = yaml.safe_load(f)
        config = prepare_config(config)
        try:
            validate_config(config)
        except Exception:
            self.fail("Config did not pass validation test!")

    def testProviderException(self):
        config_path = self.write_config(SMALL_CLUSTER)
        self.provider = MockProvider()
        self.provider.error_creates = True
        runner = MockProcessRunner()
        mock_metrics = Mock(spec=ClusterPrometheusMetrics())
        autoscaler = MockClusterScaler(
            config_path,
            ClusterMetrics(),
            max_failures=0,
            process_runner=runner,
            update_interval_s=0,
            prometheus_metrics=mock_metrics,
        )
        autoscaler.update()


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(["-v", __file__]))
