# A virtual machine for two axes
# Written to be called from mods.cba.mit.edu
# From e.g. the "fabnet.js" module
# Running the fabnetserver "fabserver.js"
# or from the commandline
# like python fabnet_xyaxes.py '[[[1,2],[0,0]]]'
#
# Users: set the portName, e.g. /dev/ttyUSB0
# Change the kinematics (incl direction) in initKinematics
# If you change which PCBs you use, delete the
# virtual machine persistance file to start over (e.g. thismachine.vmp)
#
# Nadya Peek 2016


#------IMPORTS-------
from pygestalt import nodes
from pygestalt import interfaces
from pygestalt import machines
from pygestalt import functions
from pygestalt.machines import elements
from pygestalt.machines import kinematics
from pygestalt.machines import state
from pygestalt.utilities import notice
from pygestalt.publish import rpc    #remote procedure call dispatcher
import time
import io
import sys
import json


#------VIRTUAL MACHINE------
class virtualMachine(machines.virtualMachine):

    def initInterfaces(self):
        if self.providedInterface: self.fabnet = self.providedInterface        #providedInterface is defined in the virtualMachine class.
        else: self.fabnet = interfaces.gestaltInterface('FABNET', interfaces.serialInterface(baudRate = 115200, interfaceType = 'ftdi', portName = '/dev/ttyUSB0'))

    def initControllers(self):
        self.xAxisNode = nodes.networkedGestaltNode('X Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
        self.kAxisNode = nodes.networkedGestaltNode('K Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
        self.yAxisNode = nodes.networkedGestaltNode('Y Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
        self.zAxisNode = nodes.networkedGestaltNode('Z Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
        ##self.zkNode = nodes.compoundNode(self.xAxisNode, self.kAxisNode)
        self.xyzkNode = nodes.compoundNode(self.xAxisNode, self.kAxisNode ,self.yAxisNode,self.zAxisNode)

    def initCoordinates(self):
        self.position = state.coordinate(['mm','mm','mm', "mm"])

    def initKinematics(self):
        self.xAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(True)])
        self.kAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(True)])
        self.yAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(True)])
        self.zAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(True)])
        self.stageKinematics = kinematics.direct(4)    #direct drive on all axes

    def initFunctions(self):
        self.move = functions.move(virtualMachine = self, virtualNode = self.xyzkNode, axes = [self.xAxis, self.kAxis ,self.yAxis, self.zAxis], kinematics = self.stageKinematics, machinePosition = self.position,planner = 'null')
        self.jog = functions.jog(self.move)    #an incremental wrapper for the move function
        pass

    def initLast(self):
        #self.machineControl.setMotorCurrents(aCurrent = 0.8, bCurrent = 0.8, cCurrent = 0.8)
        #self.xNode.setVelocityRequest(0)    #clear velocity on nodes. Eventually this will be put in the motion planner on initialization to match state.
        pass

    def publish(self):
        #self.publisher.addNodes(self.machineControl)
        pass

    def getPosition(self):
        return {'position':self.position.future()}

    def setPosition(self, position  = [None]):
        self.position.future.set(position)

    def setSpindleSpeed(self, speedFraction):
        #self.machineControl.pwmRequest(speedFraction)
        pass

#------IF RUN DIRECTLY FROM TERMINAL------
if __name__ == '__main__':
    # The persistence file remembers the node you set. It'll generate the first time you run the
    # file. If you are hooking up a new node, delete the previous persistence file.
    stages = virtualMachine(persistenceFile = "fabnet3axes.vmp")

    # You can load a new program onto the nodes if you are so inclined. This is currently set to
    # the path to the 086-005 repository on Nadya's machine.
    #stages.xyzNode.loadProgram('../../../086-005/086-005a.hex')

    # This is a widget for setting the potentiometer to set the motor current limit on the nodes.
    # The A4982 has max 2A of current, running the widget will interactively help you set.
    #stages.xyzNode.setMotorCurrent(0.7)

    # This is for how fast the motors move
    stages.xyzkNode.setVelocityRequest(2)

    # Pull the moves out of the provided string
    moves = []
    try:
        movestr = sys.argv[1] # moves are passed as a string, this may break with very long strings
    except:
        print "No moves file provided"

    #read in the moves from the commandline, e.g. '[[[10],[0]]]'
    segs = json.loads(movestr)
    for seg in segs:
        for move in seg:
            moves.append(move)
    #print "Moves:"
    #print moves

    # Move!
    for move in moves:
        stages.move(move, 0)
        status = stages.xAxisNode.spinStatusRequest()
        # This checks to see if the move is done.
        while status['stepsRemaining'] > 0:
            time.sleep(0.001)
            status = stages.xAxisNode.spinStatusRequest()
