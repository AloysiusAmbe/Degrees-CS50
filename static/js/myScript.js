
// var memoryLoaded = false;
// if (!memoryLoaded) {
//     $('body').css('opacity', '0.1');
//     $('#clackers').css('display', 'flex');

//     // Server request
//     const load_data_request = new XMLHttpRequest();
//     load_data_request.open('POST', '/load_data');
//     load_data_request.onload = () => {
//         $('body').css('opacity', '1');
//         $('#clackers').css('display', 'none');
//         memoryLoaded = true;
//     }
//     load_data_request.send();
// }


// Initializing needed variables
var scraped_data;
var current_slide = 0;
var images = document.getElementById('images'); // Gets images div
var star1 = document.getElementById('star1');
var star2 = document.getElementById('star2');
var star1_id = null;
var star2_id = null;

// Button on main page is clicked
document.getElementById('button').addEventListener('click', () => {
    let data_to_send = {
        'star1': star1.value,
        'star2': star2.value,
        'by_star_name': 'true'
    };
    getConnectionsFromServer(data_to_send);
});

// When the button on the multiple star page is clicked
document.querySelector('.by-star-id-btn').addEventListener('click', () => {
    // Gets the stars selected by the user
    if (star1_id == null)
        star1_id = document.querySelector('input[name=first-star-id]:checked').value;
    
    if (star2_id == null)
        star2_id = document.querySelector('input[name=second-star-id]:checked').value;

    let data_to_send = {
        'star1_id': star1_id,
        'star2_id': star2_id,
        'by_star_name': 'false'
    };

    // Gets the connection between two stars
    getConnectionsFromServer(data_to_send);
    document.querySelector('#multiple-stars').style.display = 'none';

    star1_id = null;
    star2_id = null;
});

// Sends the entered data to the server to get the connection between two actors
function getConnectionsFromServer(data_to_send) {
    // Gets the chosen speed by the user
    let speed_option = document.querySelector('input[name=option]:checked').value;
    speed_option = speed_option.toLowerCase();

    // Getting needed elements
    const clackers = document.getElementById('clackers');
    const main_content = document.getElementById('main');
    const main_images = document.getElementById('images');
    const fast_div = document.querySelector('#fast');
    let degrees = document.querySelector('#degree');
    let message = document.getElementById('message');

    // Displays the loading screen and hides other elements
    main_content.style.display = 'none';
    main_images.style.display = 'none';
    fast_div.style.display = 'none';
    clackers.style.display = 'block';
    message.style.display = 'none';
    degrees.style.display = 'none';

    // Server request
    const request = new XMLHttpRequest();
    request.open('POST', '/connection');

    // When request finish loading
    request.onload = () => {
        var data = JSON.parse(request.responseText); // Extracts the JSON data
        scraped_data = data;
        clackers.style.display = 'none';

        if (data_to_send.by_star_name == 'true') {
            // Removes the previous input and label elements
            let first = document.querySelector('#first');
            let second = document.querySelector('#second');
            first.querySelectorAll('div').forEach(removeAllChildNodes);
            second.querySelectorAll('div').forEach(removeAllChildNodes);

            document.querySelector('#first-star').innerHTML = data_to_send.star1;
            document.querySelector('#second-star').innerHTML = data_to_send.star2;

            let msg = document.querySelector('#msg');
            if (data.status == 'both') {
                msg.innerHTML = 'Both stars have multiple people with thesame name. Please select one of each.';
                queryForStarId(data.first_star, 'first', first);

                queryForStarId(data.second_star, 'second', second);
                document.querySelector('#multiple-stars').style.display = 'grid';
                return;
            }

            else if (data.status == 'has_multiple_first') {
                msg.innerHTML = 'First star has multiple people with thesame name. Please select one.';
                queryForStarId(data.first_star, 'first', first);

                second.innerHTML = `Second star's ID: ${data.second_star}`;
                star2_id = data.second_star;
                document.querySelector('#multiple-stars').style.display = 'grid';
                return;
            }

            else if (data.status == 'has_multiple_second') {
                msg.innerHTML = 'Second star has multiple people with thesame name. Please select one.';
                queryForStarId(data.second_star, 'second', second);

                first.innerHTML = `First star's ID: ${data.first_star}`;
                star1_id = data.first_star;
                document.querySelector('#multiple-stars').style.display = 'grid';
                return;
            }

            // Checks whether there was a problem
            if (data.success == false) {
                message.innerHTML = data.message;
                message.style.display = 'flex';

                main_content.style.display = 'flex';
                return;
            }
        }

        // If the user wants the connection to be displayed fast and without images
        if (speed_option == 'fast') {
            removeAllChildNodes(fast_div);
            for (let [key, value] of Object.entries(data)) {
                let text_div = document.createElement('div');
                text_div.className = 'text-div';
                let index = 0;
                for (let [key, val] of Object.entries(value)) {
                    let div = document.createElement('div');
                    let h5 = document.createElement('h5');
                    if (index == 0) {
                        h5.innerHTML = `${val} stars in `;
                    }
                    if (index == 1) {
                        h5.innerHTML = `"${val}" with `;
                    }
                    if (index == 2) {
                        h5.innerHTML = `${val}.`;
                    }

                    div.appendChild(h5);
                    text_div.appendChild(div);
                    index++;
                }
                fast_div.appendChild(text_div);
            }
            fast_div.style.display = 'flex';
        }

        // Scraped images displayed
        else {
            changesImgAtributes('route0');
            main_images.style.display = 'flex';
        }

        main_content.style.display = 'flex';
        main_content.style.height = 'auto';
        degrees.style.display = 'flex';
        document.getElementById('dont-show').style.display = 'none';
        document.getElementById('show-after-load').style.height = '15vh';
        degrees.innerHTML = `${Object.keys(data).length} degrees of separation.`;
    }

    // Add data to send with request
    const data = new FormData();
    data.append('speed_option', speed_option);
    for (let [key, value] of Object.entries(data_to_send))
        data.append(key, value);

    // Send request
    request.send(data)
    return false;
}

// Clears div so results for new query can be put on web page
function removeAllChildNodes(parent) {
    while (parent.firstChild)
        parent.removeChild(parent.firstChild);
}

// Incase there are more than one star with thesame name
function queryForStarId(star_data, star_position, parent) {
    let index = 0;
    for (let [key, value] of Object.entries(star_data)) {
        // Creates input element
        let input = document.createElement('input');
        let input_id = `${star_position}-star-${index}`;
        input.setAttribute('name', `${star_position}-star-id`);
        input.setAttribute('type', 'radio');
        input.setAttribute('value', value.person_id);
        input.setAttribute('id', input_id);

        if (value.birth != '')
            input.checked = true;

        // Creates label element
        let label = document.createElement('label');
        label.setAttribute('class', 'mb-2 mr-sm-2');
        let labelText = `${value.name} | ID: ${value.person_id} | Birth: ${value.birth}`;
        label.innerHTML = labelText;
        label.htmlFor = input_id;

        // Putting the label and input into the DOM
        let div_elem = document.createElement('div');
        div_elem.appendChild(input);
        div_elem.appendChild(label);
        parent.appendChild(div_elem);
        index++;
    }
}

// Moves carousel to the right
document.getElementById('circle-btn-right').addEventListener('click', () => {
    let dataLength = Object.keys(scraped_data).length;
    if (current_slide != dataLength - 1) {
        current_slide++;
        // Function call to change img attribute
        changesImgAtributes();
    }
});

// Moves carousel to the left
document.getElementById('circle-btn-left').addEventListener('click', () => {
    if (current_slide != 0) {   
        current_slide--;
        // Function call to change img attribute
        changesImgAtributes();
    }
});

// Changes the img attributes in the image divs
function changesImgAtributes() {
    // Gets the imgs and texts tags
    let images = document.querySelectorAll('.main-img');
    let texts = document.querySelectorAll('.main-text');

    // Sets an index to loop over the selected tags
    let index = 0;
    let key_index = `route${current_slide}`;

    for (let [key, value] of Object.entries(scraped_data[`${key_index}`])) {
        // Changes the src and alt value of the img tags
        let img = images[index];
        img.src = value;
        img.alt = key;

        // Changes the text to match the scraped data
        texts[index].innerHTML = key;
        index++;
    }
}

// Shows suggestions for the star1 input field
star1.addEventListener('keyup', () => {
    showHint(star1.value, star1);
});

// Shows suggestions for the star2 input field
star2.addEventListener('keyup', () => {
    showHint(star2.value, star2);
});

// Makes a server request to get input suggestions
function showHint(str, elementName) {
    let txtHint = document.getElementById("txtHint");
    str = str.trim();
    if (str.length == 0) {
        txtHint.innerHTML = "";
        return;
    }

    const request = new XMLHttpRequest;
    request.open('POST', '/gethint');

    request.onload = () => {
        const data = JSON.parse(request.responseText); // Extracts the JSON data
        
        let suggestions = '';
        for (let [key, value] of Object.entries(data)) {
            suggestions += value + ', ';
        }
        txtHint.innerHTML = suggestions;
    }
    // Sends data to server
    const data = new FormData();
    data.append('input', str);

    // Send request
    request.send(data);
    return false;
}
