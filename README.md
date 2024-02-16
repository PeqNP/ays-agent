# ays-agent

The At Your Service Agent is a single Python script that allows you to monitor a server.

The agent provides a few mechanisms to report status to @ys. You can:

- Use the built-in resource usage agent. This will send CPU, HDD, RAM, and/or network usage. Which systems you monitor is configurable.
- Call the agent as a one-shot script with a value or status.
- Monitor a CSV file that is written by an external process. Each value is on a separate line. The name is the first column, the value in the second column.

This agent integrates directly with the [Self Reporting Agents service](https://api.bithead.io:8443/help/library/what-is-an-agent/). Therefore, the property values provided to the CLI app are the same as those described in the documentation. For example, the alerting levels (`critical` ... `warning`), status states (`critical` ... `healthy`), etc. use the same parameter values.

## Installation

TBD - `curl`? `pip`?

## Before You Start

It is best practice to first execute the script with the desired configuration that the agent will use to communicate with @ys. This allows you to only pass the values that change on subsequent calls of the agent, if necessary.

For example, if you want to use the agent to send values to @ys, you can do the following:
```bash
$ ays-agent --server="https://api.bithead.io:9443/agent/" --interval=300 --parent="com.example.server" --create-child --value=50
```

This will send a `value` of `50` to the @ys server every 5 minutes. It will also create a new child node under `com.example.server` using the hostname of the device.

**NOTE:** You may specify the name of the child with `--child` or set the `--monitor-name` and the child will adopt the monitor name value. How the agent derives its names is explained later in the documentation. There will also be several examples showing you how to send data to @ys.

Because the `server`, `interval`, and `parent` values will never change, we can provide the `--write-config` parameter to have this information saved to the `~/.ays-agent` configuration file.

First, send the `--write-config` parameter:

```bash
$ ays-agent --server="https://api.bithead.io:9443/agent/" --interval=300 --parent="com.example.server" --create-child --value=50 --write-config
```

This will write the config to disk. It will _not_ communicate with the @ys server.

Subsequent calls to the `ays-agent` will be:

```bash
$ ays-agent
```

The `write-config` parameter will write _all_ values provided to the config file, including the `value` parameter. However, if you do send the `value` parameter on a subsequent call, the `value` provided will over-write the config's `value`.

You may also write the configuration directly to `~/.ays-agent` yourself. Below are all of the key/value pairs:

```yaml
server: '[server]'
org_secret: '[org_secret]'
interval: '[interval_in_seconds]'
parent: '[parent_node_path]'
monitor_name: '[monitor_associated_to_node]'
child: '[relative_child_node_path_to_parent]'
node_type: '[type_of_node]'
managed: '[is_managed]'
heartbeat:
  level: '[alerting_level]'
  timeout: '[timeout_in_seconds]'

// Provide single value
value:
  name: '[name_of_value]'
  value: '[value_as_double]'
  threshold: '[threshold_value]'
// OR provide more than one value. This uses the same struct as the `value` property.
values:
- name: '[name_of_value]'
  value: '[value_as_double]'
  threshold: '[threshold_value]'
// OR provide status
status:
  message: '[status_message]'
  state: '[healthy_to_critical_state]'
```

## A Note On Statusing

If no `value`, `values`, `status`, or the agent has not been configured to collect data as a service, the agent will act as a heartbeat sensor. In other words, it's not necessary to send data to @ys if the only purpose of the agent is to inform @ys that the service is living.

## Parameters

### `--server`

The path to the @ys `agent` service endpoint.

**Default:** https://api.bithead.io:9443/agent/

## `--org-secret`

A required secret that allows you to communicate with your respective organization's system graph. Please get this value from your administrator.

### `--interval` (optional)

Interval, in seconds, that the agent will report a given value, status, heartbeat, or service information. Do _not_ provide this value if using this script as a one-shot! Providing `interval` turns the agent into a long-running service.

Again, if you wish to manually report `--value`, `--values`, `--status`, on your own schedule do not provide the `interval` parameter.

### `--parent`

The parent node path this agent will communicate with.

### `--monitor-name` (optional)

The name of the monitor that will be associated to the respective node.

**Default:** If a monitor name is not provided, the agent will attempt to derive the hostname of the device and use that as the monitor's name.

If the hostname can not be determined, this will raise an `Exception`.

The hostname will be formatted to conform to @ys node naming convention. This means spaces, special characters, etc. will be transformed into hyphens. If more than one hyphen is adjacent to another, they will be compressed to a single hyphen.

### `--child` (optional)

A relative path to a child node that lives under the `parent`'s node path. e.g. it can be a single path name `my-machine` or it define the group it is part of `building-1.floor-3.room-2.my-machine`.

For example, if the `parent` node path is `com.example.sites`, the single path node will live at `com.example.sites.my-machine`, the group path `com.example.sites.building-1.floor-3.room-2.my-machine`, respectively.

### `--create-child` (optional)

This will create a child node that lives under the `parent`'s node path. Use this if you wish to adopt the `monitor-name` value for the child node.

Use either `child` or `create-child`. Do not use both.

### `--node-type` (optional)

The type of node to create when a child is created.

**Default:** `machine`

### `--managed` (optional)

Indicates that this agent is responsible for managing its own configuration. Any subsequent call, with different configuration, will be re-written with the latest config.

Supported values are `t`, `y`, `true`, `1` for the value of "true." All other values are considered "false."

The only context where this should be `false` is if multiple agents should be associated to the same child node. Leave this `true` in all other contexts. Otherwise, the health status of the node may be skewed over time.

This value is ignored if no child is created.

**Default:** `true`

### Heartbeat Configuration (optional)

#### `--heartbeat-timeout`

The timeout, in seconds, in which the agent will be considered unhealthy if it doesn't report within specified time.

#### `--heartbeat-level`

The alerting level to transition into if hearbeat timeout exceeded.

Ignored if `hearbeat-interval` not provided.

**Default:** `critical`

### Values & Status

Please provide only _one_ reporting type. Or, provide no reporting types.

Again, if no reporting type is provided, the agent will act as a heartbeat sensor.

#### Single value (optional)

##### `--value`

Report a single value to report to @ys.

```bash
$ --value=70
```

##### `--value-name`

The respective name for the value.

**Default:** `value_name`

##### `--value-threshold`

The threshold range this value must be in to be considered healthy.

Trigger when value is below threshold of `20`:
```bash
$ --value-threshold="<20"
```

Please replace `20` with your own value. All other examples below should have their values replaced with the respective value you wish to use.

Trigger when value is above threshold of `90`:
```bash
$ --value-threshold=">90"
```

Trigger when value is equal to `1`:
```bash
$ --value-threshold="=1"
```

Trigger when value is not equal to `1`:
```bash
$ --value-threshold="!=1"
```

Trigger when value falls outside of the range of `20` and `90`:
```bash
$ --value-threshold="20-90"
```

#### Multiple values (optional)

##### `--values`

Report multiple values to @ys as a comma delimited list.

```bash
$ --values=45,50,60
```

##### `--value-names`

The respective value names for each value. These will map to the respective values provided by `--values`.

```bash
$ --value-names=cpu,hdd,ram
```

**Default:** `value_name0` ... `value_nameN`

##### `--value-thresholds`

Define thresholds for multiple values shares the same syntax used for single threshold values (please refer to `--value-threshold`) but with a comma delimited list.

This defines three thresholds for the above three values:
```bash
$ --value-thresholds="<20,>90,20-90"
```

The first value (`45` - `cpu`) will trigger if the value is below `20`.
The second value (`50` - `hdd`) will trigger if the value is above `90`.
The third value (`60` - `ram`) will trigger when the value falls outside of the range of `20` and `90`.

#### Status Message (optional)

You may provide the message, state, or both the message and the state. Default values listed below.

##### `--status-message`

The message as to why the status is changing.

**Default:** An empty string.

##### `--status-state`

The state the node will transition into.

**Default:** `critical`
