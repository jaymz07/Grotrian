#!/usr/bin/env python3
"""Create spectroscopic energy-level diagrams from YAML files."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import yaml

from typing import Any, Iterable
from matplotlib.axes import Axes

class Grotrian:
    """Represent and draw a Grotrian diagram."""

    def __init__(self, filename):
        self.filename = Path(filename)
        self.data = self._read_file(self.filename)
        self._validate()

        self.transitions = self.data.get("transitions", [])

    @staticmethod
    def _read_file(filename: Path) -> dict[str, Any]:
        try:
            with filename.open("r", encoding="utf-8") as stream:
                data = yaml.safe_load(stream)
        except OSError as exc:
            raise OSError(f"Could not read Grotrian file {filename}: {exc}") from exc
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML in {filename}: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError("The input file must contain a YAML mapping.")
        return data

    def _validate(self) -> None:
        if self.data.get("format") != "grotrian":
            raise ValueError("Input file must specify format: grotrian")

        if self.data.get("version") != 1:
            raise ValueError("Unsupported or missing Grotrian format version.")

        if not isinstance(self.data.get("diagram"), dict):
            raise ValueError("'diagram' must be a mapping.")

        if not isinstance(self.data.get("levels"), list):
            raise ValueError("'levels' must be a list.")

        if not isinstance(self.data["diagram"].get("horizontal_axis", {}).get("order"), list):
            raise ValueError("'diagram.horizontal_axis.order' must be a list.")

    def _get_col_dict(self) -> dict[str, float]:
        """Map from term symbols to diagram x-coordinates."""
        column_order = self.data["diagram"]["horizontal_axis"]["order"]
        return {
            name: i for i, name in enumerate(column_order)
        }

    def _parse_levels(self, level_width=0.3, delta_p=0.3, delta_c=0.6) -> None:
        """Flatten the hierarchy and calculate absolute energies."""
        self.levels = {}

        def visit(level, parent=None, w=level_width, offs=0, parent_energy=0.0, parent_col=None):
            energy = (
                level["energy"]
                if "energy" in level
                else parent_energy + level["offset"]
            )
            col = level.get("col", parent_col)
            has_child = "split" in level
            width = w*delta_p if has_child else w
            x0 = offs - w + delta_p*w if has_child else offs


            self.levels[level["id"]] = {
                "id": level["id"],
                "label": level.get("label", level["id"]),
                "energy": energy,
                "col": col,
                "parent": parent,
                "has_child": has_child,
                "show": level.get("show", True),
                "width": width,
                "x_offs": x0,
            }

            for child in level.get("split", []):
                visit(child,
                      parent=level["id"],
                      w=w*delta_c,
                      offs=offs + w - delta_c*w,
                      parent_energy=energy,
                      parent_col=col)

        for level in self.data["levels"]:
            visit(level)

    def _calculate_coordinates(self) -> None:
        """Scale to diagram coordinates."""
        column_x = self._get_col_dict()

        self.coordinates = {}

        for level_id, level in self.levels.items():

            x = column_x[level["col"]]
            x = x + level["x_offs"]
            energy = level["energy"]

            parent = level["parent"]

            self.coordinates[level_id] = {
                "left": x - level['width'],
                "right": x + level['width'],
                "energy": energy,
                "parent": parent,
                "show": level["show"]
            }

    def draw(self, ax=None, text_offset=0.05, level_width=0.3, delta_p=0.3, delta_c=0.6, ax_expan=0.25) -> Axes:
        """Draw the energy-level diagram."""

        self._parse_levels(level_width=level_width, delta_p=delta_p, delta_c=delta_c)
        self._calculate_coordinates()

        if ax is None:
            _, ax = plt.subplots()
        assert isinstance(ax, Axes)

        for level_id, coords in self.coordinates.items():
            if not coords["show"]:
                continue

            # Draw the levels
            ax.hlines(
                y=coords["energy"],
                xmin=coords["left"],
                xmax=coords["right"],
                color="black",
                linewidth=1.5,
            )

            # Draw the splitting lines for each child
            if coords['parent'] is not None:
                par_coords = self.coordinates[coords['parent']]
                ax.plot([par_coords['right'], coords['left']],[par_coords['energy'], coords['energy']], lw=1.0, c='black', ls='--', alpha=0.4)

            # Level Labels
            ax.text(
                coords["left"] - text_offset,
                coords["energy"],
                self.levels[level_id]["label"],
                va="center",
                ha="right",
            )

        column_x = self._get_col_dict()

        # Draw the transitions
        for transition in self.transitions:
            source = self.coordinates[transition['from']]
            target = self.coordinates[transition['to']]

            x0, y0 = (source["left"]+source["right"])/2, source["energy"]
            x1, y1 = (target["left"]+target["right"])/2, target["energy"]
            ax.annotate(
                "",
                xy=(x1, y1),
                xytext=(x0, y0),
                arrowprops={
                    "arrowstyle": "->",
                    "color": transition.get("color", "tab:blue"),
                    "linewidth": float(transition.get("linewidth", 1.5)),
                    #"shrinkA": 4,
                    #"shrinkB": 4,
                },
                zorder=2,
            )

        ax.set_ylabel(
            self.data["diagram"]["vertical_axis"].get("property", "energy")
        )
        xl = ax.get_xlim()
        lbls = self._get_col_dict().keys()
        ax.set_xticks(range(len(lbls)), labels=lbls)
        ax.set_xlim([xl[0] - ax_expan, xl[1]]) # Create extra space for labels

        return ax
