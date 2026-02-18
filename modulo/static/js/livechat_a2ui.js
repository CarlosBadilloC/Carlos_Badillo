odoo.define('modulo.LivechatA2UIRender', function () {
    'use strict';

    const MARKER = '[[A2UI]]';

    function renderInNode(root) {
        if (!root || !root.querySelectorAll) {
            return;
        }
        const nodes = root.querySelectorAll('.o_livechat_message_content, .o_thread_message_content, .o_message_content');
        nodes.forEach((el) => {
            const text = (el.textContent || '').trim();
            if (text.startsWith(MARKER)) {
                const html = text.slice(MARKER.length);
                el.innerHTML = html;
            }
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        renderInNode(document);

        const observer = new MutationObserver((mutations) => {
            for (const m of mutations) {
                for (const node of m.addedNodes) {
                    if (node.nodeType === 1) {
                        renderInNode(node);
                    }
                }
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });
});