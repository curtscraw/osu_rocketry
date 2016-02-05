import Adafruit_BBIO.UART as UART

#enable all relevant UART ports for gps and xbee
UART.setup("UART1")   #xbee
UART.setup("UART2")   #gps
