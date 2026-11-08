---
title: "tooooo-fancy-😏"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 1300
techniques: ["reverse-engineering", "encoding", "vm-reverse"]
tools: ["python"]
keywords: ["tooooo-fancy-😏", "Pwny-CTF", "reverse", "reverse-engineering", "encoding", "vm-reverse", "python", "hex"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Rev/tooooo-fancy-😏/notes.md"
---

# tooooo-fancy-😏 (Pwny-CTF, reverse)

## Summary
Challenge **tooooo-fancy-😏** from the Pwny-CTF CTF, reverse category. Main technique: reverse-engineering..tbc -> tbcload/cmpRead.c gives the base85 (little-endian!) alphabet and grammar; the Tcl 8.6 opcode table gives the disassembly. No need to rebuild the runtime just to read.

## Statement and artefacts
I really hope this challenge TiCkLes your fancy! It is my most cursed challenge yet.

**Author**: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 1.7 KB)`
- `work/main.tbc (file, 8.6 KB)`

## Recognition signals
- Signal:.tbc + “TiCkLes” in the statement = Tcl; the file starts with tbcload::bceval { TclPro ByteCode 2 0 1.7 8.6. }. Runtime provided by Dockerfile (ActiveTcl + tbcload from teapot).
- Signal: Indices (Ax / = b) -> linear system. auto_path./tcllib1.18 + package require md5 -> md5 used.
- Signal: Parenthesis trap: condition was (($n+3)$n+1)/2 (= ((n+3)·n+1)//2), not ($n+1). To be checked to the nearest character: this is what makes the positions fall right on 1.1296.

## Resolution method
1. **The program**

```tcl
# flag -> list of char-codes = x
foreach char [split [gets stdin] ""] { lappend input [scan $char "%c"] }
set wtf  {502126 ...}          ;# b  (36 values)
set definitely_not_flag_length 36
# stores wat (1296 values) in variables named by an MD5 HASH STRING:
set set set
foreach wat {254 109 ...} { set set [md5::md5 -hex $set]; set $set $wat }  ;# var(hash#p)=wat[p-1]
set unfanciness 0
for {set n 0} {$n<36} {incr n} {
  set set [md5::md5 -hex set]                          ;# repart position 1
  set epic 0
  for {set k 0} {$k<36} {incr k} {
    if {$k==0} { repeat (($n+3)*$n+1)/2 times: set set [md5 $set] } ;# advance Tn
    set epic [expr "$epic + \$$set * [lindex $input [expr {35-$k}]]"] ;# + coeff*char
    set offset [expr {$n+$k+1}] ; if {$k>=35-$n} {set offset [expr {71-$offset}]}
    repeat $offset times: set set [md5 $set] ;# offset advance
  }
  set unfanciness [expr "$unfanciness | $epic ^ [lindex $wtf $n]"]     ;# |= epic_n ^ b[n]
}
# success if unfanciness==0 (so epic_n == b[n] for all n)
```
The MD5 string is just an **obfuscated counter**: the position `p` ↔ `wat[p-1]`. The feeds (triangular `Tn=((n+3)*n+1)//2` + tenting `offset`) go through positions 1..1296 **exactly** (36×36 readings), forming the matrix `A` (36×36). `epic_n = Σ_k A[n][k]·x[35-k]`.

`A·x = b` square 36×36 → `x = A⁻¹·b` in **exact rationals** (Fraction). We just emulate the position counter (no need for MD5) to recover `A[n][k]=wat[p-1]`, then Gauss. `x` = 36 printable ASCII char-codes.

See `work/solve.py` (`.tbc` decoder + meter emulation + exact resolution, standalone). Runtime check: `tclsh` + `package require md5` on the reconstructed checker.

2. **Recognize**

- `.tbc` + “TiCkLes” in the statement = **Tcl**; the file starts with `tbcload::bceval { TclPro ByteCode 2 0 1.7 8.6... }`. Runtime provided by Dockerfile (ActiveTcl + `tbcload` from teapot).
- Indices `(Ax` / `= b)` → linear system. `auto_path.../tcllib1.18` + `package require md5` → md5 used.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{1_hope_that_tcls_y0ur_f4ncy}

## Lessons and reusable patterns
- .tbc -> tbcload/cmpRead.c gives the base85 (little-endian!) alphabet and grammar; the Tcl 8.6 opcode table gives the disassembly. No need to rebuild the runtime just to read.
- Obfuscation = disguised counter: a hash string h->md5(h) that names variables is just a sequential index; we emulate it with a simple counter (position ↔ value).
- An all-or-nothing “correct/incorrect” checker on a linear system is solved, not brute-forced: extract A and b, solve x=A⁻¹b exactly.
- Parenthesis trap: the condition was (($n+3)$n+1)/2 (= ((n+3)·n+1)//2), not ($n+1). To be checked to the nearest character: this is what makes the positions fall exactly on 1..1296.
