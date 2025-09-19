// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if(targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if(targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Registration form handling
document.getElementById('registrationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = {
        teamName: formData.get('teamName'),
        leaderName: formData.get('leaderName'),
        email: formData.get('email'),
        university: formData.get('university'),
        experienceLevel: formData.get('experienceLevel'),
        theme: formData.get('theme')
    };
    
    // Collect team member data
    for (let i = 1; i <= 4; i++) {
        const memberName = formData.get(`member${i}Name`);
        const memberEmail = formData.get(`member${i}Email`);
        if (memberName) {
            data[`member${i}Name`] = memberName;
            data[`member${i}Email`] = memberEmail || '';
        }
    }
    
    // Show loading state
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.textContent;
    submitBtn.textContent = 'Registering...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Registration successful! Welcome to NECSprint 2024!\nCheck your email for confirmation.');
            this.reset();
            // Reset team members section
            document.getElementById('teamMembers').innerHTML = `
                <div class="member-input">
                    <input type="text" name="member1Name" placeholder="Member 2 Name">
                    <input type="email" name="member1Email" placeholder="Member 2 Email">
                </div>
            `;
            memberCount = 1;
            document.getElementById('addMember').style.display = 'inline-block';
        } else {
            alert('Registration failed: ' + result.message);
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed. Please check your internet connection and try again.');
    } finally {
        // Reset button state
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
    }
});

// Add animation on scroll
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
});

// Countdown Timer
function updateCountdown() {
    const eventDate = new Date('2024-12-31T18:00:00').getTime();
    const now = new Date().getTime();
    const timeLeft = eventDate - now;
    
    if (timeLeft > 0) {
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
        
        document.getElementById('days').textContent = days.toString().padStart(2, '0');
        document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
        document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
        document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
    } else {
        document.getElementById('days').textContent = '00';
        document.getElementById('hours').textContent = '00';
        document.getElementById('minutes').textContent = '00';
        document.getElementById('seconds').textContent = '00';
    }
}

setInterval(updateCountdown, 1000);
updateCountdown();

// Team Member Management
let memberCount = 1;
document.getElementById('addMember').addEventListener('click', function() {
    if (memberCount < 4) {
        memberCount++;
        const memberDiv = document.createElement('div');
        memberDiv.className = 'member-input';
        memberDiv.innerHTML = `
            <input type="text" name="member${memberCount}Name" placeholder="Member ${memberCount + 1} Name">
            <input type="email" name="member${memberCount}Email" placeholder="Member ${memberCount + 1} Email">
        `;
        document.getElementById('teamMembers').appendChild(memberDiv);
        
        if (memberCount === 4) {
            this.style.display = 'none';
        }
    }
});