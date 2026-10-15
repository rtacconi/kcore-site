(function () {
    var banner = document.querySelector(".docs-version-banner");
    if (!banner) return;

    function versionsUrl() {
        var path = window.location.pathname;
        if (/\/docs\/\d+\.\d+\.\d+\//.test(path)) return "../../versions.json";
        return "../versions.json";
    }

    function pageName() {
        var parts = window.location.pathname.split("/");
        return parts[parts.length - 1] || "index.html";
    }

    function currentVersion() {
        var marked = banner.getAttribute("data-docs-version");
        if (marked && marked !== "latest") return marked;
        var match = window.location.pathname.match(/\/docs\/(\d+\.\d+\.\d+)\//);
        return match ? match[1] : "";
    }

    function hrefFor(version, latest) {
        var page = pageName();
        if (!version || version === latest) return "../user/" + page;
        return "../" + version + "/user/" + page;
    }

    fetch(versionsUrl())
        .then(function (response) {
            if (!response.ok) throw new Error("versions.json");
            return response.json();
        })
        .then(function (doc) {
            var versions = doc.versions || [];
            if (!versions.length) return;
            var latest = doc.latest || versions[0].version;
            var selected = currentVersion() || latest;
            var label = document.createElement("label");
            label.className = "docs-version-switch";
            label.appendChild(document.createTextNode("kcore "));
            var select = document.createElement("select");
            select.setAttribute("aria-label", "Documentation version");
            versions.forEach(function (entry) {
                var option = document.createElement("option");
                option.value = entry.version;
                option.textContent = entry.version === latest ? entry.version + " (latest)" : entry.version;
                if (entry.version === selected) option.selected = true;
                select.appendChild(option);
            });
            select.addEventListener("change", function () {
                window.location.href = hrefFor(select.value, latest);
            });
            label.appendChild(select);
            banner.textContent = "";
            banner.appendChild(label);
            var note = document.createElement("span");
            var shown = versions.filter(function (entry) { return entry.version === selected; })[0] || versions[0];
            note.textContent = " Documents kcore " + shown.version + ".";
            banner.appendChild(note);
        })
        .catch(function () {});
})();
