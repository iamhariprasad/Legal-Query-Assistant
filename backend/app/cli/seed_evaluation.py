"""Seed the evaluation table with the labeled dataset metrics baseline."""

from app.cli.run_evaluation import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

