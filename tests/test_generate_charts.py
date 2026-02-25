import unittest

import pandas as pd
import plotly.graph_objs as go

from demo_configs import CPU_CAP, MEMORY_CAP
from src import generate_charts


class TestGenerateCharts(unittest.TestCase):
    def test_get_df(self):
        """Test if DataFrames are generated properly"""
        vms = {
            "VM 1": {
                "status": "Running",
                "current_host": "Host 1",
                "cpu": CPU_CAP / 4,
                "mem": MEMORY_CAP / 4,
            },
            "VM 2": {
                "status": "Running",
                "current_host": "Host 1",
                "cpu": CPU_CAP / 4,
                "mem": MEMORY_CAP / 4,
            },
        }

        hosts = {
            "Host 1": {
                "processor_type": "CPU",
                "cpu_used": CPU_CAP / 2,
                "mem_used": MEMORY_CAP / 2,
                "cpu_cap": CPU_CAP,
                "mem_cap": MEMORY_CAP,
            }
        }

        df_percent, df = generate_charts.get_df(hosts, vms, "cpu")

        # Check DataFrame lengths are equal to the number of hosts and vms
        self.assertEqual(len(df_percent), len(hosts))
        self.assertEqual(len(df), len(vms))

        # Check DataFrames have correct columns
        self.assertTrue(({"Host", "Percent"}).issubset(set(df_percent.columns)))
        self.assertTrue(({"Host", "Use", "Virtual Machine"}).issubset(set(df.columns)))

        # Check correct percent value
        self.assertEqual(df_percent.at[0, "Percent"], 50)

        # Check correct use
        self.assertEqual(df.at[0, "Use"], CPU_CAP / 4)

    def test_generate_percent_chart(self):
        """Test generating the percent chart fig"""
        df = pd.DataFrame(
            {
                "Host": ["Host 1"],
                "Percent": [50],
                "Virtual Machine": ["VM 1"],
            }
        )

        fig = generate_charts.generate_percent_chart(df, "Test Title")

        # Check return type is go.Figure
        self.assertTrue(type(fig) is go.Figure)

        fig_dict = fig.to_dict()

        # Check title
        self.assertEqual(fig_dict["layout"]["title"]["text"], "Test Title")

        # Check x and y axes
        self.assertEqual(fig_dict["data"][0]["y"], ["Host 1"])

    def test_generate_vm_bar_chart(self):
        """Test generating the vm bar chart fig"""
        df = pd.DataFrame(
            {
                "Host": ["Host 1"],
                "Use": [CPU_CAP / 4],
                "Virtual Machine": ["VM 1"],
            }
        )

        units = "GHz"

        fig = generate_charts.generate_vm_bar_chart(df, CPU_CAP, "Test Title", units)

        # Check return type is go.Figure
        self.assertTrue(type(fig) is go.Figure)

        fig_dict = fig.to_dict()

        # Check title
        self.assertEqual(fig_dict["layout"]["title"]["text"], "Test Title")

        # Check x axis title
        self.assertEqual(fig_dict["layout"]["xaxis"]["title"]["text"], f"Usage ({units})")

        # Check x and y axes
        self.assertEqual(fig_dict["data"][0]["y"], ["Host 1"])
