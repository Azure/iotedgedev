const { spawn } = require('child_process');
var kill = require('tree-kill');

var ls = spawn('iothub-explorer', ['monitor-events', '--login', process.argv[2], process.argv[3]], { shell: true }).on('error', function (err) { console.log(err); throw err });

setTimeout(function () { kill(ls.pid) }, process.argv[4])

ls.stdout.on('data', (data) => {
    console.log(`${data}`);
});

ls.stderr.on('data', (data) => {
    console.log(`ERROR: ${data}`);
});

