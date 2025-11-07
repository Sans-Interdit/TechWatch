document.addEventListener('DOMContentLoaded', () => {
    const articles = document.querySelectorAll('.article');

    articles.forEach(article => {
        article.addEventListener('click', () => {
            // Récupère le bouton "Lu" dans l'article cliqué
            const readBtn = article.querySelector('.read-btn');
            if (readBtn) {
                readBtn.classList.add('checked');
                readBtn.textContent = "Lu ✔️"; // ajoute le texte ✔️ si nécessaire
            }
        });
    });
});


const searchInput = document.getElementById('tag-search');
const tagsGrid = document.getElementById('tags-grid');
if (searchInput) {
    searchInput.addEventListener('input', async () => {
        const q = searchInput.value.trim();
        const response = await fetch(`/api/tags/search?q=${encodeURIComponent(q)}`);
        const tags = await response.json();

        tagsGrid.innerHTML = tags.length
            ? tags.map(tag => `
                <div class="tag-card">
                    <h2>${tag.name}</h2>
                    <p>${tag.desc}</p>
                </div>
            `).join('')
            : '<p>Aucun tag trouvé.</p>';
    });
}

// const loginForm = document.getElementById('loginForm')
// if (loginForm) {
//     loginForm.addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const formData = new FormData(e.target);
    
//     const response = await fetch('/log', {
//         method: 'POST',
//         body: formData
//     });
    
//     const data = await response.json();
    
//     if (data.token) {
//         localStorage.setItem('token', data.token);
//         window.location.href = '/';
//     } else {
//         console.log(data)
//         document.getElementById('error').textContent = data.error;
//     }
//     });
// }

// const registerForm = document.getElementById('registerForm')
// if (registerForm) {
//     registerForm.addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const formData = new FormData(e.target);
    
//     const response = await fetch('/create_account', {
//         method: 'POST',
//         body: formData
//     });
    
//     const data = await response.json();
    
//     if (data.token) {
//         localStorage.setItem('token', data.token);
//         window.location.href = '/';
//     } else {
//         console.log(data)
//         document.getElementById('error').textContent = data.error;
//     }
//     });
// }