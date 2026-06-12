export function initLogMessageBtns() {
    const closeAlertBtn = document.querySelector("#close-alert")

    closeAlertBtn.addEventListener("click", () => {
        document.querySelector("#log-message").setAttribute("hidden", "hidden")
    })
}

export function setLogMessage(msg, className) {
    const logBlock = document.querySelector("#log-message")
    const alertMessage = document.querySelector("#alert-message")

    const classNameList = [
        "alert-success", 
        "alert-warning", 
        "alert-danger", 
        "alert-secondary"
    ]
    const usageClassList = classNameList.slice()


    alertMessage.textContent = msg
    alertMessage.classList.add(
        ...usageClassList.splice(usageClassList.indexOf(className), 1))
    alertMessage.classList.remove(...usageClassList)

    logBlock.removeAttribute("hidden")
}

export function validateEmail(email){
  return String(email)
    .toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    )
}

export function parseDetail(detail) {
    let msg = detail

    if (Array.isArray(detail))
        msg = detail[0]["msg"]

    return msg
}