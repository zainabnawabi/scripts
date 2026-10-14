"""A small GUI for sketching a threat model and recording its risks."""

from __future__ import annotations

from dataclasses import dataclass, field
import textwrap
from tkinter import messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch


NODE_TYPES = ("External", "Process", "Data Store", "Security Control")
SEVERITIES = ("Low", "Medium", "High", "Critical")
SEVERITY_RANK = {severity: rank for rank, severity in enumerate(SEVERITIES)}
SEVERITY_COLORS = {
    "Low": "#55a868",
    "Medium": "#e6b84f",
    "High": "#e07a3f",
    "Critical": "#d9534f",
}
LANE_ORDER = {node_type: index for index, node_type in enumerate(NODE_TYPES)}


@dataclass
class Component:
    component_id: int
    name: str
    node_type: str
    severity: str = "Low"
    threats: list[str] = field(default_factory=list)


class ThreatModelApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Threat Analysis Graph")
        self.geometry("1180x760")
        self.minsize(900, 620)

        self.components: list[Component] = []
        self.connections: list[tuple[int, int]] = []
        self.next_component_id = 1
        self._add_sample_model()
        self._build_interface()
        self._redraw_graph()
        self._refresh_threat_register()

    def _add_sample_model(self) -> None:
        sample = [
            ("Attacker", "External", "High"),
            ("Customer", "External", "Low"),
            ("Web App", "Process", "High"),
            ("API", "Process", "Medium"),
            ("Identity Service", "Security Control", "Medium"),
            ("Customer Database", "Data Store", "High"),
        ]
        for name, node_type, severity in sample:
            self.components.append(
                Component(self.next_component_id, name, node_type, severity)
            )
            self.next_component_id += 1

        by_name = {component.name: component.component_id for component in self.components}
        self.connections = [
            (by_name["Attacker"], by_name["Web App"]),
            (by_name["Customer"], by_name["Web App"]),
            (by_name["Web App"], by_name["API"]),
            (by_name["API"], by_name["Identity Service"]),
            (by_name["API"], by_name["Customer Database"]),
        ]
        for component, description, severity in (
            (by_name["Web App"], "Credential stuffing against customer accounts", "High"),
            (by_name["API"], "Request tampering may bypass authorization checks", "Medium"),
            (by_name["Customer Database"], "Sensitive records need encryption at rest", "High"),
        ):
            self._record_threat(component, description, severity)

    def _build_interface(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self,
            text="Threat Analysis Graph",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 8), sticky="w")

        controls = ctk.CTkScrollableFrame(self, width=280, label_text="Model controls")
        controls.grid(row=1, column=0, padx=(16, 8), pady=(8, 16), sticky="nsew")
        controls.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(controls, text="Add component", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=12, pady=(12, 4), sticky="w"
        )
        self.component_name = ctk.CTkEntry(controls, placeholder_text="Component name")
        self.component_name.grid(row=1, column=0, padx=12, pady=5, sticky="ew")
        self.component_type = ctk.CTkOptionMenu(controls, values=list(NODE_TYPES))
        self.component_type.grid(row=2, column=0, padx=12, pady=5, sticky="ew")
        self.component_severity = ctk.CTkOptionMenu(controls, values=list(SEVERITIES))
        self.component_severity.set("Low")
        self.component_severity.grid(row=3, column=0, padx=12, pady=5, sticky="ew")
        ctk.CTkButton(controls, text="Add component", command=self._add_component).grid(
            row=4, column=0, padx=12, pady=(5, 14), sticky="ew"
        )

        ctk.CTkLabel(controls, text="Add data flow", font=ctk.CTkFont(weight="bold")).grid(
            row=5, column=0, padx=12, pady=(4, 4), sticky="w"
        )
        self.source_menu = ctk.CTkOptionMenu(controls, values=["Select component"])
        self.source_menu.grid(row=6, column=0, padx=12, pady=5, sticky="ew")
        self.target_menu = ctk.CTkOptionMenu(controls, values=["Select component"])
        self.target_menu.grid(row=7, column=0, padx=12, pady=5, sticky="ew")
        ctk.CTkButton(controls, text="Connect components", command=self._add_connection).grid(
            row=8, column=0, padx=12, pady=(5, 14), sticky="ew"
        )

        ctk.CTkLabel(controls, text="Record a threat", font=ctk.CTkFont(weight="bold")).grid(
            row=9, column=0, padx=12, pady=(4, 4), sticky="w"
        )
        self.threat_component = ctk.CTkOptionMenu(controls, values=["Select component"])
        self.threat_component.grid(row=10, column=0, padx=12, pady=5, sticky="ew")
        self.threat_description = ctk.CTkEntry(
            controls, placeholder_text="Threat or mitigation"
        )
        self.threat_description.grid(row=11, column=0, padx=12, pady=5, sticky="ew")
        self.threat_severity = ctk.CTkOptionMenu(controls, values=list(SEVERITIES))
        self.threat_severity.set("Medium")
        self.threat_severity.grid(row=12, column=0, padx=12, pady=5, sticky="ew")
        ctk.CTkButton(controls, text="Record threat", command=self._add_threat).grid(
            row=13, column=0, padx=12, pady=(5, 14), sticky="ew"
        )

        graph_area = ctk.CTkFrame(self)
        graph_area.grid(row=1, column=1, padx=(8, 16), pady=(8, 16), sticky="nsew")
        graph_area.grid_columnconfigure(0, weight=1)
        graph_area.grid_rowconfigure(0, weight=3)
        graph_area.grid_rowconfigure(1, weight=1)

        self.figure = Figure(figsize=(8, 5), dpi=100, facecolor="#f4f4f4")
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_area)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=8, pady=(8, 4), sticky="nsew")

        register = ctk.CTkFrame(graph_area)
        register.grid(row=1, column=0, padx=8, pady=(4, 8), sticky="nsew")
        register.grid_columnconfigure(0, weight=1)
        register.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            register, text="Threat register", font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")
        self.threat_register = ctk.CTkTextbox(register, height=120, wrap="word")
        self.threat_register.grid(row=1, column=0, padx=8, pady=(2, 8), sticky="nsew")
        self._refresh_component_menus()

    def _component_by_name(self, name: str) -> Component | None:
        return next((item for item in self.components if item.name == name), None)

    def _refresh_component_menus(self) -> None:
        names = [component.name for component in self.components] or ["Select component"]
        for menu in (self.source_menu, self.target_menu, self.threat_component):
            previous = menu.get()
            menu.configure(values=names)
            menu.set(previous if previous in names else names[0])

    def _add_component(self) -> None:
        name = self.component_name.get().strip()
        if not name:
            messagebox.showwarning("Missing name", "Enter a component name.")
            return
        if self._component_by_name(name):
            messagebox.showwarning("Duplicate name", "Component names must be unique.")
            return

        self.components.append(
            Component(
                self.next_component_id,
                name,
                self.component_type.get(),
                self.component_severity.get(),
            )
        )
        self.next_component_id += 1
        self.component_name.delete(0, "end")
        self._refresh_component_menus()
        self._redraw_graph()

    def _add_connection(self) -> None:
        source = self._component_by_name(self.source_menu.get())
        target = self._component_by_name(self.target_menu.get())
        if source is None or target is None:
            messagebox.showwarning("Missing component", "Add or select both components first.")
            return
        if source.component_id == target.component_id:
            messagebox.showwarning("Invalid flow", "A component cannot connect to itself.")
            return
        edge = (source.component_id, target.component_id)
        if edge in self.connections:
            messagebox.showwarning("Existing flow", "That data flow is already on the graph.")
            return
        self.connections.append(edge)
        self._redraw_graph()

    def _record_threat(self, component_id: int, description: str, severity: str) -> None:
        component = next(item for item in self.components if item.component_id == component_id)
        component.threats.append(f"{severity}: {description}")
        if SEVERITY_RANK[severity] > SEVERITY_RANK[component.severity]:
            component.severity = severity

    def _add_threat(self) -> None:
        component = self._component_by_name(self.threat_component.get())
        description = self.threat_description.get().strip()
        if component is None:
            messagebox.showwarning("Missing component", "Select a component for this threat.")
            return
        if not description:
            messagebox.showwarning("Missing description", "Describe the threat or mitigation.")
            return
        self._record_threat(component.component_id, description, self.threat_severity.get())
        self.threat_description.delete(0, "end")
        self._refresh_threat_register()
        self._redraw_graph()

    def _refresh_threat_register(self) -> None:
        self.threat_register.configure(state="normal")
        self.threat_register.delete("1.0", "end")
        for component in self.components:
            for threat in component.threats:
                self.threat_register.insert(
                    "end", f"[{threat.split(':', 1)[0]}] {component.name}: "
                    f"{threat.split(':', 1)[1].strip()}\n"
                )
        self.threat_register.configure(state="disabled")

    def _redraw_graph(self) -> None:
        self.axes.clear()
        self.axes.set_facecolor("#f4f4f4")

        lane_members = {
            node_type: [
                component
                for component in self.components
                if component.node_type == node_type
            ]
            for node_type in NODE_TYPES
        }
        positions: dict[int, tuple[float, float]] = {}
        for node_type, members in lane_members.items():
            y = -LANE_ORDER[node_type]
            for index, component in enumerate(members):
                positions[component.component_id] = (float(index), y)

        for source_id, target_id in self.connections:
            source_x, source_y = positions[source_id]
            target_x, target_y = positions[target_id]
            self.axes.annotate(
                "",
                xy=(target_x, target_y),
                xytext=(source_x, source_y),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": "#667085",
                    "linewidth": 1.5,
                    "shrinkA": 24,
                    "shrinkB": 24,
                },
                zorder=1,
            )

        for component in self.components:
            x, y = positions[component.component_id]
            label = textwrap.fill(component.name, width=18)
            self.axes.text(
                x,
                y,
                f"{label}\n{component.severity}",
                ha="center",
                va="center",
                fontsize=9,
                color="#17202a",
                bbox={
                    "boxstyle": "round,pad=0.55",
                    "facecolor": SEVERITY_COLORS[component.severity],
                    "edgecolor": "#344054",
                    "alpha": 0.9,
                },
                zorder=2,
            )

        max_lane_size = max((len(members) for members in lane_members.values()), default=1)
        self.axes.set_xlim(-0.7, max(0.7, max_lane_size - 0.3))
        self.axes.set_ylim(-len(NODE_TYPES) + 0.4, 0.55)
        self.axes.set_yticks(
            [-LANE_ORDER[node_type] for node_type in NODE_TYPES],
            labels=NODE_TYPES,
        )
        self.axes.tick_params(axis="y", labelsize=8, length=0, pad=8)
        self.axes.tick_params(axis="x", bottom=False, labelbottom=False)
        self.axes.set_title("Components and data flows", loc="left", fontsize=13, pad=12)
        self.axes.grid(axis="y", color="#d0d5dd", linestyle="--", linewidth=0.7)
        self.axes.set_axisbelow(True)
        self.axes.spines[["top", "right", "bottom", "left"]].set_visible(False)
        self.axes.legend(
            handles=[
                Patch(facecolor=SEVERITY_COLORS[level], label=level)
                for level in SEVERITIES
            ],
            loc="upper right",
            ncols=4,
            frameon=False,
            fontsize=8,
        )
        self.figure.tight_layout()
        self.canvas.draw_idle()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ThreatModelApp()
    app.mainloop()