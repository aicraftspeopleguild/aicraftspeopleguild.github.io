        // Configuration - UPDATE THESE VALUES
        const CONFIG = {
            SHEET_ID: '1WldGelJJZUkQc4-r9PaCwpNWcI9sc7Rtif_7XB7x7hc',  // Get this from the Sheet URL
            SHEET_NAME: 'Form Responses 1',     // Usually this is the default name
            API_KEY: 'YOUR_GOOGLE_API_KEY'      // Optional - for public sheets you may not need this
        };

        // Handle form submission
        const form = document.getElementById('signatureForm');
        const submitBtn = document.getElementById('submitBtn');
        const formStatus = document.getElementById('formStatus');

        form.addEventListener('submit', function(e) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            // Show success message after a delay (form submits to iframe)
            setTimeout(() => {
                formStatus.className = 'form-status success';
                formStatus.textContent = 'Thank you for signing the manifesto! Your signature will appear below shortly.';
                form.reset();
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign the Manifesto';
                
                // Reload signatures after 2 seconds
                setTimeout(() => {
                    loadSignatories();
                }, 2000);
            }, 1000);
        });

        // Spam / scam detection for signatory entries.
        // Returns true when ANY field of the row looks like spam.
        function isSpamEntry(row) {
            // Fields: [timestamp, name, title, org, email]
            const fields = [row[1], row[2], row[3]];
            const combined = fields.filter(Boolean).join(' ');

            // URL patterns
            if (/https?:\/\//i.test(combined)) return true;
            // Bare domain patterns with suspicious TLDs or known spam domains
            if (/[\w-]+\.(org|io|net|com)\/\S/i.test(combined)) return true;
            // Crypto / payment keywords
            if (/\b(usdc|usdt|btc|eth|payment|transfer|crypto|wallet|withdraw|deposit)\b/i.test(combined)) return true;
            // Arrow spam characters often used in phishing
            if (/➤|►|⇒|→{2,}/.test(combined)) return true;
            // Suspicious hash strings (long hex-like tokens in a name field)
            if (/[a-f0-9]{20,}/i.test(combined)) return true;
            return false;
        }

        // Function to load signatories from Google Sheets
        async function loadSignatories() {
            const signatoriesList = document.getElementById('signatoriesList');
            const signatoriesCount = document.getElementById('signatoriesCount');
            
            try {
                // For public sheets, you can use the published CSV URL
                const csvUrl = `https://docs.google.com/spreadsheets/d/${CONFIG.SHEET_ID}/gviz/tq?tqx=out:csv&sheet=${encodeURIComponent(CONFIG.SHEET_NAME)}`;
                
                const response = await fetch(csvUrl);
                const csvText = await response.text();
                
                // Parse CSV
                const rows = parseCSV(csvText);
                
                // Skip header row, filter spam, and reverse to show newest first
                const signatories = rows.slice(1).filter(row => !isSpamEntry(row)).reverse();
                
                // Update count
                signatoriesCount.textContent = `${signatories.length} ${signatories.length === 1 ? 'signatory' : 'signatories'}`;
                
                // Display signatories
                if (signatories.length === 0) {
                    signatoriesList.innerHTML = '<div class="loading">Be the first to sign!</div>';
                } else {
                    signatoriesList.innerHTML = signatories.map(row => {
                        // Assuming columns: Timestamp, Name, Title, Organization, Email
                        const name = row[1] || 'Anonymous';
                        const title = row[2] || '';
                        const org = row[3] || '';
                        
                        return `
                            <div class="signatory-card">
                                <div class="signatory-name">${escapeHtml(name)}</div>
                                ${title ? `<div class="signatory-title">${escapeHtml(title)}</div>` : ''}
                                ${org ? `<div class="signatory-org">${escapeHtml(org)}</div>` : ''}
                            </div>
                        `;
                    }).join('');
                }
            } catch (error) {
                console.error('Error loading signatories:', error);
                signatoriesList.innerHTML = '<div class="loading">Unable to load signatories. Please check back later.</div>';
                signatoriesCount.textContent = '';
            }
        }

        // Simple CSV parser
        function parseCSV(csv) {
            const rows = [];
            let currentRow = [];
            let currentField = '';
            let inQuotes = false;
            
            for (let i = 0; i < csv.length; i++) {
                const char = csv[i];
                const nextChar = csv[i + 1];
                
                if (char === '"') {
                    if (inQuotes && nextChar === '"') {
                        currentField += '"';
                        i++;
                    } else {
                        inQuotes = !inQuotes;
                    }
                } else if (char === ',' && !inQuotes) {
                    currentRow.push(currentField);
                    currentField = '';
                } else if ((char === '\n' || char === '\r') && !inQuotes) {
                    if (currentField || currentRow.length > 0) {
                        currentRow.push(currentField);
                        rows.push(currentRow);
                        currentRow = [];
                        currentField = '';
                    }
                    if (char === '\r' && nextChar === '\n') i++;
                } else {
                    currentField += char;
                }
            }
            
            if (currentField || currentRow.length > 0) {
                currentRow.push(currentField);
                rows.push(currentRow);
            }
            
            return rows;
        }

        // Escape HTML to prevent XSS
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Load signatories on page load
        loadSignatories();

        // Refresh signatories every 30 seconds
        setInterval(loadSignatories, 30000);

        // Scroll reveal animation
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.scroll-reveal').forEach(el => {
            observer.observe(el);
        });

        // Smooth scroll for in-page anchor links ONLY (e.g. "#manifesto", "#sign").
        // Route hashes (#/charter, #/members, ...) must fall through to the
        // hashchange listener in renderer.js. Without this guard, the code was
        // calling document.querySelector("#/charter") — invalid selector → throws —
        // and preventDefault() was blocking the hash change before the route fired.
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (!href || href === '#' || href.startsWith('#/')) return;  // route hashes
                e.preventDefault();
                let target;
                try { target = document.querySelector(href); } catch { return; }
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
