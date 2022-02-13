import copy
import numpy
from timer import timer
import time

numberNodesGenerated = 0
numberNodesExpanded = 0


class Node:
    def __init__(self, data, parent, gval, hval, fval) -> None:
        self.data = data
        self.parent = parent
        self.gval = gval
        self.hval = hval
        self.fval = fval

    '''Function to generate successors of a current position'''

    def generateSuccessors(self):
        i, j = self.findBlankSpace('0')
        children = []
        '''Generate successors based on the position of the blank tile'''
        if(i+1 < len(self.data)):
            children.append(self.generateChildNode(self.data, i, j, i+1, j))
        if(j+1 < len(self.data)):
            children.append(self.generateChildNode(self.data, i, j, i, j+1))
        if(i-1 >= 0):
            children.append(self.generateChildNode(self.data, i, j, i-1, j))
        if(j-1 >= 0):
            children.append(self.generateChildNode(self.data, i, j, i, j-1))
        return children

    '''Find the position of blank tile'''

    def findBlankSpace(self, space):
        data = self.data
        for i in range(0, len(self.data)):
            for j in range(0, len(self.data)):
                if(data[i][j] == space):
                    return i, j

    def generateChildNode(self, data, old_x, old_y, new_x, new_y):
        copy_data = copy.deepcopy(data)
        temp = copy_data[old_x][old_y]
        copy_data[old_x][old_y] = data[new_x][new_y]
        copy_data[new_x][new_y] = temp
        child = Node(copy_data, None, self.gval+1, 0, 0)
        return child


class Puzzle:
    def __init__(self, size) -> None:
        #Adding Default Goal State
        self.goal_state="1,2,3,4,5,6,7,8,0"
        self.current_input=None
        #Adding File System Input Flag
        self.isfile=False
        #Adding Time Limit Threshold
        self.limit = 100
        self.size = size
        self.frontier = []
        self.expanded = []

    def getInput(self):
        Matrix = []
        count = 0
        temp = []

        tempList=None
        if self.isfile ==True:
            tempList = self.current_input.split(",")
        else:
            tempList = input().split(",")
        
        for i in range(0, 9):
            temp.append(tempList[i])
            count += 1
            if count == 3:
                Matrix.append(temp)
                temp = []
                count = 0
        return Matrix
        
    def getMatrix(self,initailval):
        Matrix = []
        count = 0
        temp = []
        tempList = initailval.split(",")
        for i in range(0, 9):
            temp.append(tempList[i])
            count += 1
            if count == 3:
                Matrix.append(temp)
                temp = []
                count = 0
        return Matrix

    def printArr(self, data):
        for i in range(0, len(data)):
                print(data[i])

    def getIndex(self, current):
        for index, node in enumerate(self.frontier):
            if(numpy.array_equal(current.data, node.data)):
                return index
        return None

    '''Function to check if the problem is solvable based on initial and current states'''
    def checkSolvability(self,initial,goal):
        initialArray = numpy.array(initial).flatten()
        goalArray = numpy.array(goal).flatten()
        initialStateParity = self.checkParity(initialArray)
        goalStateParity = self.checkParity(goalArray)
        if initialStateParity == goalStateParity:
            return True
        else:
            return False
        
    def checkParity(self,state):
        noOfInversions = 0
        state = state[state != "0"]
        for i in range(9):
            for j in range(i+1,8):
                if state[i] > state[j]:
                    noOfInversions = noOfInversions + 1
        if noOfInversions % 2 == 0:
            return "even"
        else:
            return "odd"

    def solve(self,initialval):
        '''Get initial and goal state as well as heuristic function choice from the user'''
        heuristicVal = ""
        
        if initialval == "":
            print("Enter the initial state:")
            initial = self.getInput()
            print("Enter the goal state:")
            goal = self.getInput()
            '''Check if the problem is solvable'''
            isSolvable = self.checkSolvability(initial,goal)
            if not isSolvable:
                return None
            heuristicFunction = HeuristicMisplacedTiles(initial,goal)
        else:
            self.current_input = initialval
            initial = self.getInput()

            self.current_input = self.goal_state
            goal = self.getInput()

            
            isSolvable = self.checkSolvability(initial,goal)
            if not isSolvable:
                return None
            heuristicFunction = HeuristicMisplacedTiles(initial,goal)
            
        # else:
        #     initial = self.getMatrix(initialval)
        #     goal = self.getMatrix("0,1,2,3,4,5,6,7,8")
        #     '''Check if the problem is solvable'''
        #     isSolvable = self.checkSolvability(initial,goal)
        #     if not isSolvable:
        #         return None
        #     heuristicFunction = HeuristicMisplacedTiles(initial,goal)
            
      
        '''Initialize the problem'''
        initial = Node(initial, None, 0 , 0, 0)
        initial.hval = heuristicFunction.calculateHval(initial.data)
        initial.fval = initial.hval + initial.gval
        '''Insert the initial node in the frontier list'''
        self.frontier.append(initial)
        numberNodesGenerated = 1
        with timer() as t:
            while(len(self.frontier) > 0):
                if int(t.elapse)>=self.limit:
                    raise Exception ("Time Limit Exceeded")

                '''Take out the node from the frontier with the minimum fval'''
                current = self.frontier.pop(0)
                self.expanded.append(current.data)
                '''Check if the goal state is reached'''
                if(numpy.array_equal(current.data,goal)):
                    print("Reached Goal")
                    numberNodesExpanded = len(self.expanded)
                    print("No of nodes Expanded: ", numberNodesExpanded)
                    print("Path Cost:", current.gval)
                    return current
                '''Generate successors of the current node'''
                for child in current.generateSuccessors():
                    '''Check if the successor node is already explored'''
                    if(not(any(numpy.array_equal(child.data, x) for x in self.expanded))):
                        child.hval = heuristicFunction.calculateHval(child.data)
                        child.fval = child.hval + child.gval
                        child.parent = current
                        index = self.getIndex(child)
                        '''Check if the frontier has the same node with greater fval, if yes then replace the node in frontier'''
                        if(index != None):
                            if(current.fval < self.frontier[index].fval):
                                self.frontier[index] = child
                        else:
                            '''Add the successor in the frontier list'''
                            self.frontier.append(child)  
                '''Sort the frontier list according to fval'''
                self.frontier.sort(key = lambda data:data.fval, reverse= False)
        return None


class HeuristicMisplacedTiles:
    def __init__(self, initial, goal) -> None:
        self.initial = initial
        self.goal = goal

    '''Heuristic function to calculate misplaced tiles'''
    def calculateHval(self, current):
        misplacedTilesCount = 0
        for i in range(3):
            for j in range(3):
                if current[i][j] != self.goal[i][j] and (current[i][j] != "0"):
                    misplacedTilesCount +=1
        return misplacedTilesCount


solution = ""
print("Enter your choice:")
print("1. Pre defined initial states")
print("2. Custom initial state")
choice = input()
if(choice == "1"):
    lines=[]
    with open('data.txt') as f:
        lines = f.readlines()
        
    for line in lines:
        try:
            print(line)
            print("")
            puzzle = Puzzle(3)
            puzzle.isfile=True

            
            solution = puzzle.solve(line.rstrip('\n'))
            if solution == None:
                print("The problem is not solvable")
            else:
                print("Final Path from Initial State to Goal State:\n")
                solutionPath = []
                while(solution != None):
                    solutionPath.append(solution.data)
                    solution = solution.parent
                solutionPath.reverse()
                while(len(solutionPath) > 1):
                    path = solutionPath.pop(0)
                    puzzle.printArr(path)
                    print(" ")
                    print("       ||      ")
                    print("       ||      ")
                    print("       \/      ")
                    print(" ")  
                path = solutionPath.pop(0)     
                puzzle.printArr(path)
                print(" ")
        except Exception as e:
            if str(e) == "Time Limit Exceeded":
                print("Time Limit Exceeded\n")
            else:
                raise
        

elif(choice == "2"):
    puzzle = Puzzle(3)
    solution = puzzle.solve("")
    if solution == None:
        print("The problem is not solvable")
    else:
        print("Final Path from Initial State to Goal State:\n")
        solutionPath = []
        while(solution != None):
            solutionPath.append(solution.data)
            solution = solution.parent
        solutionPath.reverse()
        while(len(solutionPath) > 1):
            path = solutionPath.pop(0)
            puzzle.printArr(path)
            print(" ")
            print("       ||      ")
            print("       ||      ")
            print("       \/      ")
            print(" ")  
        path = solutionPath.pop(0)     
        puzzle.printArr(path)
        print(" ")
else:
    print("Wrong choice")