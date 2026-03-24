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
Interactive world-view animation for the ecosystem ABM.

Signals visualized:
- fertility background
- dynamic resource field
- agent positions with movement trails
- agent energy gradient
- local crowding / population pressure via point size
- population dynamics through time

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



def _set_agent_axis(ax: plt.Axes, width: int, height: int) -> None:
    ax.set_facecolor("black")
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])



def _point_sizes(positions: np.ndarray) -> np.ndarray:
    if positions.size == 0:
        return np.asarray([], dtype=float)

    unique_positions, counts = np.unique(positions, axis=0, return_counts=True)
    count_lookup = {
        tuple(position): count
        for position, count in zip(unique_positions.tolist(), counts.tolist())
    }
    return np.asarray(
        [10 + 8 * count_lookup[tuple(position)] for position in positions.tolist()],
        dtype=float,
    )



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
) -> animation.FuncAnimation:
    frames = _require_world_view(metrics)

    height, width = fertility.shape
    n_frames = len(frames)
    sampled_ticks = _sample_ticks(metrics, capture_every)
    population = np.asarray(metrics.population, dtype=int)
    all_ticks = np.arange(len(population), dtype=int)
    sampled_population = population[sampled_ticks]

    state = {
        "paused": False,
        "fps": fps,
        "frame": 0,
    }
    position_history: list[np.ndarray] = []

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    ax_fertility = axes[0, 0]
    ax_resources = axes[0, 1]
    ax_agents = axes[1, 0]
    ax_population = axes[1, 1]

    ax_fertility.imshow(fertility, vmin=0, vmax=max_resource_level)
    ax_fertility.set_title("Fertility")
    ax_fertility.set_xticks([])
    ax_fertility.set_yticks([])

    resource_img = ax_resources.imshow(
        frames[0].resources,
        vmin=0,
        vmax=max_resource_level,
    )
    ax_resources.set_title("Resources")
    ax_resources.set_xticks([])
    ax_resources.set_yticks([])

    _set_agent_axis(ax_agents, width=width, height=height)
    energy_norm = Normalize(vmin=0, vmax=_max_energy(frames))
    colorbar_mappable = plt.cm.ScalarMappable(norm=energy_norm, cmap="plasma")
    colorbar_mappable.set_array([])
    fig.colorbar(colorbar_mappable, ax=ax_agents, label="Agent Energy")

    ax_population.set_title("Population Dynamics")
    ax_population.set_xlim(0, max(1, len(population) - 1))
    ax_population.set_ylim(0, max(1, int(population.max())) * 1.1)
    ax_population.set_xlabel("Tick")
    ax_population.set_ylabel("Population")

    population_line, = ax_population.plot([], [], color="black", lw=2)
    time_marker = ax_population.axvline(0, color="red", linestyle="--")

    def update(frame_index: int):
        state["frame"] = frame_index

        current_frame = frames[frame_index]
        positions = current_frame.positions
        energies = current_frame.energies
        current_tick = int(sampled_ticks[frame_index])
        current_population = int(sampled_population[frame_index])

        ax_agents.clear()
        _set_agent_axis(ax_agents, width=width, height=height)

        position_history.append(positions.copy())
        if len(position_history) > trail_length:
            position_history.pop(0)

        for trail_age, trail_positions in enumerate(position_history[:-1]):
            if trail_positions.size == 0:
                continue

            xs = trail_positions[:, 0]
            ys = trail_positions[:, 1]
            ax_agents.scatter(
                xs,
                ys,
                s=3,
                color="white",
                alpha=0.12 * (trail_age + 1),
                linewidth=0,
            )

        sizes = _point_sizes(positions)
        if positions.size == 0:
            xs = np.asarray([])
            ys = np.asarray([])
        else:
            xs = positions[:, 0]
            ys = positions[:, 1]

        scatter = ax_agents.scatter(
            xs,
            ys,
            c=energies,
            cmap="plasma",
            norm=energy_norm,
            s=sizes,
            alpha=0.9,
            linewidth=0,
        )
        ax_agents.set_title(f"Agents | Tick {current_tick} | Pop {current_population}")

        resource_img.set_data(current_frame.resources)

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
