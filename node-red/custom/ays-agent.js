module.exports = function(RED) {
    function AYSAgentNode(config) {
        RED.nodes.createNode(this, config);
        var node = this;
        node.on('input', function(msg) {
            // TODO: Add logic here
            // msg.payload = msg.payload.toLowerCase();
            node.send(msg);
            //this.status({fill: "red", shape: "ring",text:"disconnected"});
            // RED.settings.aysParentNode
        });
    }
    RED.nodes.registerType("ays-agent", AYSAgentNode, {
        settings: {
            aysParentNode: {
                value: "",
                exportable: true
            },
            // Child node should be derived from name(?)
            aysChildNode: {
                value: "",
                exportable: true
            },
            aysMonitorName: {
                value: "node-red",
                exportable: true
            }
        }
    });
}
