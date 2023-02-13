var elems = document.getElementsByClassName("require-redirect-input");
for(let i = 0; i < elems.length; i++){
	var input = document.createElement("input");
	input.setAttribute("type", "hidden");
	input.setAttribute("name", "r");
	input.setAttribute("value", document.URL);

	let elem = elems[i]
	elem.appendChild(input)
}