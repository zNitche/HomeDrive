function getFileName(myFile){
   var file = myFile.files[0];

   document.getElementById("file_name").innerHTML = file.name;
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