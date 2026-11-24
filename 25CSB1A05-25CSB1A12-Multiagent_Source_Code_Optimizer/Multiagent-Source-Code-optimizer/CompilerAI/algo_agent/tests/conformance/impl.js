function add(a, b) {
    return a + b;
}

function reverse_list(xs) {
    return xs.slice().reverse();
}

function raise_on_negative(x) {
    if (x < 0) throw new RangeError("negative");
    return x;
}

function mutates_argument(xs) {
    xs.push(99);
    return xs.length;
}

function prints_text(s) {
    console.log(s);
    return s;
}

function infinite_loop(x) {
    while (true) { x++; }
}

function crashes_hard(x) {
    process.exit(139);
}

function returns_special_values(x) {
    return [NaN, -0, undefined, 1000000000000000000000000000000n];
}
