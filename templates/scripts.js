const CONFIG = {
MAX_CHARS: 5000,
STATUS_ENDPOINT: "/session-status",
API_ENDPOINT: "/generate-audio"
};

class TextToSpeechApp {

constructor() {

    this.textArea = document.querySelector("#text");
    this.fileNameInput = document.querySelector("#filename");
    this.languageSelect = document.querySelector("#language");

    this.counter = document.querySelector("#count");
    this.usedCount = document.querySelector("#usedCount");
    this.remainingCount = document.querySelector("#remainingCount");
    this.sessionExpiry = document.querySelector("#sessionExpiry");
    this.status = document.querySelector("#status");
    this.sessionInfo = document.querySelector("#sessionInfo");

    this.audioPlayer = document.querySelector("#audioPlayer");
    this.audioSection = document.querySelector("#audioSection");
    this.downloadBtn = document.querySelector("#downloadBtn");

    this.currentAudioUrl = null;
    this.remainingGenerations = 5;
    this.statusTimer = null;

    this.initialize();
}

initialize() {

    document.querySelector("#generateBtn").addEventListener(
        "click",
        () => this.generateAudio()
    );

    this.textArea.addEventListener(
        "input",
        () => this.updateCounter()
    );

    this.updateCounter();
    this.updateRemainingCount();
    this.loadSessionStatus();
}

updateCounter() {

    const length = this.textArea.value.length;

    this.counter.textContent = length;

    if (length > CONFIG.MAX_CHARS) {

        this.counter.style.color = "#ff4d4d";

    } else {

        this.counter.style.color = "#ffffff";
    }
}

updateRemainingCount() {

    if (this.remainingCount) {
        this.remainingCount.textContent = this.remainingGenerations;
    }

    if (this.remainingGenerations <= 0) {
        this.showStatus(
            "Generation limit reached for this session.",
            true
        );
        this.setLoading(false);
        document.querySelector("#generateBtn").disabled = true;
    }
}

updateSessionInfo(message, isError = false) {

    if (!this.sessionInfo) {
        return;
    }

    this.sessionInfo.textContent = message;
    this.sessionInfo.style.color = isError ? "#ff6b6b" : "#00ff9d";
}

async loadSessionStatus() {

    try {
        const response = await fetch(CONFIG.STATUS_ENDPOINT, {
            method: "GET",
            headers: { "Accept": "application/json" }
        });

        const data = await response.json();

        if (typeof data.remaining_generations === "number") {
            this.remainingGenerations = data.remaining_generations;
            this.updateRemainingCount();
        }

        if (typeof data.used_generations === "number" && this.usedCount) {
            this.usedCount.textContent = data.used_generations;
        }

        if (typeof data.session_expires_in_minutes === "number" && this.sessionExpiry) {
            this.sessionExpiry.textContent = data.session_expires_in_minutes;
        }

        if (data.session_expired) {
            this.updateSessionInfo("Session expired. Reload the page to start a new one.", true);
        } else {
            this.updateSessionInfo("Session is active on this device.");
        }
    } catch (error) {
        this.updateSessionInfo("Unable to load session status.", true);
    }
}

getFormData() {

    return {
        text: this.textArea.value.trim(),
        filename: this.fileNameInput.value.trim(),
        language: this.languageSelect.value
    };
}

validate(data) {

    if (!data.text) {
        throw new Error("Please enter text");
    }

    if (!data.filename) {
        throw new Error("Please enter filename");
    }

    if (data.text.length > CONFIG.MAX_CHARS) {
        throw new Error(
            `Maximum ${CONFIG.MAX_CHARS} characters allowed`
        );
    }
}

setLoading(isLoading) {

    const button =
        document.querySelector("#generateBtn");

    button.disabled = isLoading;

    button.innerHTML = isLoading
        ? "Generating..."
        : "Generate Audio";
}

showStatus(message, isError = false) {

    if (this.statusTimer) {
        clearTimeout(this.statusTimer);
        this.statusTimer = null;
    }

    this.status.textContent = message;

    this.status.style.color =
        isError
            ? "#ff6b6b"
            : "#00ff9d";

    if (!isError && message) {
        this.statusTimer = setTimeout(() => {
            if (this.status.textContent === message) {
                this.status.textContent = "";
            }
            this.statusTimer = null;
        }, 3000);
    }
}

cleanupOldAudio() {

    if (this.currentAudioUrl) {

        URL.revokeObjectURL(
            this.currentAudioUrl
        );

        this.currentAudioUrl = null;
    }
}

async requestAudio(payload) {

    const controller =
        new AbortController();

    const timeout =
        setTimeout(
            () => controller.abort(),
            30000
        );

    try {

        const response =
            await fetch(
                CONFIG.API_ENDPOINT,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(payload),

                    signal:
                        controller.signal
                }
            );

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";

        const bodyText =
            await response.text();

        let data = {};

        if (bodyText.trim()) {

            if (
                contentType.includes(
                    "application/json"
                )
            ) {
                data = JSON.parse(bodyText);
            } else {
                throw new Error(
                    bodyText
                        .replace(/<[^>]*>/g, " ")
                        .replace(/\s+/g, " ")
                        .trim() ||
                    "Unexpected non-JSON response from server"
                );
            }
        }

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Audio generation failed"
            );
        }

        return data;

    } finally {

        clearTimeout(timeout);
    }
}

applyRemainingLimit(data) {

    if (typeof data.remaining_generations === "number") {
        this.remainingGenerations = data.remaining_generations;
        this.updateRemainingCount();
    }

    if (typeof data.used_generations === "number" && this.usedCount) {
        this.usedCount.textContent = data.used_generations;
    }
}

renderAudio(data) {

    this.cleanupOldAudio();

    this.audioPlayer.src =
        data.audio_data_url;

    this.downloadBtn.href =
        data.audio_data_url;

    this.downloadBtn.download =
        data.download_name;

    this.audioSection.style.display =
        "block";

    this.audioPlayer.load();

    this.audioPlayer.play()
        .catch(() => {});
}

async generateAudio() {

    try {

        this.setLoading(true);

        const payload =
            this.getFormData();

        this.validate(payload);

        this.showStatus(
            "Generating audio..."
        );

        const data =
            await this.requestAudio(
                payload
            );

        this.applyRemainingLimit(data);
        if (typeof data.session_expires_in_minutes === "number" && this.sessionExpiry) {
            this.sessionExpiry.textContent = data.session_expires_in_minutes;
        }
        this.updateSessionInfo("Audio generated on the page.");
        this.renderAudio(data);

        this.showStatus(
            "✅ Audio generated successfully"
        );

    } catch (error) {

        console.error(error);

        this.showStatus(
            error.message,
            true
        );

    } finally {

        this.setLoading(false);
    }
}

}

const app =
new TextToSpeechApp();
