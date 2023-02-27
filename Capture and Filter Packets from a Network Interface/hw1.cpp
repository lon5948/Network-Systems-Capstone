#include <iostream>
#include <stdlib.h>
#include <pcap/pcap.h> 
#include <string.h>
#include <vector>
using namespace std;

#define ETHER_ADDR_LEN 6 /* Ethernet addresses are 6 bytes */
#define SIZE_ETHERNET 14 /* ethernet headers are always exactly 14 bytes */

/* Ethernet header */
struct sniff_ethernet {
	u_char ether_dhost[ETHER_ADDR_LEN]; /* Destination host address */
	u_char ether_shost[ETHER_ADDR_LEN]; /* Source host address */
	u_short ether_type; /* IP? ARP? RARP? etc */
};

/* IP header */
struct sniff_ip {
	u_char ip_vhl;		/* version << 4 | header length >> 2 */
	u_char ip_tos;		/* type of service */
	u_short ip_len;		/* total length */
	u_short ip_id;		/* identification */
	u_short ip_off;		/* fragment offset field */
#define IP_RF 0x8000		/* reserved fragment flag */
#define IP_DF 0x4000		/* don't fragment flag */
#define IP_MF 0x2000		/* more fragments flag */
#define IP_OFFMASK 0x1fff	/* mask for fragmenting bits */
	u_char ip_ttl;		/* time to live */
	u_char ip_p;		/* protocol */
	u_short ip_sum;		/* checksum */
	struct in_addr ip_src,ip_dst; /* source and dest address */
};
#define IP_HL(ip)		(((ip)->ip_vhl) & 0x0f)
#define IP_V(ip)		(((ip)->ip_vhl) >> 4)

/* TCP header */
typedef u_int tcp_seq;

struct sniff_tcp {
	u_short th_sport;	/* source port */
	u_short th_dport;	/* destination port */
	tcp_seq th_seq;		/* sequence number */
	tcp_seq th_ack;		/* acknowledgement number */
	u_char th_offx2;	/* data offset, rsvd */
#define TH_OFF(th)	(((th)->th_offx2 & 0xf0) > 4)
	u_char th_flags;
#define TH_FIN 0x01
#define TH_SYN 0x02
#define TH_RST 0x04
#define TH_PUSH 0x08
#define TH_ACK 0x10
#define TH_URG 0x20
#define TH_ECE 0x40
#define TH_CWR 0x80
#define TH_FLAGS (TH_FIN|TH_SYN|TH_RST|TH_ACK|TH_URG|TH_ECE|TH_CWR)
	u_short th_win;		/* window */
	u_short th_sum;		/* checksum */
	u_short th_urp;		/* urgent pointer */
};

int main(int argc, const char * argv[]) {
    pcap_if_t *devices = NULL; 
    const char *interface = NULL;
    char errbuf[PCAP_ERRBUF_SIZE];
    //char ntop_buf[256];
    struct ether_header *eptr;
    struct pcap_pkthdr header;
    vector<pcap_if_t*> vec; // vec is a vector of pointers pointing to pcap_if_t 
    int count = -1;
    const char *filter = "all";

    for(int i = 1; i < argc; i+=2) {
        if(!strcmp(argv[i], "-i") || !strcmp(argv[i], "--interface"))
            interface = argv[i+1];
        else if(!strcmp(argv[i], "-c") || !strcmp(argv[i], "--count"))
            count = stoi(argv[i+1]);
        else if(!strcmp(argv[i], "-f") || !strcmp(argv[i], "--filter"))
            filter = argv[i+1];
        else {
            printf("wrong command\n"); 
            exit(1);
        }
    }
    
    if(interface == NULL) {
        printf("wrong command.\n");
        exit(1);
    }
    
    // get all devices 
    if(-1 == pcap_findalldevs(&devices, errbuf)) {
        fprintf(stderr, "pcap_findalldevs: %s\n", errbuf); // if error, fprint error message --> errbuf
        exit(1);
    }

    //list all device
    int cnt = 0;
    for(pcap_if_t *d = devices; d ; d = d->next, cnt++) {
        vec.push_back(d);
        cout << "Name: " << d->name << endl;
    }
    
    struct bpf_program fp; // for filter, compiled in "pcap_compile"
    pcap_t *handle;
    handle = pcap_open_live(interface, 65535, 1, 1, errbuf);  
    //pcap_open_live(device, snaplen, promise, to_ms, errbuf), interface is your interface, type is "char *"   
    
    if(!handle || handle == NULL) {
        fprintf(stderr, "pcap_open_live(): %s\n", errbuf);
        exit(1);
    }
    
    if(filter != "all") {
        if(-1 == pcap_compile(handle, &fp, filter, 1, PCAP_NETMASK_UNKNOWN) ) { // compile "your filter" into a filter program, type of {your_filter} is "char *" 
            pcap_perror(handle, "pkg_compile compile error\n");
            exit(1);
        }
        if(-1 == pcap_setfilter(handle, &fp)) { // make it work
            pcap_perror(handle, "set filter error\n");
            exit(1);
        }
    }
    
    bpf_u_int32 mask;
    bpf_u_int32 net;
    const struct sniff_ethernet *ethernet; /* The ethernet header */
    const struct sniff_ip *ip; /* The IP header */
    const struct sniff_tcp *tcp; /* The TCP header */
    const char *payload; /* Packet payload */
    u_int size_ip;
    u_int size_tcp;

    while(count-- != 0) {   
        const unsigned char* packet = pcap_next(handle, &header);
        ethernet = (struct sniff_ethernet*)(packet);
        ip = (struct sniff_ip*)(packet + SIZE_ETHERNET);
        size_ip = IP_HL(ip)*4;
        tcp = (struct sniff_tcp*)(packet + SIZE_ETHERNET + size_ip);
        size_tcp = TH_OFF(tcp)*4;
        payload = (char *)(packet + SIZE_ETHERNET + size_ip + size_tcp);
	if(ip->ip_p == 1) {
	    printf("Transport type: ICMP\n");
	    printf("Source IP: \n");
	    printf("Destination IP: \n");
	    printf("ICMP type value: \n");
	}
	else if(ip->ip_p == 17) {
            printf("Transport type: UDP\n");
	    printf("Source IP: %d\n", ethernet->ether_shost[ETHER_ADDR_LEN]);
            printf("Destination IP: %d\n", ethernet->ether_dhost[ETHER_ADDR_LEN]);
            printf("Source port: %d\n", tcp->th_sport);
            printf("Destination port: %d\n", tcp->th_dport);
            int len = strlen(payload);
            char hex_payload[len*3];
            int p = 0, h = 0;
            while(payload[p] != '\0') {
                sprintf((char*)(hex_payload+h), "%02X", payload[p]);
                p++;
                h += 3;
            }
            hex_payload[h] = '\0';
            printf("Payload: %s\n\n", hex_payload);
	}
	else if(ip->ip_p == 6) {
	    printf("Transport type: TCP\n");
            printf("Source IP: %d\n", ethernet->ether_shost[ETHER_ADDR_LEN]);
            printf("Destination IP: %d\n", ethernet->ether_dhost[ETHER_ADDR_LEN]);
            printf("Source port: %d\n", tcp->th_sport);
            printf("Destination port: %d\n", tcp->th_dport);
	    int len = strlen(payload);
	    char hex_payload[len*3];
	    int p = 0, h = 0;
	    while(payload[p] != '\0') {
	    	sprintf((char*)(hex_payload+h), "%03X", payload[p]);
		p++;
		h += 3;
            }
	    hex_payload[h] = '\0';
            printf("Payload: %s\n\n", hex_payload);
	}
    }
    
    pcap_freealldevs(devices);
    
    return 0;
}
