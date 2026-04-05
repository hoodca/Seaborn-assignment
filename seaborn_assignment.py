from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


@dataclass
class ExercisePulseAnalysis:
    """Analyze gym/school pulse data and generate assignment visualizations."""

    csv_path: Path
    output_dir: Path
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    long_data: pd.DataFrame = field(default_factory=pd.DataFrame)

    pulse_columns: tuple[str, ...] = ("1 min", "15 min", "30 min")
    diet_order: tuple[str, ...] = ("low fat", "no fat")
    exercise_order: tuple[str, ...] = ("rest", "walking", "running")
    palette: dict[str, str] = field(
        default_factory=lambda: {"low fat": "#4C78A8", "no fat": "#F58518"}
    )

    def load_data(self) -> None:
        self.data = pd.read_csv(self.csv_path)
        required_columns = {"id", *self.pulse_columns, "diet", "kind"}
        missing_columns = required_columns.difference(self.data.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Exercise data is missing required columns: {missing}")

    def prepare_long_data(self) -> None:
        self.long_data = self.data.melt(
            id_vars=["id", "diet", "kind"],
            value_vars=list(self.pulse_columns),
            var_name="time_point",
            value_name="pulse",
        )
        self.long_data["time_point"] = pd.Categorical(
            self.long_data["time_point"],
            categories=list(self.pulse_columns),
            ordered=True,
        )
        self.long_data["diet"] = pd.Categorical(
            self.long_data["diet"],
            categories=list(self.diet_order),
            ordered=True,
        )
        self.long_data["kind"] = pd.Categorical(
            self.long_data["kind"],
            categories=list(self.exercise_order),
            ordered=True,
        )

    def create_heatmap(self) -> None:
        heatmap_data = (
            self.long_data.groupby(["diet", "kind", "time_point"], observed=True)["pulse"]
            .mean()
            .reset_index()
            .assign(group=lambda df: df["diet"].str.title() + " | " + df["kind"].str.title())
            .pivot(index="group", columns="time_point", values="pulse")
            .reindex(
                [
                    f"{diet.title()} | {kind.title()}"
                    for diet in self.diet_order
                    for kind in self.exercise_order
                ]
            )
        )

        plt.figure(figsize=(11.5, 5.75), dpi=160)
        ax = sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".1f",
            cmap=sns.color_palette("rocket_r", as_cmap=True),
            linewidths=0.8,
            linecolor="#f3eee8",
            cbar_kws={"label": "Average Pulse (bpm)"},
        )
        ax.set_title("Average Pulse by Diet, Exercise Type, and Time", pad=14, fontsize=15)
        ax.set_xlabel("Measurement Time")
        ax.set_ylabel("Diet | Exercise Type")
        plt.tight_layout()
        plt.savefig(self.output_dir / "01_exercise_heatmap.png")
        plt.close()

    def create_categorical_plot(self) -> None:
        fig, axes = plt.subplots(1, len(self.pulse_columns), figsize=(16, 5.6), sharey=True, dpi=160)
        legend_handles: list[object] = []
        legend_labels: list[str] = []

        for ax, time_point in zip(axes, self.pulse_columns):
            subset = self.long_data[self.long_data["time_point"] == time_point]
            sns.boxplot(
                data=subset,
                x="kind",
                y="pulse",
                hue="diet",
                order=list(self.exercise_order),
                hue_order=list(self.diet_order),
                palette=self.palette,
                width=0.66,
                fliersize=0,
                linewidth=1.2,
                ax=ax,
            )
            sns.stripplot(
                data=subset,
                x="kind",
                y="pulse",
                hue="diet",
                order=list(self.exercise_order),
                hue_order=list(self.diet_order),
                palette=self.palette,
                dodge=True,
                alpha=0.72,
                size=4.4,
                edgecolor="white",
                linewidth=0.45,
                legend=False,
                ax=ax,
            )

            handles, labels = ax.get_legend_handles_labels()
            for handle, label in zip(handles, labels):
                if label not in legend_labels:
                    legend_handles.append(handle)
                    legend_labels.append(label)

            if ax.get_legend() is not None:
                ax.get_legend().remove()

            ax.set_title(f"{time_point} Pulse Check", pad=10)
            ax.set_xlabel("Exercise Type")
            ax.set_xticks(range(len(self.exercise_order)))
            ax.set_xticklabels([label.title() for label in self.exercise_order])
            if ax is axes[0]:
                ax.set_ylabel("Pulse (beats per minute)")
            else:
                ax.set_ylabel("")

        fig.suptitle(
            "Pulse by Exercise Type and Diet Across Time",
            fontsize=16,
            y=1.03,
        )
        fig.legend(
            legend_handles[: len(self.diet_order)],
            [label.title() for label in legend_labels[: len(self.diet_order)]],
            title="Diet",
            loc="upper center",
            bbox_to_anchor=(0.5, 1.02),
            ncol=2,
            frameon=True,
        )
        plt.tight_layout()
        plt.savefig(self.output_dir / "02_exercise_categorical_plot.png", bbox_inches="tight")
        plt.close(fig)

    def summarize(self) -> str:
        by_kind = (
            self.long_data.groupby(["kind", "time_point"], observed=True)["pulse"]
            .mean()
            .unstack("time_point")
        )
        by_diet = (
            self.long_data.groupby(["diet", "time_point"], observed=True)["pulse"]
            .mean()
            .unstack("time_point")
        )
        running_change = by_kind.loc["running", "30 min"] - by_kind.loc["running", "1 min"]
        rest_change = by_kind.loc["rest", "30 min"] - by_kind.loc["rest", "1 min"]
        higher_diet = by_diet["30 min"].idxmax().title()

        return (
            f"Running changed pulse the most in this class sample, rising by about {running_change:.1f} beats "
            f"per minute from the 1-minute mark to the 30-minute mark. Rest changed very little "
            f"(about {rest_change:.1f} beats per minute), and walking stayed in the middle. "
            f"The {higher_diet} group had somewhat higher pulse averages overall, but the much bigger story is "
            "that harder exercise makes the heart work more. That is the main takeaway to share with "
            "elementary students from this dataset."
        )

    def run(self) -> str:
        self.load_data()
        self.prepare_long_data()
        self.create_heatmap()
        self.create_categorical_plot()
        return self.summarize()


@dataclass
class PlanetsSeabornAnalysis:
    """Create relational, distributional, and categorical plots from seaborn's planets dataset."""

    output_dir: Path
    dataset_cache_path: Path = Path("planets_dataset.csv")
    data: pd.DataFrame = field(default_factory=pd.DataFrame)

    def load_data(self) -> None:
        if self.dataset_cache_path.exists():
            self.data = pd.read_csv(self.dataset_cache_path)
            return

        try:
            self.data = sns.load_dataset("planets")
        except Exception as exc:
            raise RuntimeError(
                "Unable to load seaborn's built-in 'planets' dataset. "
                "Run the project once with internet access or provide a local planets_dataset.csv cache."
            ) from exc

        self.data.to_csv(self.dataset_cache_path, index=False)

    def _top_methods(self, limit: int) -> list[str]:
        return self.data["method"].value_counts().head(limit).index.tolist()

    def create_relational_plots(self) -> None:
        relational_data = self.data.dropna(
            subset=["mass", "orbital_period", "distance", "year", "method"]
        ).copy()
        top_methods = self._top_methods(5)
        relational_data["method_group"] = relational_data["method"].where(
            relational_data["method"].isin(top_methods), "Other"
        )

        plt.figure(figsize=(10, 6), dpi=160)
        ax1 = sns.scatterplot(
            data=relational_data,
            x="orbital_period",
            y="mass",
            hue="method_group",
            hue_order=top_methods + ["Other"],
            palette="Set2",
            alpha=0.82,
            s=75,
            edgecolor="white",
            linewidth=0.35,
        )
        ax1.set_xscale("log")
        ax1.set_yscale("log")
        ax1.set_title("Relational Plot 1: Planet Mass vs Orbital Period", pad=12, fontsize=13)
        ax1.set_xlabel("Orbital Period (days, log scale)")
        ax1.set_ylabel("Planet Mass (Jupiter masses, log scale)")
        ax1.legend(title="Detection Method", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
        plt.tight_layout()
        plt.savefig(self.output_dir / "03_planets_relational_scatter.png")
        plt.close()

        yearly = self.data.groupby("year", observed=True)["number"].sum().reset_index()
        plt.figure(figsize=(10, 5.5), dpi=160)
        ax2 = sns.lineplot(data=yearly, x="year", y="number", marker="o", color="#1d3557", linewidth=2.4)
        ax2.fill_between(yearly["year"], yearly["number"], color="#a8dadc", alpha=0.35)
        ax2.set_title("Relational Plot 2: Number of Detected Planets by Year", pad=12, fontsize=13)
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Total Planets Detected")
        plt.tight_layout()
        plt.savefig(self.output_dir / "04_planets_relational_line.png")
        plt.close()

    def create_distribution_plots(self) -> None:
        distance_data = self.data.dropna(subset=["distance"]).copy()
        distance_data = distance_data[distance_data["distance"] > 0]

        plt.figure(figsize=(10, 5.5), dpi=160)
        ax1 = sns.histplot(
            data=distance_data,
            x="distance",
            bins=30,
            kde=True,
            color="#E76F51",
        )
        ax1.set_xscale("log")
        ax1.set_title("Distribution Plot 1: Distance of Exoplanets from Earth", pad=12, fontsize=13)
        ax1.set_xlabel("Distance (parsecs, log scale)")
        ax1.set_ylabel("Count")
        plt.tight_layout()
        plt.savefig(self.output_dir / "05_planets_distribution_hist.png")
        plt.close()

        top_methods = self._top_methods(4)
        period_data = self.data.dropna(subset=["orbital_period", "method"]).copy()
        period_data = period_data[period_data["method"].isin(top_methods)]

        plt.figure(figsize=(10, 5.5), dpi=160)
        ax2 = sns.kdeplot(
            data=period_data,
            x="orbital_period",
            hue="method",
            hue_order=top_methods,
            fill=True,
            common_norm=False,
            alpha=0.2,
            linewidth=1.3,
            warn_singular=False,
        )
        ax2.set_xscale("log")
        ax2.set_title(
            "Distribution Plot 2: Orbital Period by Detection Method",
            pad=12,
            fontsize=13,
        )
        ax2.set_xlabel("Orbital Period (days, log scale)")
        ax2.set_ylabel("Density")
        plt.tight_layout()
        plt.savefig(self.output_dir / "06_planets_distribution_kde.png")
        plt.close()

    def create_categorical_plots(self) -> None:
        methods_top = self._top_methods(6)
        top_method_data = self.data[self.data["method"].isin(methods_top)].copy()

        plt.figure(figsize=(10, 6), dpi=160)
        ax1 = sns.countplot(
            data=top_method_data,
            y="method",
            hue="method",
            order=methods_top,
            palette="crest",
            legend=False,
        )
        ax1.set_title("Categorical Plot 1: Most Common Planet Detection Methods", pad=12, fontsize=13)
        ax1.set_xlabel("Count")
        ax1.set_ylabel("Detection Method")
        for patch in ax1.patches:
            width = patch.get_width()
            ax1.text(width + 4, patch.get_y() + patch.get_height() / 2, f"{int(width)}", va="center")
        plt.tight_layout()
        plt.savefig(self.output_dir / "07_planets_categorical_count.png")
        plt.close()

        mass_data = top_method_data.dropna(subset=["mass"]).copy()
        mass_methods = mass_data["method"].value_counts().head(5).index.tolist()

        plt.figure(figsize=(10.5, 6), dpi=160)
        ax2 = sns.boxplot(
            data=mass_data[mass_data["method"].isin(mass_methods)],
            x="method",
            y="mass",
            hue="method",
            order=mass_methods,
            palette="Set3",
            legend=False,
        )
        ax2.set_yscale("log")
        ax2.set_title("Categorical Plot 2: Planet Mass by Detection Method", pad=12, fontsize=13)
        ax2.set_xlabel("Detection Method")
        ax2.set_ylabel("Planet Mass (Jupiter masses, log scale)")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(self.output_dir / "08_planets_categorical_box.png")
        plt.close()

    def summarize(self) -> str:
        yearly = self.data.groupby("year", observed=True)["number"].sum()
        peak_year = int(yearly.idxmax())
        peak_count = int(yearly.max())
        top_method = self.data["method"].value_counts().idxmax()
        return (
            f"The yearly discovery line plot best highlights a notable pattern: planet detections surged over time "
            f"and peaked in {peak_year} with {peak_count} planets recorded in this dataset. The count plot supports "
            f"that story by showing how strongly methods such as {top_method} dominate exoplanet discovery records, "
            "which helps explain why some kinds of planets appear more often than others in the rest of the graphs."
        )

    def run(self) -> str:
        self.load_data()
        self.create_relational_plots()
        self.create_distribution_plots()
        self.create_categorical_plots()
        return self.summarize()


@dataclass
class SeabornAssignmentProject:
    """Orchestrates both project sections and saves output graphics and summary."""

    csv_path: Path
    output_dir: Path = Path("output_plots")

    def _style(self) -> None:
        sns.set_theme(
            style="whitegrid",
            context="talk",
            rc={
                "axes.facecolor": "#fcfaf6",
                "figure.facecolor": "#fcfaf6",
                "grid.color": "#ddd8cf",
            },
        )
        sns.set_palette("deep")

    def run(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._style()

        exercise_analysis = ExercisePulseAnalysis(self.csv_path, self.output_dir)
        exercise_summary = exercise_analysis.run()

        planets_analysis = PlanetsSeabornAnalysis(self.output_dir)
        planets_summary = planets_analysis.run()

        report = (
            "SEABORN ASSIGNMENT SUMMARY\n\n"
            "Exercise Data Conclusion:\n"
            f"{exercise_summary}\n\n"
            "Planets Dataset Conclusion:\n"
            f"{planets_summary}\n"
        )
        (self.output_dir / "assignment_summary.txt").write_text(report, encoding="utf-8")
        print(report)


def main() -> None:
    project = SeabornAssignmentProject(csv_path=Path("Exercise_Data.csv"))
    project.run()


if __name__ == "__main__":
    main()
