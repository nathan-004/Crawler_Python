// Create neon circles
function createNeonCircle() {
	const circle = document.createElement('div');
	circle.className = 'neon-circle';
	
	const size = Math.random() * 150 + 50;
	circle.style.width = size + 'px';
	circle.style.height = size + 'px';
	circle.style.left = Math.random() * (window.innerWidth - size) + 'px';
	circle.style.top = Math.random() * (window.innerHeight - size) + 'px';
	circle.style.animationDelay = Math.random() * 4 + 's';
	
	document.body.appendChild(circle);
	
	setTimeout(() => {
		circle.remove();
	}, 12000);
}

// Create floating particles
function createParticle() {
	const particle = document.createElement('div');
	particle.className = 'particle';
	
	particle.style.left = Math.random() * window.innerWidth + 'px';
	particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
	particle.style.animationDelay = Math.random() * 2 + 's';
	
	const colors = ['#ff00ff', '#00ffff', '#ffff00', '#ff0080', '#80ff00'];
	const color = colors[Math.floor(Math.random() * colors.length)];
	particle.style.background = `radial-gradient(circle, ${color}, transparent)`;
	particle.style.boxShadow = `0 0 10px ${color}`;
	
	document.getElementById('particles').appendChild(particle);
	
	setTimeout(() => {
		particle.remove();
	}, 8000);
}

// Initialize effects
function initEffects() {
	// Create initial circles
	for (let i = 0; i < 5; i++) {
		setTimeout(createNeonCircle, i * 1500);
	}
	
	// Continuous particle generation
	setInterval(createParticle, 200);
	
	// Continuous circle generation
	setInterval(createNeonCircle, 4000);
}

// Mouse interaction
document.addEventListener('mousemove', (e) => {
	if (Math.random() < 0.1) {
		const spark = document.createElement('div');
		spark.style.position = 'absolute';
		spark.style.left = e.clientX + 'px';
		spark.style.top = e.clientY + 'px';
		spark.style.width = '6px';
		spark.style.height = '6px';
		spark.style.background = 'radial-gradient(circle, #ffffff, #ff00ff)';
		spark.style.borderRadius = '50%';
		spark.style.pointerEvents = 'none';
		spark.style.zIndex = '20';
		spark.style.boxShadow = '0 0 15px #ff00ff';
		spark.style.animation = 'sparkle 1s ease-out forwards';
		
		document.body.appendChild(spark);
		
		setTimeout(() => spark.remove(), 1000);
	}
});

// Add sparkle animation
const style = document.createElement('style');
style.textContent = `
	@keyframes sparkle {
		0% { transform: scale(0) rotate(0deg); opacity: 1; }
		50% { transform: scale(1.5) rotate(180deg); opacity: 0.8; }
		100% { transform: scale(0) rotate(360deg); opacity: 0; }
	}
`;
document.head.appendChild(style);

// Start the effects
initEffects();

// Handle window resize
window.addEventListener('resize', () => {
	// Clean up particles on resize
	const particles = document.querySelectorAll('.particle');
	particles.forEach(p => p.remove());
});