function follow()
{
    var elem = document.getElementById("follow-button");
    if (elem.innerHTML.trim() == "Follow")
		elem.innerHTML = "Unfollow";
    else
		elem.innerHTML = "Follow";
}