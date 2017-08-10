var IDs = ["1", "2", "3", "4"]


function render_table () {
	for (var i=0, l=IDs.length; i<l; i++) { 
		ele = document.getElementById(IDs[i])
		if (ele.getAttribute("selectable") === "False") {
			ele.childNodes[1].innerHTML = "（不可选）"
		} else if (ele.getAttribute("selected") === "False") {
			ele.childNodes[1].innerHTML = "（可选）"
		} else if (ele.getAttribute("selected") === "True") {
			ele.childNodes[1].innerHTML = "（已选）"
		}
	}
}


function click_toggle (ele) {
	if (ele.getAttribute("selectable") !== "False") {
		if (ele.getAttribute("selected") === "False") {
			ele.setAttribute("selected", "True");
			ele.childNodes[3].setAttribute("value", "True");
		} else if (ele.getAttribute("selected") === "True") {
			ele.setAttribute("selected", "False");
			ele.childNodes[3].setAttribute("value", "False");
		}
	} else {
		ele.childNodes[3].setAttribute("value", "False");
	}
	render_table();
}


window.onload = function () {
	render_table();
	for (var i=0, l=IDs.length; i<l; i++) { 
		ele = document.getElementById(IDs[i])
		if (ele.getAttribute("selectable") === "True") {
			ele.onclick = function (ele) {
				return function () {
					return click_toggle(ele);
				}
			}(ele);
		}
	}
}
