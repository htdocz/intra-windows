package main

import (
	"bufio"
	"context"
	"encoding/binary"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"strconv"
	"strings"
	"time"

	"localhost/Intra/Android/app/src/go/doh"
	"localhost/Intra/Android/app/src/go/intra/split"
	"golang.org/x/net/dns/dnsmessage"
)

func resolveWithJigsawDOH(ctx context.Context, resolver doh.Resolver, domain string) ([]net.IP, error) {
	queryDomain := domain
	if !strings.HasSuffix(queryDomain, ".") {
		queryDomain += "."
	}

	name, err := dnsmessage.NewName(queryDomain)
	if err != nil {
		return nil, err
	}

	msg := dnsmessage.Message{
		Header: dnsmessage.Header{
			ID:               0xbeef,
			Response:         false,
			RecursionDesired: true,
		},
		Questions: []dnsmessage.Question{
			{
				Name:  name,
				Type:  dnsmessage.TypeA,
				Class: dnsmessage.ClassINET,
			},
		},
	}

	packed, err := msg.Pack()
	if err != nil {
		return nil, err
	}

	respBytes, err := resolver.Query(ctx, packed)
	if err != nil {
		return nil, err
	}

	var respMsg dnsmessage.Message
	if err := respMsg.Unpack(respBytes); err != nil {
		return nil, err
	}

	var ips []net.IP
	for _, ans := range respMsg.Answers {
		if ans.Header.Type == dnsmessage.TypeA {
			aRecord, ok := ans.Body.(*dnsmessage.AResource)
			if ok {
				ips = append(ips, net.IP(aRecord.A[:]))
			}
		}
	}

	if len(ips) == 0 {
		return nil, fmt.Errorf("no A records found for %s", domain)
	}

	return ips, nil
}

func startDNSProxy(bindAddr string, resolver doh.Resolver) {
	if bindAddr == "" {
		return
	}
	addr, err := net.ResolveUDPAddr("udp", bindAddr)
	if err != nil {
		log.Printf("[DNS HATA] UDP adresi cozumlenemedi: %v", err)
		return
	}

	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		log.Printf("[DNS HATA] Yerel DNS portu (53) dinlenemedi: %v", err)
		return
	}
	defer conn.Close()

	log.Printf("[DNS] Yerel DNS sunucusu %s adresinde baslatildi.", bindAddr)

	buf := make([]byte, 2048)
	for {
		n, clientAddr, err := conn.ReadFrom(buf)
		if err != nil {
			continue
		}

		query := make([]byte, n)
		copy(query, buf[:n])

		go func(q []byte, cAddr net.Addr) {
			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer cancel()

			resp, err := resolver.Query(ctx, q)
			if err != nil {
				return
			}

			_, _ = conn.WriteTo(resp, cAddr)
		}(query, clientAddr)
	}
}

func handleHTTPClient(clientConn net.Conn, resolver doh.Resolver) {
	defer clientConn.Close()

	reader := bufio.NewReader(clientConn)
	reqLine, err := reader.ReadString('\n')
	if err != nil {
		return
	}

	parts := strings.Split(strings.TrimSpace(reqLine), " ")
	if len(parts) < 2 {
		return
	}

	method := parts[0]
	target := parts[1]

	if method != "CONNECT" {
		// Return 501 Not Implemented for non-HTTPS traffic to remain simple
		clientConn.Write([]byte("HTTP/1.1 501 Not Implemented\r\n\r\n"))
		return
	}

	// Consume headers
	for {
		line, err := reader.ReadString('\n')
		if err != nil || line == "\r\n" || line == "\n" {
			break
		}
	}

	host, portStr, err := net.SplitHostPort(target)
	if err != nil {
		host = target
		portStr = "443"
	}
	port, _ := strconv.Atoi(portStr)

	var targetIP string
	ctx, cancel := context.WithTimeout(context.Background(), 4*time.Second)
	ips, err := resolveWithJigsawDOH(ctx, resolver, host)
	cancel()
	if err != nil {
		sysIPs, sysErr := net.LookupIP(host)
		if sysErr != nil {
			clientConn.Write([]byte("HTTP/1.1 502 Bad Gateway\r\n\r\n"))
			return
		}
		targetIP = sysIPs[0].String()
	} else {
		targetIP = ips[0].String()
	}

	targetAddr, err := net.ResolveTCPAddr("tcp", net.JoinHostPort(targetIP, strconv.Itoa(port)))
	if err != nil {
		clientConn.Write([]byte("HTTP/1.1 502 Bad Gateway\r\n\r\n"))
		return
	}

	log.Printf("[PROXY] HTTP CONNECT istek: %s:%d", host, port)
	dialer := &net.Dialer{Timeout: 5 * time.Second}
	ctx, cancel = context.WithTimeout(context.Background(), 5*time.Second)
	targetConn, err := split.DialWithSplitRetry(ctx, dialer, targetAddr, nil)
	cancel()
	if err != nil {
		log.Printf("[PROXY HATA] HTTP CONNECT %s:%d baglantisi basarisiz: %v", host, port, err)
		clientConn.Write([]byte("HTTP/1.1 502 Bad Gateway\r\n\r\n"))
		return
	}
	defer targetConn.Close()

	if _, err := clientConn.Write([]byte("HTTP/1.1 200 Connection Established\r\n\r\n")); err != nil {
		return
	}

	errChan := make(chan error, 2)
	go func() {
		_, err := io.Copy(targetConn, reader) // Read from buffer
		errChan <- err
	}()
	go func() {
		_, err := io.Copy(clientConn, targetConn)
		errChan <- err
	}()

	<-errChan
}

func startHTTPProxy(bindAddr string, resolver doh.Resolver) {
	if bindAddr == "" {
		return
	}
	listener, err := net.Listen("tcp", bindAddr)
	if err != nil {
		log.Printf("[HTTP HATA] HTTP Proxy baslatilamadi: %v", err)
		return
	}
	defer listener.Close()

	log.Printf("HTTP Proxy listening on %s...", bindAddr)
	for {
		conn, err := listener.Accept()
		if err != nil {
			continue
		}
		go handleHTTPClient(conn, resolver)
	}
}

func handleClient(clientConn net.Conn, resolver doh.Resolver) {
	defer clientConn.Close()

	buf := make([]byte, 262)
	if _, err := io.ReadFull(clientConn, buf[:2]); err != nil {
		return
	}
	if buf[0] != 0x05 {
		return
	}
	nMethods := int(buf[1])
	if _, err := io.ReadFull(clientConn, buf[:nMethods]); err != nil {
		return
	}

	if _, err := clientConn.Write([]byte{0x05, 0x00}); err != nil {
		return
	}

	if _, err := io.ReadFull(clientConn, buf[:4]); err != nil {
		return
	}

	if buf[0] != 0x05 || buf[1] != 0x01 {
		clientConn.Write([]byte{0x05, 0x07, 0x00, 0x01, 0, 0, 0, 0, 0, 0})
		return
	}

	atyp := buf[3]
	var host string
	var port int

	switch atyp {
	case 0x01:
		ipBuf := make([]byte, 4)
		if _, err := io.ReadFull(clientConn, ipBuf); err != nil {
			return
		}
		host = net.IP(ipBuf).String()
	case 0x03:
		lenBuf := make([]byte, 1)
		if _, err := io.ReadFull(clientConn, lenBuf); err != nil {
			return
		}
		domainLen := int(lenBuf[0])
		domainBuf := make([]byte, domainLen)
		if _, err := io.ReadFull(clientConn, domainBuf); err != nil {
			return
		}
		host = string(domainBuf)
	case 0x04:
		ipBuf := make([]byte, 16)
		if _, err := io.ReadFull(clientConn, ipBuf); err != nil {
			return
		}
		host = net.IP(ipBuf).String()
	default:
		clientConn.Write([]byte{0x05, 0x08, 0x00, 0x01, 0, 0, 0, 0, 0, 0})
		return
	}

	portBuf := make([]byte, 2)
	if _, err := io.ReadFull(clientConn, portBuf); err != nil {
		return
	}
	port = int(binary.BigEndian.Uint16(portBuf))

	var targetIP string
	if atyp == 0x03 {
		ctx, cancel := context.WithTimeout(context.Background(), 4*time.Second)
		ips, err := resolveWithJigsawDOH(ctx, resolver, host)
		cancel()
		if err != nil {
			log.Printf("[PROXY UYARI] SOCKS DoH ile cozumlenemedi (%s): %v. Sistem DNS fallback deneniyor...", host, err)
			sysIPs, sysErr := net.LookupIP(host)
			if sysErr != nil {
				log.Printf("[PROXY HATA] SOCKS DNS cozumu basarisiz (%s): %v", host, sysErr)
				clientConn.Write([]byte{0x05, 0x04, 0x00, 0x01, 0, 0, 0, 0, 0, 0})
				return
			}
			targetIP = sysIPs[0].String()
		} else {
			targetIP = ips[0].String()
			log.Printf("[PROXY] SOCKS %s adresi DoH ile cozuldu: %s", host, targetIP)
		}
	} else {
		targetIP = host
	}

	targetAddr, err := net.ResolveTCPAddr("tcp", net.JoinHostPort(targetIP, strconv.Itoa(port)))
	if err != nil {
		log.Printf("[PROXY HATA] SOCKS TCP adresi gecersiz (%s:%d): %v", targetIP, port, err)
		clientConn.Write([]byte{0x05, 0x04, 0x00, 0x01, 0, 0, 0, 0, 0, 0})
		return
	}

	log.Printf("[PROXY] SOCKS Baglanti kuruluyor: %s:%d ...", host, port)
	dialer := &net.Dialer{Timeout: 5 * time.Second}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	targetConn, err := split.DialWithSplitRetry(ctx, dialer, targetAddr, nil)
	cancel()
	if err != nil {
		log.Printf("[PROXY HATA] SOCKS %s:%d baglantisi basarisiz: %v", host, port, err)
		clientConn.Write([]byte{0x05, 0x03, 0x00, 0x01, 0, 0, 0, 0, 0, 0})
		return
	}
	defer targetConn.Close()

	if _, err := clientConn.Write([]byte{0x05, 0x00, 0x00, 0x01, 0, 0, 0, 0, 0, 0}); err != nil {
		return
	}

	errChan := make(chan error, 2)
	go func() {
		_, err := io.Copy(targetConn, clientConn)
		errChan <- err
	}()
	go func() {
		_, err := io.Copy(clientConn, targetConn)
		errChan <- err
	}()

	<-errChan
}

func main() {
	bindAddr := flag.String("addr", "127.0.0.1:10808", "SOCKS5 proxy bind address")
	httpBind := flag.String("http", "127.0.0.1:10809", "HTTP proxy bind address")
	dnsBind := flag.String("dns", "", "Local DNS proxy bind address")
	dohURL := flag.String("doh", "https://cloudflare-dns.com/dns-query", "DoH Server URL")
	bootstrap := flag.String("bootstrap", "1.1.1.1,1.0.0.1", "Comma separated bootstrap IPs for DoH")
	flag.Parse()

	log.Printf("Starting Jigsaw Intra Windows Backend")
	log.Printf("SOCKS5 Address: %s", *bindAddr)
	log.Printf("HTTP Proxy Address: %s", *httpBind)
	log.Printf("DoH Resolver: %s", *dohURL)
	log.Printf("Bootstrap IPs: %s", *bootstrap)

	bootstrapIPs := strings.Split(*bootstrap, ",")
	for i, ip := range bootstrapIPs {
		bootstrapIPs[i] = strings.TrimSpace(ip)
	}

	dialer := &net.Dialer{Timeout: 5 * time.Second}
	resolver, err := doh.NewResolver(*dohURL, bootstrapIPs, dialer, nil, nil)
	if err != nil {
		log.Fatalf("Failed to initialize DoH Resolver: %v", err)
	}

	// Start yerel DNS sunucusu (if enabled)
	go startDNSProxy(*dnsBind, resolver)

	// Start HTTP Proxy
	go startHTTPProxy(*httpBind, resolver)

	listener, err := net.Listen("tcp", *bindAddr)
	if err != nil {
		log.Fatalf("Failed to listen on %s: %v", *bindAddr, err)
	}
	defer listener.Close()

	log.Printf("Intra SOCKS5 backend listening on %s...", *bindAddr)

	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Failed to accept SOCKS5 connection: %v", err)
			continue
		}
		go handleClient(conn, resolver)
	}
}
