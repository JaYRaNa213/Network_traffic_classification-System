// static/js/ml_visualizer.js

class MLVisualizer {
    constructor() {
        this.gaugeCanvas = document.getElementById('confidenceGauge');
        if (this.gaugeCanvas) {
            this.ctx = this.gaugeCanvas.getContext('2d');
            this.gaugeCanvas.width = 160;
            this.gaugeCanvas.height = 160;
        }
    }

    drawGauge(percentage, color) {
        if(!this.ctx) return;
        const ctx = this.ctx;
        const centerX = 80;
        const centerY = 80;
        const radius = 70;

        ctx.clearRect(0, 0, 160, 160);

        // Background track
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, 2.25 * Math.PI);
        ctx.lineWidth = 12;
        ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--bg-main').trim();
        ctx.lineCap = 'round';
        ctx.stroke();

        // Fill track
        const endAngle = 0.75 * Math.PI + (1.5 * Math.PI * (percentage / 100));
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, endAngle);
        ctx.lineWidth = 12;
        ctx.strokeStyle = color;
        ctx.lineCap = 'round';
        ctx.stroke();
    }

    animateGauge(targetPercent, color) {
        let current = 0;
        const step = targetPercent / 30;
        const valEl = document.getElementById('gaugeValue');
        
        const animate = () => {
            current += step;
            if (current > targetPercent) current = targetPercent;
            
            this.drawGauge(current, color);
            if(valEl) valEl.innerText = Math.round(current) + '%';

            if (current < targetPercent) {
                requestAnimationFrame(animate);
            }
        };
        requestAnimationFrame(animate);
    }

    updateFeatureBars(featureData) {
        const container = document.getElementById('featureChart');
        if(!container) return;
        container.innerHTML = '';

        // Sort features by importance
        const sorted = Object.entries(featureData)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6); // Top 6 features

        const maxVal = sorted[0][1] || 1;

        sorted.forEach(([name, val], index) => {
            const width = (val / maxVal) * 100;
            
            const row = document.createElement('div');
            row.className = 'bar-row fade-in';
            row.style.animationDelay = `${index * 0.1}s`;

            row.innerHTML = `
                <div class="bar-label">${name}</div>
                <div class="bar-track">
                    <div class="bar-fill" style="width: ${width}%;"></div>
                </div>
                <div class="bar-value">${val.toFixed(3)}</div>
            `;
            container.appendChild(row);
        });
    }

    updateEnsembleGrid(treeVotes, totalActive, resultClass) {
        const grid = document.getElementById('ensembleGrid');
        if(!grid) return;
        grid.innerHTML = '';

        const maxTreesToShow = Math.min(totalActive, 200); // Visual limit
        
        // Calculate proportional representation
        let majorityVotes = treeVotes[resultClass] || 0;
        let minorityVotes = totalActive - majorityVotes;
        
        const majorityNodes = Math.round((majorityVotes / totalActive) * maxTreesToShow);
        const minorityNodes = maxTreesToShow - majorityNodes;

        const baseColor = getComputedStyle(document.body).getPropertyValue('--bg-main').trim();
        const highlightColor = getComputedStyle(document.body).getPropertyValue('--accent-indigo').trim();
        const errorColor = getComputedStyle(document.body).getPropertyValue('--text-muted').trim();

        // Create nodes
        const nodes = [];
        for(let i=0; i<majorityNodes; i++) nodes.push(highlightColor);
        for(let i=0; i<minorityNodes; i++) nodes.push(errorColor);
        
        // Shuffle for organic look
        nodes.sort(() => Math.random() - 0.5);

        nodes.forEach((color, i) => {
            const node = document.createElement('div');
            node.className = 'tree-node';
            grid.appendChild(node);
            
            setTimeout(() => {
                node.style.background = color;
            }, i * (500 / maxTreesToShow)); // Waterfall effect
        });

        document.getElementById('ensembleMeta').innerText = `${majorityVotes} out of ${totalActive} trees voted for ${resultClass}`;
    }
}

window.MLVis = new MLVisualizer();
