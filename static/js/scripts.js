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

            document.getElementById('overlay').style.display = 'block';
            document.getElementById('popup').style.display = 'flex';
            
            document.getElementById('popup-button').value = 'Potvrdit';
            document.getElementById('popup-button').onclick = function() { giftClaim(name); };
        }
    });
}

function giftClaim(name) {
    $.ajax({
        type: "POST",
        url: "/claim",
        data: { name: name },
        success: function(response) {
            if (response == "success") {
                document.getElementById('claim-result').innerHTML = 'Svatební dar úspěšně rezervován';
                document.getElementById('claim-result').style.color = 'green';
    
                document.getElementById('popup-button').value = 'Zavřít';
                document.getElementById('popup-button').onclick = closePopup;
    
                updateGiftState(name, true);
            }
        }
    });
}

function popupFree(itemId) {
    var name = itemId;
    
    // Display response in the pop-up
    document.getElementById('popup-content').innerHTML = (
        "<p>Zadej kód pro uvolnění daru:</p>");

    document.getElementById('overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'flex';
    document.getElementById('code-input').style.display = 'block';
    
    document.getElementById('popup-button').value = 'Potvrdit';
    document.getElementById('popup-button').onclick = function() { giftFree(name); };
}

function giftFree(name) {
    const regex = /^[0-9A-F]*$/; // Regular expression for hexadecimal characters
    var code = document.getElementById('code-input').value.toUpperCase();

    if (code == null || code == "") {
        inputError(document.getElementById('code-input'),
                   document.getElementById('claim-result'),
                   'Pole pro kód je prázdné')
        return -1;
    }

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
            switch(response) {
                case "success":
                    document.getElementById('claim-result').innerHTML = 'Svatební dar úspěšně uvolněn';
                    document.getElementById('claim-result').style.color = 'green';

                    document.getElementById('popup-button').value = 'Zavřít';
                    document.getElementById('popup-button').onclick = closePopup;

                    updateGiftState(name, false);
                    break;

                case "error":
                    inputError(document.getElementById('code-input'),
                               document.getElementById('claim-result'),
                               'Nesprávný kód pro tento dar')
                    break;
            }
        }
    });

}

function inputError(inputField, msgField, msg) {
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