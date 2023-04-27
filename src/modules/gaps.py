import math


def calculate_gap(value_1:float,value_2:float,sensitivity:float=80.0,inverse=False)->float:
    """
    Input:
        value_1: value of the First Player
        value_2: value of the Second Player
        sensitivity: the higher the less sensitive the gap calculation is to the difference in values
      
    Returns:
        A Float between 0 and 1 representing the gap between the two Players.
        The closer the number is to 0 the more skilled is the First Player compared to the Second Player.
        The closer the number is to 1 the more skilled is the Second Player compared to the First Player.
        If the number is close to 0.5 the Players are equal.
    """
    def sigmoid(x:float):
        return 1.0/(1.0+math.exp(-x/sensitivity))
    
    return sigmoid(float(value_1-value_2) if not inverse else float(value_2-value_1))


def skill_gap(value_1:float,value_2:float)->float:
    return calculate_gap(value_1,value_2,60.0)

def age_gap(value_1:float,value_2:float)->float:
    return calculate_gap(value_1,value_2,8.0)

def height_gap(value_1:float,value_2:float)->float:
    return calculate_gap(value_1,value_2,30.0,True)

def knowledge_gap(value_1:float,value_2:float)->float:
    return calculate_gap(value_1,value_2,90.0,True)

def historical_gap(value_1:float,value_2:float)->float:
    return calculate_gap(value_1,value_2,3.0,True)


def seed_gap(value_1:float,value_2:float)->float:
    return calculate_gap(value_1,value_2,10.0)
