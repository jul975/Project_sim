
## main entry point for runs

from engine_build.experiments.run_experiment import run_experiment_mode
from engine_build.test.validation import run_validation_mode

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
        choices=["extinction", "stable", "saturated"],
        default="stable",
        help="Select ecological regime type"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot batch population dynamics (experiment only)"
    )

    return parser.parse_args()



def main():
     
    args = parse_args()

    if args.mode == "validation":
        run_validation_mode(args)

    elif args.mode == "experiment":
        run_experiment_mode(args)
    



if __name__ == "__main__":


    main()