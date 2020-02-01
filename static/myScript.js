function charLeft(val, maxLength) {
	var remaining = maxLength - val.value.length;
	document.getElementById("charLeft").innerHTML = remaining + " characters left"
}

