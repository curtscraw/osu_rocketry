import Adafruit_BBIO.UART as UART

print "Initialize UART1 for XBEE"
UART.setup("UART1")

print "Initialize UART2 for GPS"
UART.setup("UART2")
