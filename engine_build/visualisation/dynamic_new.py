import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

from engine_build.core.step_results import WorldView
from engine_build.metrics.metrics import SimulationMetrics
from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec
from engine_build.runner.regime_runner import RunArtifacts, Runner

"""
Mesa-style discrete-space animation for the ecosystem ABM.

Key differences from the older dynamic plot:
- the agent-space panel uses cell-centered coordinates
- the axis bounds are [-0.5, width-0.5] / [-0.5, height-0.5]
- resource/space layers use origin="lower"
- optional dotted grid lines mimic Mesa's orthogonal grid rendering
- occupied cells can be aggregated so multi-occupancy remains visible

Controls:
- space: pause / resume
- left/right: step one sampled frame while paused
- up/down: increase / decrease playback FPS
"""

WORLD_VIEW_CAPTURE_EVERY = 10


def _require_world_view(metrics: SimulationMetrics) -> list[WorldView]:
    if not metrics.world_view:
        raise ValueError(
            "No world_view data available for this run. "
            "Run the simulation with include_world_frames=True."
        )
    return metrics.world_view



def _sample_ticks(metrics: SimulationMetrics, capture_every: int) -> np.ndarray:
    sample_ticks = np.arange(0, len(metrics.population), capture_every, dtype=int)
    return sample_ticks[: len(metrics.world_view)]



def _resource_extent(width: int, height: int) -> tuple[float, float, float, float]:
    return (-0.5, width - 0.5, -0.5, height - 0.5)



def _set_grid_axis(
    ax: plt.Axes,
    width: int,
    height: int,
    *,
    draw_grid: bool,
    background: str | None = None,
) -> None:
    if background is not None:
        ax.set_facecolor(background)

    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    if draw_grid:
        for x in np.arange(-0.5, width, 1.0):
            ax.axvline(x, color="gray", linestyle=":", linewidth=0.4, alpha=0.35, zorder=2)
        for y in np.arange(-0.5, height, 1.0):
            ax.axhline(y, color="gray", linestyle=":", linewidth=0.4, alpha=0.35, zorder=2)



def _aggregate_cell_view(
    positions: np.ndarray,
    energies: np.ndarray,
    width: int,
    height: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Aggregate agents by occupied cell.

    Returns:
        occupied_positions: (n_occupied, 2) int array with [x, y]
        mean_energy: (n_occupied,) float array
        cell_counts: (n_occupied,) int array
    """
    if positions.size == 0:
        return (
            np.empty((0, 2), dtype=np.int32),
            np.empty((0,), dtype=float),
            np.empty((0,), dtype=np.int32),
        )

    linear_idx = positions[:, 1] * width + positions[:, 0]
    unique_idx, inverse, counts = np.unique(linear_idx, return_inverse=True, return_counts=True)
    energy_sums = np.bincount(inverse, weights=energies.astype(float), minlength=len(unique_idx))
    mean_energy = energy_sums / counts

    xs = unique_idx % width
    ys = unique_idx // width
    occupied_positions = np.column_stack((xs, ys)).astype(np.int32, copy=False)
    return occupied_positions, mean_energy, counts.astype(np.int32, copy=False)



def _mesa_marker_sizes(width: int, height: int, counts: np.ndarray, *, scale_with_count: bool) -> np.ndarray:
    if counts.size == 0:
        return np.asarray([], dtype=float)

    base_size = (180 / max(width, height)) ** 2
    if not scale_with_count:
        return np.full(counts.shape, base_size, dtype=float)

    # Non-linear scaling keeps crowding visible without exploding marker area.
    return base_size * (1.0 + 0.85 * np.sqrt(np.maximum(counts - 1, 0)))



def _max_energy(frames: list[WorldView]) -> int:
    max_energy = max(
        (int(frame.energies.max()) if frame.energies.size else 0 for frame in frames),
        default=0,
    )
    return max(1, max_energy)



def animate_world(
    metrics: SimulationMetrics,
    fertility: np.ndarray,
    max_resource_level: int,
    *,
    capture_every: int = WORLD_VIEW_CAPTURE_EVERY,
    trail_length: int = 4,
    fps: int = 20,
    draw_grid: bool = True,
    aggregate_cells: bool = True,
    overlay_resources_in_space: bool = True,
    overlay_fertility_in_space: bool = False,
) -> animation.FuncAnimation:
    """Animate sampled world-view frames using a Mesa-like grid-space style.

    Args:
        metrics: Per-run metrics containing optional world_view snapshots.
        fertility: Static fertility field shaped (height, width).
        max_resource_level: Resource upper bound for colormap normalization.
        capture_every: World-view sampling interval in ticks.
        trail_length: Number of previous sampled frames to retain as faint occupancy trails.
        fps: Playback speed.
        draw_grid: Whether to draw dotted grid lines in the space panel.
        aggregate_cells: If True, merge all agents in the same cell into a single marker.
            This is recommended because the model permits multi-occupancy and raw Mesa-style
            overplotting would hide stacks.
        overlay_resources_in_space: Draw the dynamic resource field underneath the agent markers.
        overlay_fertility_in_space: Draw the fertility field underneath the agent markers.
            Use this instead of resource overlay if you want a static background.
    """
    frames = _require_world_view(metrics)

    height, width = fertility.shape
    extent = _resource_extent(width, height)
    n_frames = len(frames)
    sampled_ticks = _sample_ticks(metrics, capture_every)
    population = np.asarray(metrics.population, dtype=int)
    all_ticks = np.arange(len(population), dtype=int)
    sampled_population = population[sampled_ticks]

    state = {"paused": False, "fps": fps, "frame": 0}
    position_history: list[np.ndarray] = []

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    ax_fertility = axes[0, 0]
    ax_resources = axes[0, 1]
    ax_space = axes[1, 0]
    ax_population = axes[1, 1]

    fertility_img = ax_fertility.imshow(
        fertility,
        origin="lower",
        extent=extent,
        vmin=0,
        vmax=max_resource_level,
        interpolation="nearest",
    )
    ax_fertility.set_title("Fertility")
    _set_grid_axis(ax_fertility, width=width, height=height, draw_grid=False)
    fig.colorbar(fertility_img, ax=ax_fertility, label="Fertility")

    resource_img = ax_resources.imshow(
        frames[0].resources,
        origin="lower",
        extent=extent,
        vmin=0,
        vmax=max_resource_level,
        interpolation="nearest",
    )
    ax_resources.set_title("Resources")
    _set_grid_axis(ax_resources, width=width, height=height, draw_grid=False)
    fig.colorbar(resource_img, ax=ax_resources, label="Resources")

    energy_norm = Normalize(vmin=0, vmax=_max_energy(frames))
    colorbar_mappable = plt.cm.ScalarMappable(norm=energy_norm, cmap="plasma")
    colorbar_mappable.set_array([])
    fig.colorbar(colorbar_mappable, ax=ax_space, label="Agent Energy")

    ax_population.set_title("Population Dynamics")
    ax_population.set_xlim(0, max(1, len(population) - 1))
    ax_population.set_ylim(0, max(1, int(population.max())) * 1.1)
    ax_population.set_xlabel("Tick")
    ax_population.set_ylabel("Population")
    population_line, = ax_population.plot([], [], color="black", lw=2)
    time_marker = ax_population.axvline(0, color="red", linestyle="--")

    def draw_space_frame(frame_index: int):
        current_frame = frames[frame_index]
        positions = current_frame.positions
        energies = current_frame.energies
        current_tick = int(sampled_ticks[frame_index])
        current_population = int(sampled_population[frame_index])

        ax_space.clear()
        _set_grid_axis(ax_space, width=width, height=height, draw_grid=draw_grid, background="black")

        if overlay_fertility_in_space:
            ax_space.imshow(
                fertility,
                origin="lower",
                extent=extent,
                vmin=0,
                vmax=max_resource_level,
                cmap="Greens",
                interpolation="nearest",
                alpha=0.35,
                zorder=0,
            )

        if overlay_resources_in_space:
            ax_space.imshow(
                current_frame.resources,
                origin="lower",
                extent=extent,
                vmin=0,
                vmax=max_resource_level,
                cmap="viridis",
                interpolation="nearest",
                alpha=0.75,
                zorder=0,
            )

        position_history.append(positions.copy())
        if len(position_history) > trail_length:
            position_history.pop(0)

        # Faint occupancy trails: cloud of previous occupied positions.
        for trail_age, trail_positions in enumerate(position_history[:-1]):
            if trail_positions.size == 0:
                continue
            ax_space.scatter(
                trail_positions[:, 0],
                trail_positions[:, 1],
                s=(110 / max(width, height)) ** 2,
                marker="o",
                c="white",
                alpha=0.08 + 0.08 * trail_age,
                linewidths=0,
                zorder=3,
            )

        if aggregate_cells:
            plot_positions, plot_energies, cell_counts = _aggregate_cell_view(
                positions, energies, width, height
            )
            sizes = _mesa_marker_sizes(width, height, cell_counts, scale_with_count=True)
            size_label = f"Occupied {len(plot_positions)} | Agents {current_population}"
        else:
            plot_positions = positions
            plot_energies = energies.astype(float, copy=False)
            cell_counts = np.ones(len(plot_positions), dtype=np.int32)
            sizes = _mesa_marker_sizes(width, height, cell_counts, scale_with_count=False)
            size_label = f"Agents {current_population}"

        if plot_positions.size == 0:
            xs = np.asarray([], dtype=float)
            ys = np.asarray([], dtype=float)
        else:
            xs = plot_positions[:, 0]
            ys = plot_positions[:, 1]

        scatter = ax_space.scatter(
            xs,
            ys,
            c=plot_energies,
            cmap="plasma",
            norm=energy_norm,
            s=sizes,
            marker="o",
            edgecolors="black",
            linewidths=0.25,
            alpha=0.95,
            zorder=4,
        )
        ax_space.set_title(f"Space | Tick {current_tick} | {size_label}")
        return scatter

    def update(frame_index: int):
        state["frame"] = frame_index
        current_frame = frames[frame_index]
        current_tick = int(sampled_ticks[frame_index])

        resource_img.set_data(current_frame.resources)
        scatter = draw_space_frame(frame_index)

        population_line.set_data(
            all_ticks[: current_tick + 1],
            population[: current_tick + 1],
        )
        time_marker.set_xdata([current_tick])

        return resource_img, scatter, population_line, time_marker

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=n_frames,
        interval=int(1000 / state["fps"]),
        blit=False,
    )

    def apply_fps() -> None:
        ani.event_source.interval = int(1000 / state["fps"])
        fig.canvas.draw_idle()

    def toggle_pause() -> None:
        if state["paused"]:
            ani.event_source.start()
        else:
            ani.event_source.stop()
        state["paused"] = not state["paused"]

    def step_frame(step: int) -> None:
        if not state["paused"]:
            return
        state["frame"] = int(np.clip(state["frame"] + step, 0, n_frames - 1))
        update(state["frame"])
        fig.canvas.draw_idle()

    def on_key(event) -> None:
        if event.key == " ":
            toggle_pause()
        elif event.key == "up":
            state["fps"] = min(state["fps"] + 5, 120)
            apply_fps()
        elif event.key == "down":
            state["fps"] = max(state["fps"] - 5, 1)
            apply_fps()
        elif event.key == "left":
            step_frame(-1)
        elif event.key == "right":
            step_frame(1)

    fig.canvas.mpl_connect("key_press_event", on_key)
    fig._animation = ani
    update(0)
    plt.tight_layout()
    plt.show()
    return ani



def animate_run(
    run_results: RunArtifacts,
    *,
    capture_every: int = WORLD_VIEW_CAPTURE_EVERY,
    trail_length: int = 4,
    fps: int = 20,
    draw_grid: bool = True,
    aggregate_cells: bool = True,
    overlay_resources_in_space: bool = True,
    overlay_fertility_in_space: bool = False,
) -> animation.FuncAnimation:
    if run_results.metrics is None:
        raise ValueError("run_results.metrics is None")
    if run_results.engine_final is None:
        raise ValueError("run_results.engine_final is None")

    return animate_world(
        metrics=run_results.metrics,
        fertility=run_results.engine_final.world.fertility,
        max_resource_level=run_results.engine_final.resource_params.max_resource_level,
        capture_every=capture_every,
        trail_length=trail_length,
        fps=fps,
        draw_grid=draw_grid,
        aggregate_cells=aggregate_cells,
        overlay_resources_in_space=overlay_resources_in_space,
        overlay_fertility_in_space=overlay_fertility_in_space,
    )



def main() -> None:
    regime_spec = get_regime_spec("stable")
    regime_config: CompiledRegime = compile_regime(regime_spec)

    seed = np.random.SeedSequence(42)
    runner = Runner(
        regime_config,
        n_runs=1,
        include_world_frames=True,
    )

    run_results: RunArtifacts = runner.run_single(seed, ticks=1000)
    animate_run(run_results)


if __name__ == "__main__":
    main()
