package main
import (
	"fmt"
	"strconv"
	"strings"
	"bufio"
	"os"
)

func main() {
	reader := bufio.NewReader(os.Stdin)
	text, _ := reader.ReadString('\n')
	text = strings.Replace(text, "\n", "", -1)
	n,_:=strconv.ParseInt(text,10,64)
	for i:=0;i<int(n);i++ {
		line, _ := reader.ReadString('\n')
		line = strings.Replace(line, "\n", "", -1)
		a,_:=strconv.ParseInt(line,10,64)

		line, _ = reader.ReadString('\n')
		line = strings.Replace(line, "\n", "", -1)
		b,_:=strconv.ParseInt(line,10,64)
		fmt.Println(a+b)
	}
}

