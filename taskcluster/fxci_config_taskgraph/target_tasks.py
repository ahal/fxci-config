from taskgraph.target_tasks import register_target_task


@register_target_task("os-integration")
def os_integration(full_task_graph, parameters, graph_config):
    return ["schedule-os-integration"]
