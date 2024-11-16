import mesa
from mesa.space import MultiGrid
import numpy as np
import seaborn as sns
import agents

# Function to set cells in a specified layer
def set_layer(self, coordinate_dict, layer_name):
    for item in coordinate_dict:
        direction, start, end = item
        if direction == "Y":
            x = start[0]
            for y in range(start[1], end[1] + 1):
                self.grid.properties[layer_name].set_cell((x, y), 1)
        elif direction == "X":
            y = start[1]
            for x in range(start[0], end[0] + 1):
                self.grid.properties[layer_name].set_cell((x, y), 1)

class CityModel(mesa.Model):
    def __init__(self, n, width, height, dataStructure, seed=None):
        super().__init__(seed=seed)
        self.n = n
        self.width = width
        self.height = height
        self.buildingLayer = mesa.space.PropertyLayer("buildingLayer", self.width, self.height, default_value=np.float64(0))
        self.trafficLightLayer = mesa.space.PropertyLayer("trafficLightLayer", self.width, self.height, default_value=np.float64(0))
        self.parkingLayer = mesa.space.PropertyLayer("parkingLayer", self.width, self.height, default_value=np.float64(0))

        # Movement layers
        self.RightLayer = mesa.space.PropertyLayer("RightLayer", self.width, self.height, default_value=np.float64(0))
        self.LeftLayer = mesa.space.PropertyLayer("LeftLayer", self.width, self.height, default_value=np.float64(0))
        self.UpLayer = mesa.space.PropertyLayer("UpLayer", self.width, self.height, default_value=np.float64(0))
        self.DownLayer = mesa.space.PropertyLayer("DownLayer", self.width, self.height, default_value=np.float64(0))

        self.grid = mesa.space.MultiGrid(width, height, True, (self.buildingLayer,
                                                               self.trafficLightLayer,
                                                               self.parkingLayer,
                                                               self.RightLayer,
                                                               self.LeftLayer,
                                                               self.UpLayer,
                                                               self.DownLayer))

        def set_Data_Structures(coordinateStructurePositions):
            set_buildingsLayer(coordinateStructurePositions["Buildings"])
            set_traffic_lightsLayer(coordinateStructurePositions["Semaphores"])
            set_parking_lotsLayer(coordinateStructurePositions["Parking_Lots"])

            # Movement layers
            set_left_Layer(coordinateStructurePositions["Left"])
            set_right_Layer(coordinateStructurePositions["Right"])
            set_up_Layer(coordinateStructurePositions["Up"])
            set_down_Layer(coordinateStructurePositions["Down"])
            return

        def set_buildingsLayer(buildingsArray):
            for x, y in buildingsArray:
                self.grid.properties["buildingLayer"].set_cell((x, y), 1)

        def set_traffic_lightsLayer(coordinateStructurePositions):
            for coordinate_pair in coordinateStructurePositions:
                for (x, y), isOn in coordinate_pair:
                    if isOn:
                        self.grid.properties["trafficLightLayer"].set_cell((x, y), 1)
                    else:
                        self.grid.properties["trafficLightLayer"].set_cell((x, y), 2)

        def set_parking_lotsLayer(coordinateStructurePositions):
            for (x, y), isOccupied in coordinateStructurePositions:
                if isOccupied:
                    self.grid.properties["parkingLayer"].set_cell((x, y), 2)  # 2 occupied
                else:
                    self.grid.properties["parkingLayer"].set_cell((x, y), 1)

        # Movement layers
        def set_right_Layer(coordinateStructurePositions):
            set_layer(self, coordinateStructurePositions, "RightLayer")

        def set_left_Layer(coordinateStructurePositions):
            set_layer(self, coordinateStructurePositions, "LeftLayer")

        def set_up_Layer(coordinateStructurePositions):
            set_layer(self, coordinateStructurePositions, "UpLayer")

        def set_down_Layer(coordinateStructurePositions):
            set_layer(self, coordinateStructurePositions, "DownLayer")

        set_Data_Structures(dataStructure)

        # Create Traffic Light Agents
        for idSemaphore in dataStructure["Semaphores"]:
            coords = []
            status = False
            for (x, y), value in idSemaphore:
                coords.append((x, y))
                status = value
            agents.TrafficLightAgent(self, idSemaphore, coords, status)

        '''
        Create car Agent:
        '''

        def createCarInParking(availableParkinLot, availablePositions):
            '''
            I know this can be simplified, but adding a condition that will always make the agent appear at least
            one time in the parking position
            '''
            startingPosition = self.random.choice(list(availableParkinLot))
            availableParkinLot.discard(startingPosition)
            availablePositions.discard(startingPosition)

            endingPosition = self.random.choice(list(availableParkinLot))
            availablePositions.discard(endingPosition)
            availableParkinLot.discard(endingPosition)

            self.grid.properties["parkingLayer"].set_cell(startingPosition, 2)

            return startingPosition, endingPosition, True

        availablePositions = set()
        availableParkinLot = set()
        for x in range(self.width):
            for y in range(self.height):
                if self.grid.properties["buildingLayer"].data[x,y] == 0:
                    availablePositions.add((x, y))
                    if self.grid.properties["parkingLayer"].data[x,y] == 1:
                        availableParkinLot.add((x, y))


        carIsOnParking = False
        for iDCar in range(self.n):
            startingPosition = None
            endingPosition = None
            isParked = False
            if not carIsOnParking:
                startingPosition,endingPosition,isParked = createCarInParking(availableParkinLot, availablePositions)
                carIsOnParking = True
            else:
                if self.random.randint(0,2) != 0:
                    #Case Where they don't spawn in a parking lot
                    startingPosition = self.random.choice(list(availablePositions))
                    availableParkinLot.discard(startingPosition)
                    availableParkinLot.discard(startingPosition)
                    endingPosition = self.random.choice(list(availablePositions))
                    availableParkinLot.discard(endingPosition)
                    availablePositions.discard(endingPosition)
                else:
                    startingPosition, endingPosition, isParked = createCarInParking(availableParkinLot,
                                                                                    availablePositions)

            carAgent = agents.CarAgent(self, isParked, startingPosition, endingPosition)  # model, isParked, startingPosition, endingPosition
            print(f"Starting Position: {startingPosition} and ending position {endingPosition}")
            self.grid.place_agent(carAgent, (startingPosition[0],startingPosition[1]))

    def step(self):
        for agent in self.agents_by_type[agents.TrafficLightAgent]:
            agent.step()
        self.agents_by_type[agents.CarAgent].shuffle_do("step")
