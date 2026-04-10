class LuckyWheel {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        this.radius = this.canvas.width / 2 - 10;
        this.isSpinning = false;
        this.currentAngle = 0;
        this.spinSpeed = 0;
        this.friction = 0.98;
        
        this.prizes = [
            { label: '10 積分', color: '#ef4444, value: 10 },
            { label: '20 積分', color: '#f59e0b', value: 20 },
            { label: '50 積分', color: '#10b981', value: 50 },
            { label: '100 積分', color: '#3b82f6', value: 100 },
            { label: '200 積分', color: '#8b5cf6', value: 200 },
            { label: '500 積分', color: '#ec4899', value: 500 },
            { label: '1000 積分', color: '#06b6d4', value: 1000 },
            { label: '再轉一次', color: '#6366f1', value: 'respin' }
        ];
        
        this.drawWheel();
    }
    
    drawWheel() {
        const numPrizes = this.prizes.length;
        const arcSize = (Math.PI * 2) / numPrizes;
        
        for (let i = 0; i < numPrizes; i++) {
            const startAngle = i * arcSize + this.currentAngle;
            const endAngle = (i + 1) * arcSize + this.currentAngle;
            
            this.ctx.beginPath();
            this.ctx.fillStyle = this.prizes[i].color;
            this.ctx.moveTo(this.centerX, this.centerY);
            this.ctx.arc(this.centerX, this.centerY, this.radius, startAngle, endAngle);
            this.ctx.closePath();
            this.ctx.fill();
            
            this.ctx.strokeStyle = 'rgba(255,255,255,0.2)';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            this.ctx.save();
            this.ctx.translate(this.centerX, this.centerY);
            this.ctx.rotate(startAngle + arcSize / 2);
            this.ctx.textAlign = 'right';
            this.ctx.fillStyle = 'white';
            this.ctx.font = 'bold 14px Noto Sans TC';
            this.ctx.fillText(this.prizes[i].label, this.radius - 30, 5);
            this.ctx.restore();
        }
        
        this.ctx.beginPath();
        this.ctx.fillStyle = '#0f172a';
        this.ctx.arc(this.centerX, this.centerY, 60, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.strokeStyle = '#3b82f6';
        this.ctx.lineWidth = 4;
        this.ctx.stroke();
    }
    
    spin() {
        if (this.isSpinning) return;
        this.isSpinning = true;
        this.spinSpeed = 0.3 + Math.random() * 0.2;
        
        const targetIndex = Math.floor(Math.random() * this.prizes.length);
        const targetAngle = Math.PI * 2 * 5 + (targetIndex * ((Math.PI * 2) / this.prizes.length;
        
        const animate = () => {
            this.currentAngle += this.spinSpeed;
            this.spinSpeed *= this.friction;
            this.drawWheel();
            
            if (this.spinSpeed > 0.002) {
                requestAnimationFrame(animate);
            } else {
                this.isSpinning = false;
                const winningIndex = Math.floor(((this.currentAngle % (Math.PI * 2)) / ((Math.PI * 2) * this.prizes.length;
                this.onSpinEnd?.(this.prizes[Math.floor(winningIndex)]);
            }
        };
        
        animate();
    }
}

let wheel;
let userData = {
    points: 0,
    streak: 0,
    spins: 0,
    checkedInToday: false
};

document.addEventListener('DOMContentLoaded', () => {
    wheel = new LuckyWheel('wheel-canvas');
    
    const spinBtn = document.getElementById('spin-btn');
    const checkinBtn = document.getElementById('checkin-btn');
    
    spinBtn.addEventListener('click', () => {
        if (userData.spinsLeft <= 0) return;
        
        wheel.spin();
        userData.spinsLeft--;
        updateUI();
    });
    
    checkinBtn.addEventListener('click', () => {
        if (userData.checkedInToday) return;
        
        userData.checkedInToday = true;
        userData.points += 10;
        userData.streak++;
        userData.spinsLeft = Math.floor(userData.points / 20);
        
        checkinBtn.disabled = true;
        checkinBtn.textContent = '✅ 已簽到';
        updateUI();
    });
    
    wheel.onSpinEnd = (prize) => {
        if (prize.value === 'respin') {
            userData.spinsLeft++;
        } else {
            userData.points += prize.value;
            userData.spinsLeft = Math.floor(userData.points / 20);
        }
        updateUI();
        alert(`🎉 恭喜獲得 ${prize.label}！`);
    };
    
    loadUserData();
    updateUI();
});

function updateUI() {
    document.getElementById('user-points').textContent = userData.points;
    document.getElementById('streak').textContent = userData.streak;
    document.getElementById('spins-left').textContent = userData.spinsLeft;
    document.getElementById('spin-btn').disabled = userData.spinsLeft <= 0;
}

function loadUserData() {
    const saved = localStorage.getItem('chujiu_user');
    if (saved) {
        userData = JSON.parse(saved);
        
        const today = new Date().toDateString();
        if (userData.lastCheckinDate !== today) {
            userData.checkedInToday = false;
        }
    }
}

function saveUserData() {
    userData.lastCheckinDate = new Date().toDateString();
    localStorage.setItem('chujiu_user', JSON.stringify(userData));
}
