/* UrbanPulse AI — City Particle Network Engine */
/* Creates animated smart-city data visualization on canvas */

(function () {
  'use strict';

  function initParticleNetwork(canvasId, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const opts = Object.assign({
      particleCount:    55,
      connectionDist:   160,
      nodeColor:        '#00d4ff',
      lineColor:        'rgba(0, 212, 255,',
      bgColor:          'transparent',
      speed:            0.35,
      nodeMinSize:      1.5,
      nodeMaxSize:      4,
      pulseNodes:       6,    // highlighted "city hub" nodes
      dataFlow:         true, // moving packets along connections
    }, options);

    let W, H, particles, animId, dataPackets;

    function resize() {
      W = canvas.width  = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
    }

    function randomBetween(a, b) { return a + Math.random() * (b - a); }

    class Particle {
      constructor(isPulse) {
        this.reset(true);
        this.isPulse = isPulse || false;
        this.size    = isPulse ? randomBetween(3, opts.nodeMaxSize) : randomBetween(opts.nodeMinSize, 2.5);
        this.pulseR  = this.isPulse ? 0 : null;
        this.pulseMax = randomBetween(20, 40);
        this.pulseAlpha = 1;
        this.color = this.isPulse
          ? (Math.random() > 0.5 ? '#00d4ff' : '#a78bfa')
          : opts.nodeColor;
      }

      reset(initial) {
        this.x  = randomBetween(0, W || window.innerWidth);
        this.y  = randomBetween(0, H || window.innerHeight);
        this.vx = randomBetween(-opts.speed, opts.speed);
        this.vy = randomBetween(-opts.speed, opts.speed);
        if (!initial) {
          // re-enter from edge
          const side = Math.floor(Math.random() * 4);
          if (side === 0) { this.x = 0; }
          else if (side === 1) { this.x = W; }
          else if (side === 2) { this.y = 0; }
          else { this.y = H; }
        }
        this.opacity = randomBetween(0.4, 1.0);
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        if (this.x < -20 || this.x > W + 20 || this.y < -20 || this.y > H + 20) {
          this.reset(false);
        }
        if (this.isPulse && this.pulseR !== null) {
          this.pulseR += 0.6;
          this.pulseAlpha = 1 - (this.pulseR / this.pulseMax);
          if (this.pulseR >= this.pulseMax) { this.pulseR = 0; this.pulseAlpha = 1; }
        }
      }

      draw() {
        // Pulse ring for city hub nodes
        if (this.isPulse && this.pulseR > 0) {
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.pulseR, 0, Math.PI * 2);
          ctx.strokeStyle = this.color.replace(')', `, ${this.pulseAlpha * 0.4})`).replace('rgb', 'rgba').replace('##', '#');
          if (this.color === '#00d4ff') ctx.strokeStyle = `rgba(0,212,255,${this.pulseAlpha * 0.35})`;
          else ctx.strokeStyle = `rgba(167,139,250,${this.pulseAlpha * 0.35})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
        // Node dot
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        const alpha = this.opacity * (this.isPulse ? 1 : 0.65);
        if (this.color === '#00d4ff') ctx.fillStyle = `rgba(0,212,255,${alpha})`;
        else if (this.color === '#a78bfa') ctx.fillStyle = `rgba(167,139,250,${alpha})`;
        else ctx.fillStyle = `rgba(0,212,255,${alpha * 0.5})`;
        ctx.fill();

        // Glow for pulse nodes
        if (this.isPulse) {
          ctx.shadowBlur  = 12;
          ctx.shadowColor = this.color;
          ctx.fill();
          ctx.shadowBlur  = 0;
        }
      }
    }

    class DataPacket {
      constructor(from, to) {
        this.from = from;
        this.to   = to;
        this.t    = 0; // 0→1 along path
        this.speed = randomBetween(0.006, 0.014);
        this.color = Math.random() > 0.5 ? '#00d4ff' : '#a78bfa';
        this.size  = randomBetween(2, 3.5);
      }
      update() {
        this.t += this.speed;
        return this.t < 1; // return false when done
      }
      draw() {
        const x = this.from.x + (this.to.x - this.from.x) * this.t;
        const y = this.from.y + (this.to.y - this.from.y) * this.t;
        ctx.beginPath();
        ctx.arc(x, y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color === '#00d4ff'
          ? `rgba(0,212,255,0.9)` : `rgba(167,139,250,0.9)`;
        ctx.shadowBlur  = 8;
        ctx.shadowColor = this.color;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    function init() {
      resize();
      particles = [];
      dataPackets = [];

      // Create pulse (hub) nodes first
      for (let i = 0; i < opts.pulseNodes; i++) {
        particles.push(new Particle(true));
      }
      // Regular nodes
      for (let i = 0; i < opts.particleCount - opts.pulseNodes; i++) {
        particles.push(new Particle(false));
      }
    }

    let frameCount = 0;
    function draw() {
      animId = requestAnimationFrame(draw);
      ctx.clearRect(0, 0, W, H);
      frameCount++;

      // Spawn data packets periodically
      if (opts.dataFlow && frameCount % 40 === 0 && particles.length > 1) {
        const idxA = Math.floor(Math.random() * opts.pulseNodes);
        const idxB = Math.floor(Math.random() * opts.pulseNodes);
        if (idxA !== idxB) {
          const dist = Math.hypot(particles[idxA].x - particles[idxB].x, particles[idxA].y - particles[idxB].y);
          if (dist < opts.connectionDist * 1.5) {
            dataPackets.push(new DataPacket(particles[idxA], particles[idxB]));
          }
        }
      }

      // Update + draw connections
      for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < opts.connectionDist) {
            const alpha = (1 - dist / opts.connectionDist) * 0.22;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            // Violet lines between pulse nodes, cyan otherwise
            const bothPulse = i < opts.pulseNodes && j < opts.pulseNodes;
            ctx.strokeStyle = bothPulse
              ? `rgba(167,139,250,${alpha * 1.5})`
              : `rgba(0,212,255,${alpha})`;
            ctx.lineWidth = bothPulse ? 1 : 0.5;
            ctx.stroke();
          }
        }
      }

      // Draw particles
      particles.forEach(p => p.draw());

      // Draw + update data packets
      dataPackets = dataPackets.filter(dp => {
        const alive = dp.update();
        if (alive) dp.draw();
        return alive;
      });
    }

    window.addEventListener('resize', () => {
      resize();
      init();
    });

    init();
    draw();

    // Return controller
    return {
      destroy() {
        cancelAnimationFrame(animId);
        ctx.clearRect(0, 0, W, H);
      }
    };
  }

  // Expose globally
  window.UrbanParticles = { init: initParticleNetwork };
})();
