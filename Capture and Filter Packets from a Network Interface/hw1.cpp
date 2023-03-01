#include <iostream>
#include <stdlib.h>
#include <pcap/pcap.h> 
#include <string.h>
#include <vector>
using namespace std;

#define ETHER_ADDR_LEN 6 /* Ethernet addresses are 6 bytes */
#define SIZE_ETHERNET 14 /* ethernet headers are always exactly 14 bytes */
#define SIZE_UDP 8 /* udp headers are always exactly 8 bytes */

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
	u_short ip_off;		/* flags, fragment offset */
#define IP_RF 0x8000		/* reserved fragment flag */
#define IP_DF 0x4000		/* don't fragment flag */
#define IP_MF 0x2000		/* more fragments flag */
#define IP_OFFMASK 0x1fff	/* mask for fragmenting bits */
	u_char ip_ttl;		/* time to live */
	u_char ip_p;		/* protocol */
	u_short ip_sum;		/* checksum */
	struct in_addr ip_src,ip_dst; /* source and dest address */
};
#define IP_HL(ip) (((ip)->ip_vhl) & 0x0f)
#define IP_V(ip)  (((ip)->ip_vhl) >> 4)

/* TCP header */
struct sniff_tcp {
	u_short th_sport;	/* source port */
	u_short th_dport;	/* destination port */
	u_int th_seq;		/* sequence number */
	u_int th_ack;		/* acknowledgement number */
	u_char th_offx2;	/* data offset, reversed */
#define TH_OFF(th)	(((th)->th_offx2 & 0xf0) >> 4)
	u_char th_flags;
#define TH_FIN 0x01
#define TH_SYN 0x02
#define TH_RST 0x04
#define TH_PSH 0x08
#define TH_ACK 0x10
#define TH_URG 0x20
#define TH_ECE 0x40
#define TH_CWR 0x80
#define TH_FLAGS (TH_FIN|TH_SYN|TH_RST|TH_ACK|TH_URG|TH_ECE|TH_CWR)
	u_short th_win;		/* window */
	u_short th_sum;		/* checksum */
	u_short th_urp;		/* urgent pointer */
};

/* UDP header */
struct sniff_udp {
    u_short uh_sport;    /* source port */
    u_short uh_dport;    /* destination port */
    u_short uh_len;      /* udp length */
    u_short uh_sum;      /* udp checksum */
};

/* ICMP header */
struct sniff_icmp {
    u_char ih_type;     /* icmp type */
    u_char ih_code;     /* icmp code */
    u_short ih_sum;     /* icmp checksum */
    u_int ih_roh;       /* icmp rest of header */
};

void print_payload(const u_char *payload, int len) {
	const u_char *ch = payload;
    if(len > 16) len = 16;
    else len--;
	for(int i = 0; i < len; i++) {
		printf("%02x ", *ch);
		ch++;
	}
    return;
}

int main(int argc, const char * argv[]) {
    pcap_if_t *devices = NULL; 
    const char *interface = NULL;
    char errbuf[PCAP_ERRBUF_SIZE];
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
        //cout << "Name: " << d->name << endl;
    }
    
    struct bpf_program fp; // for filter, compiled in "pcap_compile"
    pcap_t *handle;
    handle = pcap_open_live(interface, 65535, 1, 1, errbuf);  
    //pcap_open_live(device, snaplen, promise, to_ms, errbuf), interface is your interface, type is "char *"   
    
    if(!handle || handle == NULL) {
        fprintf(stderr, "pcap_open_live(): %s\n", errbuf);
        exit(1);
    }
    
    if(!strcmp(filter, "all"))
        filter = "ip"; 
    if(-1 == pcap_compile(handle, &fp, filter, 1, PCAP_NETMASK_UNKNOWN) ) { // compile "your filter" into a filter program, type of {your_filter} is "char *" 
        pcap_perror(handle, "pkg_compile compile error\n");
        exit(1);
    }
    if(-1 == pcap_setfilter(handle, &fp)) { // make it work
        pcap_perror(handle, "set filter error\n");
        exit(1);
    }
    
    const struct sniff_ethernet *ethernet; /* The ethernet header */
    const struct sniff_ip *ip; /* The IP header */
    const struct sniff_tcp *tcp; /* The TCP header */
    const struct sniff_udp *udp; /* The UDP header */
    const struct sniff_icmp *icmp; /* The ICMP header */
    const u_char *payload; /* Packet payload */
    int size_ip;
    int size_tcp;
    int size_payload;

    while(count != 0) {   
        const unsigned char* packet = pcap_next(handle, &header);
        ethernet = (struct sniff_ethernet*)(packet);
        ip = (struct sniff_ip*)(packet + SIZE_ETHERNET);
        size_ip = IP_HL(ip)*4;

        switch(ip->ip_p) {
            case IPPROTO_ICMP:
                icmp = (struct sniff_icmp*)(packet + SIZE_ETHERNET + size_ip);
                printf("Transport type: ICMP\n");
                printf("Source IP: %s\n", inet_ntoa(ip->ip_src));
                printf("Destination IP: %s\n", inet_ntoa(ip->ip_dst));
                printf("ICMP type value: %d\n", icmp->ih_type);
                break;
            case IPPROTO_UDP:
                udp = (struct sniff_udp*)(packet + SIZE_ETHERNET + size_ip);
                payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + SIZE_UDP);
                size_payload = ntohs(ip->ip_len) - (size_ip + SIZE_UDP);
                printf("Transport type: UDP\n");
                printf("Source IP: %s\n", inet_ntoa(ip->ip_src));
                printf("Destination IP: %s\n", inet_ntoa(ip->ip_dst));
                printf("Source port: %d\n", htons(udp->uh_sport));
                printf("Destination port: %d\n", htons(udp->uh_dport));
                printf("Payload: ");
                print_payload(payload, size_payload);
                printf("\n");
                break;
            case IPPROTO_TCP:
                tcp = (struct sniff_tcp*)(packet + SIZE_ETHERNET + size_ip);
                size_tcp = TH_OFF(tcp)*4;
                payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + size_tcp);
                size_payload = ntohs(ip->ip_len) - (size_ip + size_tcp);
                printf("Transport type: TCP\n");
                printf("Source IP: %s\n", inet_ntoa(ip->ip_src));
                printf("Destination IP: %s\n", inet_ntoa(ip->ip_dst));
                printf("Source port: %d\n", htons(tcp->th_sport));
                printf("Destination port: %d\n", htons(tcp->th_dport));
                printf("Payload: ");
                print_payload(payload, size_payload);
                printf("\n");
                break;
        }
        printf("\n");
        count--;
    }

    pcap_freealldevs(devices);
    
    return 0;
}
