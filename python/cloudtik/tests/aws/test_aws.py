import pytest
from unittest.mock import Mock, patch

from cloudtik.core._private.providers import _get_node_provider
from cloudtik.providers._private.aws.node_provider import AWSNodeProvider
from cloudtik.tests.aws.utils.constants import DEFAULT_SG, DEFAULT_CLUSTER_NAME, DEFAULT_LT
import cloudtik.tests.aws.utils.stubs as stubs
import cloudtik.tests.aws.utils.helpers as helpers

#
# @pytest.mark.parametrize("num_on_demand_nodes", [0, 1001, 9999])
# @pytest.mark.parametrize("num_spot_nodes", [0, 1001, 9999])
# @pytest.mark.parametrize("stop", [True, False])
# def test_terminate_nodes(num_on_demand_nodes, num_spot_nodes, stop):
#     # This test makes sure that we stop or terminate all the nodes we're
#     # supposed to stop or terminate when we call "terminate_nodes". This test
#     # also makes sure that we don't try to stop or terminate too many nodes in
#     # a single EC2 request. By default, only 1000 nodes can be
#     # stopped/terminated in one request. To terminate more nodes, we must break
#     # them up into multiple smaller requests.
#     #
#     # "num_on_demand_nodes" is the number of on-demand nodes to stop or
#     #   terminate.
#     # "num_spot_nodes" is the number of on-demand nodes to terminate.
#     # "stop" is True if we want to stop nodes, and False to terminate nodes.
#     #   Note that spot instances are always terminated, even if "stop" is True.
#
#     # Generate a list of unique instance ids to terminate
#     on_demand_nodes = {
#         "i-{:017d}".format(i)
#         for i in range(num_on_demand_nodes)
#     }
#     spot_nodes = {
#         "i-{:017d}".format(i + num_on_demand_nodes)
#         for i in range(num_spot_nodes)
#     }
#     node_ids = list(on_demand_nodes.union(spot_nodes))
#
#     with patch("cloudtik.providers._private.aws.utils.make_ec2_client"):
#         provider = AWSNodeProvider(
#             provider_config={
#                 "region": "nowhere",
#                 "cache_stopped_nodes": stop
#             },
#             cluster_name="default")
#
#     # "_get_cached_node" is used by the AWSNodeProvider to determine whether a
#     # node is a spot instance or an on-demand instance.
#     def mock_get_cached_node(node_id):
#         result = Mock()
#         result.spot_instance_request_id = "sir-08b93456" if \
#             node_id in spot_nodes else ""
#         return result
#
#     provider._get_cached_node = mock_get_cached_node
#
#     provider.terminate_nodes(node_ids)
#
#     stop_calls = provider.ec2.meta.client.stop_instances.call_args_list
#     terminate_calls = provider.ec2.meta.client.terminate_instances \
#         .call_args_list
#
#     nodes_to_stop = set()
#     nodes_to_terminate = spot_nodes
#
#     if stop:
#         nodes_to_stop.update(on_demand_nodes)
#     else:
#         nodes_to_terminate.update(on_demand_nodes)
#
#     for calls, nodes_to_include_in_call in (stop_calls, nodes_to_stop), (
#             terminate_calls, nodes_to_terminate):
#         nodes_included_in_call = set()
#         for call in calls:
#             assert len(call[1]["InstanceIds"]) <= provider.max_terminate_nodes
#             nodes_included_in_call.update(call[1]["InstanceIds"])
#
#         assert nodes_to_include_in_call == nodes_included_in_call


def test_launch_templates(
    ec2_client_stub, ec2_client_stub_fail_fast, ec2_client_stub_max_retries
):

    # given the launch template associated with our default head node type...
    # expect to first describe the default launch template by ID
    stubs.describe_launch_template_versions_by_id_default(ec2_client_stub, ["$Latest"])
    # given the launch template associated with our default worker node type...
    # expect to next describe the same default launch template by name
    stubs.describe_launch_template_versions_by_name_default(ec2_client_stub, ["2"])
    # use default stubs to skip ahead to subnet configuration
    stubs.configure_key_pair_default(ec2_client_stub)

    # given the security groups associated with our launch template...
    sgids = [DEFAULT_SG["GroupId"]]
    security_groups = [DEFAULT_SG]
    # expect to describe all security groups to ensure they share the same VPC
    stubs.describe_sgs_by_id(ec2_client_stub, sgids, security_groups)

    # use a default stub to skip subnet configuration
    stubs.configure_subnet_default(ec2_client_stub)

    # given our mocks and an example config file as input...
    # expect the config to be loaded, validated, and bootstrapped successfully
    config = helpers.bootstrap_aws_example_config_file("example-launch-templates.yaml")

    # instantiate a new node provider
    new_provider = _get_node_provider(
        config["provider"],
        DEFAULT_CLUSTER_NAME,
        False,
    )

    max_count = 1
    for name, node_type in config["available_node_types"].items():
        # given our bootstrapped node config as input to create a new node...
        # expect to first describe all stopped instances that could be reused
        stubs.describe_instances_with_any_filter_consumer(ec2_client_stub_max_retries)
        # given no stopped EC2 instances to reuse...
        # expect to create new nodes with the given launch template config
        node_cfg = node_type["node_config"]
        stubs.run_instances_with_launch_template_consumer(
            ec2_client_stub_fail_fast,
            config,
            node_cfg,
            name,
            DEFAULT_LT["LaunchTemplateData"],
            max_count,
        )
        tags = helpers.node_provider_tags(config, name)
        new_provider.create_node(node_cfg, tags, max_count)

    ec2_client_stub.assert_no_pending_responses()
    ec2_client_stub_fail_fast.assert_no_pending_responses()
    ec2_client_stub_max_retries.assert_no_pending_responses()


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(["-v", __file__]))
