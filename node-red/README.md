# Node-RED `ays-agent`

This provides an interface to the At Your Service agent from within Node-RED. This is accomplished by adding an `ays-agent` subflow and adding two global environment variables.

## Installation

Please note: The agent has only been tested on Node-RED v3.1.6.

### Install the Subflow

There are two ways to install the `ays-agent` subflow.

**1. Import subflow.json file**

- Clone the `ays-agent` repository
- Open Node-RED
- Tap the menu button on the top right > `Import` > `select a file to import`
- Select the `/path/to/ays-agent/node-red/subflow.json` file and import

**2. Import JSON structure**

You may also copy the [subflow JSON structure](https://github.com/PeqNP/ays-agent/blob/main/node-red/subflow.json) directly.

- Copy the raw contents, of the [subflow JSON structure](https://github.com/PeqNP/ays-agent/blob/main/node-red/subflow.json)
- Open Node-RED
- Tap the menu button on the top right > `Import`
- Paste the contents into the `Clipboard`'s text area box
- Tap `Import`

### Add Environment Variables

Tap the menu button on the top right > `Settings` > `Environment`. Add these environment variables:

- `AYS_SERVER` with the value `http://localhost:9443/agent/`. If necessary, please change this to the location of your local instance.
- `AYS_ORG_SECRET` with the value of your respective Organization's secret.
  - To find your org secret, navigate to the top-most org node in your System Graph
  - Tap the `Edit` mode
  - Tap your organization node in the System Graph
  - Once the form appears, tap the `Organization configuration`
  - Tap the "Copy" icon in the `Secret` row
  - Paste this value into your `AYS_ORG_SECRET` environment variable value inside Node-RED

## Usage

Drag the `ays-agent` subflow into your flow. It should be located in the `network` category.

Connect any of your HW/SW systems to the `ays-agent` input. The input must be a numeric value.

**Required Parameters:**

- `Server` Unless you need a different server, leave this as `AYS_SERVER`, or update the environment variable.
- `Org Secret`. If you are sending messages to multiple orgs (uncommon),  leave this as `AYS_ORG_SECRET`, or update the environment variable.
- `Parent Node` This is the parent node your child will live under.
- `Child Node` The name of the child node. Please use the character range `[a-z0-9]`, or the hyphen (`-`) character, where the first character in the name is a letter. e.g. `my-node-01`

**Optional Parameters:**

- `Monitor Name` The name of the monitor. If none is provided, `node-red` is used.
- `Threshold` Trigger a threshold if a value falls outside of specified range. Refer to the [ays-agent API docs](../docs/api.md) for a list of supported threshold formats.
- `Heartbeat` The default is set for 5 minutes. If you don't want to monitor the node, set the heartbeat value to `0`.
- `Template` Adopt a template located at the specified node path.

## Debugging

The `ays-agent` subflow emits `node.error`s messages (which can be seen in the Debug panel) _and_ provides node status messages hints that display under the `ays-agent` subflow instance. If an node status is displayed, please open the Debug menu for more information.

The most common problems are:

- A required parameter is not provided
- Connection to the AYS server failed

## Help

Do you need help configuring the agent? Do you have a feature suggestion? If so, please call me at 253-329-1280.
