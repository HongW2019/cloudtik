import pytest
from unittest.mock import Mock, patch

from cloudtik.providers._private.aws.node_provider import AWSNodeProvider

@pytest.mark.parametrize("num_on_demand_nodes", [0, 1001, 9999])
@pytest.mark.parametrize("num_spot_nodes", [0, 1001, 9999])
@pytest.mark.parametrize("stop", [True, False])
def test_terminate_nodes(num_on_demand_nodes, num_spot_nodes, stop):
    # This test makes sure that we stop or terminate all the nodes we're
    # supposed to stop or terminate when we call "terminate_nodes". This test
    # also makes sure that we don't try to stop or terminate too many nodes in
    # a single EC2 request. By default, only 1000 nodes can be
    # stopped/terminated in one request. To terminate more nodes, we must break
    # them up into multiple smaller requests.
    #
    # "num_on_demand_nodes" is the number of on-demand nodes to stop or
    #   terminate.
    # "num_spot_nodes" is the number of on-demand nodes to terminate.
    # "stop" is True if we want to stop nodes, and False to terminate nodes.
    #   Note that spot instances are always terminated, even if "stop" is True.

    # Generate a list of unique instance ids to terminate
    on_demand_nodes = {
        "i-{:017d}".format(i)
        for i in range(num_on_demand_nodes)
    }
    spot_nodes = {
        "i-{:017d}".format(i + num_on_demand_nodes)
        for i in range(num_spot_nodes)
    }
    node_ids = list(on_demand_nodes.union(spot_nodes))

    with patch("cloudtik.providers._private.aws.utils.make_ec2_client"):
        provider = AWSNodeProvider(
            provider_config={
                "region": "nowhere",
                "cache_stopped_nodes": stop
            },
            cluster_name="default")

    # "_get_cached_node" is used by the AWSNodeProvider to determine whether a
    # node is a spot instance or an on-demand instance.
    def mock_get_cached_node(node_id):
        result = Mock()
        result.spot_instance_request_id = "sir-08b93456" if \
            node_id in spot_nodes else ""
        return result

    provider._get_cached_node = mock_get_cached_node

    provider.terminate_nodes(node_ids)

    stop_calls = provider.ec2.meta.client.stop_instances.call_args_list
    terminate_calls = provider.ec2.meta.client.terminate_instances \
        .call_args_list

    nodes_to_stop = set()
    nodes_to_terminate = spot_nodes

    if stop:
        nodes_to_stop.update(on_demand_nodes)
    else:
        nodes_to_terminate.update(on_demand_nodes)

    for calls, nodes_to_include_in_call in (stop_calls, nodes_to_stop), (
            terminate_calls, nodes_to_terminate):
        nodes_included_in_call = set()
        for call in calls:
            assert len(call[1]["InstanceIds"]) <= provider.max_terminate_nodes
            nodes_included_in_call.update(call[1]["InstanceIds"])

        assert nodes_to_include_in_call == nodes_included_in_call


def test_network_interface_conflict_keys():
    # If NetworkInterfaces are defined, SubnetId and SecurityGroupIds
    # can't be specified in the same node type config.
    conflict_kv_pairs = [
        ("SubnetId", "subnet-0000000"),
        ("SubnetIds", ["subnet-0000000", "subnet-1111111"]),
        ("SecurityGroupIds", ["sg-1234abcd", "sg-dcba4321"]),
    ]
    expected_error_msg = (
        "If NetworkInterfaces are defined, subnets and "
        "security groups must ONLY be given in each "
        "NetworkInterface."
    )
    for conflict_kv_pair in conflict_kv_pairs:
        config = helpers.load_aws_example_config_file("example-network-interfaces.yaml")
        head_name = config["head_node_type"]
        head_node_cfg = config["available_node_types"][head_name]["node_config"]
        head_node_cfg[conflict_kv_pair[0]] = conflict_kv_pair[1]
        with pytest.raises(ValueError, match=expected_error_msg):
            helpers.bootstrap_aws_config(config)

if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(["-v", __file__]))
