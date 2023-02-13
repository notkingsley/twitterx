function follow(user)
{
	var elems = document.getElementsByClassName("follow-button");
	for(let i = 0; i < elems.length; i++){
		let elem = elems[i];
		if (elem.getAttribute("data-bs-user") != user)
			continue;

		if (elem.innerHTML.trim().includes("Follow"))
			elem.innerHTML = elem.innerHTML.replace("Follow", "Unfollow");
		else
			elem.innerHTML = elem.innerHTML.replace("Unfollow", "Follow");
	}
}