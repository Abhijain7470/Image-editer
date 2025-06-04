// Toggle UI elements based on user action and background type
document.addEventListener('DOMContentLoaded', function () {
    const actionSelect = document.getElementById('action-select');
    const bgTypeSelect = document.getElementById('bg-type-select');
    const bgOptions = document.getElementById('bg-options');
    const imagePicker = document.getElementById('image-picker');
    const colorPicker = document.getElementById('color-picker');

    function updateUI() {
        const action = actionSelect.value;
        const bgType = bgTypeSelect.value;

        // Show/hide background section based on action
        bgOptions.style.display = (action === 'replace_image' || action === 'replace_color') ? 'block' : 'none';

        // Show color or image picker
        imagePicker.style.display = (bgType === 'image') ? 'block' : 'none';
        colorPicker.style.display = (bgType === 'color') ? 'block' : 'none';
    }

    actionSelect.addEventListener('change', updateUI);
    bgTypeSelect.addEventListener('change', updateUI);

    updateUI(); // Initialize on page load
});
