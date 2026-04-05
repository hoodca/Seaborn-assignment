# Seaborn Visualization Assignment

## Purpose
This project completes a Seaborn-based visualization assignment with two goals:

- Analyze `Exercise_Data.csv` to show how diet and exercise type relate to pulse over time.
- Use Seaborn's built-in `planets` dataset to create examples of relational, distributional, and categorical plots.

The script generates all required graphs, adds polished titles and labels, writes a short summary of conclusions, and saves everything in `output_plots/`.

## Output
Running the project creates:

- `01_exercise_heatmap.png`
- `02_exercise_categorical_plot.png`
- `03_planets_relational_scatter.png`
- `04_planets_relational_line.png`
- `05_planets_distribution_hist.png`
- `06_planets_distribution_kde.png`
- `07_planets_categorical_count.png`
- `08_planets_categorical_box.png`
- `assignment_summary.txt`

The project also stores a local `planets_dataset.csv` cache after a successful load so later runs are more reliable.

## How To Run
1. Install the required libraries:

```bash
python -m pip install -r requirements.txt
```

2. Run the assignment script:

```bash
python seaborn_assignment.py
```

3. Open the images and summary text in `output_plots/`.

## Class Design And Implementation
The program is split into small classes so each part of the assignment has a clear responsibility.

### `ExercisePulseAnalysis`
Purpose:
Handles the school and gym pulse dataset from loading through plotting and written interpretation.

Attributes:
- `csv_path`: location of `Exercise_Data.csv`.
- `output_dir`: folder where exercise plot images are saved.
- `data`: the raw pulse dataset after loading the CSV.
- `long_data`: the reshaped version of the dataset used for Seaborn plotting.
- `pulse_columns`: the pulse measurement columns (`1 min`, `15 min`, `30 min`).
- `diet_order`: the display order for diet categories.
- `exercise_order`: the display order for exercise categories.
- `palette`: custom colors used to distinguish diet groups clearly.

Methods:
- `load_data()`: reads the CSV file and validates that the required columns exist.
- `prepare_long_data()`: converts the wide pulse table into long format and applies ordered categories for cleaner plots.
- `create_heatmap()`: builds a heatmap of average pulse by diet, exercise type, and time point.
- `create_categorical_plot()`: creates a multi-panel categorical plot using box plots with overlaid individual points.
- `summarize()`: produces a short explanation of the main trends in language that could be shared with elementary school students.
- `run()`: executes the full exercise-data workflow in order.

Implementation notes:
This class separates preparation from plotting so the same reshaped dataset can power multiple graph types without duplicated logic.

### `PlanetsSeabornAnalysis`
Purpose:
Creates the required two relational, two distributional, and two categorical plots from the `planets` dataset.

Attributes:
- `output_dir`: folder where planets graphs are saved.
- `dataset_cache_path`: local CSV cache used to make future runs more reliable.
- `data`: the loaded planets dataset.

Methods:
- `load_data()`: loads the planets dataset from a local cache when available, otherwise fetches it through Seaborn and saves a cache file.
- `_top_methods(limit)`: returns the most common detection methods to keep legends readable and visuals less cluttered.
- `create_relational_plots()`: creates a scatter plot and a yearly discovery line plot.
- `create_distribution_plots()`: creates a histogram with KDE and a KDE comparison plot by detection method.
- `create_categorical_plots()`: creates a count plot and a box plot for the most common detection methods.
- `summarize()`: identifies the most notable planets trend shown by the graphs.
- `run()`: executes the full planets plotting workflow.

Implementation notes:
This class keeps dataset loading separate from visualization logic and intentionally filters to the most common methods in some plots so the results stay readable and aesthetically strong.

### `SeabornAssignmentProject`
Purpose:
Coordinates the full project and applies a consistent visual style.

Attributes:
- `csv_path`: source path for the exercise dataset.
- `output_dir`: folder used for all generated plots and summary output.

Methods:
- `_style()`: applies the shared Seaborn theme, grid, and background styling used across the project.
- `run()`: creates the output folder, runs both analysis classes, writes `assignment_summary.txt`, and prints the conclusions.

Implementation notes:
This top-level class keeps the script organized by acting as the single orchestration point instead of putting all logic directly in `main()`.

## Brief Conclusions
### Exercise data
The exercise graphs show that running increases pulse the most, walking produces a smaller increase, and resting keeps pulse the most stable. The difference between exercise types is much larger than the difference between diet groups in this small sample, so the clearest message for elementary students is that more active exercise makes the heart beat faster because the body needs more oxygen and energy.

### Planets data
The yearly line plot best demonstrates something notable because it clearly shows the rapid growth in planet discoveries over time, especially the strong peak in 2011. The count plot also helps explain the rest of the dataset by showing that a few detection methods, especially radial velocity and transit, make up most of the records, which influences which kinds of planets appear most often in the other graphs.

## Limitations
- The exercise dataset contains only 30 participants, so the conclusions are useful for class discussion but not strong scientific proof.
- Diet labels are broad and do not capture full nutrition habits, sleep, age differences, or other factors that could affect pulse.
- Some planets plots exclude rows with missing values because mass, distance, or orbital period is not recorded for every planet.
