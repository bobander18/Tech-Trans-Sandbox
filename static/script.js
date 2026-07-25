// ---------- Gloabl Variables ----------
// ---------- Application State ----------
let editingNoteId = null;
let currentPage = 1;
let currentSearch = "";
let totalPages = 1;
// ---------- DOM Elements ----------
const loadProfileButton = document.getElementById("load-profile");
const createNoteButton = document.getElementById("create-note");
const notesContainer = document.getElementById("notes-container");
const searchNoteButton = document.getElementById("search-note");
const previousPageButton = document.getElementById("previous-page");
const nextPageButton = document.getElementById("next-page");

// ---------- Profile ----------
if(loadProfileButton){
    loadProfileButton.addEventListener("click", loadProfile);
}

async function loadProfile(){
    const response = await fetch("/api/profile");
    const data = await response.json();
    console.log(data);
    const usernameElement = document.getElementById("username-display");
    usernameElement.textContent = data.username;
}

// ---------- Notes ----------
if (createNoteButton){
    createNoteButton.addEventListener("click", createNote);
}

async function createNote(){
    const titleInput = document.getElementById("note-title");
    const contentInput = document.getElementById("note-content");
    const title = titleInput.value;
    const content = contentInput.value;
    if(!title.trim() && !content.trim()){
        return;
    }
    const note = {
        title,
        content
    };
    let url = "/api/notes";
    let method = "POST";
    if(editingNoteId !== null){
        url = `/api/notes/${editingNoteId}`;
        method="PUT";
    }
    const response = await fetch(url, {
        method,
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify(note)
    });
    const data = await response.json();
    if(!response.ok){
        console.log("Could not create note:", data.error);
        return;
    };
    titleInput.value = "";
    contentInput.value = "";
    editingNoteId=null;
    if(method === "POST"){
        console.log("Created note.");
    } else {
        console.log("Updated note.")
    }
    if(response.ok){
        loadNotes();
    }
}

if(notesContainer){
    loadNotes();
}

async function loadNotes(search="", page = 1){
    const response = await fetch(
        `/api/notes?search=${encodeURIComponent(search)}&page=${encodeURIComponent(page)}`
    );
    const data = await response.json();
    const notes = data.notes;
    totalPages = data.totalPages;
    updatePaginationButtons();
    notesContainer.innerHTML = "";
    for (const note of notes){
        const noteElement=createNoteElement(note);
        notesContainer.appendChild(noteElement);
    }
}

function createNoteElement(note){
    const noteElement = document.createElement("div");
    noteElement.classList.add("note");
    noteElement.innerHTML = `
        <h2>${note.title}</h2>
        <p>${note.content}</p>
        <button class="edit-button" data-note-id="${note.id}">Edit</button>
        <button class="delete-button" data-note-id="${note.id}">Delete</button>
    `;
    const editButton = noteElement.querySelector(".edit-button")
    editButton.addEventListener("click", async function(){
        editingNoteId = note.id;
        document.getElementById("note-title"). value = note.title;
        document.getElementById("note-content").value = note.content;
    });
    const deleteButton = noteElement.querySelector(".delete-button")
    deleteButton.addEventListener("click", async function(){
        const response = await fetch(`/api/notes/${note.id}`, {
            method:"DELETE"
        });
        if(response.ok){
            loadNotes();
        };
    });
    return noteElement;
}

// ---------- Search ----------
if (searchNoteButton){
    searchNoteButton.addEventListener("click", searchNote);
}

async function searchNote(){
    const searchInput = document.getElementById("note-search-box");
    currentSearch = searchInput.value.trim();
    currentPage = 1;
    loadNotes(currentSearch, currentPage);
}

// ---------- Pagination ----------
if(previousPageButton){
    previousPageButton.addEventListener("click", previousPage);
}

if(nextPageButton){
    nextPageButton.addEventListener("click", nextPage);
}

function previousPage(){
    if(currentPage>1){
            currentPage--;
            loadNotes(currentSearch,currentPage);
    }
}

function nextPage(){
    if(currentPage<totalPages){
        currentPage++;
        loadNotes(currentSearch,currentPage);
    }
}

function updatePaginationButtons(){
    if (previousPageButton){
        previousPageButton.disabled = currentPage === 1;
    }
    if(nextPageButton){
        nextPageButton.disabled = currentPage === totalPages;
    }
}