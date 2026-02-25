# Copyright 2024 D-Wave
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

from __future__ import annotations

from typing import NamedTuple

import dash
import plotly.graph_objs as go
from dash import ALL, MATCH, ctx
from dash.dependencies import Input, Output, State

from demo_configs import CPU_CAP, CPU_UNITS, MEMORY_CAP, MEMORY_UNITS
from src import cqm_balancer, generate_charts, generate_data
from src.demo_enums import PriorityType


@dash.callback(
    Output({"type": "to-collapse-class", "index": MATCH}, "className"),
    inputs=[
        Input({"type": "collapse-trigger", "index": MATCH}, "n_clicks"),
        State({"type": "to-collapse-class", "index": MATCH}, "className"),
    ],
    prevent_initial_call=True,
)
def toggle_left_column(collapse_trigger: int, to_collapse_class: str) -> str:
    """Toggles a 'collapsed' class that hides and shows some aspect of the UI.

    Args:
        collapse_trigger (int): The (total) number of times a collapse button has been clicked.
        to_collapse_class (str): Current class name of the thing to collapse, 'collapsed' if not
            visible, empty string if visible.

    Returns:
        str: The new class name of the thing to collapse.
    """

    classes = to_collapse_class.split(" ") if to_collapse_class else []
    if "collapsed" in classes:
        classes.remove("collapsed")
        return " ".join(classes)
    return to_collapse_class + " collapsed" if to_collapse_class else "collapsed"


@dash.callback(
    Output({"type": "graph", "index": ALL}, "className"),
    Output({"type": "magnifying", "index": ALL}, "className"),
    inputs=[
        Input({"type": "magnifying", "index": ALL}, "n_clicks"),
        State({"type": "graph", "index": ALL}, "className"),
    ],
    prevent_initial_call=True,
)
def magnify_graph(
    magnifying: int,
    graph_classes: list[str],
) -> tuple[list[str], list[str]]:
    """Zooms in or out of a graph when the graph's magnifying button is clicked.

    Args:
        magnifying (int): The number of times a magnifying button has been clicked.
        graph_classes (list[str]): The class names of all the graphs.

    Returns:
        list[str]: A list of the new graph class names.
        list[str]: A list of the new magnifying button class names.
    """
    triggered_index = ctx.triggered_id["index"]
    one_page_count = int(len(graph_classes) / 2)

    no_update_page = [dash.no_update] * one_page_count
    display_none_page = ["display-none"] * one_page_count
    reset_graph_page = ["graph-element"] * one_page_count
    reset_mag_page = ["magnifying"] * one_page_count
    is_expanded = "graph-element-expanded" in graph_classes[triggered_index]
    on_first_page = triggered_index < one_page_count

    if on_first_page:  # On first page
        if is_expanded:
            return reset_graph_page + no_update_page, reset_mag_page + no_update_page

        graph_class_names = display_none_page + no_update_page
        mag_class_names = display_none_page + no_update_page
    else:  # On second page
        if is_expanded:
            return no_update_page + reset_graph_page, no_update_page + reset_mag_page

        graph_class_names = no_update_page + display_none_page
        mag_class_names = no_update_page + display_none_page

    graph_class_names[triggered_index] = "graph-element-expanded"
    mag_class_names[triggered_index] = "magnifying minus"

    return graph_class_names, mag_class_names


class RenderInitialStateReturn(NamedTuple):
    """Return type for the ``render_initial_state`` callback function."""

    fig_mem_percent: go.Figure
    fig_mem: go.Figure
    fig_cpu_percent: go.Figure
    fig_cpu: go.Figure
    vms: dict[dict]
    hosts: dict[dict]


@dash.callback(
    Output({"type": "graph", "index": 0}, "figure"),
    Output({"type": "graph", "index": 1}, "figure"),
    Output({"type": "graph", "index": 2}, "figure"),
    Output({"type": "graph", "index": 3}, "figure"),
    Output("vms-store", "data"),
    Output("hosts-store", "data"),
    inputs=[
        Input("vms", "value"),
        Input("hosts", "value"),
        State("priority", "value"),
    ],
)
def render_initial_state(num_vms: int, num_hosts: int, priority: int) -> RenderInitialStateReturn:
    """Runs on load and any time the value of Virtual Machines or Hosts is updated.

    Args:
        num_vms (int): The value of the virtual machine slider.
        num_hosts (int): The value of the host slider.
        priority (int): The value of the priority selector.

    Returns:
        fig_mem_percent: The figure for the memory percent graph.
        fig_mem: The figure for the memory virtual machine graph.
        fig_cpu_percent: The figure for the CPU percent graph.
        fig_cpu: The figure for the CPU virtual machine graph.
        vms: The dict of virtual machine dictionaries to store.
        hosts: The dict of host dictionaries to store.
    """
    vms = generate_data.generate_vms(num_vms, num_hosts)
    hosts = generate_data.generate_hosts(num_hosts, vms)

    df_mem_percent, df_mem = generate_charts.get_df(hosts, vms, "mem")
    df_cpu_percent, df_cpu = generate_charts.get_df(hosts, vms, "cpu")

    fig_mem_percent = generate_charts.generate_percent_chart(df_mem_percent, "Percent Memory Used")
    fig_cpu_percent = generate_charts.generate_percent_chart(df_cpu_percent, "Percent CPU Used")
    fig_mem = generate_charts.generate_vm_bar_chart(
        df_mem, MEMORY_CAP, f"Memory Usage per VM (Max: {MEMORY_CAP} {MEMORY_UNITS})", MEMORY_UNITS
    )
    fig_cpu = generate_charts.generate_vm_bar_chart(
        df_cpu, CPU_CAP, f"CPU Usage per VM (Max: {CPU_CAP} {CPU_UNITS})", CPU_UNITS
    )

    return RenderInitialStateReturn(
        fig_mem_percent=fig_mem_percent,
        fig_mem=fig_mem,
        fig_cpu_percent=fig_cpu_percent,
        fig_cpu=fig_cpu,
        vms=vms,
        hosts=hosts,
    )


class RunOptimizationReturn(NamedTuple):
    """Return type for the ``run_optimization`` callback function."""

    fig_mem_percent_result: go.Figure
    fig_mem_result: go.Figure
    fig_cpu_percent_result: go.Figure
    fig_cpu_result: go.Figure
    results_tab_disabled: bool


@dash.callback(
    Output({"type": "graph", "index": 4}, "figure"),
    Output({"type": "graph", "index": 5}, "figure"),
    Output({"type": "graph", "index": 6}, "figure"),
    Output({"type": "graph", "index": 7}, "figure"),
    Output("results-tab", "disabled"),
    background=True,
    inputs=[
        Input("run-button", "n_clicks"),
        State("solver-time-limit", "value"),
        State("priority", "value"),
        State("vms-store", "data"),
        State("hosts-store", "data"),
    ],
    running=[
        (Output("cancel-button", "className"), "", "display-none"),  # Show/hide cancel button.
        (Output("run-button", "className"), "display-none", ""),  # Hides run button while running.
        (Output("results-tab", "disabled"), True, True),  # Disables results tab while running.
        (Output("results-tab", "label"), "Loading...", "Updated State"),
        (Output("tabs", "value"), "input-tab", "input-tab"),  # Switch to input tab while running.
    ],
    cancel=[Input("cancel-button", "n_clicks")],
    prevent_initial_call=True,
)
def run_optimization(
    run_click: int,
    time_limit: float,
    priority: int,
    vms: dict[dict],
    hosts: dict[dict],
) -> RunOptimizationReturn:
    """Runs the optimization and updates UI accordingly.

    This is the main function which is called when the ``Run Optimization`` button is clicked.
    This function takes in all form values and runs the optimization, updates the run/cancel
    buttons, deactivates (and reactivates) the results tab, and updates all relevant HTML
    components.

    Args:
        run_click: The (total) number of times the run button has been clicked.
        time_limit: The solver time limit.
        priority: The value of the priority selector.
        vms: The dict of virtual machine dictionaries to store.
        hosts: The dict of host dictionaries to store.

    Returns:
        A NamedTuple (RunOptimizationReturn) containing all outputs to be used when updating the HTML
        template (in ``demo_interface.py``). These are:

            fig_mem_percent_result: The figure for the memory percent graph.
            fig_mem_result: The figure for the memory virtual machine graph.
            fig_cpu_percent_result: The figure for the CPU percent graph.
            fig_cpu_result: The figure for the CPU virtual machine graph.
            results_tab_disabled: Whether the results tab should be disabled.
    """
    priority = PriorityType(priority)
    cqm = cqm_balancer.build_cqm(vms, hosts, priority)
    plan = cqm_balancer.get_solution(cqm, time_limit)

    resulting_hosts, resulting_vms = cqm_balancer.format_results(plan, vms, hosts)

    df_mem_percent, df_mem = generate_charts.get_df(resulting_hosts, resulting_vms, "mem")
    df_cpu_percent, df_cpu = generate_charts.get_df(resulting_hosts, resulting_vms, "cpu")

    fig_mem_percent = generate_charts.generate_percent_chart(df_mem_percent, "Percent Memory Used")
    fig_cpu_percent = generate_charts.generate_percent_chart(df_cpu_percent, "Percent CPU Used")
    fig_mem = generate_charts.generate_vm_bar_chart(
        df_mem, MEMORY_CAP, f"Memory Usage per VM (max: {MEMORY_CAP} {MEMORY_UNITS})", MEMORY_UNITS
    )
    fig_cpu = generate_charts.generate_vm_bar_chart(
        df_cpu, CPU_CAP, f"CPU Usage per VM (max: {CPU_CAP} {CPU_UNITS})", CPU_UNITS
    )

    return RunOptimizationReturn(
        fig_mem_percent_result=fig_mem_percent,
        fig_mem_result=fig_mem,
        fig_cpu_percent_result=fig_cpu_percent,
        fig_cpu_result=fig_cpu,
        results_tab_disabled=False,
    )
