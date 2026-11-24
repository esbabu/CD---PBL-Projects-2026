function contains(items, target) {
    for (const item of items) {
        if (item === target) {
            return true;
        }
    }
    return false;
}

const values = [4, 8, 15, 16, 23, 42];
console.log(contains(values, 15));
