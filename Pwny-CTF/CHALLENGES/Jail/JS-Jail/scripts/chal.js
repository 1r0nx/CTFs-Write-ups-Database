// JS-Jail — Pwny-CTF (script de solve)
const { exit } = require('node:process');
const readline = require('node:readline');
const fs = require('node:fs');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

const check_chars = (message) => /^[\[\]()!+]+$/.test(message);

const win = () => console.log(fs.readFileSync('/flag.txt', 'utf-8'));

rl.question('I love parenthesis, brackets, exclamation marks and pluses. Give me some... ', message => {
    if (!check_chars(message)) {
        console.log("Hey! I told you what I wanted!");
        exit(1);
    }

    if (eval(message) == "gimme the flag") win();
    rl.close();
})