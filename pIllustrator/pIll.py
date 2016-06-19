from scapy.all import *
import matplotlib.pyplot as plt

pcap = rdpcap("C:/Users/slouli/Desktop/mel_merge.pcap")

def getRtpSeq(pkt):
    SeqByte1 = 2
    SeqByte2 = 3
    return (pkt["Raw"].load[SeqByte1] << 8) + pkt["Raw"].load[SeqByte2]


ip_src = "10.2.196.204" #Should be a string
port_src = 32570 #Should be a number
time_offset = pcap[0].time

seq_ls = [(pkt.time-time_offset, getRtpSeq(pkt)) for pkt in pcap \
        if pkt.haslayer("IP") \
        if pkt.haslayer("UDP") \
        if pkt["IP"].src==ip_src \
        if pkt["UDP"].sport==port_src \
        if getRtpSeq(pkt) >= 0]

"""
time_tup, seq_tup = zip(*seq)
time_ls = list(time_tup)
seq_ls = list(seq_tup)
"""

sent = {}
received = {}
"""seq_ls = list(seq_tup)"""

for time, seq in seq_ls:
    if seq not in sent:
        sent[seq] = [0, time]
    else:
        received[seq] = [1, time]

for key, coords in sent.items():
    if key in received:
        plt.plot([0,1], [coords[1], received[key][1]],'g-', lw=1)
    else:
        plt.plot([0,1], [coords[1], coords[1]], 'r-', lw=1)

plt.show()




