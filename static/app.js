// HostelMate AI Frontend Application Logic

let sessionId = localStorage.getItem("hostel_session_id");
if (!sessionId) {
    sessionId = "session_" + Math.random().toString(36).substring(2, 9);
    localStorage.setItem("hostel_session_id", sessionId);
}

document.addEventListener("DOMContentLoaded", () => {
    lucide.createIcons();

    const messagesContainer = document.getElementById("messages-container");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const typingIndicator = document.getElementById("typing-indicator");
    const suggestionChips = document.querySelectorAll(".chip");
    
    // Side Drawer elements
    const complaintsDrawer = document.getElementById("complaints-drawer");
    const viewComplaintsBtn = document.getElementById("view-complaints-btn");
    const closeDrawerBtn = document.getElementById("close-drawer-btn");
    const drawerBackdrop = document.getElementById("drawer-backdrop");
    const complaintsList = document.getElementById("complaints-list");
    const complaintsCounter = document.getElementById("complaints-counter");
    const filterBtn = document.getElementById("filter-btn");
    const filterRoomInput = document.getElementById("filter-room-input");
    const refreshComplaintsBtn = document.getElementById("refresh-complaints-btn");

    // Menu Modal elements
    const menuModal = document.getElementById("menu-modal");
    const viewMenuBtn = document.getElementById("view-menu-btn");
    const closeMenuBtn = document.getElementById("close-menu-btn");
    const menuBackdrop = document.getElementById("menu-backdrop");
    const menuModalContent = document.getElementById("menu-modal-content");

    // Reset button
    const resetSessionBtn = document.getElementById("reset-session-btn");

    // Load initial complaints count
    updateComplaintsCount();

    // Event: Submit Chat Message
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        appendUserMessage(message);
        userInput.value = "";
        userInput.disabled = true;
        showTyping(true);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message, session_id: sessionId })
            });

            if (!res.ok) {
                throw new Error(`Server returned ${res.status}`);
            }

            const data = await res.json();
            showTyping(false);
            appendBotMessage(data.response, data.action, data.data);

            // If a complaint was created, refresh counter
            if (data.action === "complaint_created") {
                updateComplaintsCount();
            }
        } catch (err) {
            showTyping(false);
            appendBotMessage("⚠️ *Sorry, I encountered an error connecting to the hostel server. Please try again.*");
            console.error(err);
        } finally {
            userInput.disabled = false;
            userInput.focus();
        }
    });

    // Event: Suggestion Chips
    suggestionChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt");
            userInput.value = prompt;
            chatForm.dispatchEvent(new Event("submit"));
        });
    });

    // Event: Drawer Open/Close
    viewComplaintsBtn.addEventListener("click", () => {
        openComplaintsDrawer();
    });

    closeDrawerBtn.addEventListener("click", closeComplaintsDrawer);
    drawerBackdrop.addEventListener("click", closeComplaintsDrawer);

    filterBtn.addEventListener("click", () => {
        const room = filterRoomInput.value.trim();
        loadComplaints(room);
    });

    filterRoomInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            loadComplaints(filterRoomInput.value.trim());
        }
    });

    refreshComplaintsBtn.addEventListener("click", () => {
        loadComplaints(filterRoomInput.value.trim());
    });

    // Event: Menu Modal
    viewMenuBtn.addEventListener("click", openMenuModal);
    closeMenuBtn.addEventListener("click", closeMenuModal);
    menuBackdrop.addEventListener("click", closeMenuModal);

    // Event: Reset Session
    resetSessionBtn.addEventListener("click", async () => {
        if (confirm("Reset current conversation and start fresh?")) {
            await fetch(`/api/reset-session?session_id=${sessionId}`, { method: "POST" });
            messagesContainer.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shrink-0 shadow-sm">
                        <i data-lucide="bot" class="w-4 h-4"></i>
                    </div>
                    <div class="bg-slate-100/90 text-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%] text-sm leading-relaxed border border-slate-200/60 shadow-sm">
                        <p class="font-medium text-slate-900 mb-1">Session Reset! 👋</p>
                        <p>How can I help you today with hostel services, food timings, or maintenance?</p>
                    </div>
                </div>
            `;
            lucide.createIcons();
        }
    });

    // Helper: Append User Message
    function appendUserMessage(text) {
        const wrapper = document.createElement("div");
        wrapper.className = "flex items-start justify-end space-x-3";
        wrapper.innerHTML = `
            <div class="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%] text-sm leading-relaxed shadow-sm">
                ${escapeHtml(text)}
            </div>
            <div class="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center text-slate-600 shrink-0 text-xs font-bold">
                YOU
            </div>
        `;
        messagesContainer.appendChild(wrapper);
        scrollToBottom();
    }

    // Helper: Append Bot Message
    function appendBotMessage(markdownText, action, data) {
        const wrapper = document.createElement("div");
        wrapper.className = "flex items-start space-x-3";

        let htmlContent = marked.parse(markdownText);

        // Render card if complaint was just created
        let actionCardHtml = "";
        if (action === "complaint_created" && data) {
            const urgencyClass = `badge-urgency-${data.urgency}`;
            const statusClass = `badge-status-${data.status.replace(" ", "-")}`;

            actionCardHtml = `
                <div class="mt-3 p-4 bg-white border border-slate-200 rounded-xl shadow-xs space-y-2.5">
                    <div class="flex items-center justify-between">
                        <span class="font-mono text-xs font-bold bg-slate-100 text-slate-700 px-2 py-1 rounded border border-slate-200">
                            Ticket ${data.id}
                        </span>
                        <div class="flex items-center space-x-1.5">
                            <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold ${urgencyClass}">
                                Urgency: ${data.urgency}
                            </span>
                            <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold ${statusClass}">
                                ${data.status}
                            </span>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-xs text-slate-600 pt-1">
                        <div><span class="text-slate-400">Room:</span> <strong class="text-slate-800">${data.room_number}</strong></div>
                        <div><span class="text-slate-400">Category:</span> <strong class="text-slate-800">${data.category}</strong></div>
                    </div>
                    <p class="text-xs text-slate-700 bg-slate-50 p-2 rounded border border-slate-100">
                        "${escapeHtml(data.description)}"
                    </p>
                    <div class="pt-1 flex justify-end">
                        <button onclick="document.getElementById('view-complaints-btn').click()" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center">
                            View in Live Tracker &rarr;
                        </button>
                    </div>
                </div>
            `;
        }

        wrapper.innerHTML = `
            <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shrink-0 shadow-sm">
                <i data-lucide="bot" class="w-4 h-4"></i>
            </div>
            <div class="bg-slate-100/90 text-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%] text-sm leading-relaxed border border-slate-200/60 shadow-sm">
                <div class="bot-rendered-text">${htmlContent}</div>
                ${actionCardHtml}
            </div>
        `;
        messagesContainer.appendChild(wrapper);
        lucide.createIcons();
        scrollToBottom();
    }

    function showTyping(show) {
        if (show) {
            typingIndicator.classList.remove("hidden");
            scrollToBottom();
        } else {
            typingIndicator.classList.add("hidden");
        }
    }

    function scrollToBottom() {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 50);
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;
    }

    // Complaints Drawer Functions
    async function updateComplaintsCount() {
        try {
            const res = await fetch("/api/complaints");
            if (res.ok) {
                const list = await res.json();
                complaintsCounter.innerText = list.length;
            }
        } catch (e) {
            console.error("Could not fetch complaints count", e);
        }
    }

    function openComplaintsDrawer() {
        complaintsDrawer.classList.remove("hidden");
        loadComplaints();
    }

    function closeComplaintsDrawer() {
        complaintsDrawer.classList.add("hidden");
    }

    async function loadComplaints(roomNumber = null) {
        complaintsList.innerHTML = `<div class="text-center py-10 text-slate-400 text-xs">Loading database records...</div>`;
        try {
            let url = "/api/complaints";
            if (roomNumber) {
                url += `?room_number=${encodeURIComponent(roomNumber)}`;
            }
            const res = await fetch(url);
            const complaints = await res.json();

            if (complaints.length === 0) {
                complaintsList.innerHTML = `
                    <div class="text-center py-12 text-slate-400">
                        <i data-lucide="inbox" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
                        <p class="text-xs">No complaints found ${roomNumber ? 'for Room ' + roomNumber : 'in the database'}.</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            complaintsList.innerHTML = "";
            complaints.forEach(c => {
                const card = document.createElement("div");
                card.className = "p-3.5 bg-slate-50 hover:bg-white border border-slate-200 rounded-xl transition shadow-2xs space-y-2";
                
                const urgencyClass = `badge-urgency-${c.urgency}`;
                const statusClass = `badge-status-${c.status.replace(" ", "-")}`;

                card.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="font-mono text-xs font-bold text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">
                            ${c.id}
                        </span>
                        <div class="flex items-center space-x-1.5">
                            <span class="text-[11px] px-2 py-0.5 rounded-full font-semibold ${urgencyClass}">
                                ${c.urgency}
                            </span>
                            <span class="text-[11px] px-2 py-0.5 rounded-full font-semibold ${statusClass}">
                                ${c.status}
                            </span>
                        </div>
                    </div>
                    <div class="text-xs font-medium text-slate-800">
                        ${escapeHtml(c.description)}
                    </div>
                    <div class="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-200/60">
                        <span>Room <strong>${c.room_number}</strong> • ${c.category}</span>
                        <span>${c.created_at.split(" ")[0]}</span>
                    </div>
                `;
                complaintsList.appendChild(card);
            });
            lucide.createIcons();
        } catch (err) {
            complaintsList.innerHTML = `<div class="text-center py-8 text-rose-500 text-xs">Error loading complaints</div>`;
            console.error(err);
        }
    }

    // Mess Modal Functions
    async function openMenuModal() {
        menuModal.classList.remove("hidden");
        menuModalContent.innerHTML = `<div class="text-center py-8 text-slate-400">Loading weekly menu...</div>`;
        try {
            const res = await fetch("/api/mess-menu");
            const menu = await res.json();
            
            // Group by day
            const grouped = {};
            menu.forEach(item => {
                if (!grouped[item.day_of_week]) grouped[item.day_of_week] = [];
                grouped[item.day_of_week].push(item);
            });

            let html = "";
            for (const [day, items] of Object.entries(grouped)) {
                html += `
                    <div class="border border-slate-200 rounded-xl p-3 bg-slate-50/60">
                        <h4 class="font-bold text-sm text-indigo-900 mb-2">${day}</h4>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            ${items.map(m => `
                                <div class="bg-white p-2.5 rounded-lg border border-slate-200">
                                    <div class="flex items-center justify-between mb-1">
                                        <span class="font-semibold text-xs text-slate-800">${m.meal_type}</span>
                                        <span class="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono">${m.timing}</span>
                                    </div>
                                    <p class="text-xs text-slate-600 leading-snug">${m.items}</p>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            }
            menuModalContent.innerHTML = html;
        } catch (e) {
            menuModalContent.innerHTML = `<div class="text-rose-500 text-center py-6">Failed to load mess schedule</div>`;
        }
    }

    function closeMenuModal() {
        menuModal.classList.add("hidden");
    }
});
