let countdownInterval;

// Start polling for door status
window.addEventListener('DOMContentLoaded', () => {
    updateDoorStatus();
    setInterval(updateDoorStatus, 1000);
});

async function updateDoorStatus() {
    try {
        let response = await fetch("/status");
        let result = await response.json();
        updateUI(result.status);
    } catch (error) {
        console.error("Error fetching door status:", error);
    }
}

function updateUI(status) {
    const doorStatus = document.getElementById("door-status");
    const statusText = document.getElementById("status-text");
    
    if (status === "unlocked") {
        doorStatus.className = "unlocked";
        statusText.innerText = "ĐÃ MỞ";
    } else {
        doorStatus.className = "locked";
        statusText.innerText = "KHOÁ";
        
        // Hide countdown if door is locked
        document.getElementById("countdown").classList.add("hidden");
        clearInterval(countdownInterval);
    }
}

function addDigit(digit) {
    const password = document.getElementById("password");
    if (password.value.length < 4) {
        password.value += digit;
    }
}

function clearInput() {
    document.getElementById("password").value = "";
}

async function unlockDoor() {
    let password = document.getElementById("password").value;
    if (!password) {
        document.getElementById("message").innerText = "Please enter a PIN";
        return;
    }
    
    let response = await fetch("/unlock", {
        method: "POST",
        body: new URLSearchParams({ password: password }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    
    let result = await response.json();
    document.getElementById("message").innerText = result.message;
    document.getElementById("password").value = "";
    
    // Start countdown if door unlocked successfully
    if (result.status === "success") {
        startCountdown(20);
    }
}

async function lockDoor() {
    let response = await fetch("/lock", { method: "POST" });
    let result = await response.json();
    document.getElementById("message").innerText = result.message;
    
    // Stop countdown timer
    document.getElementById("countdown").classList.add("hidden");
    clearInterval(countdownInterval);
}

function startCountdown(seconds) {
    const countdownElement = document.getElementById("countdown");
    const timerElement = document.getElementById("timer");
    let timeLeft = seconds;
    
    countdownElement.classList.remove("hidden");
    timerElement.innerText = timeLeft;
    
    clearInterval(countdownInterval);
    
    countdownInterval = setInterval(() => {
        timeLeft--;
        timerElement.innerText = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(countdownInterval);
        }
    }, 1000);
}