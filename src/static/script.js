document.addEventListener("DOMContentLoaded", function() {
    const upButton = document.getElementById("up-button");
    const downButton = document.getElementById("down-button");
    const heightDisplay = document.getElementById("height-display");

    upButton.addEventListener("click", function() {
        sendCommand("up");
    });

    downButton.addEventListener("click", function() {
        sendCommand("down");
    });

    function sendCommand(command) {
        fetch("/command", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                console.log(`Command ${command} executed successfully.`);
            } else {
                console.error(`Failed to execute command: ${data.message}`);
            }
        });
    }

    function updateHeight() {
        fetch("/height")
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                heightDisplay.textContent = `Height: ${data.height}`;
            } else {
                heightDisplay.textContent = "Height: --";
                console.error(`Failed to get height: ${data.message}`);
            }
        });
    }

    setInterval(updateHeight, 1000);
});
