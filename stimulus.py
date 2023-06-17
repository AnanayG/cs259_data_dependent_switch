import random

SEED = random.randint(1, 2**32)
# SEED = 3844299209
print(f"{SEED=}")

NUM_CLK_CYCLES = 10000
MAX_DATA       = 10000

NUM_CLK_CYCLES_DATA = 300
MIN_NUM_PACKETS = 900
MAX_NUM_PACKETS = 1100

random.seed(SEED)
class Data:
    def __init__(self, feeder_num = None, data = None, index = None, time = None) -> None:
        self.feeder_num = feeder_num
        self.data = data
        self.data_index = index

        self.stall_cycles = 0
        # self.wait_cycles  = 0

        self.start_time  = time
        self.finish_time = None
        self.latency     = None
    
    def randomize(self, feeders, levels):
        self.feeder_num = random.randint(0,feeders-1)
        self.data       = random.randint(1, MAX_DATA)
        self.data_index = [random.randint(0, 1) for _ in range(levels)]
        return self
    
    def __str__(self) -> str:
        return f"@{self.start_time} Data[f:{self.feeder_num}, data:{self.data}, index:{self.data_index}]" + " "

    def update_finish_time(self, time):
        self.finish_time = time
        self.latency = self.finish_time - self.start_time + 1

#4x4
# stimulus = {
#     0: [Data(1,  5, [0,1], 0)],
#     2: [Data(2,200, [1,1], 2)],
#     3: [Data(3,700, [1,1], 3)]
# }

# stimulus = {
#     0: [Data(time=0).randomize(4,2), Data(time=0).randomize(4,2)],
#     2: [Data(time=2).randomize(4,2)],
#     3: [Data(time=3).randomize(4,2)]
# }

def generate_random_stimulus(stimulus):
    num_packets = random.randint(MIN_NUM_PACKETS, MAX_NUM_PACKETS)
    stimulus_clk_ticks = [random.randint(1,NUM_CLK_CYCLES_DATA) for _ in range(num_packets)]
    for clk_num in range(NUM_CLK_CYCLES_DATA):
        if (stimulus_clk_ticks.count(clk_num) > 4):
            while(stimulus_clk_ticks.count(clk_num) > 4):
                stimulus_clk_ticks.remove(clk_num)

    for clk_tick in stimulus_clk_ticks:
        pkt = Data(time=clk_tick).randomize(4, 2)
        try:
            while(True):
                match_found = False
                for old_pkt in stimulus[clk_tick]:
                    if(old_pkt.feeder_num == pkt.feeder_num):
                        match_found = True
                        break
                if(match_found is False):
                    break
                pkt = Data(time=clk_tick).randomize(4, 2)
            stimulus[clk_tick].append(pkt)
        except KeyError:
            stimulus[clk_tick] = [pkt]

stimulus = dict()
generate_random_stimulus(stimulus)

#2x2
# stimulus = {
#     0: [[1,  5,[1]]],
#     2: [[1,200,[0]]]
# }