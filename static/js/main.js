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
