import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

from engine_build.core.step_results import WorldView
from engine_build.metrics.metrics import SimulationMetrics
from engine_build.regimes.compiled import CompiledRegime
from engine_build.regimes.compiler import compile_regime
from engine_build.regimes.registry import get_regime_spec
from engine_build.runner.batch_runner import RunArtifacts, Runner

"""
Mesa-style discrete-space animation for the ecosystem ABM.

This version renders agent occupancy as a density matrix instead of circles.

Controls:
- space: pause / resume
- left/right: step one sampled frame while paused
- up/down: increase / decrease playback FPS
"""

WORLD_VIEW_CAPTURE_EVERY = 10


def _occupancy_matrix(
    positions: np.ndarray,
    width: int,
    height: int,
) -> np.ndarray:
    """
    Convert agent positions (x, y) into a density matrix shaped (height, width),
    where density[y, x] = number of agents in that cell.
    """
    if positions.size == 0:
        return np.zeros((height, width), dtype=np.int32)

    linear_idx = positions[:, 1] * width + positions[:, 0]
    counts = np.bincount(linear_idx, minlength=width * height)
    return counts.reshape(height, width)


def _masked_occupancy_matrix(
    positions: np.ndarray,
    width: int,
    height: int,
) -> np.ma.MaskedArray:
    density = _occupancy_matrix(positions, width, height)
    return np.ma.masked_where(density == 0, density)


def _max_occupancy(
    frames: list[WorldView],
    width: int,
    height: int,
) -> int:
    max_occ = 1

    for frame in frames:
        positions = frame.positions
        if positions.size == 0:
            continue

        linear_idx = positions[:, 1] * width + positions[:, 0]
        counts = np.bincount(linear_idx, minlength=width * height)
        frame_max = int(counts.max()) if counts.size else 0
        max_occ = max(max_occ, frame_max)

    return max_occ


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
            ax.axvline(
                x, color="gray", linestyle=":", linewidth=0.4, alpha=0.35, zorder=2
            )
        for y in np.arange(-0.5, height, 1.0):
            ax.axhline(
                y, color="gray", linestyle=":", linewidth=0.4, alpha=0.35, zorder=2
            )


def animate_world(
    metrics: SimulationMetrics,
    fertility: np.ndarray,
    max_resource_level: int,
    *,
    capture_every: int = WORLD_VIEW_CAPTURE_EVERY,
    fps: int = 20,
    draw_grid: bool = True,
    overlay_resources_in_space: bool = False,
    overlay_fertility_in_space: bool = False,
    density_alpha: float = 0.95,
) -> animation.FuncAnimation:
    """
    Animate sampled world-view frames using a matrix-colored density plot
    instead of plotting agent circles.

    The space panel renders:
    - optional fertility/resource background
    - occupancy density matrix via imshow

    density[y, x] = number of agents at cell (x, y)
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

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    ax_fertility = axes[0, 0]
    ax_resources = axes[0, 1]
    ax_space = axes[1, 0]
    ax_population = axes[1, 1]

    # --------------------------------------------------
    # Fertility panel
    # --------------------------------------------------
    fertility_img = ax_fertility.imshow(
        fertility,
        origin="lower",
        extent=extent,
        vmin=0,
        vmax=max_resource_level,
        interpolation="nearest",
        cmap="Greens",
    )
    ax_fertility.set_title("Fertility")
    _set_grid_axis(ax_fertility, width=width, height=height, draw_grid=False)
    fig.colorbar(fertility_img, ax=ax_fertility, label="Fertility")

    # --------------------------------------------------
    # Resource panel
    # --------------------------------------------------
    resource_img = ax_resources.imshow(
        frames[0].resources,
        origin="lower",
        extent=extent,
        vmin=0,
        vmax=max_resource_level,
        interpolation="nearest",
        cmap="viridis",
    )
    ax_resources.set_title("Resources")
    _set_grid_axis(ax_resources, width=width, height=height, draw_grid=False)
    fig.colorbar(resource_img, ax=ax_resources, label="Resources")

    # --------------------------------------------------
    # Space density panel
    # --------------------------------------------------
    _set_grid_axis(
        ax_space,
        width=width,
        height=height,
        draw_grid=draw_grid,
        background="black",
    )

    space_background_img = None

    if overlay_fertility_in_space:
        space_background_img = ax_space.imshow(
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
    elif overlay_resources_in_space:
        space_background_img = ax_space.imshow(
            frames[0].resources,
            origin="lower",
            extent=extent,
            vmin=0,
            vmax=max_resource_level,
            cmap="viridis",
            interpolation="nearest",
            alpha=0.60,
            zorder=0,
        )

    density0 = _masked_occupancy_matrix(frames[0].positions, width, height)

    # Normalize against max per-cell occupancy, not total population.
    density_vmax = _max_occupancy(frames, width, height)
    density_norm = Normalize(vmin=1, vmax=density_vmax)

    density_cmap = plt.cm.magma.copy()
    density_cmap.set_bad((0, 0, 0, 0))  # transparent masked cells

    space_density_img = ax_space.imshow(
        density0,
        origin="lower",
        extent=extent,
        cmap=density_cmap,
        norm=density_norm,
        interpolation="nearest",
        alpha=density_alpha,
        zorder=3,
    )

    fig.colorbar(space_density_img, ax=ax_space, label="Agents per Cell")
    ax_space.set_title(
        f"Space Density | Tick {int(sampled_ticks[0])} | Pop {int(sampled_population[0])}"
    )

    # --------------------------------------------------
    # Population dynamics panel
    # --------------------------------------------------
    ax_population.set_title("Population Dynamics")
    ax_population.set_xlim(0, max(1, len(population) - 1))
    ax_population.set_ylim(0, max(1, int(population.max())) * 1.1)
    ax_population.set_xlabel("Tick")
    ax_population.set_ylabel("Population")

    population_line, = ax_population.plot([], [], color="black", lw=2)
    time_marker = ax_population.axvline(0, color="red", linestyle="--")

    # --------------------------------------------------
    # Update
    # --------------------------------------------------
    def update(frame_index: int):
        state["frame"] = frame_index

        current_frame = frames[frame_index]
        current_tick = int(sampled_ticks[frame_index])
        current_population = int(sampled_population[frame_index])

        resource_img.set_data(current_frame.resources)

        if space_background_img is not None and overlay_resources_in_space:
            space_background_img.set_data(current_frame.resources)

        density = _masked_occupancy_matrix(current_frame.positions, width, height)
        space_density_img.set_data(density)

        ax_space.set_title(
            f"Space Density | Tick {current_tick} | Pop {current_population}"
        )

        population_line.set_data(
            all_ticks[: current_tick + 1],
            population[: current_tick + 1],
        )
        time_marker.set_xdata([current_tick])

        return (
            resource_img,
            space_density_img,
            population_line,
            time_marker,
        )

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=n_frames,
        interval=int(1000 / state["fps"]),
        blit=False,
    )

    # --------------------------------------------------
    # Controls
    # --------------------------------------------------
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
    fps: int = 20,
    draw_grid: bool = True,
    overlay_resources_in_space: bool = False,
    overlay_fertility_in_space: bool = False,
    density_alpha: float = 0.95,
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
        fps=fps,
        draw_grid=draw_grid,
        overlay_resources_in_space=overlay_resources_in_space,
        overlay_fertility_in_space=overlay_fertility_in_space,
        density_alpha=density_alpha,
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
