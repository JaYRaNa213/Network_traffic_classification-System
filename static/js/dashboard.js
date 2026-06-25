// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', () => {
    // Initial random values
    let packets = 1245902;
    let threats = 432;
    let sessions = 1240;

    const pktEl = document.getElementById('statPackets');
    const threatEl = document.getElementById('statThreats');
    const sessEl = document.getElementById('statSessions');

    // Simulate real-time dashboard counting
    setInterval(() => {
        packets += Math.floor(Math.random() * 50) + 10;
        if(Math.random() > 0.8) threats += 1;
        sessions += Math.floor(Math.random() * 5) - 2; // Fluctuating

        if(pktEl) pktEl.innerText = packets.toLocaleString();
        if(threatEl) threatEl.innerText = threats.toLocaleString();
        if(sessEl) sessEl.innerText = sessions.toLocaleString();
    }, 2000);
});
