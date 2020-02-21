var readline = require('readline');
var rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});
var n=0;
var end =0;
var mod=1
var add=0

rl.on('line', function(line){
    if (n<=0){
        n=parseInt(line, 10);
        return
    }
    l=parseInt(line)
    add+=l
    if (mod%2==0){
        console.log(add)
        add=0
        end+=1
    }
    mod+=1
    if (end>=n){
        process.exit(0);
    }
})
