
import socket
import struct
import os
import time
from multiprocessing import Process, Manager, Value, Queue, Array
from socket import timeout as socket_timeout


def unpack_header(message):

    # message_size includes the 30-bytes header.
    timestamp = message[:20]
    timestamp = float(timestamp)

    sequence_number = message[20:30]
    sequence_number = int(sequence_number)

    return timestamp, sequence_number


def start_uplink_receiver(client_port, assigned_slice_queue):
    uplink_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    uplink_receiver_socket.bind((server_ip, client_port))
    uplink_receiver_socket.settimeout(5)  # Currently not needed.

    counter = 0
    total_received = 0
    current_time = time.time()

    # my_slice_queue = assigned_slice_queue

    while True:
        try:
            data, addr = uplink_receiver_socket.recvfrom(MTU)
            receive_time = time.time()

            if len(data) == 0:
                print("closing message received - injection process closed from the client side")
                break

            timestamp, sequence_number = unpack_header(data)
            packet_size = len(data)  # Note that the actual data is discarded here.
            # packet_report = [addr, receive_time, timestamp, sequence_number, packet_size]
            # my_slice_queue.put(packet_report)
            counter += 1
            total_received = total_received + packet_size

            if (receive_time - current_time) > 1:
                current_traffic = total_received * 8 / 1000000
                current_traffic = '{0:.3f}'.format(current_traffic)
                print(current_traffic, "Mbits received within", '{0:.7f}'.format(time.time() - current_time),
                      "seconds from node ", addr)
                total_received = 0
                current_time = time.time()

        except socket_timeout:
            print("Process hung for 5 seconds.")
        except KeyboardInterrupt:
            print("\nCtrl+C on receiver process for node x")
            break

    uplink_receiver_socket.close()
    print("total received", counter, "messages")


if __name__ == "__main__":

    # os.system("rm -rf ue_datasets")
    # os.system("mkdir ue_datasets")

    server_ip = 'localhost'
    server_port = 9999

    MTU = 1472  # 1500 - 20 (IP) - 8 (UDP)
    header_size = 30
    MTU_data = 'x' * (MTU - header_size)

    slice_1_queue = Queue()

    start_uplink_receiver(server_port, slice_1_queue)

    print("terminating server...")

    # ppr_header = []
    #
    # ppr_header.append("packet_size")  # In bytes.
    # ppr_header.append("timestamp")  # The timestamp of the message creation at the sender.
    # ppr_header.append("sequence_number")
    # ppr_header.append("inter_arrival_ms")  # The inter-arrival time between this packet and the last received packet.
    # ppr_header.append("lost_packets")  # The packets lost in transmission from this packet to the last received packet.
    # ppr_header.append("receive_time")  # The time the packet is received at the antenna.
    # ppr_header.append("transmission_delay_ms")  # receive_time - timestamp
    # ppr_header.append("dropped")  # "1" if the node buffer is full, and "0" otherwise.
    # ppr_header.append("buffering_delay_ms")  # receive_time - (the time the packet exited the buffer) ("-1" for dropped packets.
    # ppr_header.append("node_current_buffer_size")  # How many bytes in the node's buffer at the moment this packet was received.
    # ppr_header.append("node_max_buffer_size")  # Currently does not change once initialized.
    # ppr_header.append("slice_current_buffer_size")  # How many bytes in the whole slice buffer at the moment this packet was received.
    # ppr_header.append("slice_max_buffer_size")  # Currently does not change once initialized.
    # ppr_header.append("node_id")  # Currently does not change once initialized.
    # ppr_header.append("slice_id")  # Currently does not change once initialized.
    # ppr_header.append("slice_max_bandwidth")  # In Mbps. Currently does not change once initialized.
    # ppr_header.append("number_of_users")  # number_of_users in this slice. Currently does not change once initialized.

