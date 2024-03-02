module.exports = function(RED) {
    function AYSAgentNode(config) {
        RED.nodes.createNode(this,config);
        var node = this;
        node.on('input', function(msg) {
            // TODO: Add logic here
            // msg.payload = msg.payload.toLowerCase();
            node.send(msg);
        });
    }
    RED.nodes.registerType("ays-agent", AYSAgentNode);
}
