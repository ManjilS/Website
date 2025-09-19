async function updateLiveStats() {
    try {
        const response = await fetch('/registrations');
        const registrations = await response.json();
        document.getElementById('liveRegistrations').textContent = registrations.length;
        
        // Update event status based on registrations
        const statusElement = document.getElementById('eventStatus');
        if (registrations.length > 50) {
            statusElement.textContent = 'Almost Full!';
            statusElement.style.color = '#f59e0b';
        }
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

function updateCountdown() {
    const eventDate = new Date('2024-12-31T18:00:00').getTime();
    const now = new Date().getTime();
    const timeLeft = eventDate - now;
    
    if (timeLeft > 0) {
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
        
        document.getElementById('days').textContent = days;
        document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
        document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
        document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
    } else {
        document.getElementById('timeRemaining').textContent = 'Event Started!';
        document.getElementById('countdown').style.display = 'none';
        document.getElementById('eventStatus').textContent = 'In Progress';
        document.getElementById('eventStatus').style.color = '#10b981';
    }
}

async function loadAnnouncements() {
    try {
        const response = await fetch('/api/announcements');
        const announcements = await response.json();
        
        const container = document.getElementById('announcements');
        container.innerHTML = '';
        
        announcements.forEach(announcement => {
            const announcementElement = document.createElement('div');
            announcementElement.className = 'announcement';
            announcementElement.innerHTML = `
                <div class="announcement-time">
                    <i class="far fa-clock"></i> 
                    ${new Date(announcement.created_at).toLocaleString()}
                </div>
                <div class="announcement-content">
                    <h3>${announcement.title}</h3>
                    <p>${announcement.content}</p>
                </div>
            `;
            container.appendChild(announcementElement);
        });
    } catch (error) {
        console.error('Failed to load announcements:', error);
    }
}

// Update stats every 30 seconds
setInterval(updateLiveStats, 30000);
setInterval(updateCountdown, 1000);
setInterval(loadAnnouncements, 60000); // Refresh announcements every minute

// Initial load
updateLiveStats();
updateCountdown();
loadAnnouncements();