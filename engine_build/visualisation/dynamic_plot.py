import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

from engine_build.metrics.world_frames import WorldFrames
from engine_build.regimes.registry import get_regime_config
from engine_build.runner.regime_runner import BatchRunner


"""
Research-grade visualization for ecosystem ABM

Signals visualized:

movement
cluster formation
energy gradients
population pressure
population dynamics
"""


def animate_world(
    frames: WorldFrames,
    fertility: np.ndarray,
    max_resource_level: int,
) -> None:

    resources = frames.resources
    energies = frames.run_agent_energies

    trail_length = 4
    position_history = []

    height, width = fertility.shape
    n_frames = len(resources)

    # --------------------------------------------------
    # Animation state
    # --------------------------------------------------

    state = {
        "paused": False,
        "fps": 20,
        "frame": 0,
    }

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    ax_fertility = axes[0, 0]
    ax_resources = axes[0, 1]
    ax_agents = axes[1, 0]
    ax_population = axes[1, 1]

    # --------------------------------------------------
    # Fertility
    # --------------------------------------------------

    ax_fertility.imshow(fertility, vmin=0, vmax=max_resource_level)
    ax_fertility.set_title("Fertility")
    ax_fertility.set_xticks([])
    ax_fertility.set_yticks([])

    # --------------------------------------------------
    # Resources
    # --------------------------------------------------

    resource_img = ax_resources.imshow(
        resources[0],
        vmin=0,
        vmax=max_resource_level,
    )
    ax_resources.set_title("Resources")
    ax_resources.set_xticks([])
    ax_resources.set_yticks([])

    # --------------------------------------------------
    # Agents panel
    # --------------------------------------------------

    ax_agents.set_title("Agents")
    ax_agents.set_facecolor("black")

    ax_agents.set_xlim(0, width)
    ax_agents.set_ylim(0, height)
    ax_agents.invert_yaxis()

    ax_agents.set_xticks([])
    ax_agents.set_yticks([])

    scatter = ax_agents.scatter([], [])

    fig.colorbar(scatter, ax=ax_agents, label="Agent Energy")

    # --------------------------------------------------
    # Population dynamics
    # --------------------------------------------------

    ax_population.set_title("Population Dynamics")

    ticks = frames.ticks * frames.capture_every
    population = frames.population

    ax_population.set_xlim(0, len(ticks))
    ax_population.set_ylim(0, max(population) * 1.1)

    population_line, = ax_population.plot([], [], color="black", lw=2)
    time_marker = ax_population.axvline(0, color="red", linestyle="--")

    ax_population.set_xlabel("Tick")
    ax_population.set_ylabel("Population")

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update(i):

        state["frame"] = i

        positions = frames.agent_positions[i]
        energy = energies[i]

        ax_agents.clear()

        ax_agents.set_facecolor("black")
        ax_agents.set_xlim(0, width)
        ax_agents.set_ylim(0, height)
        ax_agents.invert_yaxis()

        ax_agents.set_xticks([])
        ax_agents.set_yticks([])

        # --------------------------
        # Population pressure
        # --------------------------

        counts = Counter(positions)
        sizes = [10 + counts[p] * 8 for p in positions]

        # --------------------------
        # Movement trails
        # --------------------------

        position_history.append(positions)

        if len(position_history) > trail_length:
            position_history.pop(0)

        for age, pos in enumerate(position_history[:-1]):

            if not pos:
                continue

            xs, ys = zip(*pos)

            ax_agents.scatter(
                xs,
                ys,
                s=3,
                color="white",
                alpha=0.12 * (age + 1),
                linewidth=0,
            )

        # --------------------------
        # Current agents
        # --------------------------

        if positions:
            xs, ys = zip(*positions)
        else:
            xs, ys = [], []

        scatter = ax_agents.scatter(
            xs,
            ys,
            c=energy,
            cmap="plasma",
            s=sizes,
            alpha=0.9,
            linewidth=0,
        )

        ax_agents.set_title(
            f"Agents | Tick {frames.ticks[i]} | Pop {frames.population[i]}"
        )

        # --------------------------
        # Resource update
        # --------------------------

        resource_img.set_data(resources[i])

        # --------------------------
        # Population time series
        # --------------------------

        population_line.set_data(
            ticks[: i + 1],
            population[: i + 1],
        )

        time_marker.set_xdata([ticks[i]])

        return resource_img, scatter, population_line, time_marker

    # --------------------------------------------------
    # Animation
    # --------------------------------------------------

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=n_frames,
        interval=int(1000 / state["fps"]),
    )

    # --------------------------------------------------
    # Controls
    # --------------------------------------------------

    def apply_fps():

        ani.event_source.interval = int(1000 / state["fps"])
        fig.canvas.draw_idle()

    def toggle_pause():

        if state["paused"]:
            ani.event_source.start()
        else:
            ani.event_source.stop()

        state["paused"] = not state["paused"]

    def step_frame(step):

        if not state["paused"]:
            return

        state["frame"] = np.clip(state["frame"] + step, 0, n_frames - 1)

        update(state["frame"])
        fig.canvas.draw_idle()

    def on_key(event):

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

    plt.tight_layout()
    plt.show()


# --------------------------------------------------
# Run simulation
# --------------------------------------------------


def main():

    regime_config = get_regime_config("stable")

    seed = np.random.SeedSequence(42)

    runner = BatchRunner(regime_config, n_runs=1, ticks=1000)

    engine, metrics, frames = runner.run_single(seed, ticks=1000)

    animate_world(
        frames,
        engine.world.fertility,
        engine.config.max_resource_level,
    )


if __name__ == "__main__":
    main()