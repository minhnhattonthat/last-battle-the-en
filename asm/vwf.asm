; vwf.asm: variable-width English text for the bitmap text canvas (docs/re/vwf.md).
; Applied by build.py with asar on the 4 MB image after the text is inserted. Code and font live at $FD:8000+
; (file 0x3E8000; 0x200000-0x3DFFFF is for moved LZ blocks and text). Hook list with reasons: docs/re/vwf.md.
;
; The game draws a 16x16 glyph into a 4-tile 2bpp buffer at $7E2F40 (TL $2F40, TR $2F50, BL $2F60, BR $2F70),
; uploads it to VRAM word $0C30 (top row) and $0C30+$100 (bottom row), and steps 12 px per glyph with $0C24 as an
; even/odd phase. Here $0C24 becomes the pixel offset inside the buffer's left column: a glyph is ORed in at that
; offset, the advance is added, and after the upload (01:B859, now vwf_post) every full 8 px column is shifted out
; and $0C20 (VRAM word address of the left column) steps 8 words. Script words $0800-$087F are English glyphs
; (ASCII = word - $0800, font build/font_en.bin); words $0300-$07FF keep the Japanese font at a 12 px advance.

lorom

!code    = $7EFFF0   ; glyph word being drawn
!lastcol = $7EFFF2   ; $0C20 the buffer was last drawn or shifted for (else the buffer is stale)
!tmp     = $7EFFF4

; ---- hooks ----------------------------------------------------------------------------------------------------
org $01B89B             ; was PLA / SEC / SBC #$0300 (5 bytes): the glyph word -> font address
    jml vwf_fetch
    nop
org $01B8C9             ; was the even/odd x mode dispatch into $2F40 and the 8/16 step of $0C20
    jml vwf_draw
org $01B859             ; was: on an even glyph shift TR->TL, BR->BL; INC $0C24 (runs after the upload)
    jml vwf_post
org $01B13C             ; was LDA $5C / STA $24: start phase of a text run in a window of width $5C
    jsl vwf_start5c
org $01BA96             ; was PHP / REP #$20 / XBA / PHA: script control-word dispatch (words >= $8000)
    jml vm_dispatch
org $01B485             ; was LDA [$10] / CMP #$FF00: the menu string drawer's fetch (01:B467)
    jml menu_fetch
    nop

; ---- code -----------------------------------------------------------------------------------------------------
org $FD8000
vwf_fetch:              ; M=16 X=16 DB=$7E D=$0C00; the glyph word is on the stack
    pla
    sta.l !code
    cmp #$0800
    bcs .en
    sec
    sbc #$0300
    jml $01B8A0         ; Japanese: the game's own fetch, then vwf_draw
.en:
    and #$007F
    asl
    asl
    asl
    asl
    tax
    ldy #$0000
-   lda.l font_en,x     ; two pixel rows at a time into the game's glyph buffer layout (TL rows 0-7, BL rows 8-15)
    sta $2620,y
    lda.l font_en+8,x
    sta $2630,y
    lda #$0000
    sta $2628,y
    sta $2638,y
    inx
    inx
    iny
    iny
    cpy #$0008
    bne -
    ; fall through

vwf_draw:               ; M=16 X=16 DB=$7E D=$0C00; glyph in $7E2620 (TL, TR, BL, BR 1bpp)
    lda $24
    beq .clear
    lda $20
    cmp.l !lastcol
    beq .keep
.clear:
    jsr bgword
    ldx #$003E
-   sta $2F40,x
    dex
    dex
    bpl -
.keep:
    lda $20
    sta.l !lastcol
    ldx #$0000          ; X = pixel row 0-15
.row:
    txa                 ; source: row r of the left half at $2620 + r (+8 for r >= 8), right half 8 bytes on
    cmp #$0008
    bcc +
    adc #$0007          ; carry set: +8
+   tay
    sep #$20
    lda $2620,y
    xba
    lda $2628,y
    rep #$20
    phx
    ldx $24
    beq +
-   lsr
    dex
    bne -
+   plx
    sta.l !tmp          ; high byte -> left column, low byte -> right column (pixels past 16 are clipped)
    txa                 ; dest: 2 bytes per row, BL/BR $20 on
    asl
    cmp #$0010
    bcc +
    adc #$000F          ; carry set: +$10
+   tay
    sep #$20
    lda.l !tmp+1
    ora $2F41,y         ; plane 1 (every mode)
    sta $2F41,y
    lda.l !tmp
    ora $2F51,y
    sta $2F51,y
    rep #$20
    lda $2A
    cmp #$0002
    bne .next
    sep #$20            ; mode 2 inks plane 0 as well (colour 3, clear background)
    lda.l !tmp+1
    ora $2F40,y
    sta $2F40,y
    lda.l !tmp
    ora $2F50,y
    sta $2F50,y
    rep #$20
.next:
    inx
    cpx #$0010
    bne .row
    lda.l !code
    cmp #$0800
    bcs .enw
    lda #$000C          ; Japanese glyph: 12 px
    bra .adv
.enw:
    and #$007F
    tax
    lda.l font_en_widths,x
    and #$00FF
.adv:
    clc
    adc $24
    sta $24
    lda $20
    sta $30             ; upload target: the left column
    jml $01B8F2         ; PLB / PLP / RTS

vwf_post:               ; JSR'd from bank 01 after the upload; returns through 01:B87F (PLB / PLP / RTS)
    php
    phb
    rep #$30
    pea $7E7E
    plb
    plb
.loop:
    lda $24
    cmp #$0008
    bcc .done
    sbc #$0008
    sta $24
    lda $20
    clc
    adc #$0008
    sta $20
    sta.l !lastcol
    jsr bgword
    sta.l !tmp
    ldx #$0000
-   lda $2F50,x
    sta $2F40,x
    lda $2F70,x
    sta $2F60,x
    lda.l !tmp
    sta $2F50,x
    sta $2F70,x
    inx
    inx
    cpx #$0010
    bne -
    bra .loop
.done:
    jml $01B87F

vwf_start5c:            ; M=16: an odd window width started the run on the odd phase (glyph 4 px into the column)
    lda $5C
    and #$0001
    beq +
    lda #$0004
+   sta $24
    lda #$FFFF
    sta.l !lastcol
    rtl

; ---- far jump: word $F700 + 24-bit address (tools/insert.py) --------------------------------------------------
; Moved English strings live in ROM past 0x300000; their slot in the block image or bank 04 holds a far jump there,
; and the moved copy ends with a far jump back. F7 is not in the game's control table (01:BAB5).
vm_dispatch:            ; M=16 X=16 D=$0C00, A = control word, $10-$12 = script pointer after it; JSR'd from 01:B7B9
    pha
    and #$FF00
    cmp #$F700
    beq .far
    pla
    php                 ; the displaced instructions
    rep #$20
    xba
    pha
    jml $01BA9B
.far:
    pla
    jsr far_load
    jml $01E675         ; LDA #$0000 / RTS: keep running

far_load:               ; $10-$12 <- the 24-bit address at [$10]
    ldy #$0002
    lda [$10],y
    and #$00FF
    tax
    lda [$10]
    sta $10
    stx $12
    rts

menu_fetch:             ; M=16 X=16 D=$0C00: next word of a menu string, following far jumps
    lda [$10]
    cmp #$F700
    bne +
    inc $10
    inc $10
    jsr far_load
    bra menu_fetch
+   cmp #$FF00
    jml $01B48A         ; BNE $B490 / end

bgword:                 ; A = the empty-pixel word of text mode $2A (mode 0: plane 0 set)
    lda $2A
    bne +
    lda #$00FF
    rts
+   lda #$0000
    rts

font_en:
    incbin "../build/font_en.bin"
font_en_widths:
    incbin "../build/font_en_widths.bin"
vwf_end:
warnpc $FDFFFF
