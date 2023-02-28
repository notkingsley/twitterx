var elems = document.getElementsByClassName("submit-on-click");
for(let i = 0; i < elems.length; ++i){
	let button = elems[i];
	button.addEventListener("click", function (e) {
		e.preventDefault();
		submit_click(this);
	});
}

function submit_click(button){
	var form = document.createElement('form');
	form.setAttribute('method', 'post');
	form.setAttribute('action', button.getAttribute("data-bs-url"));
	form.style.display = 'hidden';
	
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]');
	var input = document.createElement("input");
	input.setAttribute("type", "hidden");
	input.setAttribute("name", "csrfmiddlewaretoken");
	input.setAttribute("value", csrftoken.value);
	
	form.appendChild(input)
	document.body.appendChild(form)
	form.submit();
	document.body.removeChild(form)
}