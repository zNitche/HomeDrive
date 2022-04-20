function getFileName(myFile){
   var file = myFile.files[0];

   document.getElementById("file_name").innerHTML = file.name;
   document.getElementById("file_name").value = file.name;
   document.getElementById("upload_button").style.display = "block";
}

function showDirSelect(space){
   if (space == "shared") {
        document.getElementById("dirs").style.display = "none";
        document.getElementById("dirs_label").style.display = "none";
   }
   else {
        document.getElementById("dirs").style.display = "inline";
        document.getElementById("dirs_label").style.display = "block";
   }
}

function showDeleteModal(value){
    document.getElementById('delete-modal').style.display='flex'
    document.getElementById('delete-modal-button').value = value;
    document.getElementById('delete-file-name').innerText = "Do you want to delete " + value + " ?";
}

function closeDeleteModal(){
    document.getElementById('delete-modal').style.display='none';
}

function uploadProgressHandler(event) {
    var progress = Math.floor((event.loaded / event.total) * 100);

    document.getElementById('upload-progress-title').innerHTML = "Upload Progress (" + progress + "%):";
    document.getElementById('upload-progress-bar').value = progress;
}

function uploadCompleteHandler(event, success_endpoint) {
    window.location.replace(success_endpoint);
}

function asyncSendFile(upload_endpoint, success_endpoint) {
    const xhr = new XMLHttpRequest();

    var file = document.getElementById("file-upload").files[0];

    xhr.upload.addEventListener("progress", uploadProgressHandler, false);
    xhr.addEventListener("load", uploadCompleteHandler.bind(null, event, success_endpoint), false);

    try {
        xhr.open("POST", upload_endpoint, true);

        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.setRequestHeader("X-File-Name", file.name);
        xhr.setRequestHeader("Content-Type", file.type||"application/octet-stream");

        document.getElementById("upload-progress-container").style.display = "flex";

        xhr.send(file);
    }

    catch {
        document.getElementById("upload-message").innerHTML = "Error while uploading file";
    }
}
