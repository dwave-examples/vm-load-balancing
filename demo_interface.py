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

"""This file stores the Dash HTML layout for the app."""
from __future__ import annotations
from enum import EnumType

from dash import dcc, html
import dash_mantine_components as dmc

from demo_configs import (
    DESCRIPTION,
    HOSTS,
    MAIN_HEADER,
    SOLVER_TIME,
    THUMBNAIL,
    VMS,
)
from src.demo_enums import PriorityType

THEME_COLOR = "#2d4376"


def slider(label: str, id: str, config: dict) -> html.Div:
    """Slider element for value selection.

    Args:
        label: The title that goes above the slider.
        id: A unique selector for this element.
        config: A dictionary of slider configurations, see dcc.Slider Dash docs.
    """
    return html.Div(
        className="slider-wrapper",
        children=[
            html.Label(label, htmlFor=id),
            dmc.Slider(
                id=id,
                className="slider",
                **config,
                marks=[
                    {"value": config["min"], "label": f'{config["min"]}'},
                    {"value": config["max"], "label": f'{config["max"]}'},
                ],
                labelAlwaysOn=True,
                thumbLabel=f"{label} slider",
                color=THEME_COLOR,
            ),
        ],
    )


def dropdown(label: str, id: str, options: list) -> html.Div:
    """Dropdown element for option selection.

    Args:
        label: The title that goes above the dropdown.
        id: A unique selector for this element.
        options: A list of dictionaries of labels and values.
    """
    return html.Div(
        className="dropdown-wrapper",
        children=[
            html.Label(label, htmlFor=id),
            dmc.Select(
                id=id,
                data=options,
                value=options[0]["value"],
                allowDeselect=False,
            ),
        ],
    )


def checklist(label: str, id: str, options: list, values: list, inline: bool = True) -> html.Div:
    """Checklist element for option selection.

    Args:
        label: The title that goes above the checklist.
        id: A unique selector for this element.
        options: A list of dictionaries of labels and values.
        values: A list of values that should be preselected in the checklist.
        inline: Whether the options of the checklist are displayed beside or below each other.
    """
    return html.Div(
        className="checklist-wrapper",
        children=[
            html.Label(label, htmlFor=id),
            dcc.Checklist(
                id=id,
                className=f"checklist{' checklist--inline' if inline else ''}",
                inline=inline,
                options=options,
                value=values,
            ),
        ],
    )


def radio(label: str, id: str, options: list, value: int, inline: bool = True) -> html.Div:
    """Radio element for option selection.

    Args:
        label: The title that goes above the radio.
        id: A unique selector for this element.
        options: A list of dictionaries of labels and values.
        value: The value of the radio that should be preselected.
        inline: Whether the options are displayed beside or below each other.
    """
    return html.Div(
        className="radio-wrapper",
        children=[
            html.Label(label, htmlFor=id),
            dcc.RadioItems(
                id=id,
                className=f"radio{' radio--inline' if inline else ''}",
                inline=inline,
                options=options,
                value=value,
            ),
        ],
    )


def generate_options(options: list | EnumType, str_val: bool = False) -> list[dict]:
    """Generates options for dropdowns, checklists, radios, etc."""
    if isinstance(options, EnumType):
        return [
            {"label": option.label, "value": f"{option.value}" if str_val else option.value}
            for option in options
        ]

    return [
        {"label": option, "value": f"{option}" if str_val else i}
        for i, option in enumerate(options)
    ]


def generate_settings_form() -> html.Div:
    """This function generates settings for selecting the scenario.

    Returns:
        html.Div: A Div containing the settings for selecting the scenario.
    """
    priority_options = generate_options(PriorityType)

    return html.Div(
        className="settings",
        children=[
            slider(
                "Number of Virtual Machines",
                "vms",
                VMS,
            ),
            slider(
                "Number of Hosts",
                "hosts",
                HOSTS,
            ),
            radio(
                "Balance Priority",
                "priority",
                sorted(priority_options, key=lambda op: op["value"]),
                0,
            ),
            html.Label("Solver Time Limit (seconds)", htmlFor="solver-time-limit"),
            dmc.NumberInput(
                id="solver-time-limit",
                type="number",
                **SOLVER_TIME,
            ),
        ],
    )


def generate_run_buttons() -> html.Div:
    """Run and cancel buttons to run the optimization."""
    return html.Div(
        id="button-group",
        children=[
            html.Button("Run Optimization", id="run-button", className="button"),
            html.Button(
                "Cancel Optimization",
                id="cancel-button",
                className="button",
                style={"display": "none"},
            ),
        ],
    )


def generate_graph(index: int) -> html.Div:
    """Generates a graph with a zoom button.

    Args:
        index: A unit integer to identify the graph by.

    Returns:
        html.Div: A div containing a graph and magnifying button.
    """
    return html.Div(
        children=[
            html.Div(
                [
                    html.Div([html.Span("+"), html.Span("-")], className="magnifying-lens"),
                ],
                className="magnifying",
                id={"type": "magnifying", "index": index},
            ),
            html.Div(
                dcc.Graph(
                    id={"type": "graph", "index": index},
                    responsive=True,
                    config={"displayModeBar": False},
                    className="graph-element",
                ),
                className="graph-wrapper",
                id={"type": "graph-wrapper", "index": index},
            )
        ],
    )


def create_interface():
    """Set the application HTML."""
    return html.Div(
        id="app-container",
        children=[
            html.A(  # Skip link for accessibility
                "Skip to main content",
                href="#main-content",
                id="skip-to-main",
                className="skip-link",
                tabIndex=1,
            ),
            # Below are any temporary storage items, e.g., for sharing data between callbacks.
            dcc.Store(id="vms-store"),
            dcc.Store(id="hosts-store"),
            # Settings and results columns
            html.Main(
                className="columns-main",
                id="main-content",
                children=[
                    # Left column
                    html.Div(
                        id={"type": "to-collapse-class", "index": 0},
                        className="left-column",
                        children=[
                            html.Div(
                                className="left-column-layer-1",  # Fixed width Div to collapse
                                children=[
                                    html.Div(
                                        className="left-column-layer-2",  # Padding and content wrapper
                                        children=[
                                            html.Div(
                                                [
                                                    html.H1(MAIN_HEADER),
                                                    html.P(DESCRIPTION),
                                                ],
                                                className="title-section",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        html.Div(
                                                            [
                                                                generate_settings_form(),
                                                                generate_run_buttons(),
                                                            ],
                                                            className="settings-and-buttons",
                                                        ),
                                                        className="settings-and-buttons-wrapper",
                                                    ),
                                                    # Left column collapse button
                                                    html.Div(
                                                        html.Button(
                                                            id={
                                                                "type": "collapse-trigger",
                                                                "index": 0,
                                                            },
                                                            className="left-column-collapse",
                                                            title="Collapse sidebar",
                                                            children=[
                                                                html.Div(className="collapse-arrow")
                                                            ],
                                                            **{"aria-expanded": "true"},
                                                        ),
                                                    ),
                                                ],
                                                className="form-section",
                                            ),
                                        ],
                                    )
                                ],
                            ),
                        ],
                    ),
                    # Right column
                    html.Div(
                        className="right-column",
                        children=[
                            dmc.Tabs(
                                id="tabs",
                                value="input-tab",
                                color="white",
                                children=[
                                    html.Header(
                                        className="banner",
                                        children=[
                                            html.Nav(
                                                [
                                                    dmc.TabsList(
                                                        [
                                                            dmc.TabsTab("Current State", value="input-tab"),
                                                            dmc.TabsTab(
                                                                "Updated State",
                                                                value="results-tab",
                                                                id="results-tab",
                                                                disabled=True,
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            html.Img(src=THUMBNAIL, alt="D-Wave logo"),
                                        ],
                                    ),
                                    dmc.TabsPanel(
                                        value="input-tab",
                                        tabIndex="12",
                                        children=[
                                            html.Div(
                                                className="tab-content-wrapper",
                                                children=[
                                                    dcc.Loading(
                                                        parent_className="input",
                                                        type="circle",
                                                        color=THEME_COLOR,
                                                        children=[
                                                            html.Div(
                                                                [
                                                                    generate_graph(0),
                                                                    generate_graph(1),
                                                                ],
                                                                className="graph-container",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    generate_graph(2),
                                                                    generate_graph(3),
                                                                ],
                                                                className="graph-container",
                                                            ),
                                                        ],
                                                    ),
                                                ]
                                            )
                                        ],
                                    ),
                                    dmc.TabsPanel(
                                        value="results-tab",
                                        tabIndex="13",
                                        children=[
                                            html.Div(
                                                className="tab-content-wrapper",
                                                children=[
                                                    dcc.Loading(
                                                        parent_className="results",
                                                        type="circle",
                                                        color=THEME_COLOR,
                                                        children=[
                                                            html.Div(
                                                                [
                                                                    generate_graph(4),
                                                                    generate_graph(5),
                                                                ],
                                                                className="graph-container",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    generate_graph(6),
                                                                    generate_graph(7),
                                                                ],
                                                                className="graph-container",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
