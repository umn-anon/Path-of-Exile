# program to calculate best archmemesis combination with innocence
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numpy import random

class Archnem:
    # calc if we get an exalt from a given archnemesis / treant mob
    def __init__(self, rerolls, rewards, exRate = 0.01, multi = 1, treant = False):
        # multi is only for kitava
        # treant doesn't scale with additional rewards, need to flag it
        self.exRate = exRate
        self.rerolls = rerolls
        self.rewards = rewards*multi
        self.multi = multi
        self.treant = treant

        self.dropRate = 1 - (1-self.exRate)**(rerolls+1)
        self.avgEx()
        
        pass
    def __call__(self):
        sign = False
        for i in range(self.rerolls+1):
            sign = random.choice([True, False], p=[self.exRate, 1-self.exRate])
            if sign:
                return True
            pass
        
        return False
        pass
    def avgEx(self):
        iters = 50000
        #EX = [0]*iters
        EX = 0
        for i in range(iters):
            for j in range(int(self.rewards)):
                if random.choice([True, False],
                                 p=[self.dropRate, 1-self.dropRate]):
                    #EX[i] += 1
                    EX += 1
                    pass
                pass
            pass
        #self.avgEx = sum(EX)/iters
        self.avgEx = EX/iters
        self.std = np.std(EX)
        pass
    pass # end class Archnem

class Map:
    def __init__(self, ANs, exRate = 0.001):
        self.ANs = [Archnem(0,3)] # always start with innocence
        self.exRate = exRate
        for i in range(3):
            self.ANs += [self.AN_parser(ANs[i])]
            pass
        self.mapValue()
        pass
    def AN_parser(self,AN):
        if AN == "Kitava":
            return Archnem(0,1, multi = 2)
        if AN == "Tukohama" or AN == "Abberath":
            return Archnem(4,3)
        if AN == "Treant":
            return Archnem(0,10, treant = True)
        if AN == "Brine King":
            return Archnem(6,3)
        elif isinstance(AN,list):
            return Archnem(AN[0], AN[1])
        print("no archnemesis match")
        return Archnem(0,1) # default val

    def mapValue(self, numTreants = 10):
        EX = 0
        self.tiers = [self.ANs[0],0,0,0 ]
        self.treants = []
        rate = self.exRate
        self.numTreants = numTreants
        # create archnemesis for each tier to collect rolling reward total
        mult = 1
        for i in range(1,4):
            if self.ANs[i].multi == 2:
                mult = 2 # once we add kitava, all future tiers will have 2x multi
            if self.ANs[i].treant == False:
                self.tiers[i] = Archnem(
                    self.tiers[i-1].rerolls + self.ANs[i].rerolls,
                    self.tiers[i-1].rewards/self.tiers[i-1].multi
                        + self.ANs[i].rewards,
                    multi = mult,
                    exRate = rate
                    )
                if len(self.treants) > 0:
                    # if treant has been used, add them again for each tier
                    self.treants += [
                    Archnem(
                    self.tiers[i].rerolls,# treant mobs retain rerolls?
                    self.numTreants, # one reward per treant
                    exRate = rate)
                    ]
                pass
            
            else: # add treant mob to list plus its inherent 1 reward
                self.tiers[i] = Archnem(
                    self.tiers[i-1].rerolls,
                    self.tiers[i-1].rewards/self.tiers[i-1].multi + 1,
                    # we have to undo the multi so we can sum new tiers correctly
                    multi = mult,
                    exRate = rate
                    )
                self.treants += [
                    Archnem(
                    self.tiers[i].rerolls,# treant mobs retain rerolls?
                    self.numTreants, # one reward per treant
                    exRate = rate)
                    ]
                # treants cannot have more than one reward so we don't use multi
                pass
            pass # end for-loop

        # sum all tiers and treants
        for i in range(len(self.tiers)):
            EX += self.tiers[i].avgEx
        for i in range(len(self.treants)):
            EX += self.treants[i].avgEx

        self.avgEx = EX
        pass # end def mapValue
    


    pass  # end Map class

def run(ANs = ["Brine King","Treant", "Abberath"], exRate = 0.0001):
    m = Map(ANs, exRate)
    print("Each Archnemesis' standard deviation: ")
    x = [m.tiers[0].std, m.tiers[1].std,m.tiers[2].std,m.tiers[3].std]
    print(np.round(x,2))
    if len(m.treants) > 0:
        print("Treant hordes' standard deviation: ")
        x = []
        for i in range(len(m.treants)):
            x += [m.treants[i].std]
        print(np.round(x,2))
    print("Avg Exalts: ", round(m.avgEx, 3))
    pass


def compare():
    global exs
    exs = [0.0001,0.001,0.01]
    global an
    an = []
    an += [["Brine King","Treant", "Abberath"]]
    an += [["Brine King","Treant", "Kitava"]]
    an += [["Brine King","Kitava", "Abberath"]]
    an += [["Brine King","Kitava", "Treant"]]
    an += [["Brine King","Abberath", "Treant"]]
    an += [["Brine King","Abberath", "Kitava"]]
    an += [["Treant","Brine King", "Abberath"]]
    an += [["Treant", "Brine King","Kitava"]]

    global avgEx
    avgEx = np.zeros([len(exs),len(an)])

    for i in range(len(exs)):
        for j in range(len(an)):
            m = Map(an[j], exRate = exs[i])
            avgEx[i][j] = m.avgEx
    pass


def plot():
    for i in range(len(avgEx[1,:])):
        plt.scatter(np.log10(exs), (avgEx[:,i]/[max(avgEx[0,:]),
                                                max(avgEx[1,:]),
					     max(avgEx[2,:])])**2,
                    label = an[i][0] + " - " + an[i][1] + " - " +an[i][2])
        for x,y in zip(np.log10(exs), (avgEx[:,i]/[max(avgEx[0,:]),
                                                   max(avgEx[1,:]),
					     max(avgEx[2,:])])**2):
            plt.annotate(an[i][0] + " - " + an[i][1] + " - " +an[i][2],
                     (x,y),
                     textcoords="offset points",
                     xytext=(50,5),
                     ha='center')

    plt.xlabel("log10 of Exalted orb drop rate")
    plt.ylabel("Average exalts dropped normalized from Max value")
    #plt.legend(loc='lower left')
    plt.show()















