from typing import Any, Dict, List


def list_networks_summary(cli) -> List[Dict[str, Any]]:
    """Return a summary of Docker networks with selected fields."""
    summary = []
    for network in cli.networks.list():
        attrs = network.attrs
        summary.append(
            {
                "id": attrs.get("Id"),
                "name": attrs.get("Name"),
                "driver": attrs.get("Driver"),
                "scope": attrs.get("Scope"),
                "created": attrs.get("Created"),
                "internal": attrs.get("Internal"),
                "attachable": attrs.get("Attachable"),
                "ingress": attrs.get("Ingress"),
                "containers": attrs.get("Containers"),
            }
        )
    return summary
