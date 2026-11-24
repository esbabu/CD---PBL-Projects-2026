const fs = require('fs');
const data = fs.readFileSync(0, 'utf8').trim().split(/\s+/).map(Number);
let total = 0;
for (const x of data) total += x;
console.log(total);
