module.exports = function(RED) {
    function AYSAgentServerNode(n) {
        RED.nodes.createNode(this,n);
        this.endpoint = n.endpoint;
    }
    RED.nodes.registerType("ays-agent-server", AYSAgentServerNode);
}
