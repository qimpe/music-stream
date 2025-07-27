// preview_image.js
document.getElementById('id_cover').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewContainer = document.getElementById('cover-preview');
            previewContainer.innerHTML = `
                <div class="relative w-full h-full">
                    <img src="${e.target.result}" class="w-full h-full object-cover rounded-xl">
                    <button type="button" class="absolute top-2 right-2 bg-black/50 rounded-full p-1 text-white hover:bg-black/80" onclick="resetCoverPreview()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            `;
        }
        reader.readAsDataURL(file);
    }
});

function resetCoverPreview() {
    const previewContainer = document.getElementById('cover-preview');
    previewContainer.innerHTML = `
        <svg class="w-12 h-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z">
            </path>
        </svg>
    `;
    document.getElementById('id_cover').value = '';
}