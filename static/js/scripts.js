// Smooth scrolling for menu links
function smooth_scroll() {
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const target = document.querySelector(this.getAttribute('href'));
            window.scrollTo({
                top: target.offsetTop,
                behavior: 'smooth'
            });

            // Update URL
            const url = new URL(window.location.href);
            url.hash = this.getAttribute('href');
            //console.info(url.hash)
            if (url.hash === "#home") {
                url.hash = ''
            }
            history.pushState(null, null, url);
        });
    });
}