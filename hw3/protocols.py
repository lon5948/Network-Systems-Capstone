import random

def aloha(setting, show_history=False):
    host_actions = [[] for i in range(setting.host_num)]
    packet_come = [[] for i in range(setting.host_num)]
    packet_num = [0 for i in range(setting.host_num)]
    sending_time = [0 for i in range(setting.host_num)]
    collision = [False for i in range(setting.host_num)]
    waiting_time = [0 for i in range(setting.host_num)]
    success_count = 0
    idle_count = 0
    collision_count = 0
    random.seed(setting.seed)
    for t in range(setting.total_time):
        # All hosts decide the action (send/idle/stop sending)
        sending_now = []
        # Hosts that decide to send packets.
        for i in range(setting.host_num):
            if t in setting.packets[i]:
                packet_come[i].append('V')
                packet_num[i] += 1
            else:
                packet_come[i].append(' ')
            
            if waiting_time[i] > 0:
                host_actions[i].append('.')
                waiting_time[i] -= 1
            elif sending_time[i] > 1:
                host_actions[i].append('-')
                sending_time[i] -= 1
                sending_now.append(i)
            elif sending_time[i] == 1:
                sending_now.append(i)
            elif packet_num[i] > 0:
                host_actions[i].append('<')
                sending_time[i] = setting.packet_time
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
                    host_actions[i][t] = '|'
                    collision[i] = False
                    waiting_time[i] = random.randint(1, setting.max_colision_wait_time)
                else:
                    host_actions[i][t] = '>'
                    success_count += setting.packet_time
                    packet_num[i] -= 1
                sending_time[i] = 0

    # Show the history of each host
    if show_history:
        for ind in range(setting.host_num):
            print('    ', end='')
            for p in packet_come[ind]:
                print(p, end='')
            print('')
            print('h' + str(ind) + ': ', end='')
            for a in host_actions[ind]:
                print(a, end='')
            print('')

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


def slotted_aloha(setting, show_history=False):
    host_actions = [[] for i in range(setting.host_num)]
    packet_come = [[] for i in range(setting.host_num)]
    packet_num = [0 for i in range(setting.host_num)]
    sending = [False for i in range(setting.host_num)]
    collision = [False for i in range(setting.host_num)]
    retransmit = [False for i in range(setting.host_num)]
    success_count = 0
    idle_count = 0
    collision_count = 0
    random.seed(setting.seed)
    pr = random.SystemRandom()
    for t in range(setting.total_time):
        # All hosts decide the action (send/idle/stop sending)
        sending_now = []
        # Hosts that decide to send packets.
        for i in range(setting.host_num):
            if t in setting.packets[i]:
                packet_come[i].append('V')
                packet_num[i] += 1
            else:
                packet_come[i].append(' ')
            
            if sending[i] == True:
                host_actions[i].append('-')
                sending_now.append(i)
            elif retransmit[i] == True and t % setting.packet_time == 0:
                if pr.random() < setting.p_resend:
                    host_actions[i].append('<')
                    sending[i] = True
                    retransmit[i] = False
                    sending_now.append(i)
                else:
                    host_actions[i].append('.')
            elif packet_num[i] > 0 and t % setting.packet_time == 0:
                host_actions[i].append('<')
                sending[i] = True
                sending_now.append(i)
            else:
                host_actions[i].append('.')

        # Check collision if two or above hosts are sending.
        if len(sending_now) > 1:
            for host in sending_now:
                collision[host] = True

        # If the host finishes a packet, it stops sending.
        for i in range(setting.host_num):
            if sending[i] == True and t % setting.packet_time == (setting.packet_time - 1):
                if collision[i] == True:
                    host_actions[i][t] = '|'
                    collision[i] = False
                    retransmit[i] = True
                else:
                    host_actions[i][t] = '>'
                    success_count += setting.packet_time
                    packet_num[i] -= 1
                sending[i] = False

    # Show the history of each host
    if show_history:
        for ind in range(setting.host_num):
            print('    ', end='')
            for p in packet_come[ind]:
                print(p, end='')
            print('')
            print('h' + str(ind) + ': ', end='')
            for a in host_actions[ind]:
                print(a, end='')
            print('')

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


def csma(setting, show_history=False):
    host_actions = [[] for i in range(setting.host_num)]
    packet_come = [[] for i in range(setting.host_num)]
    packet_num = [0 for i in range(setting.host_num)]
    sending_time = [0 for i in range(setting.host_num)]
    collision = [False for i in range(setting.host_num)]
    waiting_time = [0 for i in range(setting.host_num)]
    detect_waiting_time = [0 for i in range(setting.host_num)]
    sound = [False for i in range(setting.total_time)]
    success_count = 0
    idle_count = 0
    collision_count = 0
    random.seed(setting.seed)
    for t in range(setting.total_time):
        # All hosts decide the action (send/idle/stop sending)
        sending_now = []
        # Hosts that decide to send packets.
        for i in range(setting.host_num):
            if t in setting.packets[i]:
                packet_come[i].append('V')
                packet_num[i] += 1
            else:
                packet_come[i].append(' ')
            
            if waiting_time[i] > 0:
                host_actions[i].append('.')
                waiting_time[i] -= 1
            elif sending_time[i] > 1:
                host_actions[i].append('-')
                sending_time[i] -= 1
                sending_now.append(i)
                sound[t] = True
            elif sending_time[i] == 1:
                sending_now.append(i)
                sound[t] = True
            elif detect_waiting_time[i] > 0:
                host_actions[i].append('.')
                detect_waiting_time[i] -= 1
            elif packet_num[i] > 0:
                if t - 1 >= setting.link_delay and (sound[t - 1 - setting.link_delay] == False or host_actions[i][t-1] == '>'):
                    host_actions[i].append('<')
                    sending_time[i] = setting.packet_time
                    sending_now.append(i)
                    sound[t] = True
                else:
                    host_actions[i].append('.')
                    detect_waiting_time[i] = random.randint(1, setting.max_colision_wait_time)
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
                    host_actions[i][t] = '|'
                    collision[i] = False
                    waiting_time[i] = random.randint(1, setting.max_colision_wait_time)
                else:
                    host_actions[i][t] = '>'
                    success_count += setting.packet_time
                    packet_num[i] -= 1
                sound[t] = False
                sending_time[i] = 0

    # Show the history of each host
    if show_history:
        for ind in range(setting.host_num):
            print('    ', end='')
            for p in packet_come[ind]:
                print(p, end='')
            print('')
            print('h' + str(ind) + ': ', end='')
            for a in host_actions[ind]:
                print(a, end='')
            print('')

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


def csma_cd(setting, show_history=False):
    host_actions = [[] for i in range(setting.host_num)]
    packet_come = [[] for i in range(setting.host_num)]
    packet_num = [0 for i in range(setting.host_num)]
    sending_time = [0 for i in range(setting.host_num)]
    waiting_time = [0 for i in range(setting.host_num)]
    detect_waiting_time = [0 for i in range(setting.host_num)]
    sound = [[] for i in range(setting.total_time)]
    success_count = 0
    idle_count = 0
    collision_count = 0
    random.seed(setting.seed)
    for t in range(setting.total_time):
        # All hosts decide the action (send/idle/stop sending)
        for i in range(setting.host_num):
            if t in setting.packets[i]:
                packet_come[i].append('V')
                packet_num[i] += 1
            else:
                packet_come[i].append(' ')
            
            if waiting_time[i] > 0:
                host_actions[i].append('.')
                waiting_time[i] -= 1
            elif sending_time[i] > 1:
                host_actions[i].append('-')
                sending_time[i] -= 1
                sound[t].append(i)
            elif sending_time[i] == 1:
                sound[t].append(i)
            elif detect_waiting_time[i] > 0:
                host_actions[i].append('.')
                detect_waiting_time[i] -= 1
            elif packet_num[i] > 0:
                if t - 1 >= setting.link_delay and (len(sound[t - 1 - setting.link_delay]) == 0 or (len(sound[t - 1 - setting.link_delay]) == 1 and sound[t - 1 - setting.link_delay][0] == i)):
                    host_actions[i].append('<')
                    sending_time[i] = setting.packet_time
                    sound[t].append(i)
                else:
                    host_actions[i].append('.')
                    detect_waiting_time[i] = random.randint(1, setting.max_colision_wait_time)
            else:
                host_actions[i].append('.')

        for i in range(setting.host_num):
            # Check collision if two or above hosts are sending.
            if sending_time[i] >= 1 and t - 1 >= setting.link_delay and (len(sound[t - 1 - setting.link_delay]) > 1 or (len(sound[t - 1 - setting.link_delay]) == 1 and sound[t - 1 - setting.link_delay][0] != i)): 
                host_actions[i][t] = '|'
                waiting_time[i] = random.randint(1, setting.max_colision_wait_time)
                sending_time[i] = 0
            elif sending_time[i] == 1: # If the host finishes a packet, it stops sending.
                host_actions[i][t] = '>'
                success_count += setting.packet_time
                packet_num[i] -= 1
                sending_time[i] = 0

    # Show the history of each host
    if show_history:
        for ind in range(setting.host_num):
            print('    ', end='')
            for p in packet_come[ind]:
                print(p, end='')
            print('')
            print('h' + str(ind) + ': ', end='')
            for a in host_actions[ind]:
                print(a, end='')
            print('')

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