def aloha(setting, show_history=False):
    host_actions = [[] for i in range(setting.host_num)]
    packet_time = [[] for i in range(setting.host_num)]
    for t in range(setting.total_time):
        # All hosts decide the action (send/idle/stop sending)
        for i in range(setting.host_num):
            if t in setting.packets[i]:
                packet_time[i].append('V')
            else:
                packet_time[i].append(' ')

        # Hosts that decide to send send packets.

        # Check collision if two or above hosts are sending.

        # If the host finishes a packet, it stops sending.
    
    # Show the history of each host
    if show_history:
        for ind in range(setting.host_num):
            print('h' + str(ind) + ': ', end='')
            for p in packet_time[ind]:
                print(p, end='')
            print('h' + str(ind) + ': ', end='')
            for p in host_actions[ind]:
                print(p, end='')

    return success_rate, idle_rate, collision_rate