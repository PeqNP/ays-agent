# Usage

This provides use examples for common use cases of the **@ys** agent.

To avoid writing the relationship configuration in every request, please configure the agent beforehand.

The example below will associate a new monitor to the node `com.example.server`:

```bash
$ ays-agent --org-secret="your_org_secret" --parent="com.example.server" --write-config
```

This examples show how to create a new child node under the `com.example.server` node:

```bash
$ ays-agent --org-secret="your_org_secret" --parent="com.example.server" --create-child --write-config
```

The following will configure a heartbeat timeout to alert you when the sensor fails to report within 5 minutes. It will transition your node into a "Critical" state.

```bash
$ ays-agent --org-secret="your_org_secret" --parent="com.example.server" --create-child --heartbeat-timeout=300 heartbeat-level=critical --write-config
```

If you are not using the public **@ys** server, you must provide the `--server` option:

```bash
ays-agent --server="https://ays.myserver.com/agent" --org-secret="your_org_secret" --parent="com.example.server" --create-child --heartbeat-timeout=300 heartbeat-level=critical --write-config
```

Now all subsequent executions of the `ays-agent` will use this configuration.

**NOTES:**

- Any options provided in subsequent executions will be used over the config for that specific execution. For example, if you provide a different value for the `--org-secret` option, it will use the value provided in that execution. It will _not_ write that name to the config.
- To over-write config, you must re-run the command using the `--write-config` option. Also, _all_ options must be provided when using `write-config`. This may change in the future to where the configuration for a single option may be changed at a time. Please let me know if you need this feature.

## Monitor Server Resource Usage

To monitor all of a server's resource usage:

```bash
$ ays-agent --monitor-resources=all
```

This will monitor all possible system resources.

**NOTE:** Some systems may or may not provide a way to monitor certain resources. In this context, the agent will send only the resources it is capable of monitoring.

If you wish to monitor specific resources:

```bash
$ ays-agent --monitor-resources=cpu,ram
```

This will monitor only the CPU and RAM resource usage.

For all available resource types, please refer to `docs/api.md`.

To change the reporting resolution, provide an interval value using the `interval` option.

```bash
$ ays-agent --monitor-resources=all --interval=60
```

This will send resource usage every 60 seconds, instead of the default of 5 minutes.

## Monitor a Program

Using the `--monitor-program` option you can report one or more values of your application's state.

Here's an example where we return a `1`, if the application is running, or `0`, if not running:

```bash
#!/bin/bash

process=`ps aux | grep "my_process_name" | grep -v 'grep' | grep -v 'bash'`
if [ "$process" == "" ]; then
    echo "0"
else
    echo "1"
fi
```

**NOTE:** Make sure your script has the correct (execute) permissions.

Now configure the agent to run this script every 2 minutes and alert when the value is not equal to `1`.

```bash
$ agent-sensor --monitor-program=/path/to/script.sh --interval=120 --value-threshold=ne1
```

The values echoed by the script must match the formatting requirements of the `--value` or `--values` options. For a single `value`, a numeric value e.g. `1.0`. For multiple `values`, a comma delimited list of numeric values e.g. `1.0,2.0,3.0`.

**NOTE:** If the script fails to execute for any reason, it will be reported to **@ys** with the error message included.

## One Shot Executions

There may be instances where you wish to have another process, `cron` etc., manage the execution of the agent.

A value, or values, may be passed to the agent via a one shot execution.

Below will send a value of `25` and alert if the value is greater than 50:

```bash
$ agent-sensor --value=25 --value-threshold=">50"
```