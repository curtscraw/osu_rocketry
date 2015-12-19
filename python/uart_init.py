import Adafruit_BBIO.UART as UART

def init_uart1( ):
	"initialize the BBB UART1 interface for the GPS"
	UART.setup("UART1")

