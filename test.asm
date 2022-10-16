$SYMBOL_1 = 137
$MAIN_ADDR = 0x1000

#0x0000
// main code bootlader
init:
  jmp ${MAIN_ADDR}

#0x0010
// some static values at current address [0x0010]
.160
.0xA1
.0xA2
.0xA3
.164

// we can go back to a previous address 
// and overwrite whats in there
// in this case [0x002: 0xA2] => [0x002: 0x00]
#0x0012
.0x00   

// somewhere else in new code segment 
#${MAIN_ADDR}
main:
  // execute some commands
  LDA 0xA
  LDA 0xF0
  LDA 10
  LDA 240
  // we can also use symbols in our code
  LDA ${SYMBOL_1}
  jmp main


#0xff00
exit:
  // execption handler
  jmp main   



