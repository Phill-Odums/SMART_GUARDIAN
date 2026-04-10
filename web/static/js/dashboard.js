/**
 * Starts a camera stream
 * @param {number} camId 
 */
async function startStream(camId) {
    try {
        const res = await fetch('/start_camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ camera_id: camId })
        });
        const data = await res.json();
        if (data.success) {
            // Find the image for this camera and refresh its src to restart the stream
            // In this specific UI, CAM-01 is ID 0
            const img = document.querySelector(`img[alt="Video Feed ${camId + 1}"]`);
            if (img) {
                const baseUrl = `/video_feed/${camId}`;
                img.src = `${baseUrl}?t=${new Date().getTime()}`;
            }
            console.log(`Camera ${camId} started`);
        }
    } catch (e) {
        console.error('Error starting stream:', e);
    }
}

/**
 * Stops a camera stream
 * @param {number} camId 
 */
async function stopStream(camId) {
    try {
        const res = await fetch('/stop_camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ camera_id: camId })
        });
        const data = await res.json();
        if (data.success) {
            const img = document.querySelector(`img[alt="Video Feed ${camId + 1}"]`);
            if (img) {
                img.src = ""; // Clear the stream
                // Optional: show a placeholder or "Offline" UI
            }
            console.log(`Camera ${camId} stopped`);
        }
    } catch (e) {
        console.error('Error stopping stream:', e);
    }
}

/**
 * Toggles AI detection for a camera
 * @param {number} camId 
 */
async function toggleAI(camId, event) {
    if (event) event.stopPropagation();

    try {
        const res = await fetch('/toggle_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ camera_id: camId })
        });
        const data = await res.json();
        if (data.success) {
            const btn = event.currentTarget;
            if (data.ai_enabled) {
                btn.classList.add('bg-cyan-500', 'shadow-[0_0_15px_rgba(6,182,212,0.8)]');
                btn.classList.remove('bg-black/60');
            } else {
                btn.classList.remove('bg-cyan-500', 'shadow-[0_0_15px_rgba(6,182,212,0.8)]');
                btn.classList.add('bg-black/60');
            }
        }
    } catch (e) {
        console.error('Error toggling AI:', e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialize default grid to 2x2 (4 cameras layout)
    setGrid(2);
});

/**
 * Changes the camera grid layout
 * @param {number} mode - 1 for 1x1, 2 for 2x2, 3 for 3x3
 */
function setGrid(mode) {
    const gridEl = document.getElementById('camera-grid');
    if (!gridEl) return;

    // Reset grid classes
    gridEl.className = 'grid gap-2 h-full transition-all duration-300';

    // Add new layout classes based on mode
    if (mode === 1) {
        gridEl.classList.add('grid-cols-1');
    } else if (mode === 2) {
        gridEl.classList.add('grid-cols-2');
    } else if (mode === 3) {
        gridEl.classList.add('grid-cols-3');
    }
}

/**
 * Toggles a camera cell to become fullscreen within the grid area
 * (Simple implementation showing expanding a cell. Can be expanded upon for real fullscreen)
 * @param {HTMLElement} cellElement 
 */
function toggleFullscreen(cellElement) {
    // If it's already full screen, shrink it back
    if (cellElement.classList.contains('fixed', 'inset-4', 'z-50')) {
        cellElement.classList.remove('fixed', 'inset-4', 'z-50', 'bg-dark');
        cellElement.classList.add('relative');
    } else {
        // Remove fullscreen from any other cell first
        document.querySelectorAll('.camera-cell').forEach(el => {
            el.classList.remove('fixed', 'inset-4', 'z-50', 'bg-dark');
            el.classList.add('relative');
        });

        // Make this cell full screen (covering just the main area, or actual fixed screen)
        cellElement.classList.remove('relative');
        cellElement.classList.add('fixed', 'inset-4', 'z-50', 'bg-dark');
    }
}
