from scapy.all import *
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Network parameters for analysis.')
parser.add_argument('ip', type=str, help='Source IP address')
parser.add_argument('port', type=int, help='Source UDP port')
args = parser.parse_args()


pcap = rdpcap("C:/Users/slouli/Desktop/merged_capture.pcap")

def getRtpSeq(pkt):
    SeqByte1 = 2
    SeqByte2 = 3
    return (pkt["Raw"].load[SeqByte1] << 8) + pkt["Raw"].load[SeqByte2]

#Extract destination IP for the graph
def getIpDst(pcap, ip_src, port_src):
    def _getIpDst(pkt_iter, ip_src, port_src):
        pkt = next(pkt_iter)

        if pkt.haslayer("IP") and \
                pkt.haslayer("UDP") and \
                pkt["IP"].src == ip_src and \
                pkt["UDP"].sport==port_src:
            return pkt["IP"].dst
        else:
            return _getIpDst(pkt_iter, ip_src, port_src)

    pkt_iter = iter(pcap)
    return _getIpDst(pkt_iter,ip_src, port_src)

ip_src = args.ip #Should be a string
port_src = args.port #Should be a number
time_offset = pcap[0].time
ip_dst = getIpDst(pcap,ip_src, port_src)
time_display = 200
window_size = 20

seq_ls = [(pkt.time-time_offset, getRtpSeq(pkt)) for pkt in pcap \
        if pkt.haslayer("IP") \
        if pkt.haslayer("UDP") \
        if pkt["IP"].src==ip_src \
        if pkt["UDP"].sport==port_src \
        if getRtpSeq(pkt) >= 0
        if (pkt.time-time_offset) > time_display
        if (pkt.time-time_offset) < time_display + window_size]

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

plt.xticks([0,1,2,3], ['',ip_src, ip_dst, ''])

#Draw a base line to set width of the graph
plt.plot([0.5,2.5],[time_display, time_display], 'b-',lw=0.5)
for key, coords in sent.items():
    if key in received:
        plt.plot([1,2], [coords[1], received[key][1]],'g-', lw=1)
    else:
        plt.plot([1,2], [coords[1], coords[1]], 'r-', lw=1)

plt.xlabel("Hosts")
plt.ylabel("Time (s)")

plt.show()




