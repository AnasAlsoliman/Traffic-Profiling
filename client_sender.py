
import socket
import sys
import struct
import math
import time
import select
import datetime

def get_injection_parameters():
    message_size = 1000
    desired_bandwidth = 125000
    return message_size, desired_bandwidth

def create_packet(data, sequence_number):

    padding = "0" * (10 - len(sequence_number))  # sequence_number should be exactly 10 bytes.
    sequence_number = padding + sequence_number

    timestamp = time.time()
    timestamp = str(timestamp)
    padding = "0" * (20 - len(timestamp))  # timestamp should be exactly 20 bytes.
    timestamp = timestamp + padding

    packet = bytes(timestamp + sequence_number + data, 'utf')
    return packet


def send_to_uplink(data, sequence_number):
    packet = create_packet(data, str(sequence_number))
    sent = server_socket.sendto(packet, (server_ip, server_port))
    return sent


def start_uplink_traffic_injection():
    message_size, desired_bandwidth = get_injection_parameters()
    num_of_packets = message_size / MTU  # How many packets we need to send a single message.
    num_of_MTU_packets = math.floor(num_of_packets)  # The last packet is less than MTU size.

    sequence_number = 1
    total_packets = 0
    total_sent = 0  # For print purposes only.
    sleep_time = message_size / desired_bandwidth  # inter-arrival time of messages (not packets).

    print('Message size: ', message_size / 1000, "KB")
    print('Desired bandwidth: ', desired_bandwidth * 8 / 1000000, "Mbps")
    print("Whole message inter-arrivals: ", sleep_time, "second")

    one_second = time.time()

    while True:

        try:
            current_time = time.time()

            ############### Start Injection #################
            for i in range(0, num_of_MTU_packets):
                sent = send_to_uplink(MTU_data, sequence_number)
                total_sent = total_sent + sent
                sequence_number = sequence_number + 1
                total_packets += 1
                if sequence_number == 9999999999:
                    sequence_number = 1

            # Both actually works.
            # remaining_bytes = message_size - total_sent
            remaining_bytes = message_size - (MTU * num_of_MTU_packets)

            if remaining_bytes != 0:  # We still have less-than-MTU bytes to send.
                if remaining_bytes <= header_size:  # Minimum packet size is header size.
                    data = ''
                else:
                    data = MTU_data[:remaining_bytes - header_size]

                sent = send_to_uplink(data, sequence_number)
                total_sent = total_sent + sent
                sequence_number = sequence_number + 1
                total_packets += 1
                if sequence_number == 9999999999:
                    sequence_number = 1
            ################ End Injection #################

            # A summary print every 1 second.
            if (current_time - one_second) > 1:

                bandwidth_offset = total_sent / desired_bandwidth
                if bandwidth_offset < 0.95 or bandwidth_offset > 1.05:
                    timer_offset = 1 - bandwidth_offset
                    sleep_time = sleep_time - (sleep_time * timer_offset)
                    print("timer_offset", timer_offset)
                    print("new sleep_time", sleep_time)
                    print("---------------------")

                now = datetime.datetime.now()
                now = now.strftime("%H:%M:%S")
                current_traffic = total_sent * 8 / 1000000
                current_traffic = '{0:.3f}'.format(current_traffic)
                elapsed_time = time.time() - one_second
                elapsed_time = '{0:.10f}'.format(elapsed_time)
                print("sent:", current_traffic, "Mbit within", elapsed_time, "- current time:", now)
                one_second = time.time()
                total_sent = 0

                # Check for updated traffic parameters every 1 second.
                new_message_size, new_desired_bandwidth = get_injection_parameters()
                if message_size == new_message_size and desired_bandwidth == new_desired_bandwidth:
                    pass  # No change in traffic profile.
                else:
                    # print("new injection parameters for node", client_node_id, "- message_size", new_message_size, "desired_bandwidth", new_desired_bandwidth)
                    message_size = new_message_size
                    desired_bandwidth = new_desired_bandwidth
                    sleep_time = message_size / desired_bandwidth
                    num_of_packets = message_size / MTU
                    num_of_MTU_packets = math.floor(num_of_packets)

                    # Inter-arrival of packets cannot exceed 1 second.
                    if sleep_time > 1:
                        sleep_time = 1

            # Enforcing the inter-arrival time between messages.
            # wasted_time = time.time() - current_time
            # time.sleep(sleep_time - wasted_time)
            # time.sleep(sleep_time - sleep_offset)
            time.sleep(sleep_time)


        # This happens when trying to sendto() a non-empty buffer.
        # This might never happen if the socket is not set to non-blocking.
        except BlockingIOError:
            select.select([], [server_socket], [])
            print("buffer is full (the remaining of the message will be lost)")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\nctrl+C detected on injection process")
            break

    server_socket.close()
    print("total_packets:", total_packets)
    print("existing injection process for client x")


if __name__ == "__main__":

    # 1472 makes sure to fit our UDP packet to exactly a single MAC-layer frame which is 1500 bytes.
    MTU = 1472  # 1472 + IP 20-bytes + UDP 8-bytes = 1500 bytes.
    header_size = 30
    MTU_data = 'x' * (MTU - header_size)

    server_ip = 'localhost'
    server_port = 9999

    sleep_offset = 0.00176

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    start_uplink_traffic_injection()



