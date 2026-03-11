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
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

Y_AXIS_LABEL = "Host"
VM_LABEL = "Virtual Machine"


def get_df(hosts: dict[dict], vms: dict[dict], resource: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Given lists of hosts and virtual machines, generates a DataFrame of VMs and a DataFrame of
        percentages.

    Args:
        hosts: A dict of host dicts containing the CPU and memory cap as well as
            the current CPU and memory use.
        vms: A dict of VM dicts containing current host and cpu and memory use.
        resource: A string denoting what resource the DF is for (either ``mem`` or ``cpu``).

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A DataFrame containing the percentage of resource used
        for each host and a DataFrame containing the resource usage for each virtual machine
        assigned to each host.
    """
    percentages = []

    for host_id, host_data in hosts.items():
        percentage = round(host_data[f"{resource}_used"] / host_data[f"{resource}_cap"], 3)
        percentages.append((host_id, percentage))

    vm_data_list = []
    for vm_id, vm_data in vms.items():
        vm_data_list.append(
            {
                Y_AXIS_LABEL: vm_data["current_host"],
                "Use": vm_data[resource],
                VM_LABEL: vm_id,
                "order": int(vm_data["current_host"].split(" ")[1]),
            }
        )

    df = pd.DataFrame(vm_data_list).sort_values(by=["order"])

    percentages = [
        {
            Y_AXIS_LABEL: host_id,
            "Percent": percent * 100,
            "order": int(host_id.split(" ")[1]),
        }
        for host_id, percent in percentages
    ]

    df_percent = pd.DataFrame(percentages).sort_values(by=["order"])

    return df_percent, df


def generate_percent_chart(df: pd.DataFrame, title: str = "") -> go.Figure:
    """Generates a bar chart of percentages given a DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing the data to plot.
        title: The title of the plot.

    Returns:
        go.Figure: A Plotly figure object.
    """
    fig = px.bar(
        df,
        title=title,
        y=Y_AXIS_LABEL,
        x="Percent",
    )

    fig.update_traces(hovertemplate="%{x:.2f}%")

    mean = df["Percent"].mean()
    sd = df["Percent"].std()

    fig.add_vline(
        x=mean,
        line_width=2,
        line_color="#aa3a3c",
        annotation_text=f"mean: {mean:.0f}% (standard deviation: {sd:.1f})",
        line_dash="dash",
        annotation_font_size=15,
        annotation_position="top",
        annotation_font_color="#aa3a3c",
    )

    fig.layout.xaxis.type = "linear"
    fig.update_xaxes(range=[0, 100])
    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_title="Percent",
        yaxis_title=None,
        showlegend=False,
        font=dict(size=13, weight=600, family="proxima-nova, sans-serif"),
        title=dict(font=dict(size=20)),
    )

    return fig


def generate_vm_bar_chart(
    df: pd.DataFrame, max_value: int, title: str = "", units: str = ""
) -> go.Figure:
    """Generates vm bar chart given a DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing the data to plot.
        max_value: The cut off for the x axis of the plot.
        title: The title of the plot.
        units: The units of the x axis.

    Returns:
        go.Figure: A Plotly figure object.
    """
    fig = px.bar(
        df,
        title=title,
        x="Use",
        y=Y_AXIS_LABEL,
        color=VM_LABEL,
        hover_name=VM_LABEL,
        hover_data={
            VM_LABEL: False,
            "Host": False,
        },
    )

    fig.layout.xaxis.type = "linear"
    fig.update_xaxes(range=[0, max_value])
    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_title=f"Usage ({units})",
        yaxis_title=None,
        showlegend=False,
        font=dict(size=13, weight=600, family="proxima-nova, sans-serif"),
        title=dict(font=dict(size=20)),
    )

    return fig
