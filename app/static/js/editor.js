// app/static/js/editor.js

function connectWebSocket() {
    console.log('Попытка подключения к WebSocket...');
    const socket = new WebSocket('ws://' + window.location.host + '/ws');
    socket.onopen = function(event) {
        console.log('WebSocket соединение установлено');
    };
    socket.onmessage = function(event) {
        console.log('Получено сообщение от сервера:', event.data);
        document.getElementById('progressInfo').textContent = event.data;
    };
    socket.onclose = function(event) {
        console.log('WebSocket соединение закрыто. Код:', event.code, 'Причина:', event.reason);
        setTimeout(connectWebSocket, 1000);
    };
    socket.onerror = function(error) {
        console.error('Ошибка WebSocket:', error);
    };
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM полностью загружен');
    connectWebSocket();
    
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        console.log('Форма загрузки найдена');
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('Форма отправлена');
            let formData = new FormData();
            let fileInput = document.getElementById('fileInput');
            if (fileInput.files.length > 0) {
                console.log('Файл выбран:', fileInput.files[0].name);
                formData.append('file', fileInput.files[0]);
            } else {
                console.error('Файл не выбран');
                alert('Пожалуйста, выберите файл для загрузки');
                return;
            }
            
            // Показать индикатор загрузки
            document.getElementById('loadingIndicator').style.display = 'block';
            console.log('Индикатор загрузки отображен');
            
            console.log('Отправка запроса на сервер...');
            fetch('/upload_video/', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                console.log('Получен ответ от сервера:', response.status);
                if (!response.ok) {
                    throw new Error('Ошибка сети или сервера: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('Получены данные от сервера:', data);
                if (data.clips && data.clips.length > 0) {
                    console.log('Найдены клипы, отображаем...');
                    displayClips(data.clips);
                } else {
                    console.error('Клипы не были получены');
                    alert('Не удалось получить клипы. Пожалуйста, попробуйте еще раз.');
                }
            })
            .catch(error => {
                console.error('Ошибка при обработке видео:', error);
                alert('Произошла ошибка при обработке видео: ' + error.message);
            })
            .finally(() => {
                // Скрыть индикатор загрузки
                document.getElementById('loadingIndicator').style.display = 'none';
                console.log('Индикатор загрузки скрыт');
            });
        });
    } else {
        console.error('Форма загрузки не найдена');
    }
});

function displayClips(clips) {
    console.log('Отображение клипов:', clips);
    let container = document.getElementById('clipsContainer');
    if (container) {
        container.innerHTML = '';
        clips.forEach((clip, index) => {
            console.log(`Создание элемента для клипа ${index + 1}:`, clip);
            let clipElement = document.createElement('div');
            clipElement.className = 'clip';
            clipElement.innerHTML = `
                <video width="320" height="240" controls>
                    <source src="${clip.clip_path}" type="video/mp4">
                    Ваш браузер не поддерживает видео тег.
                </video>
                <p><strong>Название:</strong> <input type="text" value="${clip.metadata.title || ''}"></p>
                <p><strong>Описание:</strong> <textarea>${clip.metadata.description || ''}</textarea></p>
                <p><strong>Хештеги:</strong> <input type="text" value="${clip.metadata.hashtags ? clip.metadata.hashtags.join(' ') : ''}"></p>
                <button onclick="downloadClip('${clip.clip_path}')">Скачать</button>
            `;
            container.appendChild(clipElement);
        });
        console.log('Все клипы отображены');
    } else {
        console.error('Контейнер для клипов не найден');
    }
}

function downloadClip(clipPath) {
    console.log('Попытка скачать клип:', clipPath);
    window.location.href = `/download_clip/?clip_name=${encodeURIComponent(clipPath)}`;
}
