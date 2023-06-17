from network_4x4 import *
from stimulus import *

stall_item_l = list()
class PE():
    def __init__(self, name, op_cycles) -> None:
        self.name = name
        self.processing_cycles = op_cycles
        self.elapsed_cycles = 0

        self.free_cycles    = 0

        self.busy = False

        self.item = None
        self.processed = []

    def push_data(self, item):
        # backpressure logic
        if self.busy is True:
            print(f"{self.name} is busy. {self.processing_cycles - self.elapsed_cycles} cycles")
            return False
        
        print(f"{self.name} recived data: value:{item.data} index:{item.data_index}")
        self.item       = item
        self.busy       = True
        return True

    def tick(self, TCK_CNT = None):
        if self.busy is True:
            self.elapsed_cycles = self.elapsed_cycles + 1
        else:
            self.free_cycles += 1

        if (self.elapsed_cycles == self.processing_cycles):
            self.item.update_finish_time(TCK_CNT)
            self.processed.append(self.item)

            self.item = None
            self.elapsed_cycles = 0

            self.busy = False

    def isfree(self):
        return not self.busy

    def calculate_excess_latency(self, NUM_SW_LAYERS):
        self.excess_latency = 0
        for item in self.processed:
            # print(f"Latency of {item.data} is {item.latency}")
            excess = item.latency - self.processing_cycles - NUM_SW_LAYERS - 1
            if excess > 0:
                self.excess_latency += excess
        if self.excess_latency > 0:
            print(f"[INFO] {self.name}: \n\tStall Latency: {self.excess_latency}")
            print(f"\tNum of pkts out         :{len(self.processed)}")
            print(f"\tStall latency per output:{self.excess_latency/len(self.processed)}")


class DataSwitch():
    def __init__(self, name, left_node, right_node=None, index_level=None) -> None:
        self.left_node  = left_node
        self.right_node = right_node

        self.name = f"Switch{index_level}_{name}" if index_level is not None else f"Feeder{name}"
        self.index_level = index_level #0,1,2,3

        self.item = None
        self.wait_cycles = 0

        self.free_cycles = 0

    def push_data(self, item):
        if self.item is not None:
            print(f"{self.name} queue full")
            return False # swtich already has data, so can't accept new data
        
        self.item       = item
        print(f"{self.name} recvd data:{self.item.data}")
        return True

    def send_data(self):
        print(f"{self.name} trying to send data:{self.item.data}")
        if self.right_node is None:
            send_status = self.left_node.push_data(self.item)
        else:
            if (self.item.data_index[self.index_level] == 0):
                send_status = self.left_node.push_data(self.item)
            elif (self.item.data_index[self.index_level] == 1):
                send_status = self.right_node.push_data(self.item)
        
        if send_status is True:  # data sending succeeded
            self.item  = None
            return
        elif send_status is False:  # data sending failed
            self.wait_cycles += 1
        
    
    def tick(self, TCK_CNT = None):
        if(self.item is None):
            self.free_cycles += 1
            return #nothing to do
        
        self.send_data()

    def isfree(self):
        return self.item is None

def end_of_sim():
    # element present in feeder stall queue
    if len(stall_item_l) != 0:
        return False
    
    # element not present in any node
    pipeline_free = True
    for element in element_list:
        pipeline_free = pipeline_free & element.isfree()
    if (pipeline_free):
        print("all nodes empty; ending sim")
        return True
    return False


def record_wait_times():
    for num, layer in enumerate(layers):
        print()
        print(f"Layer{num} wait times:", end="\n\t")
        for switch in layer:
            print(f"{switch.name}:{switch.wait_cycles}", end="\n\t")
    print()

def record_stats(num_ticks):
    print(f"--------------------- STATS --------------")
    print(f"------------------- GENERAL  -------------")
    num_pkts_parsed = 0
    for PE_ in output_arr:
        num_pkts_parsed += len(PE_.processed)
    print(f"Total Number of packets:{num_pkts_parsed}")
    print(f"Total Number of cycles :{num_ticks}")
    print(f"Cycle time/Packet      :{num_ticks/num_pkts_parsed}")
    print(f"Throughput             :{num_pkts_parsed/num_ticks}")
    print()

    print(f"------------------- STALLING -------------")
    total_excess_latency = 0
    for PE_ in output_arr:
        PE_.calculate_excess_latency(NUM_SW_LAYERS)
        total_excess_latency += PE_.excess_latency
    print(f"Total Excess Latency: {total_excess_latency}")
    print(f"Total Excess Latency per pkt: {total_excess_latency/num_pkts_parsed}")
    record_wait_times()

    print(f"---------------- UTILISATION -----------")
    for PE_ in output_arr:
        print(f"\t{PE_.name}: {(num_ticks-PE_.free_cycles)*100/num_ticks}")
    for num, layer in enumerate(layers):
        print()
        print(f"Layer{num} utilisation:", end="\n\t")
        for switch in layer:
            print(f"{switch.name}:{(num_ticks-switch.free_cycles)*100/num_ticks}", end="\n\t")

def sim():
    end_sim = False
    last_feeder_num = 0
    f = open("stimulus.txt", 'w')
    for clk in range(0, NUM_CLK_CYCLES+1):
        try:
            for stimulus_item in stall_item_l:
                f_num = last_feeder_num
                # f_num = stimulus_item.feeder_num
                f.write('STALL_QUEUE: ' +str(stimulus_item) + '\n')
                data_status = feeder_layer[f_num].push_data(stimulus_item)
                if data_status is False:
                    print(f"Feeder{f_num} still busy...")
                else:
                    stall_item_l.remove(stimulus_item)
                last_feeder_num = (last_feeder_num+1) % NUM_INPUTS

            for stimulus_item in stimulus[clk]:
                f_num = last_feeder_num
                # f_num = stimulus_item.feeder_num
                f.write(str(stimulus_item) + '\n')
                data_status = feeder_layer[f_num].push_data(stimulus_item)
                if data_status is False:
                    print(f"Feeder{f_num} busy. Couldn't send {stimulus_item.data}")
                    stimulus_item.stall_cycles += 1
                    stall_item_l.append(stimulus_item)
                    # exit(1)
                last_feeder_num = (last_feeder_num+1) % NUM_INPUTS
        except KeyError:
            pass
        if (clk == max(list(stimulus.keys()))):
            end_sim = True
        print(f"---------------TICK {clk}--------------")
        for element in element_list:
            element.tick(clk)
        if end_sim and end_of_sim():
            break
    record_stats(clk)
    f.close()
        

if (__name__ == "__main__"):
    sim()