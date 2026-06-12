import {initLogMessageBtns, parseDetail, setLogMessage, validateEmail} from "./base.js"

window.addEventListener("DOMContentLoaded", () => {
    initLogMessageBtns()
    const reactionInp = document.querySelector("#reaction")
    const photoInp = document.querySelector("#photo")
    const descriptionInp = document.querySelector("#description")
    const addDayBtn = document.querySelector("#add-day")

    addDayBtn.addEventListener("click", async () => {
        if (descriptionInp.value.length < 16) {
            setLogMessage(
                "description is too small that your friends can understand you",
                "alert-danger"
            )
            return
        } else if (descriptionInp.value.length > 1024) {
            setLogMessage(
                "description is too large to save in our storage",
                "alert-danger"
            )
            return
        }

        const res = await fetch("/api/days/", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "reaction": reactionInp.value,
                "description": descriptionInp.value
            })
        })
        const response = await res.json()

        if (!res.ok) {
            setLogMessage(parseDetail(response["detail"]), "alert-danger")
            return
        }

        const dayId = response["day_id"]

        if (photoInp.files[0]) {
            const data = new FormData()
            data.append("file", photoInp.files[0])

            const photoRes = await fetch(`/api/days/${dayId}/photo/upload`, {
                method: "POST",
                // headers: {
                //     "Accept": "application/json",
                //     "Content-Type": "application/json"
                // },
                body: data
            })
            const photoResponse = await photoRes.json()

            if (!photoRes.ok) {
                setLogMessage(parseDetail(photoResponse["detail"]), "alert-danger")
                return
            }
        }

        setLogMessage("Day was successfully uploaded", "alert-success")
    })
    document.querySelector("#check-and-load").addEventListener("click", () => {
        setPreview({
            reaction: reactionInp.value,
            description: descriptionInp.value,
            photo: photoInp.files[0]
        })
    })
})

function setPreview({ reaction, description, photo }) {
    const previewDescription = document.querySelector("#preview-description")
    const previewReaction = document.querySelector("#preview-reaction")
    const previewPhoto = document.querySelector("#preview-photo")

    previewDescription.textContent = description
    previewReaction.textContent = reaction

    if (photo)
        previewPhoto.src = URL.createObjectURL(photo)

    document.querySelector("#preview").removeAttribute("hidden")
    document.querySelector("#add-day").disabled = false
}