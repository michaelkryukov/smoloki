import argparse
import os
import shutil


def main():
    parser = argparse.ArgumentParser(
        "smoloki-install",
        description="cli for installing wrapper for smoloki",
    )
    parser.add_argument(
        "--install-wrapper-for-nodejs",
        dest="install_wrapper_for_nodejs",
        type=str,
        default="",
        help="path to target node_modules/ folder",
    )

    args = parser.parse_args()

    if args.install_wrapper_for_nodejs:
        source_path = os.path.join(os.path.dirname(__file__), "nodejs.js")
        wrapper_path = os.path.join(args.install_wrapper_for_nodejs, "smoloki.js")
        shutil.copy(source_path, wrapper_path)
        print(f'Installed wrapper for NodeJS: "{wrapper_path}".')


if __name__ == "__main__":
    main()
