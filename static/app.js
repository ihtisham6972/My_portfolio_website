// Setup Three.js Scene
const scene = new THREE.Scene();

// Setup Camera
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 60; // Pulled back slightly to show the whole ring

// Setup Renderer
const canvas = document.querySelector('#bg-canvas');
const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);

// Create a 3D Particle System (Orbiting Ring)
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 2500; // Increased count for a denser ring
const posArray = new Float32Array(particlesCount * 3);

for(let i = 0; i < particlesCount; i++) {
    // Math to create a ring that leaves the center (where the card is) empty
    // Radius starts at 35 (outside the card) and extends to 100
    const radius = 35 + Math.random() * 65; 
    const angle = Math.random() * Math.PI * 2;
    
    // Position the dots in a circle around the center
    posArray[i*3] = Math.cos(angle) * radius * 1.8;   // X (Wider for desktop screens)
    posArray[i*3 + 1] = Math.sin(angle) * radius * 1.2; // Y (Height)
    posArray[i*3 + 2] = (Math.random() - 0.5) * 60;     // Z (3D Depth toward/away from you)
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

// Custom Material for the particles
const particlesMaterial = new THREE.PointsMaterial({
    size: 0.4,
    color: '#000000', /* Black Dots */
    transparent: true,
    opacity: 0.7
});

const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

// Mouse interaction tracking
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (event) => {
    mouseX = (event.clientX / window.innerWidth) - 0.5;
    mouseY = (event.clientY / window.innerHeight) - 0.5;
});

// Animation Loop
const animate = () => {
    requestAnimationFrame(animate);

    // This makes the entire ring slowly spin around the center card like a wheel
    particlesMesh.rotation.z -= 0.001; 
    
    // Gives it a slight 3D wobble
    particlesMesh.rotation.x += 0.0002;
    particlesMesh.rotation.y += 0.0005;

    // Reacts to the mouse
    particlesMesh.rotation.x += mouseY * 0.02;
    particlesMesh.rotation.y += mouseX * 0.02;

    renderer.render(scene, camera);
}
animate();

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- Scroll Reveal Animation ---
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.fade-in').forEach((element) => {
    observer.observe(element);
});

// --- Hamburger Menu Logic ---
const hamburgerBtn = document.getElementById('hamburger-btn');
const sideMenu = document.getElementById('side-menu');

hamburgerBtn.addEventListener('click', () => {
    hamburgerBtn.classList.toggle('active');
    sideMenu.classList.toggle('active');
});

document.addEventListener('click', (event) => {
    if (!sideMenu.contains(event.target) && !hamburgerBtn.contains(event.target) && sideMenu.classList.contains('active')) {
        hamburgerBtn.classList.remove('active');
        sideMenu.classList.remove('active');
    }
});