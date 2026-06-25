// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('predictionForm');
    const overlay = document.getElementById('engineOverlay');
    const resultBanner = document.getElementById('resultBanner');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Hide previous results & show overlay
            resultBanner.style.display = 'none';
            resultBanner.className = 'result-banner';
            overlay.classList.add('active');

            // Reset Pipeline highlighting
            document.querySelectorAll('.node-box').forEach(n => n.classList.remove('active'));

            const formData = new FormData(form);

            try {
                // Pipeline Step 1
                document.getElementById('nodeExtract').classList.add('active');

                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData,
                    headers: { 'Accept': 'application/json' }
                });

                if (!response.ok) throw new Error("Backend connection failed.");
                const data = await response.json();

                // Pipeline Animation Sequence
                setTimeout(() => {
                    document.getElementById('nodeInfer').classList.add('active');
                }, 400);

                setTimeout(() => {
                    document.getElementById('nodeConsensus').classList.add('active');
                }, 800);

                setTimeout(() => {
                    overlay.classList.remove('active');
                    document.getElementById('nodeOutput').classList.add('active');

                    // Populate Banner
                    document.getElementById('resTitle').innerText = data.prediction;
                    document.getElementById('resLat').innerText = data.response_time + 'ms';

                    // Set Theme Color
                    const p = data.prediction.toLowerCase();
                    let themeColor = '#64748b'; // default muted
                    if (p.includes('allow')) { resultBanner.classList.add('res-allow'); themeColor = '#10b981'; }
                    else if (p.includes('deny')) { resultBanner.classList.add('res-deny'); themeColor = '#ef4444'; }
                    else if (p.includes('drop')) { resultBanner.classList.add('res-drop'); themeColor = '#f59e0b'; }
                    else { resultBanner.classList.add('res-reset'); themeColor = '#8b5cf6'; }

                    resultBanner.style.display = 'flex';

                    // Trigger ML Visualizations
                    if (window.MLVis) {
                        window.MLVis.animateGauge(data.confidence, themeColor);
                        window.MLVis.updateFeatureBars(data.feature_importance);
                        window.MLVis.updateEnsembleGrid(data.tree_votes, data.n_active_trees, data.prediction);
                    }

                }, 1200); // UI processing delay

            } catch (err) {
                console.error(err);
                setTimeout(() => {
                    overlay.classList.remove('active');
                    document.getElementById('resTitle').innerText = "ERROR";
                    resultBanner.classList.add('res-deny');
                    resultBanner.style.display = 'flex';
                }, 800);
            }
        });
    }

    // ScrollSpy & Smooth Scrolling Logic
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.page-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('data-target');
            if (!targetId || targetId === '#') return;
            e.preventDefault();

            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            } else if (targetId === 'home') {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    });

    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('data-target') === entry.target.id) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));
});
