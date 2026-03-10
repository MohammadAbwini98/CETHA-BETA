import argparse

from app.jobs import backfill, update


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CETHA-BETA data jobs")
    parser.add_argument("job", choices=["backfill", "update"])
    args = parser.parse_args()
    if args.job == "backfill":
        backfill.run()
    else:
        update.run()
