# Node-RED ays-agent

This provides an interface to the At Your Service agent from within Node-RED. This is accomplished by adding an `ays-agent` subflow and adding two global environment variables.

## Installation

### Add Environment Variables

Tap the menu button on the top right of the menu > `Settings` > `Environment`. Add these environment variables:

- `AYS_SERVER` with the value `http://localhost:9443/agent/`. If necessary, please change this to your location of your local instance
- `AYS_ORG_SECRET` with the value of your respective Organization's secret.
  - To find your secret, navigate to the top-most org node in your System Graph
  - Tap the `Edit` mode
  - Tap the top-mode Node
  - Tap the `Organization configuration`
  - Tap the "Copy" icon in the `Secret` row
  - Paste this value into your `AYS_ORG_SECRET` environment variable value

### Install the Subflow from NPM



## Usage

Drag the `ays-agent` subflow node. It should be located in the `network` category.

Connect any of your HW/SW systems to the `ays-agent` input. The input must be a numeric value.

Required parameters:
- Server . Unless you need a different server, leave this as `AYS_SERVER` or update the environment variable.
- Org Secret. If you are sending messages to multiple orgs (uncomment),  leave this as `AYS_ORG_SECRET` or update the environment variable.
- Parent node path. This is the parent node your child will live under.
- Child node name. Please use the character range [a-z0-9], or the hyphen, where the first character in the name is a letter. e.g. `my-node-01`

Optional configuration:
- Monitor name. The name of the monitor. If none is provided, `node-red` is used.
- Heartbeat. The default is set for 5 minutes. If you don't want to monitor the node, set the heartbeat value to `0`.
- Template. Adopt a template located at the specified node path.

## Outro

Do you need help? Do you have a feature suggestion? Please call me at 253-329-1280.
