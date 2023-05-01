const { spawn } = require('child_process');
const process = require("process");


module.exports.push = async function(labels, information) {
    const child = spawn('smoloki', [JSON.stringify(labels), JSON.stringify(information)]);

    child.stdout.on("data", (x) => {
        process.stdout.write(x.toString());
    });

    child.stderr.on("data", (x) => {
        process.stderr.write(x.toString());
    });

    const exitCode = await new Promise((resolve, reject) => {
        child.on('close', resolve);
    });

    return exitCode;
}
