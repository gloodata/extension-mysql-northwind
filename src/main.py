import argparse
import logging
from toolbox import tb

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Start the server with specified host, port."
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Hostname or IP address to bind the server to. Default is '127.0.0.1'.",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8887,
        help="Port number to bind the server to. Default is 8887.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    tb.serve(host=args.host, port=args.port)
