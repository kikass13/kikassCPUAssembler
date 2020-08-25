$SYMBOL_1 = 137

#0x0000
// some static values at current address [0x0000]
.160
.0xA1
.0xA2
.0xA3
.164

// we can go back to a previous address 
// and overwrite whats in there
// in this case [0x002: 0xA2] => [0x002: 0x00]
#0x0002
.0x00   

// somewhere else in new code segment 
#0x0010
// declare label for jumps
main:
  // execute some commands
  LDA 0xA
  LDA 0xF0
  LDA 10
  LDA 240
  // we can also use symbols in our code
  LDA ${SYMBOL_1}


