from main import DataSwitch, PE

PE_PROCESSING_TIME = 5
NUM_SW_LAYERS      = 2
output_arr = [PE('PE_A', PE_PROCESSING_TIME),
              PE('PE_B', PE_PROCESSING_TIME),
              PE('PE_C', PE_PROCESSING_TIME),
              PE('PE_D', PE_PROCESSING_TIME)]

layer1 = [DataSwitch('0', output_arr[0], output_arr[1], index_level=0),
          DataSwitch('1', output_arr[0], output_arr[1], index_level=0),
          DataSwitch('2', output_arr[2], output_arr[3], index_level=0),
          DataSwitch('3', output_arr[2], output_arr[3], index_level=0)]

layer2 = [DataSwitch('0', layer1[0], layer1[2], index_level=1),
          DataSwitch('1', layer1[1], layer1[3], index_level=1),
          DataSwitch('2', layer1[0], layer1[2], index_level=1),
          DataSwitch('3', layer1[1], layer1[3], index_level=1)]

layers = [layer1, layer2]
bottom_layer = layer2

feeder_layer = [DataSwitch('0', bottom_layer[0], index_level=None),
                DataSwitch('1', bottom_layer[1], index_level=None),
                DataSwitch('2', bottom_layer[2], index_level=None),
                DataSwitch('3', bottom_layer[3], index_level=None)]
NUM_INPUTS         = len(feeder_layer)

element_list = output_arr + layer1 + layer2 + feeder_layer