// // assets/zoom.js
// (function(){
//     // Make scale variable globally accessible for Plotly charts
//     window.DASHBOARD_SCALE = 1;
    
//     // Wait until the DOM is ready
//     document.addEventListener('DOMContentLoaded', function() {
//       // Your baseline
//       const BASE_W = 1920;
//       const BASE_H = 1080;
  
//       // Actual viewport
//       const w = window.innerWidth;
//       const h = window.innerHeight;
  
//       // Calculate the ratio - when screen is smaller use min ratio to preserve aspect ratio
//       // When screen is larger than baseline, allow zooming in
//       let scale;
//       if (w <= BASE_W || h <= BASE_H) {
//         // For smaller screens - use minimum ratio to maintain aspect ratio
//         scale = Math.min(w / BASE_W, h / BASE_H);
//       } else {
//         // For larger screens - zoom in proportionally
//         scale = w / BASE_W * 2;
//       }
      
//       // Store the scale globally so it can be accessed by chart-scaling code
//       window.DASHBOARD_SCALE = scale;
  
//       // Apply to root font-size (so all rem‑based CSS will scale)
//       document.documentElement.style.fontSize = (100 * scale) + '%';
      
//       // Apply CSS variables for scaling
//       document.documentElement.style.setProperty('--dashboard-scale', scale);
//       document.documentElement.style.setProperty('--dashboard-scale-percent', (scale * 100) + '%');
      
//       // Add class to body based on scale size for CSS targeting
//       if (scale > 1.5) {
//         document.body.classList.add('large-scale');
//       } else {
//         document.body.classList.remove('large-scale');
//       }
      
//       // Wait for charts to be loaded and then apply scaling
//       waitForPlotly(function() {
//         scaleAllPlotlyCharts();
//       });
      
//       // Listen for window resize and apply scale
//       window.addEventListener('resize', function() {
//         const newW = window.innerWidth;
//         const newH = window.innerHeight;
        
//         let newScale;
//         if (newW <= BASE_W || newH <= BASE_H) {
//           newScale = Math.min(newW / BASE_W, newH / BASE_H);
//         } else {
//           newScale = newW / BASE_W * 2;
//         }
        
//         // Only update if scale has changed significantly
//         if (Math.abs(window.DASHBOARD_SCALE - newScale) > 0.01) {
//           window.DASHBOARD_SCALE = newScale;
//           document.documentElement.style.fontSize = (100 * newScale) + '%';
//           document.documentElement.style.setProperty('--dashboard-scale', newScale);
//           document.documentElement.style.setProperty('--dashboard-scale-percent', (newScale * 100) + '%');
          
//           // Update body class based on scale
//           if (newScale > 1.5) {
//             document.body.classList.add('large-scale');
//           } else {
//             document.body.classList.remove('large-scale');
//           }
          
//           // Re-scale charts
//           scaleAllPlotlyCharts();
//         }
//       });
      
//       // Listen for the custom scale event
//       document.addEventListener('dashboard-scale-updated', function() {
//         scaleAllPlotlyCharts();
//       });
//     });
    
//     // Wait for Plotly to be loaded
//     function waitForPlotly(callback) {
//       const checkInterval = 100; // check every 100ms
//       const maxChecks = 50;      // maximum 5 seconds of waiting
//       let checks = 0;
      
//       function checkPlotly() {
//         checks++;
//         if (window.Plotly) {
//           callback();
//         } else if (checks < maxChecks) {
//           setTimeout(checkPlotly, checkInterval);
//         } else {
//           console.warn('Plotly not loaded after timeout');
//         }
//       }
      
//       checkPlotly();
//     }
    
//     // Function to scale Plotly charts
//     function scaleAllPlotlyCharts() {
//       const scale = window.DASHBOARD_SCALE;
//       if (!scale || !window.Plotly) return;
      
//       // Find all Plotly charts in the document
//       const charts = document.querySelectorAll('.js-plotly-plot');
//       if (!charts.length) {
//         // Try again later if no charts found
//         setTimeout(scaleAllPlotlyCharts, 500);
//         return;
//       }
      
//       charts.forEach(function(chart) {
//         try {
//           if (!chart._fullLayout) return;
          
//           // Calculate scaled font sizes - use minimum sizes to ensure readability
//           const titleFontSize = Math.max(18, Math.round(18 * scale));
//           const baseFontSize = Math.max(14, Math.round(14 * scale));
//           const legendFontSize = Math.max(12, Math.round(12 * scale));
//           const subtitleFontSize = Math.max(16, Math.round(16 * scale));
          
//           // Calculate increased margins for larger scales to prevent overlapping
//           // Use a logarithmic scale to avoid excessive margins at very high scales
//           const marginTopMultiplier = scale > 1.5 ? 1 + Math.log10(scale) : 1;
          
//           // Build an update that only modifies font sizes without changing other layout properties
//           const updateLayout = {};
          
//           // Main font size update
//           if (chart._fullLayout.font) {
//             updateLayout['font.size'] = baseFontSize;
//           }
          
//           // Title font size update (preserves the text)
//           if (chart._fullLayout.title && chart._fullLayout.title.text) {
//             updateLayout['title.font.size'] = titleFontSize;
//           }
          
//           // Legend font size update (preserves visibility and position)
//           if (chart._fullLayout.showlegend) {
//             updateLayout['legend.font.size'] = legendFontSize;
//           }
          
//           // Update annotation font sizes if they exist
//           if (chart._fullLayout.annotations && chart._fullLayout.annotations.length > 0) {
//             chart._fullLayout.annotations.forEach((annotation, i) => {
//               updateLayout[`annotations[${i}].font.size`] = subtitleFontSize;
//             });
//           }
          
//           // For very large scales, increase the margins to prevent title overlapping
//           if (scale > 1.5 && chart._fullLayout.margin) {
//             const currentMargin = chart._fullLayout.margin;
//             // Only increase top margin to prevent title overlap
//             updateLayout['margin.t'] = Math.round(currentMargin.t * marginTopMultiplier);
//           }
          
//           // Apply the font size updates to the chart
//           Plotly.relayout(chart, updateLayout);
          
//           // Force chart redraw at full size
//           setTimeout(function() {
//             Plotly.Plots.resize(chart);
//           }, 100);
//         } catch (err) {
//           console.error('Error scaling chart:', err);
//         }
//       });
//     }
//   })();
  