/* Local exports and accessible labels. No remote resources. */
window.saveDashboardFile = async function(filename, content, base64Encoded) {
    const status = text => window.dash_clientside.set_props('export-status', {children:text});
    try {
        if (window.pywebview && window.pywebview.api && window.pywebview.api.save_file) {
            const result = await window.pywebview.api.save_file(filename, content, base64Encoded);
            status(result.saved ? 'Saved ' + result.filename : 'Save cancelled.');
            return result;
        }
        const bytes = base64Encoded ? Uint8Array.from(atob(content), c => c.charCodeAt(0)) : content;
        const blob = new Blob([bytes], {type:base64Encoded ? 'image/png' : 'text/csv;charset=utf-8'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a'); link.href=url; link.download=filename; link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        status('Downloaded ' + filename);
        return {saved:true, filename:filename};
    } catch (error) { status('Export failed: ' + error.message); throw error; }
};
document.addEventListener('click', async function(event) {
    const button = event.target.closest('.png-export');
    if (!button) return;
    try {
        button.disabled = true;
        const id = button.getAttribute('data-chart');
        const plot = document.querySelector('#' + id + ' .js-plotly-plot');
        const dataURL = await window.Plotly.toImage(plot, {format:'png', scale:2});
        await window.saveDashboardFile('green-decoupling-' + id + '.png', dataURL.split(',')[1], true);
    } finally { button.disabled = false; }
});
// Dash's searchable controls render their input after their visible label.
const attachLabels = () => document.querySelectorAll('.field').forEach(field => {
    const label = field.querySelector('label');
    if (!label) return;
    field.querySelectorAll('input,[role="combobox"],button.dash-dropdown').forEach(input => {
        const name = input.matches('button.dash-dropdown') ? label.id + ' ' + input.id + '-value' : label.id;
        if (input.getAttribute('aria-labelledby') !== name) input.setAttribute('aria-labelledby', name);
    });
});
new MutationObserver(attachLabels).observe(document.documentElement, {childList:true, subtree:true});
document.addEventListener('DOMContentLoaded', attachLabels);
