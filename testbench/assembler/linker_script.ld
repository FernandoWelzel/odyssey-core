ENTRY(main)             /* Entry point is the 'main' function */

SECTIONS {
    . = 0x00000000;     /* Start address of the program */
    .text : {           /* Text section */
        *(.text)        /* Code goes here */
    }

    .data : {           /* Data section */
        *(.data)        /* Initialized data goes here */
    }

    .bss : {            /* BSS section */
        *(.bss)         /* Uninitialized data goes here */
    }
}
