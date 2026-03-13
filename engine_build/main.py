
## main entry point for runs

from engine_build.experiments.run_experiment import run_experiment_mode


from engine_build.experiments.fertility_dist_plot import run_and_plot_population_dynamics
import argparse




        
def parse_args():        
    parser = argparse.ArgumentParser(description="Ecosystem Metrics Analysis Tool")

    parser.add_argument(
        "--mode",
        choices=["validation", "experiment"],
        required=True,
        help="Select run mode"
    )

    parser.add_argument(
        "--regime",
        choices=["extinction", "stable", "saturated", "all"],
        default="stable",
        help="Select ecological regime type"
    )
    parser.add_argument(
    "--seed",
    type=int,
    default=None,
    help="Optional master seed override"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=None,
        help="Number of runs to average over"
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="Number of ticks to run for"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot batch population dynamics (experiment only)"
    )
    parser.add_argument(
        "--plot_dev",
        action="store_true",
        help="Plot development figures (verbose)"
    )
    parser.add_argument(
        "--fertility",
        action="store_true",
        help="Run fertility experiment"
    )

    return parser.parse_args()



def main():
     
    args = parse_args()

    if args.fertility:
        run_and_plot_population_dynamics()

    elif args.mode == "experiment":
        if args.regime == "all":
            raise ValueError("Cannot run all regimes in experiment mode.")
        run_experiment_mode(args)
    



if __name__ == "__main__":


    main()