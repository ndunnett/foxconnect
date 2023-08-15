var structure;
var compounds;
var compoundInput;
var blockInput;
var compoundList;
var blockList;

const compoundListId = "compound-list";
const compoundInputId = "compound-input";
const blockListId = "block-list";
const blockInputId = "block-input";
const dropdownButtonId = "cb-dropdown";
const maxListLength = 50;

document.addEventListener('DOMContentLoaded', function() {
    // Fetch data structure
    fetch(structure_json_url)
        .then(response => response.json())
        .then(data => {
            // Separate out compounds
            structure = data;
            compounds = Object.keys(structure);
        })
        .then(_ => {
            // Find relevent elements
            compoundInput = document.getElementById(compoundInputId);
            compoundList = document.getElementById(compoundListId);
            blockInput = document.getElementById(blockInputId);
            blockList = document.getElementById(blockListId);
            
            // Add event listeners
            compoundInput.addEventListener('keyup', populateCompoundList);
            compoundList.addEventListener('click', selectCompound);
            blockInput.addEventListener('keyup', populateBlockList);
            blockList.addEventListener('click', selectBlock);
            
            // Get lists to populate on first load of dropdown
            document.getElementById(dropdownButtonId)
                .addEventListener('click', () => {
                    populateCompoundList();
                    populateBlockList();
                }, { once: true });
        });
}, false);

function getTerms(input, termCandidates) {
    if (input.value.length) {
        // Filter list of term candidates down to match input
        var regex = new RegExp(input.value.toUpperCase())
        return termCandidates.filter(function(candidate) {
            if (candidate.match(regex)) {
                return candidate;
            }
        });
    }

    // If input is empty, just list all term candidates
    return termCandidates;
}

function populateList(input, listElement, termCandidates) {
    var terms = getTerms(input, termCandidates);
    var listItems = '';

    // Populate list HTML
    for (i = 0; i < terms.length; i++) {
        listItems += '<a class="list-group-item list-group-item-action">' + terms[i] + '</a>'
        
        // Cut list short, showing too many items slows things down
        if (i == maxListLength - 1) {
            listItems += '<span class="list-group-item list-group-item-action">' + (terms.length - maxListLength) + ' more entries</span>';
            break;
        }
    }

    listElement.innerHTML = listItems;
}

function populateCompoundList() {
    populateBlockList()
    return populateList(compoundInput, compoundList, compounds);
}

function populateBlockList() {
    blocks = [];

    for (var compound of getTerms(compoundInput, compounds)) {
        blocks = [...blocks, ...structure[compound]];
    }

    return populateList(blockInput, blockList, blocks);
}

function selectItem(target, input) {
    if (target.tagName === 'A') {
        input.value = target.textContent;
        populateCompoundList();
    }
}

function selectCompound({ target }) {
    selectItem(target, compoundInput);
}

function selectBlock({ target }) {
    selectItem(target, blockInput);
}
