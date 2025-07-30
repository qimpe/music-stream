
        const queryParams = new URLSearchParams(window.location.search);
        const code = queryParams.get('code')
        const state = queryParams.get('state')
        if (code) {
            fetch("{% url 'users:google_auth_callback' %}", {
                body: JSON.stringify({ code }),
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            })
                .then(res => {
                    if (!res.ok) {
                        throw new Error('Ошибка сервера')
                    }
                    return res.json()
                })

        } else {
            this.message = '⚠️ Нет параметра code';
        }
