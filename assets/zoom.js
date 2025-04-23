// assets/zoom.js
(function(){
    // Wait until the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
      // Your baseline
      const BASE_W = 1920;
      const BASE_H = 1080;
  
      // Actual viewport
      const w = window.innerWidth;
      const h = window.innerHeight;
  
      // Choose which ratio to use
      //   — width can be more reliable if height is tall/short
      const scale = Math.min( w / BASE_W, h / BASE_H );
  
      // Apply to root font-size (so all rem‑based CSS will scale)
      // Or you could use document.body.style.zoom = scale;
      document.documentElement.style.fontSize = (100 * scale
      ) + '%';
    });
  })();
  