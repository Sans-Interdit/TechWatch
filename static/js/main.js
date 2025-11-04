// Marquer un article comme lu visuellement quand on clique dessus
document.addEventListener('DOMContentLoaded', () => {
    const articles = document.querySelectorAll('.article');
    articles.forEach(article => {
        article.addEventListener('click', () => {
            article.classList.add('read');
        });
    });
});
