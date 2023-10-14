import networkx as nx

class WHCAstarMover:
    """
        Class responsible for handling the movement validation and execution of agents
    """
    def __init__(self, mapCanvas, mapGraph, sharedInfoManager):
        self.mapCanvas = mapCanvas
        self.mapGraph = mapGraph
        self.sharedInfoManager = sharedInfoManager

    def validateAgentMove(self, agent, targetNode, collisionBehavior):
        sourceNode = agent.currentNode
        # It can happen that an agent becomes trapped:
        # - Agent is in a dead-end
        # - A second agent is attempting to advance onto the same tile
        # In this case, reject the second agent's motion and force it to replan
        if not self.mapGraph.has_node(targetNode):
            print("Node not in the graph. Malformed ID?")
            return False
        if not self.mapGraph.has_edge(sourceNode, targetNode) and not targetNode == sourceNode:
            print("Edge not in the graph. Wrong neighbor node?")
            return False
        # if self.sharedInfoManager.evaluateNodeEligibility(0, targetNode, sourceNode):
        #     print("Node or edge reserved")
        # if 'agent' in self.mapGraph.nodes(data=True)[targetNode] and collisionBehavior == "Respected":
            # print("Agent collision detected. Replan.")
        #     return False
        return True