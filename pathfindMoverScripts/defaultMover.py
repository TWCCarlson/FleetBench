import networkx as nx

class defaultAgentMover:
    """
        The fallback method for handling agent collisions
    """
    def __init__(self, mapGraph):
        self.mapGraph = mapGraph

    def validateAgentMove(self, agent, targetNode, collisionBehavior):
        sourceNode = agent.currentNode
        # Verify that the targetNode exists in the graph
        if not self.mapGraph.has_node(targetNode):
            return False
        # Verify that an edge between source and target exists
        if not self.mapGraph.has_edge(sourceNode, targetNode):
            return False
        # Verify that the target node does not contain an agent
        if 'agent' in self.mapGraph.nodes(data=True)[targetNode] and collisionBehavior == "Respected":
            return False
        return True
