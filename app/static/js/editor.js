// app/static/js/editor.js

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData();
    let fileInput = document.getElementById('fileInput');
    formData.append('file', fileInput.files[0]);
    fetch('/upload_video/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displayClips(data.clips);
    })
    .catch(error => console.error('Ошибка:', error));
});

function displayClips(clips) {
    let container = document.getElementById('clipsContainer');
    container.innerHTML = '';
    clips.forEach(clip => {
        let clipElement = document.createElement('div');
        clipElement.className = 'clip';
        clipElement.innerHTML = `
            <video width="320" height="240" controls>
                <source src="${clip.clip_path}" type="video/mp4">
            </video>
            <p><strong>Название:</strong> <input type="text" value="${clip.metadata.title}"></p>
            <p><strong>Описание:</strong> <textarea>${clip.metadata.description}</textarea></p>
            <p><strong>Хештеги:</strong> <input type="text" value="${clip.metadata.hashtags.join(' ')}"></p>
            <button onclick="downloadClip('${clip.clip_path}')">Скачать</button>
        `;
        container.appendChild(clipElement);
    });
}

function downloadClip(clipPath) {
    window.location.href = clipPath;
}
