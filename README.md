# ays-agent

The At Your Service Agent is a Python app that allows you to monitor a system.

The agent provides a few mechanisms to report status to @ys. You can:

- Use the built-in resource usage agent. This will send CPU, HDD, RAM, and/or network usage to @ys.
- Call the agent as a one-shot script with a value or status.
- Execute a program, on a specified interval, and report the values it produces.

This agent integrates directly with the [Self Reporting Agents service](https://api.bithead.io:8443/help/library/what-is-an-agent/). Therefore, the property values provided to the CLI app are the same as those described in the documentation. For example, the alerting levels (`critical` ... `warning`), status states (`critical` ... `healthy`), etc. use the same parameter values.

## Installation

TBD

- `curl`? `pip`?

The installation will:

- Install the app in `/usr/bin/ays` or `C:\Program Files\x86\`
- Add `ays-agent` to the `PATH`

## What Next?

Please refer to

- `docs/api.md` for API documentation
- `docs/usage.md` for several examples on how to use the agent
