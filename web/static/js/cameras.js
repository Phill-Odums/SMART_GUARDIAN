// Camera Management interactions

function openAddModal() {
    const modal = document.getElementById('add-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeAddModal() {
    const modal = document.getElementById('add-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.getElementById('add-camera-form').reset();
}

window.addEventListener('DOMContentLoaded', () => {

    // Form Submission
    const addForm = document.getElementById('add-camera-form');
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('camName').value;
            const source = document.getElementById('camSource').value;
            const detect = document.getElementById('camDetect').checked;

            const payload = {
                camera_id: name, // In a real app generate a UUID or let backend handle
                source: source,
                enable_detection: detect
            };

            try {
                // Determine if source is integer (USB) or string (IP)
                let parsedSource = source;
                if (!isNaN(parsedSource) && !parsedSource.includes('.')) {
                    parsedSource = parseInt(parsedSource);
                }

                const res = await fetch('/add_camera', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ camera_id: parsedSource }) // Simple mapping to existing backend
                });

                if (res.ok) {
                    alert('Camera added/started successfully!');
                    closeAddModal();
                    // Optional: reload page or dynamically append new camera card
                    window.location.reload();
                } else {
                    alert('Failed to add camera source.');
                }
            } catch (err) {
                console.error(err);
                alert('Network Error');
            }
        });
    }

});
