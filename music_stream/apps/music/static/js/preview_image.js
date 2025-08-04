document.getElementById('image').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('image-preview').innerHTML = 
                    `<img src="${e.target.result}" class="w-full h-full object-cover rounded-xl">`;
            }
            reader.readAsDataURL(file);
        }
    });
