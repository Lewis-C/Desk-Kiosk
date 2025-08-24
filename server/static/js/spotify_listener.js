var socket = io();
const originalHtmlContent = document.getElementById("warton-spotify").innerHTML;

socket.once('connect', function() {
    console.log("Connected - Initial Message Sent")
    socket.emit("listener_spotify_message",'Connection Made');
});


socket.on('socket_spotify_message', function(socket_spotify_data) {
    display_spotify(socket_spotify_data);
    socket.emit("listener_spotify_message","Currently Playing Recieved");
});

function display_spotify(track_details) {
    
    let htmlContent = originalHtmlContent;
    if (track_details['track_name']){
        htmlContent = `
        <legend>Spotify</legend>
        <img class="track-text" id="track-album-image" src="${track_details['track_album_art']}" alt="Album Art"> 
        <h1 class="track-text" id="track-name">${track_details['track_name']}</h1>
        <div class="row" id="track-info">
            <h3 class="track-text" id="track-artist">${track_details['track_artist']}</h3>
            <h3 class="track-text" id="track-album">${track_details['track_album']}</h3>
        </div>
        `;
    } else {
        htmlContent = originalHtmlContent;
    }
    
    document.getElementById("warton-spotify").innerHTML = htmlContent;
}