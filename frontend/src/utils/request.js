import m from "mithril";

function requestWithRetry(url, options, retries = 3, delay = 1000) {
    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    const attempt = (remainingRetries, currentDelay) => {
        return m.request({ url, ...options }).catch((error) => {
            if (remainingRetries <= 0) {
                throw error;
            }

            return wait(currentDelay).then(() => attempt(remainingRetries - 1, currentDelay * 2));
        });
    };

    return attempt(retries, delay);
}

export { requestWithRetry };