from main import DataSwitch, PE

PE_PROCESSING_TIME = 10
NUM_SW_LAYERS      = 1

output_arr = [PE('PE_A', PE_PROCESSING_TIME),
              PE('PE_B', PE_PROCESSING_TIME)]

layer1 = [DataSwitch('0', output_arr[0], output_arr[1], 0),
          DataSwitch('1', output_arr[1], output_arr[0], 0)]

layers = [layer1]
bottom_layer = layer1

feeder_layer = [DataSwitch('0', bottom_layer[0], None),
                DataSwitch('1', bottom_layer[1], None)]

element_list = output_arr + layer1 + feeder_layer
