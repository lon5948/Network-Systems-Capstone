import random

def aloha(setting, show_history=False):
    host_actions = [[] for i in range(setting.host_num)]
    packet_time = [[] for i in range(setting.host_num)]
    packet_list = [0 for i in range(setting.host_num)]
    sending_time = [0 for i in range(setting.host_num)]
    collision = [False for i in range(setting.host_num)]
    waiting_time = [0 for i in range(setting.host_num)]
    success_count = 0
    idle_count = 0
    collision_count = 0
    for t in range(setting.total_time):
        sending_now = []
        # All hosts decide the action (send/idle/stop sending)

        # Hosts that decide to send packets.
        for i in range(setting.host_num):
            if t in setting.packets[i]:
                packet_time[i].append('V')
                packet_list[i] += 1
            else:
                packet_time[i].append(' ')
            
            if waiting_time[i] > 0:
                host_actions[i].append('.')
                waiting_time[i] -= 1
            elif sending_time[i] > 1:
                host_actions[i].append('-')
                sending_time[i] -= 1
                sending_now.append(i)
            elif sending_time[i] == 1:
                sending_now.append(i)
            elif packet_list[i] > 0:
                host_actions[i].append('<')
                packet_list[i] -= 1
                sending_time[i] = setting.packet_time - 1
                sending_now.append(i)
            else:
                host_actions[i].append('.')

        # Check collision if two or above hosts are sending.
        if len(sending_now) > 1:
            for host in sending_now:
                collision[host] = True

        # If the host finishes a packet, it stops sending.
        for i in range(setting.host_num):
            if sending_time[i] == 1:
                if collision[i] == True:
                    host_actions[i].append('|')
                    waiting_time[i] = random.randint(1, setting.max_colision_wait_time)
                else:
                    host_actions[i].append('>')
                    success_count += setting.packet_time
                sending_time[i] = 0

    # Show the history of each host
    if show_history:
        for ind in range(setting.host_num):
            print('h' + str(ind) + ': ', end='')
            for p in packet_time[ind]:
                print(p, end='')
            print('h' + str(ind) + ': ', end='')
            for a in host_actions[ind]:
                print(a, end='')

    for t in range(setting.total_time):
        idle = True
        for i in range(setting.host_num):
            if host_actions[i][t] != '.':
                idle = False
        if idle == True:
            idle_count += 1
    
    collision_count = setting.total_time - success_count - idle_count
    success_rate = success_count/setting.total_time
    idle_rate = idle_count/setting.total_time
    collision_rate = collision_count/setting.total_time
    return success_rate, idle_rate, collision_rate