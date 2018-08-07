const { spawn } = require('child_process');

var ls = spawn('iothub-explorer', ['monitor-events', '--login', process.argv[2], process.argv[3], '--duration', process.argv[4]], { shell: true }).on('error', function (err) { console.log(err); throw err });

ls.stdout.on('data', (data) => {
    console.log(`${data}`);
});

ls.stderr.on('data', (data) => {
    console.log(`ERROR: ${data}`);
});

