# Node-RED ays-agent

This provides an interface to the At Your Service agent from within Node-RED. This is accomplished by adding an `ays-agent` and `ays-agent-server` node to your flow.

## `ays-agent`

The inputs have been simplified for easy configuration.

Required parameters:
- Parent node path. This is the parent node your child will live under.
- Child node name. Please use the character range [a-z0-9], or the hyphen, where the first character in the name is a letter. e.g. `my-node-01`

Optional configuration:
- Heartbeat. The default is set for 5 minutes. If you don't want to monitor the node, set the heartbeat value to `0`.
- Org secret. In most contexts, this value is derived from the `ays-agent-server`. Change only if you know what you're doing.

Other notes:
- The `ays-agent` node is configured to use the same AYS Agent Server (Endpoint) for all `ays-agent` node instances. Please update the `ays-agent-server` node, if you wish to point to your local instance of AYS.
- The monitor name is always `node-red`.

## `ays-agent-sensor`

The `ays-agent-server` allows you to configure the default server endpoint (`https://api.bithead.io:9443/agent`) and the org secret. It is assumed that all nodes will be placed within the same organization. If this is _not_ true, please set the org secret on the respective nodes.

## Outro

If you need help configuring your node, provide feature suggestions, etc. please call 253-329-1280.
