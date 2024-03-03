module.exports = function(RED) {
    function AYSAgentServerNode(n) {
        RED.nodes.createNode(this, n);
        this.endpoint = n.endpoint;
        this.orgSecret = n.orgSecret;
    }
    RED.nodes.registerType("ays-agent-server", AYSAgentServerNode);
}
