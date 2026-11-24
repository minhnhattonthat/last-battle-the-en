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
org $01FEF2             ; was LDA $6D80,x / AND #$00FF: byte name -> glyph words (01:FEE3)
    jml nm_fee3
    nop
    nop
org $01FEB9             ; was LDA $6D80,x / AND #$00FF: byte name -> BG3 tile words (01:FEAA)
    jml nm_feaa
    nop
    nop
org $01F3C3             ; was LDA #$007E / STA $16 / LDA #$6C80 / STA $14 / LDA #$0008 before JSR $B6FA / RTS:
    jsl nm_f3c3         ; 01:F3C0's name field width per list (nm_icap); F3CB-F3D3 are left unreachable
    jsr $B6FA
    rts
org $02D7A8             ; was LDA [$B2],y / CMP #$FE00: the staff roll's fetch (02:D789)
    jml cr_fetch
    nop
org $02D7F9             ; was PHA / LDA $1A8015 (5 bytes): the staff roll's glyph draw (bank-02 renderer)
    jml cr_glyph
    nop
org $29B2B6             ; was PHY / STA $3C / LDA [$30]: battle name -> two BG3 tile rows (enemy, spell, tactics)
    jml bt_name
    nop
org $3C8041             ; victory line: was a forward scan of the name's bottom row for its first space ($2093),
    ldx #$011C          ; which hits the leading space of a centred English name ("s defeated!" over "Slime").
-   dex                 ; Now: back from past column 7 to the last non-space; the suffix starts right after it.
    dex                 ; Same 16 bytes; 3C:8051 LDA #$000B / JSR $805C follow unchanged.
    lda $7EB800,x
    cmp #$2093
    beq -
    inx
    inx

; battle VWF (tools/bvwf.py, docs/re/battle.md §Battle VWF): English battle text redrawn in proportional type
org $29A278             ; was LDA $34 / STA $34: start of 29:A249's copy loop (window scripts, 29:A1EA)
    jml bv_copy
org $3C8057             ; was JSL $30F28C after the victory line (name rows + suffix in tilemap rows 3-4)
    jsl bv_victory
org $30AE2E             ; was JSL $30F28C after the item-found line (rows 11-12)
    jsl bv_found
org $30F242             ; was LDA $0000,x / STA $34: rectangle copier for 7-byte records (escape messages)
    jml bv_rectcopy
org $28FC08             ; upload descriptors read by the NMI queue 2A:989A with DB = $28 (VRAM word, source, size);
bv_desc:                ; zero filler in the original
    !i = 0
    while !i < 7
        dw $6000+(($011A+(!i*16))*8)
        dl $7FD800+(!i*256)
        if !i == 6
            dw (102-96)*16
        else
            dw 256
        endif
        !i #= !i+1
    endwhile

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

; ---- English byte names (docs/re/vwf.md §Names) -----------------------------------------------------------------
; A name field (item and spell records, 8 bytes) starting with a kind byte $01-$0F (never a name byte: the maps start
; at $2C) is followed by an index n; the English name is ASCII at the word pointer NM_PTRS[(kind-1)*256 + n] in bank
; $FC, written by tools/insert.py with the ASCII -> BG3 tile table NM_BG3. No length limit from the record.
!NM_BG3  = $FC8000
!NM_PTRS = $FC8100

nm_fee3:                ; M=16 X=16 DB=$7E; stack: count, X; X = byte index in $6D80, Y = word offset in $6C80
    lda $6D80,x
    and #$00FF
    cmp #$0010
    bcs .norm
    cmp #$0000
    beq .end
    phx                 ; index of the kind byte
    jsr nm_ptr
-   lda.l $FC0000,x
    and #$00FF
    beq .rank
    ora #$0800          ; English glyph word
    sta $6C80,y
    iny
    iny
    inx
    bra -
.rank:                  ; a capital after the escape (`kind, n, RANK`: spell rank in a character record) -> " RANK"
    plx
    lda $6D82,x
    and #$00FF
    cmp #$0041
    bcc .end
    cmp #$005B
    bcs .end
    ora #$0800
    pha
    lda #$0820
    sta $6C80,y
    pla
    sta $6C82,y
    iny
    iny
    iny
    iny
.end:
    jml $01FF11         ; PLX / PLA / FF00 end / return
.norm:
    jml $01FEFA         ; the game's map at $04:B053

nm_feaa:                ; as nm_fee3, for the BG3 tile map ($04:AEAB)
    lda $6D80,x
    and #$00FF
    cmp #$0010
    bcc +
    jml $01FEC1         ; the game's map (.norm, out of branch range)
+   cmp #$0000
    bne +
    jml $01FED8         ; .end
+   pha
    lda 5,s             ; the caller's count (stack: kind, X, count): the BG3 field is that many tiles
    sta.l !tmp
    lda 9,s             ; return address of the JSR $FEAA
    cmp #$FC70          ; 01:FC55 = the FA18 handler only (op table 01:E6A9): item name in a BG3 message, 9 (D18)
    bne .icap
    lda #$0009
    sta.l !tmp
    bra +
.icap:
    cmp #$FE76          ; 01:FE59: item record names, drawn by 01:F3C0 in a field nm_icap sizes per list
    bne +
    lda 15,s            ; return into 01:F3C0's caller
    jsr nm_icap
    sta.l !tmp
+   pla
    phx                 ; index of the kind byte
    jsr nm_ptr
-   lda.l !tmp
    beq .full
    lda.l $FC0000,x
    and #$007F
    beq .rank
    phx
    asl
    tax
    lda.l !NM_BG3,x
    plx
    sta $6C80,y
    lda.l !tmp
    dec
    sta.l !tmp
    iny
    iny
    inx
    bra -
.full:
    plx
    bra .end
.rank:                  ; as nm_fee3: " RANK" after the name while the field has room (!tmp tiles left)
    plx
    lda $6D82,x
    and #$00FF
    cmp #$0041
    bcc .end
    cmp #$005B
    bcs .end
    asl
    tax
    lda.l !tmp
    cmp #$0002
    bcc .end
    lda.l !NM_BG3+$40   ; ASCII space
    sta $6C80,y
    lda.l !NM_BG3,x
    sta $6C82,y
    iny
    iny
    iny
    iny
.end:
    jml $01FED8
.norm:
    jml $01FEC1

; Item record name fields (01:F3C0, called by the list ops below; docs/re/windows.md). The game draws every list
; with 8 tiles; nm_icap gives each list its own width, and lists with a space before each name hand that space to
; the name (01:B6FA starts the field at the VM position $20, so the field ends where the 8 tiles did).
nm_f3c3:                ; M=16; stack: RTL(3), return into F3C0's caller (4,s)
    lda #$007E
    sta $16
    lda #$6C80
    sta $14
    lda 4,s
    jsr nm_icap
    bcc +
    dec $20
    dec $20
+   rtl

nm_icap:                ; A = return address into F3C0's caller -> A = field tiles, carry set = take the space before
    phx
    sta.l !tmp
    ldx #$0000
-   lda.l .tab,x
    beq .none
    cmp.l !tmp
    beq .hit
    inx
    inx
    inx
    inx
    bra -
.none:
    lda #$0008
    clc
    plx
    rts
.hit:
    lda.l .tab+2,x
    cmp #$8000          ; carry = $8000 flag
    and #$00FF
    plx
    rts
.tab:                   ; return address, tiles | $8000 when the script puts a space before the name
    dw $EE73, $8009     ; FA09: space, name (window 9 wide)
    dw $EEB9, $8009     ; FA16: cursor, space, name (10)
    dw $F385, $8009     ; FA11: 2 x (cursor, space, name, space) (21)
    dw $F3B2, $0009     ; FA0E: 2 x (space, name) (20, widened by insert.WINDOW_HEADERS): field item windows; the space is the cursor's
    dw $F2EB, $0009     ; FA3C: shop buy list, cursor, name, then the price (it follows the name: 9 is the most)
    dw $F331, $0009     ; FA4B: cursor, name (18)
    dw $0000

; Battle names (docs/re/battle.md): 29:B2B6 writes A (= 8) tile pairs, the top row (dakuten in Japanese) to [$34] and
; the bottom row to [$38]. An English escape draws the name's battle form instead: two 8-char ASCII rows laid out by
; tools/insert.py (battle_rows; long names use both rows), the second form when the field holds a rank capital.
!BT_PTRS = $FC9100      ; NM_PTRS + 2 * 256 * NAME_KINDS_MAX (8)

bt_name:                ; M=16 X=16; A = tile count, [$30] = name field, [$34] / [$38] = top / bottom tile rows
    phy
    sta $3C
    lda [$30]
    and #$00FF
    beq .orig
    cmp #$0010
    bcc .en
.orig:
    jml $29B2B9         ; the game's loop (LDA [$30] ...)
.en:
    dec
    xba                 ; (kind - 1) * 256
    sep #$20
    ldy #$0001
    lda [$30],y         ; + n
    rep #$20
    asl
    tax
    lda.l !BT_PTRS,x
    tax                 ; X = battle form in bank $FC
    ldy #$0002
    lda [$30],y
    and #$00FF
    cmp #$0041
    bcc .draw
    cmp #$005B
    bcs .draw
    sta.l !tmp          ; rank capital: the form with " RANK"
    txa
    clc
    adc #$0010
    tax
.draw:
-   lda.l $FC0000,x
    jsr bt_tile
    sta [$34]
    lda.l $FC0008,x
    jsr bt_tile
    sta [$38]
    inx
    inc $30
    inc $34
    inc $34
    inc $38
    inc $38
    dec $3C
    bne -
    jml $29B307         ; PLY / RTS

bt_tile:                ; A low byte = ASCII (1 = the rank in !tmp) -> BG3 tile word with the battle palette $2000
    and #$00FF
    cmp #$0001
    bne +
    lda.l !tmp
+   phx
    asl
    tax
    lda.l !NM_BG3,x
    plx
    and #$03FF
    ora #$2000
    rts

nm_ptr:                 ; A = kind 1-15, X = index of the kind byte -> X = address of the ASCII name in bank $FC
    dec
    xba
    sep #$20
    lda $6D81,x
    rep #$20
    asl
    tax
    lda.l !NM_PTRS,x
    tax
    rts

; ---- staff roll (bank 02, docs/re/vwf.md §Staff roll) -------------------------------------------------------------
; The staff roll draws each line into a 2bpp tile image at $7E6C80 (16 tiles per row, $10 bytes per tile, the bottom
; half of a 16 px line $100 further on), X = byte offset of the current tile column, $B8 = phase. Japanese glyphs keep
; the game's 12 px packing (bit 0 of $B8 = the column's left 4 px are used). English glyphs are ORed in at pixel P of
; column X, P = 4 if bit 0 of $B8 is set, else $B8 / 2; afterwards $B8 = P * 2.
!crP   = $7EFFF6
!crX   = $7EFFF8
!crX2  = $7EFFFA
!crSrc = $7EFFFC

cr_fetch:               ; M=16 X=16, [$B2],y = next word; far jumps followed here
    lda [$B2],y
    cmp #$F700
    bne +
    iny
    iny
    lda [$B2],y         ; low word of the target
    pha
    iny
    iny
    lda [$B2],y
    and #$00FF
    sta $B4
    pla
    sta $B2
    ldy #$0000
    bra cr_fetch
+   cmp #$FE00
    jml $02D7AD         ; BEQ newline / CMP #$FF00 ...

cr_glyph:               ; M=16 X=16, A = glyph word, X = tile column; JSR'd from 02:D7B5, returns X = next column
    cmp #$0800
    bcs .en
    pha                 ; the displaced instructions, then the game's Japanese draw
    lda.l $1A8015
    jml $02D7FE
.en:
    and #$007F
    sta.l !code
    asl
    asl
    asl
    asl
    sta.l !crSrc
    lda $B8
    lsr
    bcc +
    lda #$0004
+   sta.l !crP
    txa
    sta.l !crX
    jsr cr_next
    sta.l !crX2
    ldy #$0000          ; Y = pixel row 0-15
.row:
    tya
    clc
    adc.l !crSrc
    tax
    lda.l font_en,x
    and #$00FF
    xba
    sta.l !tmp
    lda.l !crP
    tax
    lda.l !tmp
    cpx #$0000
    beq +
-   lsr
    dex
    bne -
+   sta.l !tmp          ; high byte -> column X, low byte -> the next column
    tya                 ; row offset: 2 bytes per row, rows 8-15 in the tile row below ($100 on)
    asl
    cmp #$0010
    bcc +
    adc #$00EF          ; carry set: +$F0
+   pha
    clc
    adc.l !crX
    tax
    sep #$20
    lda.l !tmp+1
    ora.l $7E6C80,x
    sta.l $7E6C80,x
    rep #$20
    pla
    clc
    adc.l !crX2
    tax
    sep #$20
    lda.l !tmp
    ora.l $7E6C80,x
    sta.l $7E6C80,x
    rep #$20
    iny
    cpy #$0010
    bne .row
    lda.l !code
    tax
    lda.l font_en_widths,x
    and #$00FF
    clc
    adc.l !crP
-   cmp #$0008
    bcc +
    sbc #$0008
    sta.l !crP
    lda.l !crX
    tax
    jsr cr_next
    sta.l !crX
    lda.l !crP
    bra -
+   asl
    sta $B8
    lda.l !crX
    tax
    jml $02D7F8         ; RTS in bank 02

cr_next:                ; A = the tile column after column X (the game's wrap: low byte 0 -> skip $110)
    txa
    clc
    adc #$0010
    bit #$00FF
    bne +
    clc
    adc #$0110
+   rts

bgword:                 ; A = the empty-pixel word of text mode $2A (mode 0: plane 0 set)
    lda $2A
    bne +
    lda #$00FF
    rts
+   lda #$0000
    rts

; ---- battle VWF (tools/bvwf.py, docs/re/battle.md §Battle VWF) ------------------------------------------------------
; English runs in a tilemap rectangle are redrawn proportionally on canvas tiles BG3 $11A-$17F (free in battle VRAM).
; A canvas tile is in use while the cell it was written to still shows it (bv_free), so tiles come back by themselves
; when a window is redrawn or cleared. Tile images are kept in a WRAM shadow and uploaded in 16-tile chunks through
; the game's NMI VRAM queue ($11E7 head, $11E9 tail, $11EB pointers; descriptors bv_desc in bank $28).
!BV_BASE  = $011A
!BV_N     = 102
!bvShadow = $D800       ; the bv_ routines run with DB = $7F: $7F:D800 102 tiles x 16 bytes (plane 0 $FF, plane 1 ink)
!bvOwner  = $DE60       ; 102 words: tilemap address ($7E:B800-BFFF) of the cell each canvas tile was written to
!bvBuf    = $DF40       ; render buffer: 8 rows x 40 bytes, one plane-1 byte per tile column
!bvNext   = $E080       ; next-fit allocation index
!bvDirty  = $E082       ; chunks to upload (bit n = tiles 16n..16n+15)
!bvRow    = $E084       ; tilemap address of the current row
!bvW      = $E086
!bvH      = $E088
!bvI      = $E08A       ; cell index in the row
!bvStart  = $E08C       ; run: first cell
!bvLast   = $E08E       ; run: last text cell
!bvLen    = $E090       ; run: chars in bvStr
!bvAttr   = $E092       ; run: attribute bits of its first tile
!bvPx     = $E094
!bvK      = $E096       ; canvas tiles the run needs
!bvN      = $E098       ; cells the run covers
!bvCol    = $E09A
!bvT      = $E09C
!bvCell   = $E09E
!bvTmp    = $E0A0
!bvCnt    = $E0A2
!bvCh     = $E0A4
!bvSh     = $E0A6
!bvB      = $E0A8
!bvY      = $E0AA
!bvStr    = $E0C0       ; 32 chars
!bvParD   = $7FE0E0     ; parameters saved by the hooks (long: the caller's DB)
!bvParW   = $7FE0E2
!bvParH   = $7FE0E4
!bvParS   = $7FE0E6
!bvParSB  = $7FE0E8

bv_copy:                ; JML from 29:A278; M=16 X=16: $34 = dest ($7E), [$38] = source, X = width, Y = height
    lda $34
    sta.l !bvParD
    lda $38
    sta.l !bvParS
    lda $3A
    sta.l !bvParSB
    txa
    sta.l !bvParW
    tya
    sta.l !bvParH
    lda $34
.row:                   ; the game's loop (29:A27A-A294)
    sta $34
    pha
    phx
.cell:
    lda [$38]
    inc $38
    inc $38
    sta [$34]
    inc $34
    inc $34
    dex
    bne .cell
    plx
    pla
    clc
    adc #$0040
    dey
    bne .row
    lda.l !bvParS       ; ROM sources only: WRAM rectangles hold names and numbers put together by code
    bpl .out
    lda.l !bvParSB
    and #$00FE
    cmp #$007E
    beq .out
    jsr bv_params
.out:
    jml $29A296         ; PLY / RTS

bv_rectcopy:            ; JML from 30:F242 (RTL'd): X = 7-byte record in bank DB: dest, src24, w, h
    lda $0000,x
    sta $34
    lda #$007E
    sta $36
    sta $3A
    lda $0002,x
    sta $30
    lda $0004,x
    and #$00FF
    sta $32
    lda $0005,x
    and #$00FF
    sta $10
    lda $0005,x
    xba
    and #$00FF
    tay
    lda $34
    sta.l !bvParD
    lda $10
    sta.l !bvParW
    tya
    sta.l !bvParH
.row:                   ; the game's loop (30:F26B-F289)
    ldx $10
    lda $34
    sta $38
.cell:
    lda [$30]
    inc $30
    inc $30
    sta [$38]
    inc $38
    inc $38
    dex
    bne .cell
    lda $34
    clc
    adc #$0040
    sta $34
    dey
    bne .row
    jsr bv_params
    rtl

bv_params:
    lda.l !bvParW
    tax
    lda.l !bvParH
    tay
    lda.l !bvParD
    jsl bvwf_rect
    rts

bv_victory:             ; JSL from 3C:8057: the name rows and the suffix (row 3-4 from column 6), then JSL $30F28C
    php
    rep #$30
    pha
    phx
    phy
    lda #$B8CC
    ldx #$0015
    ldy #$0002
    jsl bvwf_rect
    ply
    plx
    pla
    plp
    jml $30F28C

bv_found:               ; JSL from 30:AE2E: "<item> found!" (rows 11-12 from column 7), then JSL $30F28C
    php
    rep #$30
    pha
    phx
    phy
    lda #$BACE
    ldx #$0011
    ldy #$0002
    jsl bvwf_rect
    ply
    plx
    pla
    plp
    jml $30F28C

bvwf_rect:              ; A = tilemap address of a rectangle ($7E:B800+), X = width, Y = height; keeps P and DB
    php
    rep #$30
    phb
    pha
    pea $7F7F
    plb
    plb
    pla
    sta !bvRow
    stx !bvW
    sty !bvH
    cpx #$0021          ; a row is at most 32 cells
    bcs .done
    cpy #$0000
    beq .done
.row:
    stz !bvI
.scan:
    lda !bvI
    cmp !bvW
    bcs .nextrow
    jsr bv_char
    beq .skip
    cmp #$0020
    beq .skip
    jsr bv_run
    bra .scan
.skip:
    inc !bvI
    bra .scan
.nextrow:
    lda !bvRow
    clc
    adc #$0040
    sta !bvRow
    dec !bvH
    bne .row
    jsr bv_flush
.done:
    plb
    plp
    rtl

bv_run:                 ; a run starts at cell bvI: collect it, draw it, continue after its last text cell
    lda !bvI
    sta !bvStart
    sta !bvLast
    lda !bvTmp
    and #$FC00
    sta !bvAttr
    stz !bvLen
.collect:
    jsr bv_char
    beq .endrun
    cmp #$0020
    bne .put
    lda !bvI            ; a space belongs to the run only before more text
    inc
    cmp !bvW
    bcs .endrun
    sta !bvI
    jsr bv_char
    sta !bvCh
    dec !bvI
    lda !bvCh
    beq .endrun
    cmp #$0020
    beq .endrun
    lda #$0020
.put:
    ldx !bvLen
    cpx #$0020
    bcs .endrun
    sep #$20
    sta !bvStr,x
    rep #$20
    inx
    stx !bvLen
    cmp #$0020
    beq +
    ldx !bvI
    stx !bvLast
+   inc !bvI
    lda !bvI
    cmp !bvW
    bcc .collect
.endrun:
    jsr bv_render
    lda !bvLast
    inc
    sta !bvI
    rts

bv_char:                ; A = ASCII of cell bvI in row bvRow (0, Z set = not text); bvTmp = its tile word
    lda !bvI
    asl
    clc
    adc !bvRow
    tax
    lda.l $7E0000,x
    sta !bvTmp
    and #$03FF
    cmp #$0100
    bcs .no
    tax
    lda.l bv_chars,x
    and #$00FF
    rts
.no:
    lda #$0000
    rts

bv_render:              ; draw bvStr over cells bvStart..bvLast of row bvRow on canvas tiles; the rest become spaces
    lda !bvLen
    bne +
    rts
+   lda !bvLast
    sec
    sbc !bvStart
    inc
    sta !bvN
    stz !bvPx
    ldy #$0000
-   lda !bvStr,y
    and #$00FF
    tax
    lda.l bv_widths-$20,x
    and #$00FF
    clc
    adc !bvPx
    sta !bvPx
    iny
    cpy !bvLen
    bcc -
    lda !bvPx
    clc
    adc #$0007
    lsr
    lsr
    lsr
    cmp !bvN
    bcc +
    lda !bvN            ; wider than its cells: clipped (tools/bvwf.py overflow() keeps the script clear of it)
+   sta !bvK
    jsr bv_count
    bcs +
    rts                 ; canvas full: the run keeps its fixed-width tiles
+   ldx #$013E
-   stz !bvBuf,x
    dex
    dex
    bpl -
    stz !bvPx
    ldy #$0000
.glyph:
    lda !bvPx
    lsr
    lsr
    lsr
    cmp !bvK
    bcs .tiles
    sta !bvB            ; buffer index of row 0
    lda !bvPx
    and #$0007
    sta !bvSh
    lda !bvStr,y
    and #$00FF
    sec
    sbc #$0020
    sta !bvCh
    asl
    asl
    asl
    tax
    lda #$0008
    sta !bvY
.grow:
    lda.l bv_font,x
    and #$00FF
    xba
    phx
    ldx !bvSh
    beq +
-   lsr
    dex
    bne -
+   xba                 ; low byte = this tile column, high byte = the next
    ldx !bvB
    ora !bvBuf,x
    sta !bvBuf,x
    txa
    clc
    adc #$0028
    sta !bvB
    plx
    inx
    dec !bvY
    bne .grow
    ldx !bvCh
    lda.l bv_widths,x
    and #$00FF
    clc
    adc !bvPx
    sta !bvPx
    iny
    cpy !bvLen
    bcc .glyph
.tiles:
    stz !bvCol
.tile:
    lda !bvCol
    cmp !bvK
    bcs .pad
    jsr bv_alloc
    sta !bvT
    lda !bvStart
    clc
    adc !bvCol
    asl
    clc
    adc !bvRow
    sta !bvCell
    lda !bvT
    asl
    tax
    lda !bvCell
    sta !bvOwner,x
    lda !bvT
    clc
    adc.w #!BV_BASE
    ora !bvAttr
    ldx !bvCell
    sta.l $7E0000,x
    lda !bvT
    asl
    asl
    asl
    asl
    tax
    ldy !bvCol
    lda #$0008
    sta !bvY
-   lda !bvBuf,y
    xba
    ora #$00FF          ; plane 0 = background colour 1, plane 1 = ink (colour 3)
    sta !bvShadow,x
    inx
    inx
    tya
    clc
    adc #$0028
    tay
    dec !bvY
    bne -
    lda !bvT
    lsr
    lsr
    lsr
    and #$00FE          ; (tile / 16) * 2
    tax
    lda.l bv_bits,x
    ora !bvDirty
    sta !bvDirty
    inc !bvCol
    bra .tile
.pad:
    lda !bvCol
    cmp !bvN
    bcs .done
    lda !bvStart
    clc
    adc !bvCol
    asl
    clc
    adc !bvRow
    tax
    lda !bvAttr
    ora #$0093
    sta.l $7E0000,x
    inc !bvCol
    bra .pad
.done:
    rts

bv_count:               ; carry set if at least bvK canvas tiles are free
    lda !bvK
    beq .yes
    sta !bvCnt
    ldy #$0000
-   jsr bv_free
    bcc +
    dec !bvCnt
    beq .yes
+   iny
    cpy.w #!BV_N
    bcc -
    clc
    rts
.yes:
    sec
    rts

bv_free:                ; carry set if canvas tile Y is free (its cell shows something else); keeps Y
    tya
    asl
    tax
    lda !bvOwner,x
    and #$07FE
    ora #$B800
    tax
    lda.l $7E0000,x
    and #$03FF
    sta !bvTmp
    tya
    clc
    adc.w #!BV_BASE
    cmp !bvTmp
    beq .used
    sec
    rts
.used:
    clc
    rts

bv_alloc:               ; A = a free canvas tile, next-fit (bv_count made sure there is one)
    ldy !bvNext
-   cpy.w #!BV_N
    bcc +
    ldy #$0000
+   jsr bv_free
    iny                 ; (keeps carry)
    bcc -
    sty !bvNext
    dey
    tya
    rts

bv_flush:               ; queue the dirty chunks on the NMI's VRAM queue (as 30:F28C queues the tilemap)
    ldy #$0000
.chunk:
    lda !bvDirty
    and #$007F
    beq .done
    lsr
    sta !bvDirty
    bcc .next
    tya
    asl
    tax
    lda.l bv_descp,x
    pha
    lda.l $7E11E7
    and #$003F
    asl
    tax
    pla
    sta.l $7E11EB,x
    lda.l $7E11E7
    inc
    sta.l $7E11E7
.next:
    iny
    bra .chunk
.done:
    stz !bvDirty
    rts

bv_descp:
    dw bv_desc, bv_desc+7, bv_desc+14, bv_desc+21, bv_desc+28, bv_desc+35, bv_desc+42
bv_bits:
    dw $0001, $0002, $0004, $0008, $0010, $0020, $0040, $0080
bv_chars:
    incbin "../build/bvwf_chars.bin"
bv_widths:
    incbin "../build/bvwf_widths.bin"
bv_font:
    incbin "../build/bvwf_font.bin"

font_en:
    incbin "../build/font_en.bin"
font_en_widths:
    incbin "../build/font_en_widths.bin"
vwf_end:
warnpc $FDFFFF
