---
title: "Your First Mission"
ctf: "2025_SADC-NextGenCyber-CTF"
category: "Misc"
difficulty: "Not specified"
points: 0
techniques: []
tools: []
keywords: []
status: "solved"
has_script: false
source: "2025_SADC-NextGenCyber-CTF/Misc/Your First Mission.md"
---

## Summary

Challenge **Your First Mission** from the 2025_SADC-NextGenCyber-CTF CTF, misc category.

## Statement and artefacts

See the original challenge files; provided artefacts are not copied.

## Recognition signals

- (see resolution method below)

## Resolution method


# **First Mission**

**file flag.png**
Check the real type of the file *flag.png* (here you discover it’s actually a disguised ZIP archive).

**`unzip flag.png -d flag_unzipped`**
Extract the archive into the *flag_unzipped* directory.

**`cd flag_unzipped/flag/`**
Move into the folder containing the extracted files.

**`ls -la`**
List all files (including hidden ones) with their permissions and sizes — to see exactly what’s inside.

**`cat MAPPING_20251030_103836.txt`**
Display the mapping file that tells which randomized image corresponds to which original name (member01.jpg, etc.).

---

```sh
chmod +x rename_script.sh
./rename_script.sh
```

Here is the script:

```sh
#!/bin/bash

# Name of the mapping file
MAPPING_FILE="MAPPING_20251030_103836.txt"

# Check if the mapping file exists
if [ ! -f "$MAPPING_FILE" ]; then
    echo "Error: Mapping file '$MAPPING_FILE' not found."
    exit 1
fi

echo "--- Starting Reverse Renaming ---"

# Read the file line by line
# The script ignores lines starting with '#' (comments) or empty lines
while IFS=" " read -r old_name arrow new_name
do
    # Ignore empty lines or comments
    if [[ "$old_name" =~ ^#.* ]] || [[ -z "$old_name" ]]; then
        continue
    fi

    # Make sure both names are present (old and new)
    if [ -n "$old_name" ] && [ -n "$new_name" ]; then
        
        # Reverse renaming goes from $new_name (existing file) to $old_name (desired name)
        if [ -f "$new_name" ]; then
            mv "$new_name" "$old_name"
            echo "Renaming: $new_name -> $old_name"
        else
            echo "WARNING: File '$new_name' is missing and cannot be renamed."
        fi
    fi

done < "$MAPPING_FILE"

echo "--- Renaming Completed ---"
```

It uses the mapping file to automatically rename each randomized file back to its original name (memberXX). Handy when dealing with lots of files.

---

**`tail -c 10 member01.jpg | xxd`**
Display the last 10 bytes of *member01.jpg* in hexadecimal to identify the CHUNK_01 marker and the hidden 4 bytes.

**`pngcheck -v member16.png`**
Check the structure of the PNG and see if there’s any extra data after the IEND chunk.

**`grep -oba "IEND" member16.png`**
Example output: `6548:IEND` — this gives the offset where the IEND sequence appears in the PNG, useful for extracting what comes after.

**`dd if=member16.png bs=1 skip=$((0x1998)) of=png_trailer.bin`**
Extract the bytes that follow IEND (using the calculated offset) and save them to *png_trailer.bin* — that’s where CHUNK_16 is located.

**`xxd png_trailer.bin`**
Display the extra extracted content to confirm it contains CHUNK_16 + 4 hidden bytes.

---

**flag_complete.bin**
Create/truncate an empty *flag_complete.bin*, which will contain all the assembled data.

```sh
for i in $(seq -f "%02g" 1 15); do tail -c 4 member${i}.jpg >> flag_complete.bin; done
```

Loop that takes the last 4 bytes of each *member01.jpg* → *member15.jpg* (the 4 hidden bytes after each CHUNK_XX) and concatenates them into *flag_complete.bin*.

**`tail -c 4 png_trailer.bin >> flag_complete.bin`**
Append the 4 bytes from CHUNK_16 (extracted from the PNG) to complete the 64-byte encrypted blob.

**`xxd flag_complete.bin`**
Display the hexadecimal content of the assembled file to confirm the 64 bytes are correct.

---

**`KEY="Southern African Development Community"`**
Declare the passphrase used to derive the encryption key.

**`KEY_HEX=$(echo -n "$KEY" | openssl dgst -sha256 -binary | xxd -p -c 64 | cut -c1-48)`**
Generate the 3DES key: compute the SHA256 (binary) of the passphrase, convert to hex, then keep the first 48 hex chars (24 bytes) — the key for 3DES-EDE3.

**`openssl enc -d -des-ede3 -in flag_complete.bin -K "$KEY_HEX" -iv 0000000000000000 2>/dev/null`**
Decrypt *flag_complete.bin* using 3DES-EDE3 in ECB (zero IV).
If everything was done correctly, this outputs the flag in plaintext.


## Flag

Not specified

## Lessons and reusable patterns

- (see resolution method above)
