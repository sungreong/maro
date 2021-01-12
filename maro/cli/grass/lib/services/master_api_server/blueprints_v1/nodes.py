# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.


from flask import Blueprint, jsonify, request

from ..objects import redis_controller, service_config
from ...utils.name_creator import NameCreator
from ...utils.params import NodeStatus

# Flask related.

blueprint = Blueprint(name="nodes", import_name=__name__)
URL_PREFIX = "/v1/nodes"


# Api functions.

@blueprint.route(f"{URL_PREFIX}", methods=["GET"])
def list_nodes():
    """List the nodes in the cluster.

    Returns:
        None.
    """

    name_to_node_details = redis_controller.get_name_to_node_details(cluster_name=service_config["cluster_name"])
    return jsonify(list(name_to_node_details.values()))


@blueprint.route(f"{URL_PREFIX}/<node_name>", methods=["GET"])
def get_node(node_name: str):
    """Get the node with node_name.

    Returns:
        None.
    """

    node_details = redis_controller.get_node_details(
        cluster_name=service_config["cluster_name"],
        node_name=node_name
    )
    return node_details


@blueprint.route(f"{URL_PREFIX}", methods=["POST"])
def create_node():
    """Create a node.

    Returns:
        None.
    """

    node_details = request.json

    # Init runtime params.
    if "name" not in node_details and "id" not in node_details:
        node_name = NameCreator.create_node_name()
        node_details["name"] = node_name
        node_details["id"] = node_name
    node_details["image_files"] = {}
    node_details["containers"] = {}
    node_details["state"] = {
        "status": NodeStatus.PENDING
    }

    node_name = node_details["name"]
    with redis_controller.lock(f"lock:name_to_node_details:{node_name}"):
        redis_controller.set_node_details(
            cluster_name=service_config["cluster_name"],
            node_name=node_name,
            node_details=node_details
        )
    return node_details


@blueprint.route(f"{URL_PREFIX}/<node_name>", methods=["DELETE"])
def delete_node(node_name: str):
    """Delete a node.

    Returns:
        None.
    """

    redis_controller.delete_node_details(
        cluster_name=service_config["cluster_name"],
        node_name=node_name
    )
    return {}