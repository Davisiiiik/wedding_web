function smooth_scroll() {
    // Smooth scrolling for menu links
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            // Get link where to go ad scroll smoothly
            const target = document.querySelector(this.getAttribute('href'));
            window.scrollTo({
                top: target.offsetTop,
                behavior: 'smooth'
            });

            // Update the URL with section name
            const url = new URL(window.location.href);
            url.hash = this.getAttribute('href');

            // If chosen section is "home", leave URL appendix blank
            if (url.hash === "#home") {
                url.hash = ''
            }
            history.pushState(null, null, url);
        });
    });
}

function highligh_active_section() {
    // JavaScript code to handle scroll event and highlight the menu item
    window.addEventListener('scroll', function() {
        var sections = document.querySelectorAll('section');
        var scrollPosition = window.scrollY;

        sections.forEach(function(section) {
            var top = section.offsetTop;
            var height = section.offsetHeight;
            var id = section.getAttribute('id');

            // Set current section as active
            if (scrollPosition >= top && scrollPosition < top + height) {
                document.querySelector('a[href="#' + id + '"]').classList.add('active');
            } else {
                document.querySelector('a[href="#' + id + '"]').classList.remove('active');
            }
        });
    });
}

function popupClaim(itemId) {
    var name = itemId;

    $.ajax({
        type: "POST",
        url: "/get_info",
        data: { name: name },
        success: function(response) {
            // Display response in the pop-up
            document.getElementById('popup-content').innerHTML = (
                "<p>Chystáš se zarezervovat svatební dar</p>" +
                "<h2>" + response[0] + "</h2>" +
                "<p>Před potvrzením rezervace si prosím nejprve opiš kód pro uvolnění:</p>" +
                "<h3>" + response[1] + "</h3>");

            // Show Popup with claim information to user
            document.getElementById('overlay').style.display = 'block';
            document.getElementById('popup').style.display = 'flex';

            // Set Popups button text and function
            document.getElementById('popup-button').value = 'Potvrdit';
            document.getElementById('popup-button').onclick = function() { giftClaim(name, response[1]); };
        }
    });
}

function giftClaim(name, code) {
    $.ajax({
        type: "POST",
        url: "/claim",
        data: { name: name, code: code },
        success: function(response) {
            // Inform user if the claim attempt was successful
            switch(response) {
                case "success":
                    document.getElementById('claim-result').innerHTML = 'Svatební dar úspěšně rezervován';
                    document.getElementById('claim-result').style.color = 'green';
                    break;

                case "error":
                default:
                    inputError(document.getElementById('code-input'),
                               document.getElementById('claim-result'),
                               'Svatební dar už byl zarezervován někým jiným')
                    break;
            }

            // Change confirm button to close button for both cases
            document.getElementById('popup-button').value = 'Zavřít';
            document.getElementById('popup-button').onclick = closePopup;
            // Update gift as claimed for both cases
            updateGiftState(name, true);
        }
    });
}

function popupFree(itemId) {
    var name = itemId;
    
    // Display response in the pop-up
    document.getElementById('popup-content').innerHTML = (
        "<p>Zadej kód pro uvolnění daru:</p>");

    // Show Popup with claim information to user
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'flex';
    document.getElementById('code-input').style.display = 'block';
    
    // Set Popups button text and function
    document.getElementById('popup-button').value = 'Potvrdit';
    document.getElementById('popup-button').onclick = function() { giftFree(name); };
}

function giftFree(name) {
    const regex = /^[0-9A-F]*$/; // Regular expression for hexadecimal characters
    var code = document.getElementById('code-input').value.toUpperCase();

    // If the field is empty, return error
    if (code == null || code == "") {
        inputError(document.getElementById('code-input'),
                   document.getElementById('claim-result'),
                   'Pole pro kód je prázdné')
        return -1;
    }

    // If the content is outside the const regex scope, return error
    if (!regex.test(code)) {
        inputError(document.getElementById('code-input'),
                   document.getElementById('claim-result'),
                   'Pole pro kód obsahuje nepovolené znaky')
        return -1;
    }

    $.ajax({
        type: "POST",
        url: "/free",
        data: { name: name, code: code },
        success: function(response) {
            // Inform user if the free attempt was successful
            switch(response) {
                case "success":
                    document.getElementById('claim-result').innerHTML = 'Svatební dar úspěšně uvolněn';
                    document.getElementById('claim-result').style.color = 'green';

                    // Change confirm button to close button
                    document.getElementById('popup-button').value = 'Zavřít';
                    document.getElementById('popup-button').onclick = closePopup;

                    // Update gift as NOT claimed
                    updateGiftState(name, false);
                    break;

                case "error":
                default:
                    inputError(document.getElementById('code-input'),
                               document.getElementById('claim-result'),
                               'Nesprávný kód pro tento dar')
                    break;
            }
        }
    });

}

function inputError(inputField, msgField, msg) {
    // Shake input field on error
    inputField.classList.add('shake');
    setTimeout(function() { inputField.classList.remove('shake'); }, 500); // 0.5 seconds
    msgField.innerHTML = msg;
    msgField.style.color = 'red';
}

function closePopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
    document.getElementById('code-input').style.display = 'none';
    document.getElementById('code-input').value = '';
    document.getElementById('claim-result').innerHTML = '';
}

function updateGiftState(giftName, newStateClaimed) {
    // Update Claim/Free state title for particular gift
    giftState = document.getElementById(giftName + '_state');
    giftState.style.color = newStateClaimed ? 'red' : 'green';
    giftState.innerHTML = newStateClaimed ? 'Rezervované' : 'Volné';

    // Update Claim/Free button for particular gift
    giftButton = document.getElementById(giftName + '_button');
    giftButton.onclick = newStateClaimed ? function() { popupFree(giftName); } : function() { popupClaim(giftName); };
    giftButton.innerHTML = newStateClaimed ? 'Uvolnit' : 'Rezervovat';
}